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
        self.state._db = MagicMock()
        self.users = synack.plugins.Users(self.state)
        self.users._api = MagicMock()
        self.users._db = MagicMock()

    def test_get_profile(self):
        """Should get info about me"""
        self.users._api.request.return_value.status_code = 200
        self.users._api.request.return_value.json.return_value = {"one": "1"}
        self.assertEqual({"one": "1"}, self.users.get_profile())
        self.users._api.request.assert_called_with("GET",
                                                   "profiles/me")

    def test_get_profile_other(self):
        """Should get info about someone else"""
        self.users._api.request.return_value.status_code = 200
        self.users._api.request.return_value.json.return_value = {"one": "1"}
        self.assertEqual({"one": "1"}, self.users.get_profile("lngvmkpj"))
        self.users._api.request.assert_called_with("GET",
                                                   "profiles/lngvmkpj")
