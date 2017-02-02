from collections import defaultdict, Counter
from datetime import date
import logging

from plone import api
from plone.api.exc import MissingParameterError
from plone.dexterity.content import Item
from plone.directives import form
from plone.indexer import indexer
from plone.namedfile.field import NamedBlobFile
from Products.CMFCore.utils import getToolByName
from zope import schema

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implementer
from zope.interface import implements

from docent.boosters.clubmanagement import _
from docent.boosters.clubmanagement.content.bootser_club import IBoosterClub


logger = logging.getLogger("Plone")


def computeTitle():
    date_obj = date.today()
    date_str = date_obj.strftime('%B %Y')

    return u'%s' % date_str

class IAttendanceRecord(form.Schema):
    """
    Uses IDublinCore
    """

    title = schema.TextLine(
        title=_(u"Meeting Date"),
        required=True,
        defaultFactory=computeTitle,
    )

    description = schema.Text(
        title=_(u"Summary"),
        description=_(u"A summary of the meeting."),
        required=False,
    )

    clubs_present = schema.List(
        title=_(u'Clubs in Attendance'),
        description=_(u"Select the teams that attended tonight's meeting"),
        value_type=schema.Choice(vocabulary=u'docent.boosters.Active_Clubs',),
        required=True,
    )

    form.mode(clubs_absent='hidden')
    clubs_absent = schema.List(
        title=_(u'Clubs Absent'),
        description=_(u"UID of teams not attending the meeting."),
        value_type=schema.ASCIILine(),
        required=False,
    )

    form.mode(club_officers_emailed='hidden')
    club_officers_emailed = schema.List(
        title=_(u'Club Officers Emailed'),
        description=_(u"Email address of club members emailed."),
        value_type=schema.TextLine(),
        required=False,
    )

    form.mode(missing_member_data='hidden')
    missing_member_data = schema.List(
        title=_(u'Missing Member Data'),
        description=_(u"Member ids with no member data"),
        value_type=schema.ASCIILine(),
        required=False,
    )


class AttendanceRecord(Item):
    """
    Baseclass for AttendanceRecord based on Container
    """

    def after_object_added_processor(self, context, event):
        """
        Assemble a list of booster clubs that did not attend the meeting
        :return:
        """
        parent_container = event.newParent
        pc_path = '/'.join(parent_container.getPhysicalPath())
        catalog = getToolByName(parent_container, 'portal_catalog')
        active_club_brains = catalog(path={'query': pc_path, 'depth': 1},
                                     object_provides=IBoosterClub.__identifier__,
                                     review_state='active',
                                     sort_on='getObjPositionInParent')

        approved_club_brains = catalog(path={'query': pc_path, 'depth': 1},
                                     object_provides=IBoosterClub.__identifier__,
                                     review_state='approved',
                                     sort_on='getObjPositionInParent')

        expected_clubs = active_club_brains + approved_club_brains
        expected_clubs_by_uid = []
        [expected_clubs_by_uid.append(ec_brain.UID) for ec_brain in expected_clubs]

        clubs_present = getattr(context, 'clubs_present', [])

        clubs_absent = set(expected_clubs_by_uid) - set(clubs_present)
        setattr(context, 'clubs_absent', list(clubs_absent))

        #now assemble a list of emails to send email regarding their absence.
        club_officer_identifiers = ['club_president',
                                    'club_secretary',
                                    'club_treasurer',]

        email_recipients = [] #list of tuples (email_address, fullname)
        missing_members = []

        for club_uid in clubs_absent:
            #get the club
            club_obj = api.content.get(UID=club_uid)
            for officer_id in club_officer_identifiers:
                officer_member_id = getattr(club_obj, officer_id, '')
                if officer_member_id and officer_member_id != 'no_members':
                    #get the member
                    try:
                        officer_member_data = api.user.get(userid=officer_member_id)
                    except MissingParameterError:
                        logger.warn("ATTENDANCE RECORD: Could not find member_data for %s" % officer_member_id)
                        missing_members.append(officer_member_id)
                        continue

                    email_address = officer_member_data.getProperty('email')
                    fullname = officer_member_data.getProperty('fullname')
                    member_tuple = (email_address, fullname, officer_member_id)
                    email_recipients.append(member_tuple)

        if missing_members:
            setattr(context, 'missing_member_data', missing_members)

        if email_recipients:
            club_officers_emailed = []
            email_errors = []
            absence_notice_text = getattr(parent_container, 'absence_notice', '')
            booster_secretary_email = getattr(parent_container, 'executive_secretary_email', '')
            email_recipients_set = set(email_recipients)
            for m_tuple in email_recipients_set:
                m_email_address, m_fullname, m_id = m_tuple
                club_officers_emailed.append(m_tuple)
                msg = "Hi %s,\n\n" % fullname
                msg += absence_notice_text
                try:
                    api.portal.send_email(sender=booster_secretary_email,
                                          recipient=m_email_address,
                                          subject="Booster Club Meeting Absence",
                                          body=msg,
                                          immediate=True,)
                except Exception as e:
                    logger.warn("ATTENDANCE RECORD: An error occurred when sending email "
                                "to: %s, the error was: %s" % (m_email_address, e.message))
                    email_errors.append(m_tuple)

            if email_errors:
                error_msg = "The following Members had errors while sending their absence notice. Please ask an" \
                            "administrator to check the logs for details.\n\n"
                for error_tuple in email_errors:
                    error_msg += ", ".join(error_tuple[1])

                api.portal.show_message(message=error_msg,
                                        request=context.REQUEST,
                                        type='warn')

            set_of_member_tuples_sent = set(club_officers_emailed) - set(email_errors)
            final_emails_sent = set()
            [final_emails_sent.add(mts_tuple[1]) for mts_tuple in set_of_member_tuples_sent]
            setattr(context, 'club_officers_emailed', list(final_emails_sent))

            api.portal.show_message(message="%s emails were sent to absent members." % len(final_emails_sent),
                                    request=context.REQUEST,
                                    type='info')
