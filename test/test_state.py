"""test_state.py

Tests for the State class
"""

import os
import sys
import unittest
import pathlib
import requests

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class StateTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()

    def test_config_dir(self):
        self.assertEqual(pathlib.PosixPath, type(self.state.config_dir))
        self.assertEqual(pathlib.PosixPath, type(self.state._config_dir))
        default = pathlib.Path('~/.config/synack').expanduser().resolve()
        self.assertEqual(default, self.state.config_dir)
        self.state.config_dir = "/tmp"
        self.assertEqual(pathlib.PosixPath, type(self.state.config_dir))
        self.assertEqual(pathlib.Path('/tmp').expanduser().resolve(),
                         self.state.config_dir)
        self.assertEqual(pathlib.Path('/tmp').expanduser().resolve(),
                         self.state._config_dir)

    def test_template_dir(self):
        self.assertEqual(None, self.state.template_dir)
        self.assertEqual(None, self.state._template_dir)
        self.state.template_dir = "/tmp"
        self.assertEqual(pathlib.PosixPath, type(self.state.template_dir))
        self.assertEqual(pathlib.Path('/tmp').expanduser().resolve(),
                         self.state.template_dir)
        self.assertEqual(pathlib.Path('/tmp').expanduser().resolve(),
                         self.state._template_dir)

    def test_debug(self):
        self.assertEqual(None, self.state.debug)
        self.assertEqual(None, self.state._debug)
        self.state.debug = True
        self.assertEqual(True, self.state.debug)
        self.assertEqual(True, self.state._debug)

    def test_session(self):
        self.assertEqual(requests.sessions.Session, type(self.state.session))
        self.assertEqual(requests.sessions.Session, type(self.state._session))

    def test_login(self):
        self.assertEqual(None, self.state.login)
        self.assertEqual(None, self.state._login)
        self.state.login = False
        self.assertEqual(False, self.state.login)
        self.assertEqual(False, self.state._login)

    def test_use_proxies(self):
        self.assertEqual(None, self.state.use_proxies)
        self.assertEqual(None, self.state._use_proxies)
        self.state.use_proxies = True
        self.assertEqual(True, self.state.use_proxies)
        self.assertEqual(True, self.state._use_proxies)

    def test_http_proxy(self):
        self.assertEqual(None, self.state.http_proxy)
        self.assertEqual(None, self.state._http_proxy)
        self.state.http_proxy = 'http://1.1.1.1:1234'
        self.assertEqual('http://1.1.1.1:1234', self.state._http_proxy)
        self.assertEqual('http://1.1.1.1:1234', self.state.http_proxy)
        self.assertEqual(self.state.proxies, {
            'http': 'http://1.1.1.1:1234',
            'https': None
        })

    def test_https_proxy(self):
        self.assertEqual(None, self.state.https_proxy)
        self.assertEqual(None, self.state._https_proxy)
        self.state.https_proxy = 'http://1.1.1.1:1234'
        self.assertEqual('http://1.1.1.1:1234', self.state.https_proxy)
        self.assertEqual('http://1.1.1.1:1234', self.state._https_proxy)

    def test_proxies(self):
        self.assertEqual(self.state.proxies, {
            'http': None,
            'https': None
        })
        self.state.http_proxy = 'http://2.2.2.2:1234'
        self.assertEqual(self.state.proxies, {
            'http': 'http://2.2.2.2:1234',
            'https': None
        })
        self.state.https_proxy = 'http://1.1.1.1:1234'
        self.assertEqual(self.state.proxies, {
            'http': 'http://2.2.2.2:1234',
            'https': 'http://1.1.1.1:1234'
        })

    def test_otp_secret(self):
        self.assertEqual(None, self.state.otp_secret)
        self.assertEqual(None, self.state._otp_secret)
        self.state.otp_secret = '12345'
        self.assertEqual('12345', self.state.otp_secret)
        self.assertEqual('12345', self.state._otp_secret)

    def test_email(self):
        self.assertEqual(None, self.state.email)
        self.assertEqual(None, self.state._email)
        self.state.email = '1@2.com'
        self.assertEqual('1@2.com', self.state.email)
        self.assertEqual('1@2.com', self.state._email)

    def test_password(self):
        self.assertEqual(None, self.state.password)
        self.assertEqual(None, self.state._password)
        self.state.password = 'password1234'
        self.assertEqual('password1234', self.state.password)
        self.assertEqual('password1234', self.state._password)

    def test_user_id(self):
        self.assertEqual(None, self.state.user_id)
        self.assertEqual(None, self.state._user_id)
        self.state.user_id = '12345'
        self.assertEqual('12345', self.state.user_id)
        self.assertEqual('12345', self.state._user_id)
