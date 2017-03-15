import logging
from five import grok

from plone.app.uuid.utils import uuidToCatalogBrain
from plone import api
from docent.boosters.clubmanagement.content.attendance_record import IAttendanceRecord

grok.templatedir('templates')


class View(grok.View):
    grok.context(IAttendanceRecord)
    grok.require("zope2.View")
    grok.template("attendance_record")

    def update(self):
        context = self.context

        clubs_present = getattr(context, 'clubs_present', [])
        clubs_attended = getattr(context, 'clubs_attended', [])
        clubs_absent = getattr(context, 'clubs_absent', [])
        club_officers_emailed = getattr(context, 'club_officers_emailed', [])
        missing_member_data = getattr(context, 'missing_member_data', [])

        clubs_attended_brains = []
        if clubs_attended:
            [clubs_attended_brains.append(uuidToCatalogBrain(p_uuid)) for p_uuid in clubs_attended]

        clubs_absent_brains = []
        if clubs_absent:
            [clubs_absent_brains.append(uuidToCatalogBrain(a_uuid)) for a_uuid in clubs_absent]

        self.clubs_attended_brains = clubs_attended_brains
        self.clubs_absent_brains = clubs_absent_brains

        if club_officers_emailed:
            self.club_officers_emailed_string = ', '.join(club_officers_emailed)
        else:
            self.club_officers_emailed_string = ''

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

