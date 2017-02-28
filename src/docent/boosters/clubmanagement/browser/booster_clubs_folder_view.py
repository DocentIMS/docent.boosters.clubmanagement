import logging
from five import grok
from plone import api
from Products.CMFCore.utils import getToolByName

from docent.boosters.clubmanagement.content.booster_clubs_folder import IBoosterClubsFolder
from docent.boosters.clubmanagement.content.bootser_club import IBoosterClub
from docent.boosters.clubmanagement.content.attendance_record import IAttendanceRecord

from docent.boosters.clubmanagement.browser.booster_club_view import getMemberNameAndEmail

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
        active_club_objs = []
        [active_club_objs.append(active_brain.getObject()) for active_brain in active_club_brains]

        approved_club_brains = catalog(path={'query': context_path, 'depth': 1},
                                       object_provides=IBoosterClub.__identifier__,
                                       review_state='approved',
                                       sort_on='getObjPositionInParent')

        approved_club_objs = []
        [approved_club_objs.append(approved_brain.getObject()) for approved_brain in approved_club_brains]

        draft_club_brains = catalog(path={'query': context_path, 'depth': 1},
                                        object_provides=IBoosterClub.__identifier__,
                                        review_state='draft',
                                        sort_on='getObjPositionInParent')

        draft_club_objs = []
        [draft_club_objs.append(draft_brain.getObject()) for draft_brain in draft_club_brains]

        pending_club_brains = catalog(path={'query': context_path, 'depth': 1},
                                      object_provides=IBoosterClub.__identifier__,
                                      review_state='pending',
                                      sort_on='getObjPositionInParent')

        pending_club_objs = []
        [pending_club_objs.append(pending_brain.getObject()) for pending_brain in pending_club_brains]

        archived_club_brains = catalog(path={'query': context_path, 'depth': 1},
                                      object_provides=IBoosterClub.__identifier__,
                                      review_state='archived',
                                      sort_on='getObjPositionInParent')

        archived_club_objs = []
        [archived_club_objs.append(archived_brain.getObject()) for archived_brain in archived_club_brains]

        attendance_record_brains = catalog(path={'query': context_path, 'depth': 1},
                                     object_provides=IAttendanceRecord.__identifier__,
                                     sort_on='getObjPositionInParent')



        all_objs = active_club_objs + approved_club_objs + pending_club_objs + draft_club_objs + archived_club_objs

        isAnon = api.user.is_anonymous()
        self.isAnon = isAnon

        if isAnon:
            current_user_groups = []
            attendance_record_brains = []
            administrative_role = False

        else:
            current_user_data = api.user.get_current()
            current_user_id = current_user_data.getId()
            current_user_groups = api.group.get_groups(user=current_user_data)
            administrative_role = api.user.has_permission('Boosters: Manage Clubs',
                                                           user=current_user_data,
                                                           obj=context)


        isBoosterMember = False
        for user_group in current_user_groups:
            if user_group.getId() == "Booster_Members":
                isBoosterMember = True

        self.active_club_objs = active_club_objs
        self.approved_club_objs = approved_club_objs
        self.draft_club_objs = draft_club_objs
        self.pending_club_objs = pending_club_objs
        self.archived_club_objs = archived_club_objs

        self.adminisrative_role = administrative_role
        self.showProposalLink = False

        self.attendance_record_brains = attendance_record_brains

        if not administrative_role and isBoosterMember:
            self.showProposalLink = True

    def getOwnerName(self, club_obj):
        owner = club_obj.getOwner()
        fullname = owner.getProperty('fullname')
        if not fullname:
            return 'Unknown'

        return fullname

    def getPresidentEmail(self, club_obj):
        president_id = getattr(club_obj, 'club_president', '')
        email_structure = getMemberNameAndEmail(president_id)

        return email_structure

    def showOrHideTabs(self, club_objs):
        if self.adminisrative_role:
            return True

        if self.isAnon:
            return False

        current_member = api.user.get_current()
        for club_obj in club_objs:
            club_owner = club_obj.getOwner()
            if club_owner.getId() == current_member.getId():
                return True
        return False

    def isPrivate(self, attendance_brain):
        if attendance_brain.review_state == 'private':
            return True
        return False