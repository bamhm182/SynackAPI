"""test_Auth.py

Tests for the _Auth.py Auth Class
"""

import os
import pathlib
import pyotp
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.auth = synack.plugins.Auth(self.state)
        self.auth.api = MagicMock()
        self.auth.db = MagicMock()
        self.auth.users = MagicMock()

    def test_build_otp(self):
        """Should generate a OTP"""
        pyotp.TOTP = MagicMock()
        self.auth.db.otp_secret = "123"
        self.auth.build_otp()
        self.assertEqual(7, pyotp.TOTP.return_value.digits)
        self.assertEqual(10, pyotp.TOTP.return_value.interval)
        self.assertEqual('synack', pyotp.TOTP.return_value.issuer)
        pyotp.TOTP.assert_called_with('123')
        pyotp.TOTP.return_value.now.assert_called_with()

    def test_get_login_progress_token(self):
        """Should get the progress token from valid creds"""
        self.auth.api.login.return_value.status_code = 200
        self.auth.api.login.return_value.json.return_value = {
            "progress_token": "qwfars"
        }
        data = {
            "email": "bob@bob.com",
            "password": "123456"
        }
        headers = {
              "X-CSRF-Token": "abcde"
        }
        self.auth.db.email = "bob@bob.com"
        self.auth.db.password = "123456"
        returned_pt = self.auth.get_login_progress_token('abcde')
        self.assertEqual("qwfars", returned_pt)
        self.auth.api.login.assert_called_with("POST",
                                               "authenticate",
                                               headers=headers,
                                               data=data)

    def test_get_login_grant_token(self):
        """Should get the grant token from valid authy TOTP"""
        self.auth.build_otp = MagicMock(return_value="12345")
        self.auth.api.login.return_value.status_code = 200
        self.auth.api.login.return_value.json.return_value = {
            "grant_token": "qwfars"
        }
        headers = {
                      "X-Csrf-Token": "abcde"
        }
        data = {
            "authy_token": "12345",
            "progress_token": "789456123"
        }

        returned_gt = self.auth.get_login_grant_token('abcde', '789456123')
        self.assertEqual("qwfars", returned_gt)
        self.auth.api.login.assert_called_with("POST",
                                               "authenticate",
                                               headers=headers,
                                               data=data)

    def test_get_api_token(self):
        """Should complete the login workflow when check fails"""
        self.auth.db.api_token = ""
        self.auth.set_login_script = MagicMock()
        self.auth.users.get_profile = MagicMock()
        self.auth.users.get_profile.return_value = None
        self.auth.get_login_csrf = MagicMock(return_value="csrf_fwlnm")
        self.auth.get_login_progress_token = MagicMock()
        self.auth.get_login_progress_token.return_value = "pt_rsaemnt"

        self.auth.get_login_grant_token = MagicMock(return_value="gt_fwlnm")
        self.auth.api.request.return_value.status_code = 200
        ret_json = {"access_token": "api_lwfaume"}
        self.auth.api.request.return_value.json.return_value = ret_json
        self.assertEqual("api_lwfaume", self.auth.get_api_token())
        self.auth.get_login_csrf.assert_called_with()
        self.auth.set_login_script.assert_called_with()
        self.auth.get_login_progress_token.assert_called_with("csrf_fwlnm")
        self.auth.get_login_grant_token.assert_called_with("csrf_fwlnm",
                                                           "pt_rsaemnt")

    def test_get_api_token_login_success(self):
        """Should return the database token when check succeeds"""
        self.auth.db.api_token = "qweqweqwe"
        self.auth.set_login_script = MagicMock()
        self.auth.users.get_profile = MagicMock()
        self.auth.users.get_profile.return_value = {"user_id": "john"}
        self.assertEqual("qweqweqwe", self.auth.get_api_token())

    def test_get_notifications_token(self):
        """Should get the notifications token"""
        self.auth.db.notifications_token = ""
        self.auth.api.request.return_value.status_code = 200
        ret_value = {"token": "12345"}
        self.auth.api.request.return_value.json.return_value = ret_value
        self.assertEqual("12345", self.auth.get_notifications_token())
        self.assertEqual("12345", self.auth.db.notifications_token)
        self.auth.api.request.assert_called_with("GET",
                                                 "users/notifications_token")
        self.auth.api.request.return_value.json.assert_called_with()

    def test_login_csrf(self):
        """Should get the login csrf token"""
        ret_text = '<meta name="csrf-token" content="12345"'
        self.auth.api.request.return_value.text = ret_text
        self.assertEqual('12345', self.auth.get_login_csrf())
        self.auth.api.request.assert_called_with("GET",
                                                 "https://login.synack.com")

    def test_set_login_script(self):
        """Should attempt to create a login script with the api token"""
        self.auth.db.api_token = "cvghytrfdvghj"
        self.auth.state.config_dir = pathlib.Path("/tmp")
        m = unittest.mock.mock_open()
        with unittest.mock.patch("builtins.open", m, create=True):
            ret = self.auth.set_login_script()
            self.assertTrue(self.auth.db.api_token in ret)
        m.assert_called_with(self.auth.state.config_dir / 'login.js', 'w')
        m.return_value.write.assert_called()
