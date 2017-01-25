from collections import defaultdict, Counter
from datetime import date
import logging

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
        api.content.transition(obj=self, to_state='pending')

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
        club_officer_list.append(context.club_president)
        club_officer_list.append(context.club_secretary)
        club_officer_list.append(context.club_treasurer)
        club_officer_list.append(context.club_advisor)
        officer_counter = Counter(club_officer_list)

        for member_key in officer_counter.keys():
            if officer_counter[member_key] > 2:
                try:
                    officer = api.user.get(username=member_key)
                    fullname = officer.getProperty('fullname')
                except MissingParameterError:
                    fullname = "The member with id: %s" % member_key

                if member_key == 'no_members':
                    portal_msg = 'There are not enough officers to manage this club. ' \
                                 'Please assign all officers before this club can be approved.'
                else:
                    portal_msg = "%s cannot hold more than two officer positions for this club. The " \
                                 "club cannot be approved until this is changed." % fullname

                api.portal.show_message(message=portal_msg,
                                        request=context.REQUEST,
                                        type='warn')
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
