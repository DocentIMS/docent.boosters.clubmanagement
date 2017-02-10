# -*- coding: utf-8 -*-
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
    if 'clubs_obj' not in portal:
        clubs_obj = api.content.create(container=portal,
                           type='booster_clubs_folder',
                           id='booster-clubs',
                           title='Clubs')

        document = api.content.create(container=clubs_obj,
                           type='Document',
                           id='proposing-a-club',
                           title='Proposing a Club')
        IExcludeFromNavigation(document).exclude_from_nav = True
        document.reindexObject(idxs=['exclude_from_nav'])


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
