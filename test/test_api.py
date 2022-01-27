"""test_api.py

Tests for the plugins/api.py Api Class
"""

import importlib
import os
import requests
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

from src import synack
from unittest.mock import MagicMock


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        synack.Handler = MagicMock()
        self.api = synack.Api(synack.Handler())
        
    def test_login_path(self):
        """Login Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api.login('GET', 'test')
        self.api.request.assert_called_with('GET',
                                            'https://login.synack.com/api/test',
                                            None,
                                            None,
                                            None)

    def test_login_full_path(self):
        """Login Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api.login('GET', 'http://www.google.com/test')
        self.api.request.assert_called_with('GET',
                                            'http://www.google.com/test',
                                            None,
                                            None,
                                            None)

    def test_notification_path(self):
        """Notifications Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api.handler.db.notifications_token = "something"
        self.api.notifications('GET', 'test')
        self.api.request.assert_called_with('GET',
                                              'https://notifications.synack.com/api/v2/test',
                                              {"Authorization": "Bearer something"},
                                              None,
                                              None)

    def test_notification_full_path(self):
        """Notifications Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api.handler.db.notifications_token = "something"
        self.api.notifications('GET', 'http://www.google.com/api/test')
        self.api.request.assert_called_with('GET',
                                            'http://www.google.com/api/test',
                                            {"Authorization": "Bearer something"},
                                            None,
                                            None)

    def test_notification_no_token(self):
        """Notifications token should be obtained if it doesn't exist"""
        self.api.request = MagicMock()
        self.api.handler.auth.get_notifications_token = MagicMock()
        self.api.handler.db.notifications_token = ""
        self.api.notifications('GET', 'test')
        self.api.handler.auth.get_notifications_token.assert_called_with()

    def test_notification_bad_token(self):
        """Notifications token should be obtained if it doesn't exist"""
        self.api.request = MagicMock()
        self.api.request.return_value.status_code = 422
        self.api.handler.db.notifications_token = "bad_token"
        self.api.notifications('GET', 'test')
        self.api.request.assert_called_with('GET',
                                              'https://notifications.synack.com/api/v2/test',
                                              {"Authorization": "Bearer bad_token"},
                                              None,
                                              None)

    def test_request_full_url(self):
        """Base URL should not be added if a full url is passed"""
        self.api.session.get = MagicMock()
        self.api.handler.db.use_proxies = False
        self.api.request('GET', 'http://www.google.com/api/test')
        self.api.session.get.assert_called_with('http://www.google.com/api/test',
                                                headers=None,
                                                proxies=None,
                                                params=None,
                                                verify=True)

    def test_request_get(self):
        """GET requests should work"""
        self.api.session.get = MagicMock()
        self.api.handler.db.use_proxies = False
        self.api.request('GET', 'test')
        self.api.session.get.assert_called_with('https://platform.synack.com/api/test',
                                                headers=None,
                                                proxies=None,
                                                params=None,
                                                verify=True)

    def test_request_head(self):
        """HEAD requests should work"""
        self.api.session.head = MagicMock()
        self.api.handler.db.use_proxies = False
        self.api.request('HEAD', 'test')
        self.api.session.head.assert_called_with('https://platform.synack.com/api/test',
                                               headers=None,
                                               proxies=None,
                                               params=None,
                                               verify=True)

    def test_request_logged(self):
        """All requests should call the logger"""
        self.api.session.get = MagicMock()
        self.api.session.get.return_value.status_code = 200
        self.api.session.get.return_value.content = "Returned Content"
        self.api.handler.db.use_proxies = False
        self.api.request('GET', 'test')
        self.api.handler.debug.log.assert_called_with("Network Request",
                                      "200 -- https://platform.synack.com/api/test " +
                                      "-- Returned Content")

    def test_request_post(self):
        """POST requests should work"""
        self.api.session.post = MagicMock()
        data = {'test': 'test'}
        self.api.handler.db.use_proxies = False
        self.api.request('POST', 'test', data=data)
        self.api.session.post.assert_called_with('https://platform.synack.com/api/test',
                                               json=data,
                                               headers=None,
                                               proxies=None,
                                               verify=True)

    def test_request_patch(self):
        """PATCH requests should work"""
        self.api.session.patch = MagicMock()
        data = {'test': 'test'}
        self.api.handler.db.use_proxies = False
        self.api.request('PATCH', 'test', data=data)
        self.api.session.patch.assert_called_with('https://platform.synack.com/api/test',
                                                 json=data,
                                                 headers=None,
                                                 proxies=None,
                                                 verify=True)

    def test_request_proxies(self):
        """Proxies should be used if set"""
        proxies = {
            'http': 'http://127.0.0.1:8080',
            'https': 'http://127.0.0.1:8080',
        }
        self.api.session.get = MagicMock()
        self.api.handler.db.use_proxies = True
        self.api.handler.db.proxies = proxies
        self.api.request('GET', 'test')
        self.api.session.get.assert_called_with('https://platform.synack.com/api/test',
                                              headers=None,
                                              proxies=proxies,
                                              params=None,
                                              verify=False)
