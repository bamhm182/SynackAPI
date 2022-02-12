"""test_api.py

Tests for the plugins/api.py Api Class
"""

import os
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.api = synack.plugins.Api(self.state)
        self.api.debug = MagicMock()
        self.api.db = MagicMock()

    def test_login_path(self):
        """Login Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api.login('GET', 'test')
        url = 'https://login.synack.com/api/test'
        self.api.request.assert_called_with('GET',
                                            url)

    def test_login_full_path(self):
        """Login Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api.login('GET', 'http://www.google.com/test')
        self.api.request.assert_called_with('GET',
                                            'http://www.google.com/test')

    def test_notification_path(self):
        """Notifications Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api.db.notifications_token = "something"
        headers = {"Authorization": "Bearer something"}
        url = 'https://notifications.synack.com/api/v2/test'
        self.api.notifications('GET', 'test')
        self.api.request.assert_called_with('GET',
                                            url,
                                            headers=headers)

    def test_notification_full_path(self):
        """Notifications Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api.db.notifications_token = "something"
        headers = {"Authorization": "Bearer something"}
        url = 'http://www.google.com/api/test'
        self.api.notifications('GET', url)
        self.api.request.assert_called_with('GET',
                                            url,
                                            headers=headers)

    def test_notification_no_token(self):
        """Notifications token should be obtained if it doesn't exist"""
        self.api.request = MagicMock()
        self.api.db.notifications_token = ""
        self.api.notifications('GET', 'test')

    def test_notification_bad_token(self):
        """Notifications token should be obtained if it doesn't exist"""
        self.api.request = MagicMock()
        self.api.request.return_value.status_code = 422
        self.api.db.notifications_token = "bad_token"
        url = 'https://notifications.synack.com/api/v2/test'
        headers = {"Authorization": "Bearer bad_token"}
        self.api.notifications('GET', 'test')
        self.api.request.assert_called_with('GET',
                                            url,
                                            headers=headers)

    def test_request_full_url(self):
        """Base URL should not be added if a full url is passed"""
        self.api.state.session.get = MagicMock()
        self.api.db.use_proxies = False
        self.api.db.user_id = "paco"
        self.api.db.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        url = 'http://www.google.com/api/test'
        self.api.request('GET', url)
        self.api.state.session.get.assert_called_with(url,
                                                      headers=headers,
                                                      proxies=None,
                                                      params=None,
                                                      verify=True)

    def test_request_get(self):
        """GET requests should work"""
        self.api.state.session.get = MagicMock()
        self.api.db.use_proxies = False
        self.api.db.user_id = "paco"
        self.api.db.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        url = 'https://platform.synack.com/api/test'
        self.api.request('GET', 'test')
        self.api.state.session.get.assert_called_with(url,
                                                      headers=headers,
                                                      proxies=None,
                                                      params=None,
                                                      verify=True)

    def test_request_header_kwargs(self):
        """requests should merge in kwargs headers"""
        self.api.state.session.get = MagicMock()
        self.api.db.use_proxies = False
        self.api.db.user_id = "paco"
        self.api.db.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco',
            'test': 'test'
        }
        url = 'https://platform.synack.com/api/test'
        self.api.request('GET', 'test', headers={'test': 'test'})
        self.api.state.session.get.assert_called_with(url,
                                                      headers=headers,
                                                      proxies=None,
                                                      params=None,
                                                      verify=True)

    def test_request_head(self):
        """HEAD requests should work"""
        self.api.state.session.head = MagicMock()
        self.api.db.use_proxies = False
        self.api.db.user_id = "paco"
        self.api.db.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        url = 'https://platform.synack.com/api/test'
        self.api.request('HEAD', 'test')
        self.api.state.session.head.assert_called_with(url,
                                                       headers=headers,
                                                       proxies=None,
                                                       params=None,
                                                       verify=True)

    def test_request_logged(self):
        """All requests should call the logger"""
        self.api.state.session.get = MagicMock()
        self.api.state.session.get.return_value.status_code = 200
        self.api.state.session.get.return_value.content = "Returned Content"
        self.api.db.use_proxies = False
        self.api.db.user_id = "paco"
        self.api.db.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        self.api.request('GET', 'test')
        message = "200 -- GET -- https://platform.synack.com/api/test" + \
                  f"\n\tHeaders: {headers}" + \
                  "\n\tQuery: None" + \
                  "\n\tData: None" + \
                  "\n\tContent: Returned Content"
        self.api.debug.log.assert_called_with("Network Request", message)

    def test_request_post(self):
        """POST requests should work"""
        self.api.state.session.post = MagicMock()
        data = {'test': 'test'}
        self.api.db.use_proxies = False
        self.api.db.user_id = "paco"
        self.api.db.api_token = "12345"
        url = 'https://platform.synack.com/api/test'
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        self.api.request('POST', 'test', data=data)
        self.api.state.session.post.assert_called_with(url,
                                                       json=data,
                                                       headers=headers,
                                                       proxies=None,
                                                       verify=True)

    def test_request_patch(self):
        """PATCH requests should work"""
        self.api.state.session.patch = MagicMock()
        data = {'test': 'test'}
        self.api.db.use_proxies = False
        self.api.db.user_id = "paco"
        self.api.db.api_token = "12345"
        url = 'https://platform.synack.com/api/test'
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        self.api.request('PATCH', 'test', data=data)
        self.api.state.session.patch.assert_called_with(url,
                                                        json=data,
                                                        headers=headers,
                                                        proxies=None,
                                                        verify=True)

    def test_request_proxies(self):
        """Proxies should be used if set"""
        proxies = {
            'http': 'http://127.0.0.1:8080',
            'https': 'http://127.0.0.1:8080',
        }
        self.api.db.user_id = "paco"
        self.api.db.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        url = 'https://platform.synack.com/api/test'
        self.api.state.session.get = MagicMock()
        self.api.db.use_proxies = True
        self.api.db.proxies = proxies
        self.api.request('GET', 'test')
        self.api.state.session.get.assert_called_with(url,
                                                      headers=headers,
                                                      proxies=proxies,
                                                      params=None,
                                                      verify=False)
