"""test_scratchspace.py

Tests for the plugins/scratchspace.py Db class
"""

import os
import pathlib
import sys
import unittest

from unittest.mock import MagicMock, patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class ScratchspaceTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.scratchspace = synack.plugins.Scratchspace(self.state)

    def test_build_filepath_codename(self):
        """Should build the appropriate scratchspace filepath given a codename"""
        self.scratchspace.db.scratchspace_dir = pathlib.Path('/tmp')
        ret = self.scratchspace.build_filepath('test', codename='TIREDTURKEY')
        self.assertEqual('/tmp/TIREDTURKEY/test.txt', ret)

    def test_build_filepath_target(self):
        """Should build the appropriate scratchspace filepath given a filepath"""
        self.scratchspace.db.scratchspace_dir = pathlib.Path('/tmp')
        target = synack.db.models.Target(codename='TIREDTURKEY')
        ret = self.scratchspace.build_filepath('test', target=target)
        self.assertEqual('/tmp/TIREDTURKEY/test.txt', ret)

    def test_set_burp_file(self):
        """Should create a burp file within the correct directory"""
        self.scratchspace.build_filepath = MagicMock()
        self.scratchspace.build_filepath.return_value = '/tmp/TIREDTURKEY/burp.txt'
        m = mock_open()
        with patch('builtins.open', m, create=True):
            ret = self.scratchspace.set_burp_file('Test', codename='TIREDTURKEY')
            self.assertEqual('/tmp/TIREDTURKEY/burp.txt', ret)
            m.return_value.write.assert_called_with('Test')
            m.assert_called_with('/tmp/TIREDTURKEY/burp.txt', 'w')

    def test_set_burp_file_dict(self):
        """Should convert a Burp dict to a string to save"""
        self.scratchspace.build_filepath = MagicMock()
        self.scratchspace.build_filepath.return_value = '/tmp/TIREDTURKEY/burp.txt'
        m = mock_open()
        with patch('builtins.open', m, create=True):
            ret = self.scratchspace.set_burp_file({'test': 'test'}, codename='TIREDTURKEY')
            self.assertEqual('/tmp/TIREDTURKEY/burp.txt', ret)
            m.return_value.write.assert_called_with('{"test": "test"}')
            m.assert_called_with('/tmp/TIREDTURKEY/burp.txt', 'w')

    def test_set_hosts_file(self):
        """Should create a host file within the correct directory"""
        self.scratchspace.build_filepath = MagicMock()
        self.scratchspace.build_filepath.return_value = '/tmp/TIREDTURKEY/hosts.txt'
        m = mock_open()
        with patch('builtins.open', m, create=True):
            ret = self.scratchspace.set_hosts_file('Test', codename='TIREDTURKEY')
            self.assertEqual('/tmp/TIREDTURKEY/hosts.txt', ret)
            m.return_value.write.assert_called_with('Test')
            m.assert_called_with('/tmp/TIREDTURKEY/hosts.txt', 'w')

    def test_set_hosts_file_list(self):
        """Should properly set hosts file content given a list"""
        self.scratchspace.build_filepath = MagicMock()
        self.scratchspace.build_filepath.return_value = '/tmp/TIREDTURKEY/hosts.txt'
        m = mock_open()
        with patch('builtins.open', m, create=True):
            ret = self.scratchspace.set_hosts_file(['1', '2', '3'], codename='TIREDTURKEY')
            self.assertEqual('/tmp/TIREDTURKEY/hosts.txt', ret)
            m.return_value.write.assert_called_with('1\n2\n3')
            m.assert_called_with('/tmp/TIREDTURKEY/hosts.txt', 'w')
