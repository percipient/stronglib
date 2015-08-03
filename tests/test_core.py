"""Tests for stronglib core."""

import unittest

import stronglib


class StronglibTestCase(unittest.TestCase):

    def test_unauthorized(self):
        """
        Test that when it's given an invalid token, stronglib raises
        unauthorized exception when making an API request.

        """

        with self.assertRaises(stronglib.StronglibUnauthorized):
            stronglib.api_key = 'bad_token'
            stronglib.Domain.list()
