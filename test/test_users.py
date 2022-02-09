"""test_users.py

Tests for the Users Plugin
"""

import os
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class UsersTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.users = synack.plugins.Users(self.state)
        self.users.api = MagicMock()
        self.users.db = MagicMock()

    def test_get_profile(self):
        """Should get info about me"""
        self.users.api.request.return_value.status_code = 200
        self.users.api.request.return_value.json.return_value = {"one": "1"}
        self.assertEqual({"one": "1"}, self.users.get_profile())
        self.users.api.request.assert_called_with("GET",
                                                  "profiles/me")

    def test_get_profile_other(self):
        """Should get info about someone else"""
        self.users.api.request.return_value.status_code = 200
        self.users.api.request.return_value.json.return_value = {"one": "1"}
        self.assertEqual({"one": "1"}, self.users.get_profile("lngvmkpj"))
        self.users.api.request.assert_called_with("GET",
                                                  "profiles/lngvmkpj")
