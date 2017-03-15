from plone import api

from Products.CMFCore.utils import getToolByName


from docent.boosters.clubmanagement.content.attendance_record import IAttendanceRecord

import logging
logger = logging.getLogger("Plone")


def upgrade(upgrade_product,version):
    """ Decorator for updating the QuickInstaller of a upgrade """
    def wrap_func(fn):
        def wrap_func_args(context,*args):
            p = getToolByName(context,'portal_quickinstaller').get(upgrade_product)
            setattr(p,'installedversion',version)
            return fn(context,*args)
        return wrap_func_args
    return wrap_func


default_profile = 'profile-docent.boosters.clubmanagement:default'


@upgrade('docent.boosters.clubmanagement', '1001')
def updateClubManagementOneToOne(context):
    logger.info("Upgrading docent.boosters.clubmanagement to version 1001")
    portal = api.portal.get()
    catalog = getToolByName(portal, 'portal_catalog')
    attendance_roster_brains = catalog(object_provides=IAttendanceRecord.__identifier__)
    for ar_brain in attendance_roster_brains:
        ar_obj = ar_brain.getObject()
        attending_club_ids = getattr(ar_obj, 'clubs_present', [])
        if attending_club_ids:
            setattr(ar_obj, 'clubs_attended', attending_club_ids)

