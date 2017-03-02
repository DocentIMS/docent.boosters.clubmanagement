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
from zope.interface import invariant, Invalid
from z3c.form import button, field

from docent.boosters.clubmanagement import _

import logging
logger = logging.getLogger("Plone")

def getOfficerDescription():
    portal = api.portal.get()
    portal_url = portal.absolute_url()
    description_txt = u"Notes: 1) All registered users are shown in the officer pulldown lists. " \
                      u"Only advisers are shown in the adviser pulldown. If the name you are " \
                      u"looking for is not there, the person hasn't registered. Not listed? " \
                      u"<a href='%s/@@register'>Register</a>. 2) Two board " \
                      u"members must have the \"Good Practices Training\" before the club can be " \
                      u"approved. You may submit your application, and it " \
                      u"will be held until this requirement is met. 3) One person may hold up to " \
                      u"two Officer positions." % portal_url

    return description_txt

def validateAccept(value):
    if not value == True:
        return False
    return True

class IBoosterProposalForm(form.Schema):
    """
    Uses IBoosterClub Schema
    """
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
        description=getOfficerDescription,
        fields=['club_president',
                'club_secretary',
                'club_treasurer',]
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

    fieldset('advisor_information',
        label=u'Advisor Information',
        description=u'',
        fields=['club_advisor',]
    )

    club_advisor = schema.Choice(
        title=_(u"LWHS Advisor"),
        vocabulary=u'docent.group.Advisors',
        )

    # fieldset('agreement_upload',
    #     label=u'File',
    #     description=u'<p>1) We still need the paper form completed and uploaded.  Please download the Agreement.</p>'
    #                 u'<p>2) Once completed, please upload the form.</p>',
    #     fields=['agreement_file',]
    # )
    #
    # agreement_file = NamedBlobFile(
    #     title=_(u"File"),
    # )

    fieldset('financial_information',
        label=u'Financial Information',
        description=u'All booster clubs must satisfy the following criteria:'
                    u'<ul><li>1. Your group maintain a dedicated checking account.</li>'
                    u'<li>2. Two officers review expenditures.</li>'
                    u'<li>3. Two officers review revenues.</li></ul>',
        fields=['dedicated_checking', 'review_officers', 'review_revenue',
                'review_officer_one', 'review_officer_two']
    )

    dedicated_checking = schema.Bool(
        title=_(u'1. Does your group maintain a dedicated checking account?'),
        description=_(u''),
        constraint=validateAccept)

    review_officers = schema.Bool(
        title=_(u'2. Do two officers review expenditures?'),
        description=_(u''),
        constraint=validateAccept)

    review_revenue = schema.Bool(
        title=_(u'3. Do two officers review revenues?'),
        description=_(u''),
        constraint=validateAccept)

    review_officer_one = schema.Choice(
        title=_(u"4. Review Officer One."),
        description=_(u"Select the name of of your first review officer. It must match one of "
                      u"your club officers."),
        vocabulary=u'docent.group.Booster_Members',
        required=True,
        )

    review_officer_two = schema.Choice(
        title=_(u"5. Review Officer Two."),
        description=_(u"Select the name of of your second review officer. It must match one of "
                      u"your club officers."),
        vocabulary=u'docent.group.Booster_Members',
        required=True,
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

    @invariant
    def officerInvariant(data):
        if data.club_president == data.club_secretary:
            raise Invalid(_(u"The club president and secretary cannot be the same individual."))

    @invariant
    def reviewerInvariant(data):
        if data.review_officer_one == data.review_officer_two:
            raise Invalid(_(u"The reviewing officers cannot be the same people."))
        club_officers = [data.club_president, data.club_secretary, data.club_treasurer]
        if data.review_officer_one not in club_officers:
            raise Invalid(_(u"Reviewing officer one must a club officer."))
        if data.review_officer_two not in club_officers:
            raise Invalid(_(u"Reviewing officer two must a club officer."))

#grok.templatedir('templates')

class BoosterProposalForm(form.SchemaForm):
    grok.name('booster-club-proposal')
    grok.require('cmf.SetOwnPassword')
    grok.context(IBoosterClubsFolder)
    # grok.template("booster_proposal_form")

    #fields = field.Fields(IBoosterProposalForm)

    label = _(u"Booster Club Proposal")
    schema = IBoosterProposalForm
    ignoreContext = True
    enable_form_tabbing  = False
    # label = u"Booster Club Proposal"
    # template = Zope3PageTemplateFile("templates/booster_proposal_form.pt")

    def update(self):
        super(BoosterProposalForm, self).update()
        context = self.context
        if context.agreement_file:
            for fieldset_group in self.groups:
                if fieldset_group.__name__ == 'agreement_upload':
                    fieldset_description = u'<p>1) We still need the paper form completed and uploaded.  Please ' \
                                           u'download the <a href="%s/@@download/agreement_file" title="LWHS Booster Club Agreement Form">' \
                                           u'Agreement</a>.</p><p>2) Once completed, ' \
                                           u'please upload the form.</p>' % context.absolute_url()

                    setattr(fieldset_group, 'description', fieldset_description)
                    fieldset_group.update()

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        context = self.context

        request = context.REQUEST
        response = request.response
        response.redirect(context.absolute_url())

        api.portal.show_message(message=u'Club Proposal Cancelled.',
                                request=request,
                                type='info')

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
        #agreement_file = data.get('agreement_file', None)
        dedicated_checking = data.get('dedicated_checking', False)
        review_officers = data.get('review_officers', False)
        review_revenue = data.get('review_revenue', False)
        review_officer_one = data.get('review_officer_one', u'')
        review_officer_two = data.get('review_officer_two', u'')
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
            #setattr(proposed_club_obj, 'agreement_file', agreement_file)
            setattr(proposed_club_obj, 'dedicated_checking', dedicated_checking)
            setattr(proposed_club_obj, 'review_officers', review_officers)
            setattr(proposed_club_obj, 'review_revenue', review_revenue)
            setattr(proposed_club_obj, 'review_officer_one', review_officer_one)
            setattr(proposed_club_obj, 'review_officer_two', review_officer_two)
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

