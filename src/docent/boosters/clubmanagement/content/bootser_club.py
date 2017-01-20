import logging

from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.indexer import indexer
from plone.namedfile.field import NamedBlobFile
from zope import schema

from docent.boosters.clubmanagement import _

logger = logging.getLogger("Plone")

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

    form.write_permission(approval_date='manageBoosterClubs')
    approval_date = schema.Date(
        title=_(u'Date Approved'),
        description=_(u'This is a calculated field. Do not input.'),
        required=False,)

@indexer(IBoosterClub)
def organization_indexer(obj):
    if obj.booster_organization is None:
        return None
    return obj.booster_organization

@indexer(IBoosterClub)
def approval_date_indexer(obj):
    if not getattr(obj, 'approval_date', None):
        return None
    return obj.approval_date


class BoosterClub(Container):
    """
    Baseclass for BoosterClub based on Container
    """