# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s docent.boosters.clubmanagement -t test_club_folder.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src docent.boosters.clubmanagement.testing.DOCENT_BOOSTERS_CLUBMANAGEMENT_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/plonetraining/testing/tests/robot/test_club_folder.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a club_folder
  Given a logged-in site administrator
    and an add club_folder form
   When I type 'My club_folder' into the title field
    and I submit the form
   Then a club_folder with the title 'My club_folder' has been created

Scenario: As a site administrator I can view a club_folder
  Given a logged-in site administrator
    and a club_folder 'My club_folder'
   When I go to the club_folder view
   Then I can see the club_folder title 'My club_folder'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add club_folder form
  Go To  ${PLONE_URL}/++add++club_folder

a club_folder 'My club_folder'
  Create content  type=club_folder  id=my-club_folder  title=My club_folder


# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.title  ${title}

I submit the form
  Click Button  Save

I go to the club_folder view
  Go To  ${PLONE_URL}/my-club_folder
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a club_folder with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the club_folder title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
