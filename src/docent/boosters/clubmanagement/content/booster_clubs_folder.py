import logging

from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from plone.schema import Email

from zope import schema

from docent.group.vocabularies.vocabularies import BOOSTER_BOARD_MEMBERS_GROUP_ID
from docent.boosters.clubmanagement import _

logger = logging.getLogger("Plone")


def getAbsenceDefaultText():
    absence_text = u"We had our booster meeting last night.\n\nYou're receiving this email because no one from your " \
                   u"booster club attended this meeting.\n\nIn the membership application all boosters agreed to, " \
                   u"there is a requirement to send at least one person from each club to the monthly booster meeting. " \
                   u"Please attend the next meeting.\n\nAll booster meetings are listed on our website " \
                   u"(lwhsboosters.org). Also, for registered members, meeting reminders are sent out. Please contact " \
                   u"me if you need help registering on the booster website.\n\nThanks for being part of boosters. " \
                   u"LWHS is better because of our work.\n\nSincerely,\nSecretary, LWHS Boosters"

    return absence_text


class IBoosterClubsFolder(form.Schema):
    """
    Uses IDublinCore
    """

    executive_secretary_email = Email(
        title=_(u"Executive Secretary Email"),
        description=_(u"Email address of the Executive Secretary"),
        required=True,
    )

    absence_notice = schema.Text(
        title=_(u"Absence Notice"),
        description=_(u"Text of email to be sent to absent booster club officers. "
                      u"This is a multi line field and line breaks will be recognized. "
                      u"The salutation should not be part of this message."),
        required=True,
        defaultFactory=getAbsenceDefaultText,
    )

    agreement_file = NamedBlobFile(
        title=_(u"Agreement File"),
        description=_(u"This file is to be downloaded by club for the approval process."),
        required=False,
    )


class BoosterClubsFolder(Container):
    """
    Baseclass for BoosterClubsFolder based on Container
    """

    def after_creation_processor(self, context, event):
        """Add Booster Board Members as a reviewer and reindex."""
        #get the booster board members club
        try:
            booster_board_members_group = api.group.get(groupname=BOOSTER_BOARD_MEMBERS_GROUP_ID)
        except ValueError:
            return

        self.manage_setLocalRoles(BOOSTER_BOARD_MEMBERS_GROUP_ID, ['Reviewer'])

