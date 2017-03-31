from plone import api
from plone.api.exc import GroupNotFoundError

from docent.boosters.clubmanagement.content.booster_clubs_folder import IBoosterClubsFolder
from docent.boosters.clubmanagement.content.bootser_club import IBoosterClub

from docent.group.vocabularies.app_config import TRAINING_MEMBERS_GROUP_ID

from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implementer


def getGroupMemberVocabulary(group_name):
    """Return a set of groupmembers, return an empty set if group not found
    """
    try:
        group_members = api.user.get_users(groupname=group_name)
    except GroupNotFoundError:
        group_members = ()

    member_fullname_by_id_dict = {}
    for member_data in set(group_members):
        member_id = member_data.getId()
        member_fullname = member_data.getProperty('fullname')
        member_fullname_by_id_dict.update({member_id:member_fullname})

    terms = []

    if member_fullname_by_id_dict:
        terms.append(SimpleVocabulary.createTerm('', '', 'Choose One'))
        for id_key, name_value in sorted(member_fullname_by_id_dict.iteritems(), key=lambda (k,v): (v,k)):
            terms.append(SimpleVocabulary.createTerm(id_key, str(id_key), name_value))
    else:
        terms.append(SimpleVocabulary.createTerm('no_members', 'no_members', 'No Members'))

    return SimpleVocabulary(terms)


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

        approved_club_brains = catalog(path={'query': pc_path, 'depth': 1},
                                     object_provides=IBoosterClub.__identifier__,
                                     review_state='approved',
                                     sort_on='getObjPositionInParent')
        terms = []

        expected_clubs = active_club_brains + approved_club_brains

        if expected_clubs:
            for expected_club in expected_clubs:
                club_uid = expected_club.UID
                club_title = expected_club.Title
                terms.append(SimpleVocabulary.createTerm(club_uid, str(club_uid), club_title))
        else:
            terms.append(SimpleVocabulary.createTerm('no_clubs', 'no_clubs', 'No Active Clubs'))

        return SimpleVocabulary(terms)
IActiveBoosterClubVocabularyFactory = IActiveBoosterClubVocabulary()


@implementer(IVocabularyFactory)
class ITrainingRecordVocabulary(object):
    """
    build a vocabulary based on a the Trained Member Group
    """
    def __call__(self, context):
        return getGroupMemberVocabulary(TRAINING_MEMBERS_GROUP_ID)
ITrainingRecordVocabularyFactory = ITrainingRecordVocabulary()