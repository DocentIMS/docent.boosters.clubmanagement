import logging
from five import grok


from docent.boosters.clubmanagement.content.bootser_club import IBoosterClub

grok.templatedir('templates')

class View(grok.View):
    grok.context(IBoosterClub)
    grok.require("zope2.View")
    grok.template("boosterclub")

    def hasFile(self):
        context = self.context
        try:
            if context.agreement_file:
                return True
        except:
            return False

        return False
