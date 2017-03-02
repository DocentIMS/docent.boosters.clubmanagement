import logging
from AccessControl import Unauthorized

from five import grok
from plone import api
from plone.api.exc import MissingParameterError
from docent.boosters.clubmanagement.content.bootser_club import IBoosterClub
from zope.component import getMultiAdapter

grok.templatedir('templates')

class View(grok.View):
    grok.context(IBoosterClub)
    grok.require("cmf.ManagePortal")
    grok.name('update-club-owner')

    def render(self):

        return self.updateClubOwner()


    def updateClubOwner(self):
        request = self.request
        context = self.context
        authenticator = getMultiAdapter((context, request), name=u"authenticator")
        if not authenticator.verify():
            raise Unauthorized

        president_id = getattr(context, 'club_president', '')

        if president_id:
            #is this a valid user?
            try:
                president_memberdata = api.user.get(userid=president_id)
            except MissingParameterError:
                api.portal.show_message(message="Could not get the club president. Please contact an administrator.",
                                        type='warn',
                                        request=request)
                return request.response.redirect(context.absolute_url())

            current_owner = context.getOwner()
            current_owner_id = current_owner.getId()
            if president_id == current_owner_id:
                api.portal.show_message(message="The club president already owns this club.",
                                        type='info',
                                        request=request)
                return request.response.redirect(context.absolute_url())

            portal = api.portal.get()
            plone_user = portal.acl_users.getUserById(president_id)
            context.changeOwnership(plone_user, recursive=True)
            api.user.grant_roles(user=plone_user,
                                 obj=context,
                                 roles=['Owner',])

            context.reindexObject()
            context.reindexObjectSecurity()

            president_fullname = president_memberdata.getProperty('fullname')

            api.portal.show_message(message="%s has been made the owner of this club." % president_fullname,
                                    type='info',
                                    request=request)

            return request.response.redirect(context.absolute_url())

        api.portal.show_message(message="A club president is not assigned. No change made.",
                                type='warn',
                                request=request)

        return request.response.redirect(context.absolute_url())