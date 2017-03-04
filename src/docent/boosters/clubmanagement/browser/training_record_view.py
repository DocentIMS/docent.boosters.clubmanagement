import logging
from five import grok

from plone.app.uuid.utils import uuidToCatalogBrain
from plone import api

from docent.boosters.clubmanagement.content.training_record import ITrainingRecord
from docent.boosters.clubmanagement.browser.booster_club_view import getMemberNameAndEmail

grok.templatedir('templates')


class View(grok.View):
    grok.context(ITrainingRecord)
    grok.require("zope2.View")
    grok.template("training_record")

    def update(self):
        context = self.context

        members_present = getattr(context, 'members_present', [])
        members_absent = getattr(context, 'members_absent', [])
        members_emailed = getattr(context, 'members_emailed', [])
        missing_member_data = getattr(context, 'missing_member_data', [])

        members_present_html = ""
        if members_present:
            for member_id in members_present:
                members_present_html += "<li>%s</li>" % getMemberNameAndEmail(member_id)
        self.members_present_html = members_present_html

        members_absent_html = ""
        if members_absent:
            for member_id in members_absent:
                members_absent_html += "<li>%s</li>" % getMemberNameAndEmail(member_id)
        self.members_absent_html = members_absent_html

        if missing_member_data:
            self.missing_member_data_string = ', '.join(missing_member_data)
        else:
            self.missing_member_data_string = ''

        description_text = getattr(context, 'description', u'')
        if description_text:
            portal_transforms = api.portal.get_tool(name='portal_transforms')
            description_data = portal_transforms.convertTo('text/html',
                                               description_text,
                                               mimetype='text/-x-web-intelligent')

            self.description_html = description_data.getData()
        else:
            self.description_html = description_text

