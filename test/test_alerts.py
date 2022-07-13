"""test_alerts.py

Tests for the plugins/alerts.py Alerts class
"""

import os
import sys
import unittest

from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class AlertsTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.alerts = synack.plugins.Alerts(self.state)
        self.alerts.db = MagicMock()

    def test_email_no_tls(self):
        """Should send a non-TLS encrypted email"""
        self.alerts.db.smtp_starttls = False
        self.alerts.db.smtp_server = 'smtp.email.com'
        self.alerts.db.smtp_port = 587
        self.alerts.db.smtp_username = 'user5'
        self.alerts.db.smtp_password = 'password123'
        with patch('smtplib.SMTP') as mock_smtp:
            self.alerts.email('subject', 'body')
            mock_smtp.assert_called_with('smtp.email.com', 587)

    def test_email_tls(self):
        """Should send a TLS encrypted email"""
        self.alerts.db.smtp_starttls = True
        self.alerts.db.smtp_server = 'smtp.email.com'
        self.alerts.db.smtp_port = 465
        self.alerts.db.smtp_username = 'user5'
        self.alerts.db.smtp_password = 'password123'
        with patch('smtplib.SMTP_SSL') as mock_smtp:
            with patch('email.message.EmailMessage') as mock_msg:
                with patch('datetime.datetime') as mock_dt:
                    mock_dt.now.return_value.strftime.return_value = '123'
                    self.alerts.email('subject', 'body')
                    mock_msg.return_value.set_content.assert_called_with('body\nTime: 123')
                    mock_smtp.assert_called_with('smtp.email.com', 465)
                    mock_smtp.return_value.login.assert_called_with('user5', 'password123')
                    mock_smtp.return_value.send_message.assert_called_with(mock_msg.return_value)

    def test_slack(self):
        """Should POST a message to slack"""
        with patch('requests.post') as mock_post:
            self.alerts.db.slack_url = 'https://slack.com'
            self.alerts.slack('this is a test')
            mock_post.assert_called_with('https://slack.com',
                                         data='{"text": "this is a test"}',
                                         headers={'Content-Type': 'application/json'})
