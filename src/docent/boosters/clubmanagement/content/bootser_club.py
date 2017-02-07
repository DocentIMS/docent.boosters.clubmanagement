from collections import defaultdict, Counter
from datetime import datetime, date
import logging

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser

from DateTime import DateTime
import math
from plone import api
from plone.api.exc import MissingParameterError
from plone.dexterity.content import Container
from plone.directives import form
from plone.indexer import indexer
from plone.namedfile.field import NamedBlobFile
from plone.supermodel.directives import fieldset

from Products.CMFCore.utils import getToolByName
from zope import schema
from zope.interface import invariant, Invalid

from docent.boosters.clubmanagement import _

logger = logging.getLogger("Plone")

from docent.group.vocabularies.vocabularies import TRAINED_MEMBERS_GROUP_ID

def validateAccept(value):
    if not value == True:
        return False
    return True



class IBoosterClub(form.Schema):
    """
    Uses IDublinCore
    """
    # fieldset('booster_club_information',
    #     label=u'Booster Club Information',
    #     fields=['title', 'booster_organization']
    # )

    title = schema.TextLine(
        title=_(u"Club Name"),
    )

    booster_organization = schema.TextLine(
        title=_(u"LWHS Organization"),
        required=True,
    )

    # fieldset('officer_information',
    #     label=u'Officer Information',
    #     description=u'Note:  Two board members must have the "Good Practices Training" before the club can be approved. '
    #                 u'You may submit your application, and it will be held until this requirement is met. Also, one '
    #                 u'person may hold up to two Officer positions."',
    #     fields=['club_president',
    #             'club_secretary',
    #             'club_treasurer',]
    # )

    club_president = schema.Choice(
        title=_(u"President"),
        vocabulary=u'docent.group.Booster_Members',
        required=True,
        )

    club_secretary = schema.Choice(
        title=_(u"Secretary"),
        vocabulary=u'docent.group.Booster_Members',
        required=True,
        )

    club_treasurer = schema.Choice(
        title=_(u"Treasurer"),
        vocabulary=u'docent.group.Booster_Members',
        required=True,
        )

    # fieldset('advisor_information',
    #     label=u'Advisor Information',
    #     description=u'',
    #     fields=['club_advisor',]
    # )

    club_advisor = schema.Choice(
        title=_(u"LWHS Advisor"),
        vocabulary=u'docent.group.Advisors',
        )

    # fieldset('agreement_upload',
    #     label=u'File',
    #     description=u'<p>1) We still need the paper form completed and uploaded.  Please download the Agreement.</p>'
    #                 u'<p>2) Once completed, please upload the form.</p>',
    #     fields=['agreement_file',]
    # )
    #
    # agreement_file = NamedBlobFile(
    #     title=_(u"File"),
    # )

    # fieldset('financial_information',
    #     label=u'Financial Information',
    #     description=u'',
    #     fields=['dedicated_checking', 'review_officers', 'review_revenue',
    #             'review_officer_one', 'review_officer_two']
    # )

    dedicated_checking = schema.Bool(
        title=_(u'1. Does your group maintain a dedicated checking account?'),
        description=_(u''),
        constraint=validateAccept)

    review_officers = schema.Bool(
        title=_(u'2. Do two officers review expenditures?'),
        description=_(u''),
        constraint=validateAccept)

    review_revenue = schema.Bool(
        title=_(u'3. Do two officers review revenues?'),
        description=_(u''),
        constraint=validateAccept)

    review_officer_one = schema.Choice(
        title=_(u"4. Review Officer One."),
        description=_(u"Select the name of of your first review officer. It must match on of "
                      u"your club officers."),
        vocabulary=u'docent.group.Booster_Members',
        required=True,
        )

    review_officer_two = schema.Choice(
        title=_(u"4. Review Officer Two."),
        description=_(u"Select the name of of your second review officer. It must match on of "
                      u"your club officers."),
        vocabulary=u'docent.group.Booster_Members',
        required=True,
        )

    # fieldset('agreement_confirmation',
    #     label=u'Agreement',
    #     description=_(u'I understand and agree to abide by the membership agreement and '
    #                   u'financial reporting requirements'),
    #     fields=['agreement_bool',]
    # )

    agreement_bool = schema.Bool(
        title=_(u'I agree'),
        description=_(u'I understand and agree to abide by the membership agreement and '
                      u'financial reporting requirements'),
        constraint=validateAccept,
    )

    form.mode(approval_date='hidden')
    approval_date = schema.Date(
        title=_(u'Date Approved'),
        description=_(u'This is a calculated field. Do not input.'),
        required=False,)

    @invariant
    def officerInvariant(data):
        if data.club_president == data.club_secretary:
            raise Invalid(_(u"The club president and secretary cannot be the same individual."))

    @invariant
    def reviewerInvariant(data):
        if data.review_officer_one == data.review_officer_two:
            raise Invalid(_(u"The reviewing officers cannot be the same people."))
        club_officers = [data.club_president, data.club_secretary, data.club_treasurer]
        if data.review_officer_one not in club_officers:
            raise Invalid(_(u"Reviewing officer one must a club officer."))
        if data.review_officer_two not in club_officers:
            raise Invalid(_(u"Reviewing officer two must a club officer."))

class BoosterClub(Container):
    """
    Baseclass for BoosterClub based on Container
    """
    security = ClassSecurityInfo()

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
                if officer:
                    fullname = officer.getProperty('fullname')
                else:
                    fullname = "The member with id: %s" % club_president
            except MissingParameterError:
                fullname = "The member with id: %s" % club_president

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

    security.declarePublic('attendanceRecord')
    def attendanceRecord(self):
        context = self
        approval_date = getattr(context, 'approval_date', None)
        if not approval_date:
            return ''
        approval_datetime = datetime.combine(approval_date, datetime.min.time())
        approval_DateTime = DateTime(approval_datetime)

        parent_container = self.aq_parent
        context_path = '/'.join(parent_container.getPhysicalPath())

        catalog = getToolByName(context, 'portal_catalog')
        from docent.boosters.clubmanagement.content.attendance_record import IAttendanceRecord
        attendance_record_brains = catalog.unrestrictedSearchResults(path={'query': context_path, 'depth': 1},
                                     object_provides=IAttendanceRecord.__identifier__,
                                     sort_on='getObjPositionInParent')

        if not attendance_record_brains:
            return 'No Records Found'

        attendance_records_since_club_approval = []
        for a_r in attendance_record_brains:
            if approval_DateTime <= a_r.created:
                attendance_records_since_club_approval.append(a_r)

        if not attendance_records_since_club_approval:
            return '0%'

        context_uid = context.UID()
        meetings_since_creation = len(attendance_records_since_club_approval)

        attended = 0
        for attendance_record in attendance_records_since_club_approval:
            clubs_present = attendance_record.clubs_present
            if not clubs_present:
                continue
            if context_uid in clubs_present:
                attended += 1

        percentage_attended = math.ceil(100 * float(attended)/float(meetings_since_creation))
        return '%s%%' % int(percentage_attended)