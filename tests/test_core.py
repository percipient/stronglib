"""Tests for stronglib core."""

import unittest

from stronglib.core import Stronglib, StronglibUnauthorized


class StronglibTestCase(unittest.TestCase):

    def test_unauthorized(self):
        """
        Test that when it's given an invalid token, stronglib raises
        unauthorized exception when making an API request.

        """

        with self.assertRaises(StronglibUnauthorized):
            strong = Stronglib('bad_token')
            strong.get_domains()
