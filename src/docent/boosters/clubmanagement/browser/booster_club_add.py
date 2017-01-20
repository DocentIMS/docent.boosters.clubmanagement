from plone.dexterity.browser import add
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import logging
logger = logging.getLogger("Plone")

class BoosterClubAddForm(add.DefaultAddForm):
    logger.info("Booster Club Add Form")
    portal_type = 'booster_club'

class BoosterClubAddView(add.DefaultAddView):
    form = BoosterClubAddForm
    template = ViewPageTemplateFile('booster_club_add.pt')