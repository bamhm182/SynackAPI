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
        self.state._db = MagicMock()
        self.notifications = synack.plugins.Notifications(self.state)
        self.notifications._api = MagicMock()
        self.notifications._db = MagicMock()

    def test_get(self):
        """Should get a list of notifications"""
        self.notifications._api.notifications.return_value.status_code = 200
        self.notifications._api.notifications.return_value.json.return_value = {"one": "1"}
        path = "notifications?meta=1"
        self.assertEqual({"one": "1"}, self.notifications.get())
        self.notifications._api.notifications.assert_called_with("GET", path)

    def test_get_unread_count(self):
        """Should get the number of unread notifications"""
        self.notifications._api.notifications.return_value.status_code = 200
        self.notifications._api.notifications.return_value.json.return_value = {"one": "1"}
        self.notifications._state.notifications_token = "good_token"
        query = {
            "authorization_token": "good_token"
        }
        path = "notifications/unread_count"
        self.assertEqual({"one": "1"}, self.notifications.get_unread_count())
        self.notifications._api.notifications.assert_called_with("GET", path,
                                                                 query=query)

    def test_set_read(self):
        """Should set all notifications to read"""
        self.notifications._api.notifications.return_value.status_code = 200
        self.notifications._api.notifications.return_value.json.return_value = {"one": "1"}
        self.notifications._state.notifications_token = "good_token"
        query = {
            "authorization_token": "good_token"
        }
        path = "read_all"
        self.assertEqual({"one": "1"}, self.notifications.set_read())
        self.notifications._api.notifications.assert_called_with("GET", path,
                                                                 query=query)
