import logging
from five import grok
from plone import api
from plone.api.exc import MissingParameterError
from plone.protect.utils import addTokenToUrl

from docent.boosters.clubmanagement.content.bootser_club import IBoosterClub

grok.templatedir('templates')

def getMemberFullname(member_id):
    if member_id == 'no_members':
        return u'No Member Selected'
    try:
        member_data = api.user.get(username=member_id)
        fullname = member_data.getProperty('fullname')
    except MissingParameterError:
        fullname = member_id
    except AttributeError:
        fullname = member_id

    return fullname

def getMemberNameAndEmail(member_id):
    """
    Returns html structure
    :param member_id:
    :return:
    """
    if member_id == 'no_members' or member_id == '':
        return u'No Member Selected'
    email = None
    try:
        member_data = api.user.get(username=member_id)
        fullname = member_data.getProperty('fullname')
        email = member_data.getProperty('email')
    except MissingParameterError:
        fullname = member_id
    except AttributeError:
        fullname = member_id

    if email:
        return '<a href="mailto:%s">%s</a>' % (email, fullname)
    else:
        return fullname


class View(grok.View):
    grok.context(IBoosterClub)
    grok.require("zope2.View")
    grok.template("boosterclub")

    def update(self):
        context = self.context
        if not api.user.is_anonymous():
            self.context_url = context.absolute_url()
            self.club_president = getMemberNameAndEmail(context.club_president)
            self.club_secretary = getMemberNameAndEmail(context.club_secretary)
            self.club_treasurer = getMemberNameAndEmail(context.club_treasurer)
            self.club_advisor = getMemberNameAndEmail(context.club_advisor)
            self.review_officer_one = getMemberNameAndEmail(context.review_officer_one)
            self.review_officer_two = getMemberNameAndEmail(context.review_officer_two)

            current_viewer = api.user.get_current()
            active_roles = api.user.get_roles(user=current_viewer, obj=context)
            if 'Owner' in active_roles:
                context_state = api.content.get_state(obj=context)
                if context_state == 'pending':
                    context.verifyClubOfficers()
                if context_state == 'approved':
                    context.officersHaveTraining()

    def hasFile(self):
        context = self.context
        try:
            if context.agreement_file:
                return True
        except:
            return False

        return False

    def getOwnerName(self):
        context = self.context
        owner = context.getOwner()
        fullname = owner.getProperty('fullname')
        if not fullname:
            return 'Unknown'

        return fullname

    def isAnon(self):
        return api.user.is_anonymous()

    def isAdmin(self):
        current_member = api.user.get_current()

        return api.user.has_permission("cmf.ManagePortal",
                                       user=current_member)

    def statementAccess(self):
        current_member = api.user.get_current()

        if api.user.has_permission("cmf.ManagePortal",
                                   user=current_member):
            return True

        if current_member.getId() == self.club_president:
            return True

        if api.user.has_permission("Boosters: Manage Clubs",
                                   user=current_member):
            return True

        return False

    def getFileUploadLink(self):
        upload_url = '%s/++add++File' % self.context_url

        return upload_url

    def getOwnerUpdateUrl(self):
        #context = self.context
        update_url = "%s/@@update-club-owner" % self.context_url

        return addTokenToUrl(update_url)

    def getClubFiles(self):
        return self.context.getFolderContents()