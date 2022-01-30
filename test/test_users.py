"""test_Notifications.py

Tests for the _Notifications.py Notifications Class
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

from src import synack
from unittest.mock import MagicMock


class NotificationsTestCase(unittest.TestCase):
    def setUp(self):
        synack.Handler = MagicMock()
        self.users = synack.Users(synack.Handler())

    def test_get_profile(self):
        """Should get info about me"""
        self.users.handler.api.request.return_value.status_code = 200
        self.users.handler.api.request.return_value.json.return_value = {"one":"1"}
        self.assertEqual({"one":"1"}, self.users.get_profile())
        self.users.handler.api.request.assert_called_with("GET",
                                                          "profiles/me")

    def test_get_profile_other(self):
        """Should get info about someone else"""
        self.users.handler.api.request.return_value.status_code = 200
        self.users.handler.api.request.return_value.json.return_value = {"one":"1"}
        self.assertEqual({"one":"1"}, self.users.get_profile("lngvmkpj"))
        self.users.handler.api.request.assert_called_with("GET",
                                                          "profiles/lngvmkpj")
