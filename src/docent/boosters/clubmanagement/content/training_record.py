from datetime import date
import logging

from plone import api
from plone.api.exc import (MissingParameterError,
                           UserNotFoundError)
from plone.dexterity.content import Item
from plone.directives import form
from zope import schema


from docent.boosters.clubmanagement import _
from docent.group.vocabularies.app_config import (TRAINING_MEMBERS_GROUP_ID,
                                                  TRAINED_MEMBERS_GROUP_ID)

logger = logging.getLogger("Plone")


def computeTitle():
    date_obj = date.today()
    date_str = date_obj.strftime('%B %d %Y')

    return u'Training %s' % date_str


class ITrainingRecord(form.Schema):
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

    members_present = schema.List(
        title=_(u'Members in Attendance'),
        description=_(u"Select the booster members that attended tonight's meeting"),
        value_type=schema.Choice(vocabulary=u'docent.boosters.Training_Records',),
        required=True,
    )

    form.mode(members_absent='hidden')
    members_absent = schema.List(
        title=_(u'Members Absent'),
        description=_(u"Member Ids of members not attending the meeting."),
        value_type=schema.ASCIILine(),
        required=False,
    )

    form.mode(members_emailed='hidden')
    members_emailed = schema.List(
        title=_(u'Members Emailed'),
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


class TrainingRecord(Item):
    """
    Baseclass for AttendanceRecord based on Container
    """

    def after_object_added_processor(self, context, event):
        """
        Depricated instead called by transition as send_club_notice
        :param context:
        :param event:
        :return:
        """
        pass

    def after_transition_processor(self):
        context_state = api.content.get_state(obj=self)
        if context_state == 'published':
            self.send_member_notice()


    def send_member_notice(self):
        """
        Assemble a list of booster members that did not attend the meeting
        :return:
        """
        context = self
        parent_container = context.aq_parent

        expected_members = api.user.get_users(groupname=TRAINING_MEMBERS_GROUP_ID)

        expected_members_by_id = []
        [expected_members_by_id.append(member_data.getId()) for member_data in expected_members]

        members_present = getattr(context, 'members_present', [])

        members_absent = set(expected_members_by_id) - set(members_present)
        setattr(context, 'members_absent', list(members_absent))

        if members_absent:
            setattr(context, 'missing_member_data', members_absent)

            training_absence_notice_text = getattr(parent_container, 'training_absence_notice', '')
            booster_secretary_email = getattr(parent_container, 'executive_secretary_email', '')
            email_errors =[]
            members_emailed = []

            for attending_member_id in members_present:
                #remove from training group
                remove_user_error = False
                add_user_error = False

                try:
                    api.group.remove_user(groupname=TRAINING_MEMBERS_GROUP_ID,
                                          username=attending_member_id)
                except ValueError:
                    remove_user_error = True
                except UserNotFoundError:
                    remove_user_error = True

                try:
                    api.group.add_user(groupname=TRAINED_MEMBERS_GROUP_ID,
                                       username=attending_member_id)
                except ValueError:
                    add_user_error = True
                except UserNotFoundError:
                    add_user_error = True

                if remove_user_error or add_user_error:
                    a_member_obj = api.user.get(username=attending_member_id)
                    am_fullname = a_member_obj.getProperty('fullname')
                    if remove_user_error:
                        rue_msg = "There was a problem removing %s from the Training group." % am_fullname
                        api.portal.show_message(message=rue_msg,
                                        request=context.REQUEST,
                                        type='warn')
                    if add_user_error:
                        aue_msg = "There was a problem adding %s to the Trained group." % am_fullname
                        api.portal.show_message(message=aue_msg,
                                        request=context.REQUEST,
                                        type='warn')

            for member_id in members_absent:
                #get the club
                member_obj = api.user.get(username=member_id)
                m_email_address = member_obj.getProperty('email')
                m_fullname = member_obj.getProperty('fullname')
                m_tuple = (m_email_address, m_fullname, member_id)

                msg = "Hi %s,\n\n" % m_fullname
                msg += training_absence_notice_text
                try:
                    api.portal.send_email(sender=booster_secretary_email,
                                          recipient=m_email_address,
                                          subject="LHWS Boosters Best Practices Training Absence",
                                          body=msg,
                                          immediate=True,)
                    members_emailed.append(m_tuple)
                except Exception as e:
                    logger.warn("TRAINING RECORD: An error occurred when sending email "
                                "to: %s, the error was: %s" % (m_email_address, e.message))
                    email_errors.append(m_tuple)

            if email_errors:
                error_msg = "The following Members had errors while sending their absence notice. Please ask an " \
                            "administrator to check the logs for details.\n\n"

                members_with_errors = []
                [members_with_errors.append(error_tuple[1]) for error_tuple in email_errors]
                error_msg += ", ".join(members_with_errors)

                api.portal.show_message(message=error_msg,
                                        request=context.REQUEST,
                                        type='warn')

            set_of_member_tuples_sent = set(members_emailed) - set(email_errors)
            final_emails_sent = set()
            [final_emails_sent.add(mts_tuple[1]) for mts_tuple in set_of_member_tuples_sent]
            setattr(context, 'members_emailed', list(final_emails_sent))

            api.portal.show_message(message="%s emails were sent to absent members." % len(final_emails_sent),
                                    request=context.REQUEST,
                                    type='info')
