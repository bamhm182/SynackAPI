"""test_notifications.py

Tests for the Notifications Plugin
"""

import os
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class NotificationsTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.notifications = synack.plugins.Notifications(self.state)
        self.notifications.api = MagicMock()
        self.notifications.db = MagicMock()

    def test_get(self):
        """Should get a list of notifications"""
        self.notifications.api.notifications.return_value.status_code = 200
        self.notifications.api.notifications.return_value.json.return_value = {"one": "1"}
        path = "notifications?meta=1"
        self.assertEqual({"one": "1"}, self.notifications.get())
        self.notifications.api.notifications.assert_called_with("GET", path)

    def test_get_unread_count(self):
        """Should get the number of unread notifications"""
        self.notifications.api.notifications.return_value.status_code = 200
        self.notifications.api.notifications.return_value.json.return_value = {"one": "1"}
        self.notifications.db.notifications_token = "good_token"
        query = {
            "authorization_token": "good_token"
        }
        path = "notifications/unread_count"
        self.assertEqual({"one": "1"}, self.notifications.get_unread_count())
        self.notifications.api.notifications.assert_called_with("GET", path,
                                                                query=query)
