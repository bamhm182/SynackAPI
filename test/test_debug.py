"""test_debug.py

Tests for the plugins/debug.py debug class
"""

import datetime
import os
import sys
import unittest

from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class DebugTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.state._db = MagicMock()
        self.debug = synack.plugins.Debug(self.state)
        self.debug._db = MagicMock()

    def test_log_enabled(self):
        with patch('builtins.print') as mock_print:
            now = datetime.datetime.strftime(datetime.datetime.now(),
                                             "%Y-%m-%d %H:%M:%S")
            self.debug.log("title", "message")
            mock_print.assert_called_with(f"{now} -- TITLE\n\tmessage")
