"""test_handler.py

Tests for the Handler class
"""

import os
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class HandlerTestCase(unittest.TestCase):
    def setUp(self):
        for plugin in synack.plugins.base.Plugin._registry.keys():
            synack.plugins.base.Plugin._registry[plugin] = MagicMock()
        self.handler = synack.Handler()

    def test_loads_plugins(self):
        """Should Load all Plugins"""
        plugins = [
            'api', 'auth', 'debug', 'missions', 'notifications',
            'targets', 'templates', 'transactions', 'users'
        ]
        for p in plugins:
            self.assertTrue(hasattr(self.handler, p))

    def test_login(self):
        self.handler.state.login = True
        self.handler._login()
        self.handler.auth.get_api_token.assert_called_with()

    def test_state_kwargs(self):
        handler = synack.Handler(login=True, debug=False)
        self.assertTrue(handler.state.login)
        self.assertFalse(handler.state.debug)
