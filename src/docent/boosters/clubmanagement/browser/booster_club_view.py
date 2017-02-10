import logging
from five import grok
from plone import api
from plone.api.exc import MissingParameterError

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
    if member_id == 'no_members':
        return u'No Member Selected'
    email = None
    try:
        member_data = api.user.get(username=member_id)
        fullname = member_data.getProperty('fullname')
        email = member_data.getPropertry('email')
    except MissingParameterError:
        fullname = member_id
    except AttributeError:
        fullname = member_id

    if email:
        return '<a href="mailto:%s>%s</a>' % (email, fullname)
    else:
        return fullname


class View(grok.View):
    grok.context(IBoosterClub)
    grok.require("zope2.View")
    grok.template("boosterclub")

    def update(self):
        context = self.context

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
