from plone import api

from docent.boosters.clubmanagement.content.booster_clubs_folder import IBoosterClubsFolder
from docent.boosters.clubmanagement.content.bootser_club import IBoosterClub

from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implementer


@implementer(IVocabularyFactory)
class IActiveBoosterClubVocabulary(object):
    """
    build a vocabulary based on a the Booster Board Member Group
    """
    def __call__(self, context):
        """
        If called from an add view, the container will be the context,
        however if called from an edit view, the context will be the
        attendance_record so we need find the actual booster_clubs_folder
        in order to search for active clubs
        """
        if context.portal_type == "booster_clubs_folder":
            parent_container = context
        else:
            parent_container = context.aq_parent

        #if the parent_container is not a booster_clubs_folder, give up!
        if parent_container.portal_type != "booster_clubs_folder":
            return SimpleVocabulary([SimpleVocabulary.createTerm('--', '--', 'Booster Clubs Folder Not Found')])

        pc_path = '/'.join(parent_container.getPhysicalPath())
        catalog = getToolByName(parent_container, 'portal_catalog')

        active_club_brains = catalog(path={'query': pc_path, 'depth': 1},
                                     object_provides=IBoosterClub.__identifier__,
                                     review_state='active',
                                     sort_on='getObjPositionInParent')

        terms = []
        if active_club_brains:
            for active_club in active_club_brains:
                club_uid = active_club.UID
                club_title = active_club.Title
                terms.append(SimpleVocabulary.createTerm(club_uid, str(club_uid), club_title))
        else:
            terms.append(SimpleVocabulary.createTerm('no_clubs', 'no_clubs', 'No Active Clubs'))

        return SimpleVocabulary(terms)
IActiveBoosterClubVocabularyFactory = IActiveBoosterClubVocabulary()