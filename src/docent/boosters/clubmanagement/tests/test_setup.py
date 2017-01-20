# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from docent.boosters.clubmanagement.testing import DOCENT_BOOSTERS_CLUBMANAGEMENT_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that docent.boosters.clubmanagement is properly installed."""

    layer = DOCENT_BOOSTERS_CLUBMANAGEMENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if docent.boosters.clubmanagement is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'docent.boosters.clubmanagement'))

    def test_browserlayer(self):
        """Test that IDocentBoostersClubmanagementLayer is registered."""
        from docent.boosters.clubmanagement.interfaces import (
            IDocentBoostersClubmanagementLayer)
        from plone.browserlayer import utils
        self.assertIn(IDocentBoostersClubmanagementLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = DOCENT_BOOSTERS_CLUBMANAGEMENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['docent.boosters.clubmanagement'])

    def test_product_uninstalled(self):
        """Test if docent.boosters.clubmanagement is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'docent.boosters.clubmanagement'))

    def test_browserlayer_removed(self):
        """Test that IDocentBoostersClubmanagementLayer is removed."""
        from docent.boosters.clubmanagement.interfaces import \
            IDocentBoostersClubmanagementLayer
        from plone.browserlayer import utils
        self.assertNotIn(IDocentBoostersClubmanagementLayer, utils.registered_layers())
