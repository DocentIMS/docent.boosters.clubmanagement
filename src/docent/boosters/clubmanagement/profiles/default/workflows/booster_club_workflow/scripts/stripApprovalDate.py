## Script (Python) "updateApprovalDate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=self
##title=Update Approval Date
##
if hasattr(context, 'strip_approval_date'):
    context.strip_approval_date()
