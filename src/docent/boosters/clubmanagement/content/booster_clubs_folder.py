import logging

from plone.dexterity.content import Container
from plone.directives import form
from plone.schema import Email

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