## Script (Python) "sendClubNotice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=self
##title=Send Club Notice
##
if hasattr(context, 'send_club_notice'):
    context.send_club_notice()
