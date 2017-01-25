import logging

from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.schema import Email

from docent.group.vocabularies.vocabularies import BOOSTER_BOARD_MEMBERS_GROUP_ID
from docent.boosters.clubmanagement import _

logger = logging.getLogger("Plone")

class IBoosterClubsFolder(form.Schema):
    """
    Uses IDublinCore
    """

    executive_secretary_email = Email(
        title=_(u"Executive Secretary Email"),
        description=_(u"Email address of the Executive Secretary"),
        required=False,
    )

class BoosterClubsFolder(Container):
    """
    Baseclass for BoosterClubsFolder based on Container
    """

    def after_creation_processor(self):
        """Add Booster Board Members as a reviewer and reindex."""
        #get the booster board members club
        try:
            booster_board_members_group = api.group.get(groupname=BOOSTER_BOARD_MEMBERS_GROUP_ID)
        except ValueError:
            return

        self.manage_setLocalRoles(BOOSTER_BOARD_MEMBERS_GROUP_ID, ['Reviewer'])

