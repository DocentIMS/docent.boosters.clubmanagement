from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from DateTime import DateTime
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

from docent.group.vocabularies.app_config import TRAINING_MEMBERS_GROUP_ID
from docent.boosters.clubmanagement.interfaces import IBestPracticeTraining
from docent.boosters.clubmanagement import _

import logging
logger = logging.getLogger("Plone")


def getMemberFullname():
    current_memberdata = api.user.get_current()
    try:
        current_member_fullname = current_memberdata.getProperty('fullname')
    except:
        current_member_fullname = u'Unknown'

    return u"%s" % current_member_fullname


class ITrainingSignupForm(form.Schema):
    """
    Uses ITrainingSignupForm Schema
    """
    form.mode(fullname='display')
    fullname = schema.TextLine(
        title=_(u"Booster Member"),
        defaultFactory=getMemberFullname,
    )

grok.templatedir('templates')

class TrainingSignupForm(form.SchemaForm):
    grok.name('training-signup')
    grok.require('cmf.SetOwnPassword')
    grok.context(IBoosterClubsFolder)
    grok.template("best_practice_training")

    label = _(u"Best Practices Training Signup")
    schema = ITrainingSignupForm
    ignoreContext = True


    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        context = self.context
        request = context.REQUEST
        response = request.response
        response.redirect(context.absolute_url())

        api.portal.show_message(message=u'Best Practices Signup Cancelled.',
                                request=request,
                                type='info')

    @button.buttonAndHandler(u'Submit')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        context = self.context
        request = context.REQUEST
        response = request.response

        portal = api.portal.get()
        current_memberdata = api.user.get_current()
        current_member_name = current_memberdata.getProperty('fullname')
        current_member_email = current_memberdata.getProperty('email')

        #add to proper group
        api.group.add_user(groupname=TRAINING_MEMBERS_GROUP_ID,
                           user=current_memberdata)
        #send emails
        next_bpt_obj = context.getNextTrainingEventObj()
        if next_bpt_obj:
            start_DateTime = getattr(next_bpt_obj, 'start')
            local_date = start_DateTime.strftime('%b %d, %Y')
            local_time = start_DateTime.strftime('%I:%M %p')
            msg = "%s,\n\n" % current_member_name
            msg += "You have been signed up to attend the LWHS Boosters " \
                   "Best Practices Training on %s at %s." % (local_date, local_time)

            location = getattr(next_bpt_obj, 'location')
            if location:
                msg += " The training is located at: %s." % location

            msg += "\n\nYou have been granted access to the Best Practices " \
                   "Training materials at: %s/training." % portal.absolute_url()

            msg += "\n\nRegards,\n\nLWHS Boosters"

            api.portal.send_email(recipient="<%s>,<secretary@lwhsboosters.org>" % current_member_email,
                                  subject="LWHS Booster Best Practices Training Enrollment",
                                  body=msg,
                                  immediate=True)



            response.redirect(context.absolute_url())

            api.portal.show_message(message=u'You have been registered for the next Best Practices Training. '
                                            u'Please check your email for event details',
                                    request=request,
                                    type='info')

        else:
            msg = "%s,\n\n" % current_member_name
            msg += "You have  signed up to attend the a LWHS Boosters " \
                   "Best Practices Training. At this time, no sessions are available. Please check in with the LWHS " \
                   "Boosters Executive Secretary for the next availbe session."

            msg += "\n\nIn the meantime, you have been granted access to the Best Practices " \
                   "Training materials at: %s/training." % portal.absolute_url()

            msg += "\n\nRegards,\n\nLWHS Boosters"

            api.portal.send_email(recipient="<%s>,<secretary@lwhsboosters.org>" % current_member_email,
                                  subject="LWHS Booster Best Practices Training Enrollment",
                                  body=msg,
                                  immediate=True)

            response.redirect(context.absolute_url())

            api.portal.show_message(message=u'You have been granted access to the LWHS Boosters Best Practices '
                                            u'Training materials.',
                                    request=request,
                                    type='info')

