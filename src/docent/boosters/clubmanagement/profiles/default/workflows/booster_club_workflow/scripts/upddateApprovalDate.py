## Script (Python) "updateApprovalDate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=self
##title=Update Approval Date
##
if hasattr(context, 'set_approval_date'):
    context.set_approval_date()