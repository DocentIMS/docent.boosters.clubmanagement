from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser

from docent.boosters.clubmanagement.content.booster_clubs_folder import IBoosterClubsFolder
from five import grok

from plone import api
from plone.directives import form
from plone.supermodel.directives import fieldset

from plone.namedfile.field import NamedBlobFile
from Products.statusmessages.interfaces import IStatusMessage
from zope import schema
from z3c.form import button, field

from docent.boosters.clubmanagement import _

import logging
logger = logging.getLogger("Plone")

def validateAccept(value):
    if not value == True:
        return False
    return True

class IBoosterProposalForm(form.Schema):

    fieldset('booster_club_information',
        label=u'Booster Club Information',
        fields=['title', 'booster_organization']
    )

    title = schema.TextLine(
        title=_(u"Club Name"),
    )

    booster_organization = schema.TextLine(
        title=_(u"LWHS Organization"),
    )

    fieldset('officer_information',
        label=u'Officer Information',
        description=u'Note:  Two board members must have the "Good Practices Training" before the club can be approved. '
                    u'You may submit your application, and it will be held until this requirement is met.',
        fields=['club_president',
                'club_secretary',
                'club_treasurer',
                'club_advisor',]
    )

    club_president = schema.Choice(
        title=_(u"President"),
        vocabulary=u'docent.group.Booster_Members',
        )

    club_secretary = schema.Choice(
        title=_(u"Secretary"),
        vocabulary=u'docent.group.Booster_Members',
        )

    club_treasurer = schema.Choice(
        title=_(u"Treasurer"),
        vocabulary=u'docent.group.Booster_Members',
        )

    club_advisor = schema.Choice(
        title=_(u"LWHS Advisor"),
        vocabulary=u'docent.group.Advisors',
        )

    fieldset('agreement_upload',
        label=u'File',
        description=u'1) We still need the paper form completed and uploaded.  Please download the Agreement.\n'
                    u'2) Once completed, please upload the form.',
        fields=['agreement_file',]
    )

    agreement_file = NamedBlobFile(
        title=_(u"File"),
    )

    fieldset('agreement_confirmation',
        label=u'Agreement',
        description=_(u'I understand and agree to abide by the membership agreement and '
                      u'financial reporting requirements'),
        fields=['agreement_bool',]
    )

    agreement_bool = schema.Bool(
        title=_(u'I agree'),
        constraint=validateAccept,
    )

grok.templatedir('templates')

class BoosterProposalForm(form.SchemaForm):
    grok.name('booster-club-proposal')
    grok.require('zope2.View')
    grok.context(IBoosterClubsFolder)
    grok.template("booster_proposal_form")

    #fields = field.Fields(IBoosterProposalForm)

    label = _(u"Booster Club Proposal")
    schema = IBoosterProposalForm
    ignoreContext = True
    enable_form_tabbing  = False
    # label = u"Booster Club Proposal"
    # template = Zope3PageTemplateFile("templates/booster_proposal_form.pt")

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """

    @button.buttonAndHandler(u'Submit')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Do something with valid data here

        context = self.context
        current_member_data = api.user.get_current()
        current_member_id = current_member_data.getUser()

        club_title = data.get('title', u'')
        booster_organization = data.get('booster_organization', u'')
        club_president = data.get('club_president', u'')
        club_secretary = data.get('club_secretary', u'')
        club_treasurer = data.get('club_treasurer', u'')
        club_advisor = data.get('club_advisor', u'')
        agreement_file = data.get('agreement_file', None)
        agreement_bool = data.get('agreement_bool', False)

        #create a temporary security manage
        sm = getSecurityManager()
        role = 'Manager'
        tmp_user = BaseUnrestrictedUser(sm.getUser().getId(), '', [role], '')
        portal= api.portal.get()
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)
        exception_caught = False
        try:
            #create a new club in container
            proposed_club_obj = api.content.create(container=context,
                                                   type='booster_club',
                                                   title=club_title,
                                                   safe_id=True)
            #set attributes
            setattr(proposed_club_obj, 'booster_organization', booster_organization)
            setattr(proposed_club_obj, 'club_president', club_president)
            setattr(proposed_club_obj, 'club_secretary', club_secretary)
            setattr(proposed_club_obj, 'club_treasurer', club_treasurer)
            setattr(proposed_club_obj, 'club_advisor', club_advisor)
            setattr(proposed_club_obj, 'agreement_file', agreement_file)
            setattr(proposed_club_obj, 'agreement_bool', agreement_bool)

            #set ownership
            proposed_club_obj.changeOwnership(current_member_id, recursive=True)
            api.user.grant_roles(user=current_member_data,
                                 obj=proposed_club_obj,
                                 roles=['Owner',])

            proposed_club_obj.reindexObject()
            proposed_club_obj.reindexObjectSecurity()

            #reset security manager!
            setSecurityManager(sm)
        except Exception as e:
            setSecurityManager(sm)
            exception_caught = True
            logger.warn("BoosterClubProposal: There was an error creating a club proposal for: %s" % current_member_id)
            logger.warn("BoosterClubProposal: The error was: %s" % e.message)

        #all done!
        # Set status on this form page
        # (this status message is not bind to the session and does not go thru redirects)

            self.status = ""
        else:
            self.status = "Your proposal has been submitted."

        request = context.REQUEST
        response = request.response
        response.redirect(context.absolute_url())

        if exception_caught:
            info_message = "There was a problem with your proposal, please contact the site administrator."
        else:
            info_message = "Your proposal for the club, %s, has been submitted." % club_title

        api.portal.show_message(message=info_message,
                                request=request,
                                type='info')

