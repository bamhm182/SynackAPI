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
        self.notifications = synack.Notifications(synack.Handler())

    def test_get_notifications(self):
        """Should get a list of notifications"""
        self.notifications.handler.api.notifications.return_value.status_code = 200
        self.notifications.handler.api.notifications.return_value.json.return_value = {"one":"1"}
        self.assertEqual({"one":"1"}, self.notifications.get_notifications())
        self.notifications.handler.api.notifications.assert_called_with("GET",
                                                    "notifications?meta=1")

    def test_get_unread_count(self):
        """Should get the number of unread notifications"""
        self.notifications.handler.api.notifications.return_value.status_code = 200
        self.notifications.handler.api.notifications.return_value.json.return_value = {"one":"1"}
        self.notifications.handler.db.notifications_token = "good_token"
        query = {
            "authorization_token": "good_token"
        }
        self.assertEqual({"one":"1"}, self.notifications.get_unread_count())
        self.notifications.handler.api.notifications.assert_called_with("GET",
                                                    "notifications/unread_count",
                                                    query=query)
