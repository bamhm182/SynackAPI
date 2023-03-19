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
        ret = self.scratchspace.build_filepath('test.txt', codename='TIREDTURKEY')
        self.assertEqual(pathlib.Path('/tmp/TIREDTURKEY/test.txt'), ret)

    def test_build_filepath_target(self):
        """Should build the appropriate scratchspace filepath given a filepath"""
        self.scratchspace.db.scratchspace_dir = pathlib.Path('/tmp')
        target = synack.db.models.Target(codename='TIREDTURKEY')
        ret = self.scratchspace.build_filepath('test.txt', target=target)
        self.assertEqual(pathlib.Path('/tmp/TIREDTURKEY/test.txt'), ret)

    def test_set_asset_file(self):
        """Shoudl create an asset file within the correct directory"""
        self.scratchspace.build_filepath = MagicMock()
        self.scratchspace.build_filepath.return_value = '/tmp/TIREDTURKEY/assets.txt'
        m = mock_open()
        with patch('builtins.open', m, create=True):
            ret = self.scratchspace.set_assets_file('Test', codename='TIREDTURKEY')
            self.assertEqual('/tmp/TIREDTURKEY/assets.txt', ret)
            m.return_value.write.assert_called_with('Test')
            m.assert_called_with('/tmp/TIREDTURKEY/assets.txt', 'w')

    def test_set_asset_file_list(self):
        """Shoudl create an asset file within the correct directory"""
        self.scratchspace.build_filepath = MagicMock()
        self.scratchspace.build_filepath.return_value = '/tmp/TIREDTURKEY/assets.txt'
        m = mock_open()
        with patch('builtins.open', m, create=True):
            ret = self.scratchspace.set_assets_file(['one', 'two', 'three'], codename='TIREDTURKEY')
            self.assertEqual('/tmp/TIREDTURKEY/assets.txt', ret)
            m.return_value.write.assert_called_with('one\ntwo\nthree')
            m.assert_called_with('/tmp/TIREDTURKEY/assets.txt', 'w')

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

    def test_set_download_attachments_codename(self):
        """Should download files give a list of attachments"""
        dest_path = pathlib.Path('/tmp/TIREDTURKEY/burp.txt')
        self.scratchspace.build_filepath = MagicMock()
        self.scratchspace.build_filepath.return_value = dest_path
        self.scratchspace.api.request = MagicMock()
        self.scratchspace.api.request.return_value.status_code = 200
        self.scratchspace.api.request.return_value.content = b'file_content'
        m = mock_open()
        attachments = [
            {'slug': '43i7h', 'filename': 'file1.txt', 'url': 'https://downloads.com/xyzf'}
        ]
        with patch('builtins.open', m, create=True):
            ret = self.scratchspace.set_download_attachments(attachments, codename='TIREDTIGER')
            self.assertEqual([dest_path], ret)
            m.return_value.write.assert_called_with(b'file_content')
            m.assert_called_with(dest_path, 'wb')

    @patch('builtins.input', side_effect=['yes'])
    def test_set_download_attachments_prompt_overwrite(self, input_mock):
        """Should prompt to overwrite if file exists"""
        dest_path = pathlib.Path('/tmp/TIREDTURKEY/burp.txt')
        self.scratchspace.build_filepath = MagicMock()
        self.scratchspace.build_filepath.return_value = dest_path
        self.scratchspace.api.request = MagicMock()
        self.scratchspace.api.request.return_value.status_code = 200
        self.scratchspace.api.request.return_value.content = b'file_content'
        attachments = [
            {'slug': '43i7h', 'filename': 'file1.txt', 'url': 'https://downloads.com/xyzf'}
        ]
        open_mock = mock_open()

        with patch('pathlib.Path.exists') as exists_mock:
            with patch('builtins.open', open_mock, create=True):
                exists_mock.return_value = True
                ret = self.scratchspace.set_download_attachments(attachments, codename='TIREDTIGER')
                self.assertEqual([dest_path], ret)
                open_mock.return_value.write.assert_called_with(b'file_content')
                open_mock.assert_called_with(dest_path, 'wb')
                input_mock.assert_called_with('file1.txt exists. Overwrite? [y/N]: ')

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
