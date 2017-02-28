# -*- coding: utf-8 -*-
from docent.group.vocabularies.app_config import (BOOSTER_BOARD_MEMBERS_GROUP_ID,
                                                  EXECUTIVE_COMMITTEE_GROUP_ID,
                                                  BOOSTER_MEMBERS_GROUP_ID)

from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer
from plone import api


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'docent.boosters.clubmanagement:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.
    # add a booster clubs folder to the site and create a page within that uses the id: proposing-a-club
    portal = api.portal.get()
    if 'booster-clubs' not in portal:
        clubs_obj = api.content.create(container=portal,
                           type='booster_clubs_folder',
                           id='booster-clubs',
                           title='Clubs')

        api.group.grant_roles(groupname=BOOSTER_BOARD_MEMBERS_GROUP_ID,
                             roles=['Reviewer', 'Editor', 'Contributor',],
                             obj=clubs_obj)

        api.group.grant_roles(groupname=EXECUTIVE_COMMITTEE_GROUP_ID,
                             roles=['Reviewer', 'Editor', 'Contributor',],
                             obj=clubs_obj)

        clubs_obj.reindexObjectSecurity()

        document = api.content.create(container=clubs_obj,
                           type='Document',
                           id='proposing-a-club',
                           title='Proposing a Club')
        IExcludeFromNavigation(document).exclude_from_nav = True
        document.reindexObject(idxs=['exclude_from_nav'])


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
