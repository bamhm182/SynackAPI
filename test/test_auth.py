"""test_Auth.py

Tests for the _Auth.py Auth Class
"""

import os
import pathlib
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.state._db = MagicMock()
        self.state._synack_domain = 'synack.com'
        self.auth = synack.plugins.Auth(self.state)
        self.auth._api = MagicMock()
        self.auth._db = MagicMock()
        self.auth._users = MagicMock()
        self.auth._duo = MagicMock()

    def test_get_api_token(self):
        """Should use HOTP path when otp credentials are set and no virtual device is registered"""
        self.auth._state.api_token = ""
        self.auth._db.duo_akey = ''
        self.auth._db.duo_pkey = ''
        self.auth._db.duo_host = ''
        self.auth._db.otp_secret = 'TOPSECRET'
        self.auth._db.otp_count = 0
        self.auth.set_login_script = MagicMock()
        self.auth.get_authentication_response = MagicMock()
        self.auth.get_authentication_response.return_value = {
            'duo_auth_url': 'https://duoauth.local'
        }
        self.auth._users.get_profile = MagicMock()
        self.auth._users.get_profile.return_value = None
        self.auth.get_login_csrf = MagicMock(return_value="csrf_fwlnm")

        self.auth._api.request.return_value.status_code = 200
        ret_json = {"access_token": "api_lwfaume"}
        self.auth._api.request.return_value.json.return_value = ret_json
        self.assertEqual("api_lwfaume", self.auth.get_api_token())
        self.auth.get_login_csrf.assert_called_with()
        self.auth.set_login_script.assert_called_with()
        self.auth.get_authentication_response.assert_called_with('csrf_fwlnm')
        self.auth._duo.get_grant_token.assert_called_with('https://duoauth.local')
        self.auth._duo.get_grant_token_push.assert_not_called()

    def test_get_api_token_configure_mfa(self):
        """Should call configure_mfa and proceed with push when neither MFA method is configured"""
        self.auth._state.api_token = ""
        self.auth._db.duo_akey = ''
        self.auth._db.duo_pkey = ''
        self.auth._db.duo_host = ''
        self.auth._db.otp_secret = None
        self.auth._db.otp_count = None

        self.auth._duo.configure_mfa.side_effect = lambda: [
            setattr(self.auth._db, 'duo_akey', 'new_akey'),
            setattr(self.auth._db, 'duo_pkey', 'new_pkey'),
            setattr(self.auth._db, 'duo_host', 'api.duo.com'),
        ]
        self.auth.set_login_script = MagicMock()
        self.auth.get_authentication_response = MagicMock(return_value={'duo_auth_url': 'https://duoauth.local'})
        self.auth._users.get_profile = MagicMock(return_value=None)
        self.auth.get_login_csrf = MagicMock(return_value="csrf_fwlnm")
        self.auth._api.request.return_value.status_code = 200
        self.auth._api.request.return_value.json.return_value = {"access_token": "api_lwfaume"}
        self.assertEqual("api_lwfaume", self.auth.get_api_token())
        self.auth._duo.configure_mfa.assert_called_once()
        self.auth._duo.get_grant_token.assert_called_with('https://duoauth.local')

    def test_get_api_token_login_success(self):
        """Should return the database token when check succeeds"""
        self.auth._state.api_token = "qweqweqwe"
        self.auth.set_login_script = MagicMock()
        self.auth._users.get_profile = MagicMock()
        self.auth._users.get_profile.return_value = {"user_id": "john"}
        self.assertEqual("qweqweqwe", self.auth.get_api_token())

    def test_get_api_token_push(self):
        """Should use push path when a virtual device is registered"""
        self.auth._state.api_token = ""
        self.auth._db.duo_akey = 'registered_akey'
        self.auth._db.duo_pkey = 'registered_pkey'
        self.auth._db.duo_host = 'api.duosecurity.com'
        self.auth.set_login_script = MagicMock()
        self.auth.get_authentication_response = MagicMock()
        self.auth.get_authentication_response.return_value = {
            'duo_auth_url': 'https://duoauth.local'
        }
        self.auth._users.get_profile = MagicMock()
        self.auth._users.get_profile.return_value = None
        self.auth.get_login_csrf = MagicMock(return_value="csrf_fwlnm")

        self.auth._api.request.return_value.status_code = 200
        ret_json = {"access_token": "api_lwfaume"}
        self.auth._api.request.return_value.json.return_value = ret_json
        self.assertEqual("api_lwfaume", self.auth.get_api_token())
        self.auth._duo.get_grant_token.assert_called_with('https://duoauth.local')

    def test_get_authentication_response(self):
        """Should return json when credentials are accepted"""
        self.auth._state._email = 'user@example.com'
        self.auth._state._password = 'secret'
        self.auth._api.login.return_value.status_code = 200
        self.auth._api.login.return_value.json.return_value = {'duo_auth_url': 'https://duo.test'}
        result = self.auth.get_authentication_response('csrf123')
        self.assertEqual({'duo_auth_url': 'https://duo.test'}, result)
        self.auth._api.login.assert_called_with('POST', 'authenticate',
                                                headers={'X-CSRF-Token': 'csrf123'},
                                                data={'email': 'user@example.com', 'password': 'secret'})

    def test_get_authentication_response_400_confirm(self):
        """Should clear credentials and raise ValueError on 400 when confirmed"""
        self.auth._state._email = 'user@example.com'
        self.auth._state._password = 'secret'
        res_400 = MagicMock()
        res_400.status_code = 400
        self.auth._api.login.return_value = res_400
        with unittest.mock.patch('builtins.input', return_value='y'):
            with self.assertRaises(ValueError):
                self.auth.get_authentication_response('old_csrf')
        self.assertEqual('', self.auth._db.email)
        self.assertEqual('', self.auth._db.password)

    def test_get_authentication_response_400_declined(self):
        """Should keep credentials but still raise ValueError on 400 when declined"""
        self.auth._state._email = 'user@example.com'
        self.auth._state._password = 'secret'
        res_400 = MagicMock()
        res_400.status_code = 400
        self.auth._api.login.return_value = res_400
        with unittest.mock.patch('builtins.input', return_value='n'):
            with self.assertRaises(ValueError):
                self.auth.get_authentication_response('old_csrf')
        self.assertNotEqual('', self.auth._db.email)
        self.assertNotEqual('', self.auth._db.password)

    def test_get_authentication_response_400_session_conflict(self):
        """A session-conflict 400 should return the body, not clear creds/raise"""
        self.auth._state._email = 'user@example.com'
        self.auth._state._password = 'secret'
        body = {
            'success': False,
            'error': ('Simultaneous Non Launchpoint and LaunchPoint+ sessions '
                      'are not permitted. Logging in here will terminate your '
                      'existing session and deselect any selected target.')
        }
        res_400 = MagicMock()
        res_400.status_code = 400
        res_400.json.return_value = body
        self.auth._api.login.return_value = res_400
        # No input() prompt, no raise -- just returns the body
        result = self.auth.get_authentication_response('csrf')
        self.assertEqual(body, result)
        self.assertNotEqual('', self.auth._db.email)
        self.assertNotEqual('', self.auth._db.password)

    def test_get_api_token_session_conflict_retry(self):
        """Should retry when blocked by an existing session, then succeed"""
        self.auth._state.api_token = ""
        self.auth._db.duo_akey = 'ak'
        self.auth._db.duo_pkey = 'pk'
        self.auth._db.duo_host = 'api.duo.com'
        self.auth.set_login_script = MagicMock()
        self.auth._users.get_profile = MagicMock(return_value=None)
        self.auth.get_login_csrf = MagicMock(return_value='csrf')
        conflict = {'success': False, 'error': 'existing session not permitted'}
        ok = {'duo_auth_url': 'https://duoauth.local'}
        self.auth.get_authentication_response = MagicMock(side_effect=[conflict, ok])
        self.auth._duo.get_grant_token.return_value = 'grant'
        self.auth._api.request.return_value.status_code = 200
        self.auth._api.request.return_value.json.return_value = {'access_token': 'api_tok'}
        with unittest.mock.patch('synack.plugins.auth.time.sleep'):
            self.assertEqual('api_tok', self.auth.get_api_token())
        self.assertEqual(2, self.auth.get_authentication_response.call_count)
        self.auth._duo.get_grant_token.assert_called_with('https://duoauth.local')

    def test_get_authentication_response_400_non_json(self):
        """A 400 with an unparseable body falls back to invalid-credentials"""
        self.auth._state._email = 'user@example.com'
        self.auth._state._password = 'secret'
        res_400 = MagicMock()
        res_400.status_code = 400
        res_400.json.side_effect = ValueError('no json')
        self.auth._api.login.return_value = res_400
        with unittest.mock.patch('builtins.input', return_value='n'):
            with self.assertRaises(ValueError):
                self.auth.get_authentication_response('csrf')

    def test_get_authentication_response_423(self):
        """Should raise ValueError on 423 locked"""
        res_423 = MagicMock()
        res_423.status_code = 423
        self.auth._api.login.return_value = res_423
        with self.assertRaises(ValueError):
            self.auth.get_authentication_response('csrf')

    def test_get_notifications_token(self):
        """Should get the notifications token"""
        self.auth._db.notifications_token = ""
        self.auth._api.request.return_value.status_code = 200
        ret_value = {"token": "12345"}
        self.auth._api.request.return_value.json.return_value = ret_value
        self.assertEqual("12345", self.auth.get_notifications_token())
        self.assertEqual("12345", self.auth._db.notifications_token)
        self.auth._api.request.assert_called_with("GET",
                                                  "users/notifications_token")
        self.auth._api.request.return_value.json.assert_called_with()

    def test_login_csrf(self):
        """Should get the login csrf token"""
        ret_text = '<meta name="csrf-token" content="12345"'
        self.auth._api.request.return_value.text = ret_text
        self.assertEqual('12345', self.auth.get_login_csrf())
        self.auth._api.request.assert_called_with("GET",
                                                  "https://login.synack.com")

    def test_set_api_token_invalid(self):
        """Should clear the token and return True on success"""
        self.auth._api.request.return_value.status_code = 200
        result = self.auth.set_api_token_invalid()
        self.assertTrue(result)
        self.assertEqual('', self.auth._db.api_token)
        self.auth._api.request.assert_called_with('POST', 'logout')

    def test_set_api_token_invalid_failure(self):
        """Should return False when logout fails"""
        self.auth._api.request.return_value.status_code = 500
        result = self.auth.set_api_token_invalid()
        self.assertFalse(result)

    def test_set_login_script(self):
        """Should attempt to create a login script with the api token"""
        self.auth._state.api_token = "cvghytrfdvghj"
        self.auth._state.config_dir = pathlib.Path("/tmp")
        m = unittest.mock.mock_open()
        with unittest.mock.patch("builtins.open", m, create=True):
            ret = self.auth.set_login_script()
            self.assertTrue(self.auth._state.api_token in ret)
        m.assert_called_with(self.auth._state.config_dir / 'login.js', 'w')
        m.return_value.write.assert_called()
