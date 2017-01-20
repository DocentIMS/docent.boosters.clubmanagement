# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from docent.boosters.clubmanagement.interfaces import Iclub_folder
from docent.boosters.clubmanagement.testing import DOCENT_BOOSTERS_CLUBMANAGEMENT_INTEGRATION_TESTING  # noqa
from zope.component import createObject
from zope.component import queryUtility

import unittest


class club_folderIntegrationTest(unittest.TestCase):

    layer = DOCENT_BOOSTERS_CLUBMANAGEMENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='club_folder')
        schema = fti.lookupSchema()
        self.assertEqual(Iclub_folder, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='club_folder')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='club_folder')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(Iclub_folder.providedBy(obj))

    def test_adding(self):
        obj = api.content.create(
            container=self.portal,
            type='club_folder',
            id='club_folder',
        )
        self.assertTrue(Iclub_folder.providedBy(obj))
