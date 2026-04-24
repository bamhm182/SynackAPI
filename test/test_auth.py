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
        self.auth._duo.get_grant_token_push.assert_called_with('https://duoauth.local')
        self.auth._duo.get_grant_token.assert_not_called()

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
        self.auth._duo.get_grant_token_push.assert_called_with('https://duoauth.local')
        self.auth._duo.get_grant_token.assert_not_called()

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
