"""test_db.py

Tests for the plugins/db.py Db class
"""

import os
import sys
import unittest


from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class DbTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.db = synack.plugins.Db(self.state)

    def test_api_token(self):
        """Should set _api_token and update"""
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = "123"
        self.db.set_config = MagicMock()
        self.db.api_token = "123"
        self.db.set_config.assert_called_with("api_token", "123")
        self.assertEqual("123", self.db.api_token)
        self.db.get_config.assert_called_with("api_token")
