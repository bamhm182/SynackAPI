"""test_debug.py

Tests for the plugins/debug.py debug class
"""

import datetime
import os
import sys
import unittest
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

from src import synack
from unittest.mock import MagicMock, patch


class NotificationsTestCase(unittest.TestCase):
    def setUp(self):
        synack.Handler = MagicMock()
        self.debug = synack.Debug(synack.Handler(), True)

    def test_enabled(self):
        d = synack.Debug(synack.Handler(), True)
        self.assertEquals(True, d.enabled)

    def test_disabled(self):
        d = synack.Debug(synack.Handler(), False)
        self.assertEquals(False, d.enabled)

    def test_log_enabled(self):
        with patch('builtins.print') as mock_print:
            now = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
            self.debug.log("title", "message")
            mock_print.assert_called_with(f"{now} -- TITLE\n\tmessage")
                
