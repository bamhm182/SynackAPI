"""test_Auth.py

Tests for the _Auth.py Auth Class
"""

import os
import pathlib
import pyotp
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

from src import synack
from unittest.mock import MagicMock


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        synack.Handler = MagicMock()
        self.auth = synack.Auth(synack.Handler())

    def test_gen_otp(self):
        """Should generates an OTP Token"""
        pyotp.TOTP = MagicMock()
        self.auth.handler.db.otp_secret = "123"
        self.auth.gen_otp()
        self.assertEqual(7, pyotp.TOTP.return_value.digits)
        self.assertEqual(10, pyotp.TOTP.return_value.interval)
        self.assertEqual('synack', pyotp.TOTP.return_value.issuer)
        pyotp.TOTP.assert_called_with('123')
        pyotp.TOTP.return_value.now.assert_called_with()

    def test_check_api_token(self):
        """Should make a request to profiles/me"""
        self.auth.handler.api.session.headers = dict()
        self.auth.handler.api.request.return_value.status_code = 200
        self.auth.handler.api.request.return_value.json.return_value = {
            'user_id': 'sumwon'
        }
        self.auth.check_api_token()
        self.auth.handler.api.request.assert_called_with("GET",
                                                         "profiles/me")
        self.assertEqual('sumwon', self.auth.handler.api.session.headers.get('user_id'))

    def test_get_login_progress_token(self):
        """Should get the progress token from valid creds"""
        self.auth.handler.api.login.return_value.status_code = 200
        self.auth.handler.api.login.return_value.json.return_value = {
            "progress_token": "qwfars"
        }
        data = {
            "email": "bob@bob.com",
            "password": "123456"
        }
        headers = {
              "X-Csrf-Token": "abcde"
        }
        self.auth.handler.db.email = "bob@bob.com"
        self.auth.handler.db.password = "123456"
        self.assertEqual("qwfars", self.auth.get_login_progress_token(headers['X-Csrf-Token']))
        self.auth.handler.api.login.assert_called_with("POST",
                                            "authenticate",
                                            headers=headers,
                                            data=data)

    def test_get_login_grant_token(self):
        """Should get the grant token from valid authy TOTP"""
        self.auth.gen_otp = MagicMock(return_value="12345")
        self.auth.handler.api.login.return_value.status_code = 200
        self.auth.handler.api.login.return_value.json.return_value = {
            "grant_token": "qwfars"
        }
        headers = {
                      "X-Csrf-Token": "abcde"
        }
        data = {
            "authy_token": "12345",
            "progress_token": "789456123"
        }

        self.assertEqual("qwfars", self.auth.get_login_grant_token(headers['X-Csrf-Token'], "789456123"))
        self.auth.handler.api.login.assert_called_with("POST",
                                            "authenticate",
                                            headers=headers,
                                            data=data)

    def test_get_api_token(self):
        """Should get the api token"""
        self.auth.handler.db.api_token = ""
        self.auth.get_login_csrf = MagicMock(return_value="csrf_fwlnm")
        self.auth.get_login_progress_token = MagicMock(return_value="pt_rsaemnt")
        self.auth.get_login_grant_token = MagicMock(return_value="gt_fwlnm")
        self.auth.handler.api.request.return_value.status_code = 200
        self.auth.handler.api.request.return_value.json.return_value = {
                                                                "access_token": "api_lwfaume"
        }
        self.assertEqual("api_lwfaume", self.auth.get_api_token())
        self.auth.get_login_csrf.assert_called_with()
        self.auth.get_login_progress_token.assert_called_with("csrf_fwlnm")
        self.auth.get_login_grant_token.assert_called_with("csrf_fwlnm", "pt_rsaemnt")
 
    def test_get_notifications_token(self):
        """Should get the notifications token"""
        self.auth.handler.db.notifications_token = ""
        self.auth.handler.api.request.return_value.status_code = 200
        self.auth.handler.api.request.return_value.json.return_value = {
                                                                "token": "12345"
                                                            }
        self.assertEqual("12345", self.auth.get_notifications_token())
        self.assertEqual("12345", self.auth.handler.db.notifications_token)
        self.auth.handler.api.request.assert_called_with("GET", "users/notifications_token")
        self.auth.handler.api.request.return_value.json.assert_called_with()

    def test_login_csrf(self):
        """Should get the login csrf token"""
        self.auth.handler.api.request.return_value.text = '<meta name="csrf-token" content="12345"'
        self.assertEqual('12345', self.auth.get_login_csrf())
        self.auth.handler.api.request.assert_called_with("GET",
                                              "https://login.synack.com")
        

    def test_write_login_script(self):
        """Should attempt to create a login script with the current api token"""
        self.auth.handler.db.api_token = "cvghytrfdvghj"
        self.auth.handler.db.config_dir = pathlib.Path("/tmp")
        m = unittest.mock.mock_open()
        with unittest.mock.patch("builtins.open", m, create=True):
            ret = self.auth.write_login_script()
            self.assertTrue(self.auth.handler.db.api_token in ret)
        m.assert_called_with(self.auth.handler.db.config_dir / 'login.js', 'w')
        m.return_value.write.assert_called()
        
