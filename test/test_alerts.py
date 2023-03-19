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

    def test_sanitize_ipv4(self):
        """Should sanitize IPv4"""
        self.assertEqual(self.alerts.sanitize('192.168.10.254'), '[IPv4]')
        self.assertEqual(self.alerts.sanitize('This is an IP: 12.182.8.1'), 'This is an IP: [IPv4]')

    def test_sanitize_ipv6(self):
        """Should sanitize IPv6"""
        self.assertEqual(self.alerts.sanitize('::1'), '[IPv6]')
        self.assertEqual(self.alerts.sanitize('2001:db8:3333:4444:5555:6666:7777:8888'), '[IPv6]')
        self.assertEqual(self.alerts.sanitize('2001:db8::'), '[IPv6]')
        self.assertEqual(self.alerts.sanitize('::1234:5678'), '[IPv6]')
        self.assertEqual(self.alerts.sanitize('2001:db8::1234:5678'), '[IPv6]')
        self.assertEqual(self.alerts.sanitize('2001:0db8:0001:0000:0000:0ab9:C0A8:0102'), '[IPv6]')
        self.assertEqual(self.alerts.sanitize('2001:db8:1::ab9:C0A8:102'), '[IPv6]')
        self.assertEqual(self.alerts.sanitize('IPv6: 2001:db8:1::ab9:C0A8:102'), 'IPv6: [IPv6]')

    def test_sanitize_overzealous(self):
        """Should not overly sanitize things that are fine"""
        self.assertEqual(self.alerts.sanitize('This is fine'), 'This is fine')
        self.assertEqual(self.alerts.sanitize('This is fine!'), 'This is fine!')
        self.assertEqual(self.alerts.sanitize('This is: fine'), 'This is: fine')
        self.assertEqual(self.alerts.sanitize('This is fine?'), 'This is fine?')
        self.assertEqual(self.alerts.sanitize('24.0'), '24.0')

    def test_sanitize_urls(self):
        """Should sanitize URLs"""
        self.assertEqual(self.alerts.sanitize('test.cc'), '[URL]')
        self.assertEqual(self.alerts.sanitize('http://1.2.ewufg.4.test.cc'), '[URL]')
        self.assertEqual(self.alerts.sanitize('hxxp://1.2.ewufg.4.test.cc'), '[URL]')
        self.assertEqual(self.alerts.sanitize('http://1.2.ewufg.4.test.cc:8081'), '[URL]')
        self.assertEqual(self.alerts.sanitize('http://1.2.ewufg.4.test.cc:8081/tacos/are/number/1'), '[URL]')
        self.assertEqual(self.alerts.sanitize('URL: https://www.test.com/1/2/3/air'), 'URL: [URL]')
        self.assertEqual(self.alerts.sanitize('This is a URL: bob.com'), 'This is a URL: [URL]')

    def test_slack(self):
        """Should POST a message to slack"""
        with patch('requests.post') as mock_post:
            self.alerts.db.slack_url = 'https://slack.com'
            self.alerts.slack('this is a test')
            mock_post.assert_called_with('https://slack.com',
                                         data='{"text": "this is a test"}',
                                         headers={'Content-Type': 'application/json'})
