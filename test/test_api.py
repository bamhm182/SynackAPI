"""test_api.py

Tests for the plugins/api.py Api Class
"""

import os
import sys
import unittest

from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.state._db = MagicMock()
        self.state._synack_domain = 'synack.com'
        self.api = synack.plugins.Api(self.state)
        self.api._debug = MagicMock()
        self.api._db = MagicMock()

    def test_login_full_path(self):
        """Login Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api.login('GET', 'http://www.google.com/test')
        self.api.request.assert_called_with('GET',
                                            'http://www.google.com/test')

    def test_login_path(self):
        """Login Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api.login('GET', 'test')
        url = 'https://login.synack.com/api/test'
        self.api.request.assert_called_with('GET',
                                            url)

    def test_notification_bad_token(self):
        """Notifications token should be obtained if it doesn't exist"""
        self.api.request = MagicMock()
        self.api.request.return_value.status_code = 422
        self.api._state.notifications_token = "bad_token"
        url = 'https://notifications.synack.com/api/v2/test'
        headers = {"Authorization": "Bearer bad_token"}
        self.api.notifications('GET', 'test')
        self.api.request.assert_called_with('GET',
                                            url,
                                            headers=headers)

    def test_notification_full_path(self):
        """Notifications Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api._state.notifications_token = "something"
        headers = {"Authorization": "Bearer something"}
        url = 'http://www.google.com/api/test'
        self.api.notifications('GET', url)
        self.api.request.assert_called_with('GET',
                                            url,
                                            headers=headers)

    def test_notification_no_token(self):
        """Notifications token should be obtained if it doesn't exist"""
        self.api.request = MagicMock()
        self.api._state.notifications_token = ""
        self.api.notifications('GET', 'test')

    def test_notification_path(self):
        """Notifications Base URL should prepend and request should be made"""
        self.api.request = MagicMock()
        self.api._state.notifications_token = "something"
        headers = {"Authorization": "Bearer something"}
        url = 'https://notifications.synack.com/api/v2/test'
        self.api.notifications('GET', 'test')
        self.api.request.assert_called_with('GET',
                                            url,
                                            headers=headers)

    def test_request_external_url(self):
        """External URLs should not get Authorization headers"""
        self.api._state.session.get = MagicMock()
        self.api._state.session.get.return_value.status_code = 200
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        url = 'https://duo.security.com/test'
        self.api.request('GET', url)
        self.api._state.session.get.assert_called_with(url,
                                                       headers={},
                                                       proxies=None,
                                                       params=None,
                                                       verify=True)

    def test_request_full_url(self):
        """Base URL should not be added if a full url is passed"""
        self.api._state.session.get = MagicMock()
        self.api._state.session.get.return_value.status_code = 200
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        url = 'http://www.synack.com/api/test'
        self.api.request('GET', url)
        self.api._state.session.get.assert_called_with(url,
                                                       headers=headers,
                                                       proxies=None,
                                                       params=None,
                                                       verify=True)

    def test_request_get(self):
        """GET requests should work"""
        self.api._state.session.get = MagicMock()
        self.api._state.session.get.return_value.status_code = 200
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        url = 'https://platform.synack.com/api/test'
        self.api.request('GET', 'test')
        self.api._state.session.get.assert_called_with(url,
                                                       headers=headers,
                                                       proxies=None,
                                                       params=None,
                                                       verify=True)

    def test_request_head(self):
        """HEAD requests should work"""
        self.api._state.session.head = MagicMock()
        self.api._state.session.head.return_value.status_code = 200
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        url = 'https://platform.synack.com/api/test'
        self.api.request('HEAD', 'test')
        self.api._state.session.head.assert_called_with(url,
                                                        headers=headers,
                                                        proxies=None,
                                                        params=None,
                                                        verify=True)

    def test_request_header_kwargs(self):
        """requests should merge in kwargs headers"""
        self.api._state.session.get = MagicMock()
        self.api._state.session.get.return_value.status_code = 200
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco',
            'test': 'test'
        }
        url = 'https://platform.synack.com/api/test'
        self.api.request('GET', 'test', headers={'test': 'test'})
        self.api._state.session.get.assert_called_with(url,
                                                       headers=headers,
                                                       proxies=None,
                                                       params=None,
                                                       verify=True)

    def test_request_logged(self):
        """All requests should call the logger"""
        self.api._state.session.get = MagicMock()
        self.api._state.session.get.return_value.status_code = 200
        self.api._state.session.get.return_value.content = "Returned Content"
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
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
        self.api._debug.log.assert_any_call("Network Request", message)

    def test_request_patch(self):
        """PATCH requests should work"""
        self.api._state.session.patch = MagicMock()
        self.api._state.session.patch.return_value.status_code = 200
        data = {'test': 'test'}
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        url = 'https://platform.synack.com/api/test'
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        self.api.request('PATCH', 'test', data=data)
        self.api._state.session.patch.assert_called_with(url,
                                                         json=data,
                                                         headers=headers,
                                                         proxies=None,
                                                         verify=True)

    def test_request_post(self):
        """POST requests should work"""
        self.api._state.session.post = MagicMock()
        self.api._state.session.post.return_value.status_code = 200
        data = {'test': 'test'}
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        url = 'https://platform.synack.com/api/test'
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        self.api.request('POST', 'test', data=data)
        self.api._state.session.post.assert_called_with(url,
                                                        json=data,
                                                        headers=headers,
                                                        proxies=None,
                                                        verify=True)

    def test_request_post_urlencoded(self):
        """POST with urlencoded Content-Type should send form data"""
        self.api._state.session.post = MagicMock()
        self.api._state.session.post.return_value.status_code = 200
        data = {'test': 'test'}
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        url = 'https://platform.synack.com/api/test'
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.api.request('POST', 'test', data=data,
                         headers={'Content-Type': 'application/x-www-form-urlencoded'})
        self.api._state.session.post.assert_called_with(url,
                                                        data=data,
                                                        headers=headers,
                                                        proxies=None,
                                                        verify=True)

    def test_request_proxies(self):
        """Proxies should be used if set"""
        proxies = {
            'http': 'http://127.0.0.1:8080',
            'https': 'http://127.0.0.1:8080',
        }
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        url = 'https://platform.synack.com/api/test'
        self.api._state.session.get = MagicMock()
        self.api._state.session.get.return_value.status_code = 200
        self.api._state.use_proxies = True
        self.api._state.http_proxy = proxies.get('http')
        self.api._state.https_proxy = proxies.get('https')
        self.api.request('GET', 'test')
        self.api._state.session.get.assert_called_with(url,
                                                       headers=headers,
                                                       proxies=proxies,
                                                       params=None,
                                                       verify=False)

    def test_request_put(self):
        """PUT requests should work"""
        self.api._state.session.put = MagicMock()
        self.api._state.session.put.return_value.status_code = 200
        data = {'test': 'test'}
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        url = 'https://platform.synack.com/api/test'
        headers = {
            'Authorization': 'Bearer 12345',
            'user_id': 'paco'
        }
        self.api.request('PUT', 'test', data=data)
        self.api._state.session.put.assert_called_with(url,
                                                       headers=headers,
                                                       proxies=None,
                                                       params=data,
                                                       verify=True)

    def test_request_status_400(self):
        """400/401 responses should log a failure"""
        res = MagicMock()
        res.status_code = 400
        self.api._state.session.get = MagicMock(return_value=res)
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        self.api.request('GET', 'test')
        self.api._debug.log.assert_any_call('Request failed',
                                            f'({res.status_code} - {res.reason}) {res.url}')

    def test_request_status_403(self):
        """403 responses should log logged out"""
        res = MagicMock()
        res.status_code = 403
        self.api._state.session.get = MagicMock(return_value=res)
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        self.api.request('GET', 'test')
        self.api._debug.log.assert_any_call('Request failed',
                                            f'({res.status_code} - Logged Out) {res.url}')

    def test_request_status_412(self):
        """412 responses should log mission already claimed"""
        res = MagicMock()
        res.status_code = 412
        self.api._state.session.get = MagicMock(return_value=res)
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        self.api.request('GET', 'test')
        self.api._debug.log.assert_any_call('Request failed',
                                            f'({res.status_code} - Mission already claimed) {res.url}')

    def test_request_status_423(self):
        """423 responses should log locked and not retry"""
        res = MagicMock()
        res.status_code = 423
        self.api._state.session.get = MagicMock(return_value=res)
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        self.api.request('GET', 'test')
        self.api._debug.log.assert_any_call('Request failed',
                                            f'({res.status_code} - Locked) {res.url}')
        self.assertEqual(1, self.api._state.session.get.call_count)

    def test_request_status_429(self):
        """429 responses should pause and retry"""
        res_429 = MagicMock()
        res_429.status_code = 429
        res_200 = MagicMock()
        res_200.status_code = 200
        self.api._state.session.get = MagicMock(side_effect=[res_429, res_200])
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        with patch('synack.plugins.api.time.sleep') as mock_sleep:
            self.api.request('GET', 'test')
        mock_sleep.assert_called_with(30)
        self.assertEqual(2, self.api._state.session.get.call_count)

    def test_request_status_500(self):
        """5xx responses should log and retry"""
        res_500 = MagicMock()
        res_500.status_code = 500
        res_200 = MagicMock()
        res_200.status_code = 200
        self.api._state.session.get = MagicMock(side_effect=[res_500, res_200])
        self.api._state.use_proxies = False
        self.api._state.user_id = "paco"
        self.api._state.api_token = "12345"
        self.api.request('GET', 'test')
        self.assertEqual(2, self.api._state.session.get.call_count)
        self.api._debug.log.assert_any_call('Retrying', 'Attempt #1')
