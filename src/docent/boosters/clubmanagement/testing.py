# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import docent.boosters.clubmanagement


class DocentBoostersClubmanagementLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=docent.boosters.clubmanagement)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'docent.boosters.clubmanagement:default')


DOCENT_BOOSTERS_CLUBMANAGEMENT_FIXTURE = DocentBoostersClubmanagementLayer()


DOCENT_BOOSTERS_CLUBMANAGEMENT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(DOCENT_BOOSTERS_CLUBMANAGEMENT_FIXTURE,),
    name='DocentBoostersClubmanagementLayer:IntegrationTesting'
)


DOCENT_BOOSTERS_CLUBMANAGEMENT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(DOCENT_BOOSTERS_CLUBMANAGEMENT_FIXTURE,),
    name='DocentBoostersClubmanagementLayer:FunctionalTesting'
)


DOCENT_BOOSTERS_CLUBMANAGEMENT_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        DOCENT_BOOSTERS_CLUBMANAGEMENT_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='DocentBoostersClubmanagementLayer:AcceptanceTesting'
)
