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

from docent.boosters.clubmanagement import _
from docent.boosters.clubmanagement.content.bootser_club import IBoosterClub


logger = logging.getLogger("Plone")


class IAttendanceRecord(form.Schema):
    """
    Uses IDublinCore
    """

    clubs_present = schema.List(
        title=_(u'Clubs in Attendance'),
        description=_(u"Select the teams that attended tonight's meeting"),
        value_type=schema.Choice(vocabulary=u'docent.boosters.Active_Clubs',),
    )


class AttendanceRecord(Item):
    """
    Baseclass for AttendanceRecord based on Container
    """

    def after_edit_processor(self):
        pass

