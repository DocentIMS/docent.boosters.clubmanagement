import logging
from five import grok
from plone import api
from Products.CMFCore.utils import getToolByName

from docent.boosters.clubmanagement.content.booster_clubs_folder import IBoosterClubsFolder
from docent.boosters.clubmanagement.content.bootser_club import IBoosterClub

logger = logging.getLogger("Plone")

grok.templatedir('templates')

class View(grok.View):
    grok.context(IBoosterClubsFolder)
    grok.require("zope2.View")
    grok.template("boosterclubsfolder")

    def update(self):
        portal = api.portal.get()
        context = self.context
        context_path = '/'.join(context.getPhysicalPath())

        catalog = getToolByName(portal, 'portal_catalog')

        active_club_brains = catalog(path={'query': context_path, 'depth': 1},
                                     object_provides=IBoosterClub.__identifier__,
                                     review_state='active',
                                     sort_on='getObjPositionInParent')

        approved_club_brains = catalog(path={'query': context_path, 'depth': 1},
                                       object_provides=IBoosterClub.__identifier__,
                                       review_state='approved',
                                       sort_on='getObjPositionInParent')

        submitted_club_brains = catalog(path={'query': context_path, 'depth': 1},
                                        object_provides=IBoosterClub.__identifier__,
                                        review_state='submitted',
                                        sort_on='getObjPositionInParent')

        pending_club_brains = catalog(path={'query': context_path, 'depth': 1},
                                      object_provides=IBoosterClub.__identifier__,
                                      review_state='pending',
                                      sort_on='getObjPositionInParent')

        testing_brains = catalog(path={'query': context_path, 'depth': 1},
                                 object_provides=IBoosterClub.__identifier__,
                                 review_state='private',
                                 sort_on='getObjPositionInParent')

        all_brains = active_club_brains + approved_club_brains + pending_club_brains + submitted_club_brains + testing_brains
        member_club_brains = []

        if api.user.is_anonymous():
            current_user_groups = []
            administrative_role = False
        else:
            current_user_data = api.user.get_current()
            current_user_id = current_user_data.getId()
            current_user_groups = api.group.get_groups(user=current_user_data)
            administrative_role = api.user.has_permission('manageBoosterClubs',
                                                           user=current_user_data,
                                                           obj=context)

            [member_club_brains.append(i) for i in all_brains if i.Creator == current_user_id]

        isBoosterMember = False
        for user_group in current_user_groups:
            if user_group.getId() == "Booster_Members":
                isBoosterMember = True

        self.active_club_brains = active_club_brains
        self.approved_club_brains = approved_club_brains
        self.submitted_club_brains = submitted_club_brains
        self.pending_club_brains = pending_club_brains
        self.member_club_brains = member_club_brains
        self.testing_brains = testing_brains

        self.adminisrative_role = administrative_role
        self.showProposalLink = False

        if not administrative_role and isBoosterMember:
            self.showProposalLink = True



