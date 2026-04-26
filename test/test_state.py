"""test_state.py

Tests for the State class
"""

import os
import sys
import unittest
import pathlib
import requests

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class StateTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.state._db = MagicMock()

    def test_api_token(self):
        self.assertEqual(self.state._db.api_token, self.state.api_token)
        self.assertEqual(None, self.state._api_token)
        self.state.api_token = 'test_token'
        self.assertEqual('test_token', self.state.api_token)
        self.assertEqual('test_token', self.state._api_token)

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

    def test_debug(self):
        self.assertEqual(self.state._db.debug, self.state.debug)
        self.assertEqual(None, self.state._debug)
        self.state._debug = True
        self.assertEqual(True, self.state._debug)
        self.assertEqual(True, self.state._debug)

    def test_email(self):
        self.assertEqual(self.state._db.email, self.state.email)
        self.assertEqual(None, self.state._email)
        self.state.email = '1@2.com'
        self.assertEqual('1@2.com', self.state.email)
        self.assertEqual('1@2.com', self.state._email)

    def test_http_proxy(self):
        self.assertEqual(self.state._db.http_proxy, self.state.http_proxy)
        self.assertEqual(None, self.state._http_proxy)
        self.state.http_proxy = 'http://1.1.1.1:1234'
        self.assertEqual('http://1.1.1.1:1234', self.state._http_proxy)
        self.assertEqual('http://1.1.1.1:1234', self.state.http_proxy)
        self.assertEqual(self.state.proxies, {
            'http': 'http://1.1.1.1:1234',
            'https': self.state._db.https_proxy
        })

    def test_https_proxy(self):
        self.assertEqual(self.state._db.https_proxy, self.state.https_proxy)
        self.assertEqual(None, self.state._https_proxy)
        self.state.https_proxy = 'http://1.1.1.1:1234'
        self.assertEqual('http://1.1.1.1:1234', self.state.https_proxy)
        self.assertEqual('http://1.1.1.1:1234', self.state._https_proxy)

    def test_login(self):
        self.assertEqual(None, self.state.login)
        self.assertEqual(None, self.state._login)
        self.state.login = False
        self.assertEqual(False, self.state.login)
        self.assertEqual(False, self.state._login)

    def test_notifications_token(self):
        self.assertEqual(self.state._db.notifications_token, self.state.notifications_token)
        self.assertEqual(None, self.state._notifications_token)
        self.state.notifications_token = 'ntoken123'
        self.assertEqual('ntoken123', self.state.notifications_token)
        self.assertEqual('ntoken123', self.state._notifications_token)

    def test_otp_count(self):
        self.assertEqual(self.state._db.otp_count, self.state.otp_count)
        self.assertEqual(None, self.state._otp_count)
        self.state.otp_count = 5
        self.assertEqual(5, self.state.otp_count)
        self.assertEqual(5, self.state._otp_count)

    def test_otp_secret(self):
        self.assertEqual(self.state._db.otp_secret, self.state.otp_secret)
        self.assertEqual(None, self.state._otp_secret)
        self.state.otp_secret = '12345'
        self.assertEqual('12345', self.state.otp_secret)
        self.assertEqual('12345', self.state._otp_secret)

    def test_password(self):
        self.assertEqual(self.state._db.password, self.state.password)
        self.assertEqual(None, self.state._password)
        self.state.password = 'password1234'
        self.assertEqual('password1234', self.state.password)
        self.assertEqual('password1234', self.state._password)

    def test_proxies(self):
        self.assertEqual(self.state.proxies, {
            'http': self.state._db.http_proxy,
            'https': self.state._db.https_proxy
        })
        self.state.http_proxy = 'http://2.2.2.2:1234'
        self.assertEqual(self.state.proxies, {
            'http': 'http://2.2.2.2:1234',
            'https': self.state._db.https_proxy
        })
        self.state.https_proxy = 'http://1.1.1.1:1234'
        self.assertEqual(self.state.proxies, {
            'http': 'http://2.2.2.2:1234',
            'https': 'http://1.1.1.1:1234'
        })

    def test_scratchspace_dir(self):
        self.assertEqual(self.state._db.scratchspace_dir, self.state.scratchspace_dir)
        self.assertEqual(None, self.state._scratchspace_dir)
        self.state.scratchspace_dir = "/tmp"
        self.assertEqual(pathlib.PosixPath, type(self.state.scratchspace_dir))
        self.assertEqual(pathlib.Path('/tmp').expanduser().resolve(),
                         self.state.scratchspace_dir)
        self.assertEqual(pathlib.Path('/tmp').expanduser().resolve(),
                         self.state._scratchspace_dir)

    def test_session(self):
        self.assertEqual(requests.sessions.Session, type(self.state.session))
        self.assertEqual(requests.sessions.Session, type(self.state._session))

    def test_slack_app_token(self):
        self.assertEqual(self.state._db.slack_app_token, self.state.slack_app_token)
        self.assertEqual(None, self.state._slack_app_token)
        self.state.slack_app_token = 'xapp-token'
        self.assertEqual('xapp-token', self.state.slack_app_token)
        self.assertEqual('xapp-token', self.state._slack_app_token)

    def test_slack_channel(self):
        self.assertEqual(self.state._db.slack_channel, self.state.slack_channel)
        self.assertEqual(None, self.state._slack_channel)
        self.state.slack_channel = '#general'
        self.assertEqual('#general', self.state.slack_channel)
        self.assertEqual('#general', self.state._slack_channel)

    def test_slack_url(self):
        self.assertEqual(self.state._db.slack_url, self.state.slack_url)
        self.assertEqual(None, self.state._slack_url)
        self.state.slack_url = 'https://hooks.slack.com/test'
        self.assertEqual('https://hooks.slack.com/test', self.state.slack_url)
        self.assertEqual('https://hooks.slack.com/test', self.state._slack_url)

    def test_smtp_email_from(self):
        self.assertEqual(self.state._db.smtp_email_from, self.state.smtp_email_from)
        self.assertEqual(None, self.state._smtp_email_from)
        self.state.smtp_email_from = 'from@example.com'
        self.assertEqual('from@example.com', self.state.smtp_email_from)
        self.assertEqual('from@example.com', self.state._smtp_email_from)

    def test_smtp_email_to(self):
        self.assertEqual(self.state._db.smtp_email_to, self.state.smtp_email_to)
        self.assertEqual(None, self.state._smtp_email_to)
        self.state.smtp_email_to = 'to@example.com'
        self.assertEqual('to@example.com', self.state.smtp_email_to)
        self.assertEqual('to@example.com', self.state._smtp_email_to)

    def test_smtp_password(self):
        self.assertEqual(self.state._db.smtp_password, self.state.smtp_password)
        self.assertEqual(None, self.state._smtp_password)
        self.state.smtp_password = 'smtppass'
        self.assertEqual('smtppass', self.state.smtp_password)
        self.assertEqual('smtppass', self.state._smtp_password)

    def test_smtp_port(self):
        self.assertEqual(self.state._db.smtp_port, self.state.smtp_port)
        self.assertEqual(None, self.state._smtp_port)
        self.state.smtp_port = 587
        self.assertEqual(587, self.state.smtp_port)
        self.assertEqual(587, self.state._smtp_port)

    def test_smtp_server(self):
        self.assertEqual(self.state._db.smtp_server, self.state.smtp_server)
        self.assertEqual(None, self.state._smtp_server)
        self.state.smtp_server = 'smtp.example.com'
        self.assertEqual('smtp.example.com', self.state.smtp_server)
        self.assertEqual('smtp.example.com', self.state._smtp_server)

    def test_smtp_starttls(self):
        self.assertEqual(self.state._db.smtp_starttls, self.state.smtp_starttls)
        self.assertEqual(None, self.state._smtp_starttls)
        self.state.smtp_starttls = True
        self.assertEqual(True, self.state.smtp_starttls)
        self.assertEqual(True, self.state._smtp_starttls)

    def test_smtp_username(self):
        self.assertEqual(self.state._db.smtp_username, self.state.smtp_username)
        self.assertEqual(None, self.state._smtp_username)
        self.state.smtp_username = 'smtpuser'
        self.assertEqual('smtpuser', self.state.smtp_username)
        self.assertEqual('smtpuser', self.state._smtp_username)

    def test_synack_domain(self):
        self.assertEqual(self.state._db.synack_domain, self.state.synack_domain)
        self.assertEqual(None, self.state._synack_domain)
        self.state.synack_domain = 'synack.us'
        self.assertEqual('synack.us', self.state.synack_domain)
        self.assertEqual('synack.us', self.state._synack_domain)

    def test_template_dir(self):
        self.assertEqual(self.state._db.template_dir, self.state.template_dir)
        self.assertEqual(None, self.state._template_dir)
        self.state.template_dir = "/tmp"
        self.assertEqual(pathlib.PosixPath, type(self.state.template_dir))
        self.assertEqual(pathlib.Path('/tmp').expanduser().resolve(),
                         self.state.template_dir)
        self.assertEqual(pathlib.Path('/tmp').expanduser().resolve(),
                         self.state._template_dir)

    def test_use_proxies(self):
        self.assertEqual(self.state._db.use_proxies, self.state.use_proxies)
        self.assertEqual(None, self.state._use_proxies)
        self.state.use_proxies = True
        self.assertEqual(True, self.state.use_proxies)
        self.assertEqual(True, self.state._use_proxies)

    def test_user_id(self):
        self.assertEqual(self.state._db.user_id, self.state.user_id)
        self.assertEqual(None, self.state._user_id)
        self.state.user_id = '12345'
        self.assertEqual('12345', self.state.user_id)
        self.assertEqual('12345', self.state._user_id)

    def test_use_scratchspace(self):
        self.assertEqual(self.state._db.use_scratchspace, self.state.use_scratchspace)
        self.assertEqual(None, self.state._use_scratchspace)
        self.state.use_scratchspace = True
        self.assertEqual(True, self.state.use_scratchspace)
        self.assertEqual(True, self.state._use_scratchspace)
