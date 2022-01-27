"""test_db.py

Tests for the plugins/db.py Db class
"""

import os
import pathlib
import sys
import unittest
import yaml


sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

from src import synack
from unittest.mock import MagicMock, patch, mock_open

real_read = synack.Db.read
real_update = synack.Db.update

class NotificationsTestCase(unittest.TestCase):
    def setUp(self):
        synack.Handler = MagicMock()
        synack.Db.read = MagicMock()
        synack.Db.update = MagicMock()
        with patch.object(pathlib.Path, 'expanduser') as mock_expanduser:
            with patch.object(pathlib.Path, 'mkdir') as mock_mkdir:
                self.db = synack.Db(synack.Handler(), '/tmp/config', '/tmp/Templates')
                self.db.config_dir.mkdir.assert_called_with(parents=True, exist_ok=True)
                self.db.read.assert_called_with()
                self.db.update.assert_called_with()
                
    def test_read(self):
        """Should read config from the predefined config_file"""
        self.db.read = real_read
        self.db.config_file.is_file = MagicMock(return_value=True)
        self.db.load = MagicMock()
        yaml_return = {
            "someconfig": 123
        }
        read_data = """
        someconfig: 123
        """
        self.db.config_file.is_file = MagicMock()
        self.db.config_file.is_file.return_value = True
        yaml.safe_load = MagicMock()
        yaml.safe_load.return_value = yaml_return
        m = mock_open(read_data=read_data)
        with patch('builtins.open', m, create=True):
            self.db.read(self.db)
            self.db.config_file.is_file.assert_called_with()
            m.assert_called_with(self.db.config_file, 'r')
            yaml.safe_load.assert_called_with(m.return_value)
                
        self.db.load.assert_called_with(yaml_return)

    def test_load(self):
        """Should load a config into the db params"""
        config = {
            "email": "ij8y76tghj",
            "password": "i876tfvbhytrfg",
            "otp_secret": "juytghytfvbhj",
            "api_token": "u76tfghytrfghuy",
            "assessments": ["iuytgbnji87yh"],
            "known_targets": ["9876tghjk"],
            "proxies": {"http": "1", "https":"2"},
            "template_dir": "/tmp/Templates",
            "use_proxies": True
        }
        self.db.load(config)
        self.assertEquals("ij8y76tghj", self.db.email)
        self.assertEquals("i876tfvbhytrfg", self.db.password)
        self.assertEquals("juytghytfvbhj", self.db.otp_secret)
        self.assertEquals("u76tfghytrfghuy", self.db.api_token)
        self.assertEquals(["iuytgbnji87yh"], self.db.assessments)
        self.assertEquals(["9876tghjk"], self.db.known_targets)
        self.assertEquals({"http": "1", "https":"2"}, self.db.proxies)
        self.assertEquals(pathlib.Path("/tmp/Templates"), self.db.template_dir)
        self.assertEquals(True, self.db.use_proxies)

    def test_load_defaults(self):
        """Should load a config into the db params"""
        config = {}
        calls = [
            unittest.mock.call("Synack Email: "),
            unittest.mock.call("Synack Password: "),
            unittest.mock.call("Synack OTP Secret: "),
        ]
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ["email", "password", "otp"]
            self.db.load(config)
            mock_input.assert_has_calls(calls)
            self.assertEquals("email", self.db.email)
            self.assertEquals("password", self.db.password)
            self.assertEquals("otp", self.db.otp_secret)
            self.assertEquals("", self.db.api_token)
            self.assertEquals([], self.db.assessments)
            self.assertEquals([], self.db.known_targets)
            self.assertEquals({'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}, self.db.proxies)
            self.assertEquals(pathlib.Path("~/Templates").expanduser(), self.db.template_dir)
            self.assertEquals(False, self.db.use_proxies)
   
    def test_update(self):
        """Should write to the config with the current variables"""
        self.db.update = real_update
        self.db.config_file = pathlib.Path('/tmp/config')
        m = mock_open()
        yaml.safe_dump = MagicMock()
        yaml_return = "someconfig: 123"
        yaml.safe_dump.return_value = yaml_return
        with patch('builtins.open', m, create=True):
            self.db.update(self.db)
            m.assert_called_with(self.db.config_file, 'w')
            m.return_value.write.assert_called_with(yaml_return)

    def test_api_token(self):
        """Should set _api_token and update"""
        self.db.api_token = "123"
        self.db.update.assert_called_with()
        self.assertEquals("123", self.db._api_token)
        self.assertEquals("123", self.db.api_token)

    def test_notifications_token(self):
        """Should set _notifications_token and update"""
        self.db.notifications_token = "ytfgh"
        self.db.update.assert_called_with()
        self.assertEquals("ytfgh", self.db._notifications_token)
        self.assertEquals("ytfgh", self.db.notifications_token)

    def test_assessments(self):
        """Should set _assessments and update"""
        self.db.assessments = ["qweourgi"]
        self.db.update.assert_called_with()
        self.assertEquals(["qweourgi"], self.db._assessments)
        self.assertEquals(["qweourgi"], self.db.assessments)

    def test_known_targets(self):
        """Should set _known_targets and update"""
        self.db.known_targets = ["wuiqete"]
        self.db.update.assert_called_with()
        self.assertEquals(["wuiqete"], self.db._known_targets)
        self.assertEquals(["wuiqete"], self.db.known_targets)
