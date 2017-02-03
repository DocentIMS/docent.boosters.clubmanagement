from collections import defaultdict, Counter
from datetime import date
import logging

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser

from plone import api
from plone.api.exc import MissingParameterError
from plone.dexterity.content import Container
from plone.directives import form
from plone.indexer import indexer
from plone.namedfile.field import NamedBlobFile

from zope import schema

from docent.boosters.clubmanagement import _

logger = logging.getLogger("Plone")

from docent.group.vocabularies.vocabularies import TRAINED_MEMBERS_GROUP_ID

class IBoosterClub(form.Schema):
    """
    Uses IDublinCore
    """

    booster_organization = schema.TextLine(
        title=_(u"LWHS Organization"),
        description=_(u"Enter the name of the LWHS Boosterr organization sponsoring this club."),
        required=False,
    )

    club_president = schema.Choice(
        title=_(u"President"),
        description=_(u"Select LWHS Booster member that will serve as club president."),
        vocabulary=u'docent.group.Booster_Members',
        required=False,
        )

    club_secretary = schema.Choice(
        title=_(u"Secretary"),
        description=_(u"Select LWHS Booster member that will serve as club secretary."),
        vocabulary=u'docent.group.Booster_Members',
        required=False,
        )

    club_treasurer = schema.Choice(
        title=_(u"Treasurer"),
        description=_(u"Select LWHS Booster member that will serve as club treasurer."),
        vocabulary=u'docent.group.Booster_Members',
        required=False,
        )

    club_advisor = schema.Choice(
        title=_(u"LWHS Advisor"),
        description=_(u"Select LWHS Advisor for this club."),
        vocabulary=u'docent.group.Advisors',
        required=False,
        )

    agreement_file = NamedBlobFile(
        title=_(u"File"),
        description=_(u"Upload the completed Agreement file."),
        required=False,
    )

    agreement_bool = schema.Bool(
        title=_(u'I agree'),
        description=_(u'I understand and agree to abide by the membership agreement and '
                      u'financial reporting requirements'),
        required=False,
        default=False)

    form.mode(approval_date='hidden')
    approval_date = schema.Date(
        title=_(u'Date Approved'),
        description=_(u'This is a calculated field. Do not input.'),
        required=False,)


class BoosterClub(Container):
    """
    Baseclass for BoosterClub based on Container
    """

    def after_edit_processor(self):
        """
        all edits should change the workflow state back to pending
        """
        #create a temporary security manage
        sm = getSecurityManager()
        role = 'Manager'
        tmp_user = BaseUnrestrictedUser(sm.getUser().getId(), '', [role], '')
        portal= api.portal.get()
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)

        try:
            api.content.transition(obj=self, to_state='pending')
            #reset security manager!
            setSecurityManager(sm)
        except Exception as e:
            setSecurityManager(sm)
            logger.warn("BoosterClub: There was an error %s transitioning to the Pending workflow" % self.absolute_url())
            logger.warn("BoosterClub: The error was: %s" % e.message)
            api.portal.show_message(message="There was an error updating your club. Please contact an administrator.",
                                        request=self.REQUEST,
                                        type='warn')


    def after_transition_editor(self):
        context_state = api.content.get_state(obj=self)
        if context_state == 'approved':
            sm = getSecurityManager()
            role = 'Manager'
            tmp_user = BaseUnrestrictedUser(sm.getUser().getId(), '', [role], '')
            portal= api.portal.get()
            tmp_user = tmp_user.__of__(portal.acl_users)
            newSecurityManager(None, tmp_user)
            try:
                self.set_approval_date()
                #reset security manager!
                setSecurityManager(sm)
            except Exception as e:
                setSecurityManager(sm)
                logger.warn("BoosterClub: There was an error %s transitioning to the Pending workflow" % self.absolute_url())
                logger.warn("BoosterClub: The error was: %s" % e.message)
                api.portal.show_message(message="There was an error updating your club. Please contact an administrator.",
                                            request=self.REQUEST,
                                            type='warn')


    def set_approval_date(self):
        today = date.today()
        setattr(self, 'approval_date', today)


    def verifyClubOfficers(self):
        """
        Officers cannot hold more than two positions.
        :return:
        """
        context = self
        club_officer_list = []
        missing_officers = []

        club_president = context.club_president
        if not club_president or club_president == 'no_members':
            missing_officers.append('President')
        else:
            club_officer_list.append(club_president)

        club_secretary = context.club_secretary
        if not club_secretary or club_secretary == 'no_members':
            missing_officers.append('Secretary')
        else:
            club_officer_list.append(club_secretary)

        club_treasurer = context.club_treasurer
        if not club_treasurer or club_treasurer == 'no_members':
            missing_officers.append('Treasurer')
        else:
            club_officer_list.append(club_treasurer)

        club_advisor = context.club_advisor
        if club_advisor and club_advisor != 'no_members':
            club_officer_list.append(club_advisor)

        flag_errors = False
        if missing_officers:
            missing_officers_msg = "All officer positions need to be filled by a Booster member. " \
                                   "The proposal cannot progress until the following positions are " \
                                   "filled: %s." % ', '.join(missing_officers)
            api.portal.show_message(message=missing_officers_msg,
                                    request=context.REQUEST,
                                    type='warn')
            flag_errors = True

        officer_counter = Counter(club_officer_list)
        for member_key in officer_counter.keys():
            if officer_counter[member_key] > 2:
                try:
                    officer = api.user.get(username=member_key)
                    fullname = officer.getProperty('fullname')
                except MissingParameterError:
                    fullname = "The member with id: %s" % member_key

                portal_msg = "%s cannot hold more than two officer positions for this club. The " \
                             "club cannot be approved until this is changed." % fullname

                api.portal.show_message(message=portal_msg,
                                        request=context.REQUEST,
                                        type='warn')
                flag_errors = True

        if club_president == club_secretary:
            try:
                officer = api.user.get(username=club_president)
                fullname = officer.getProperty('fullname')
            except MissingParameterError:
                fullname = "The member with id: %s" % member_key

            portal_msg = "%s cannot hold both the President and Secretary positions. The club cannot be approved " \
                         "until this is changed." % fullname

            api.portal.show_message(message=portal_msg,
                                    request=context.REQUEST,
                                    type='warn')
            flag_errors = True

        if flag_errors:
            return False

        return True

    def officersHaveTraining(self):
        context = self
        club_officer_list = []
        club_officer_list.append(context.club_president)
        club_officer_list.append(context.club_secretary)
        club_officer_list.append(context.club_treasurer)

        has_training = 0

        for club_officer in set(club_officer_list):
            if club_officer == 'no_members':
                continue
            if club_officer is None:
                continue
            officer_groups = api.group.get_groups(username=club_officer)
            for o_group in officer_groups:
                if o_group.getId() == TRAINED_MEMBERS_GROUP_ID:
                    has_training += 1

        if has_training >= 2:
            return True

        api.portal.show_message(message="Waiting for club officers to be trained. Club cannot be activated until its "
                                        "officers are trained.",
                                        request=context.REQUEST,
                                        type='warn')
        return False
