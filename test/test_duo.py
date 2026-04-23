"""test_Duo.py

Tests for the duo.py Duo Class
"""

import base64
import os
import sys
import unittest

from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class DuoTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.state._db = MagicMock()
        self.duo = synack.plugins.Duo(self.state)
        self.duo._api = MagicMock()
        self.duo._db = MagicMock()
        self.duo._utils = MagicMock()

    @patch('synack.plugins.duo.RSA')
    def test_get_duo_push_values(self, mock_rsa):
        """Should register as a virtual Duo device and store credentials"""
        mock_key = MagicMock()
        mock_rsa.import_key.return_value = mock_key
        mock_key.publickey.return_value.export_key.return_value = b'fake_pubkey'
        self.duo._db.duo_rsa_key = 'fake_pem'
        self.duo._api.request.return_value.status_code = 200
        self.duo._api.request.return_value.json.return_value = {
            'response': {'akey': 'test_akey', 'pkey': 'test_pkey'}
        }
        host = 'api.duosecurity.com'
        host_b64 = base64.b64encode(host.encode()).decode()
        self.duo.get_duo_push_values(f'TESTCODE-{host_b64}')
        self.assertEqual(self.duo._db.duo_akey, 'test_akey')
        self.assertEqual(self.duo._db.duo_pkey, 'test_pkey')
        self.assertEqual(self.duo._db.duo_host, host)

    def test_get_grant_token(self):
        """Should complete MFA flow and return grant_token"""
        self.duo._get_session_variables = MagicMock()
        self.duo._set_session_variables = MagicMock()
        self.duo._get_txid = MagicMock()
        self.duo._get_status = MagicMock()
        self.duo._get_oidc_exit = MagicMock()
        self.duo._get_grant_token = MagicMock()
        self.duo._txid = 'test_txid'
        self.duo._status = 'SUCCESS'
        self.duo._progress_token = 'test_token'
        self.duo._grant_token = 'expected_token'
        result = self.duo.get_grant_token('https://duo.test/auth')
        self.assertEqual(result, 'expected_token')

    def test_get_grant_token_no_txid(self):
        """Should return None when txid is not obtained"""
        self.duo._get_session_variables = MagicMock()
        self.duo._set_session_variables = MagicMock()
        self.duo._get_txid = MagicMock()
        self.duo._txid = None
        result = self.duo.get_grant_token('https://duo.test/auth')
        self.assertIsNone(result)

    def test_set_duo_push_approved(self):
        """Should approve all pending push transactions"""
        self.duo._get_push_transactions = MagicMock(return_value=[
            {'urgid': 'txn123'}
        ])
        self.duo._generate_push_signature = MagicMock(return_value='Basic sig')
        self.duo._db.duo_akey = 'akey'
        self.duo._db.duo_host = 'api.duosecurity.com'
        self.duo._api.request.return_value.status_code = 200
        self.duo.set_duo_push_approved()
        self.duo._api.request.assert_called_once()
        call_args = self.duo._api.request.call_args
        self.assertEqual(call_args[0][0], 'POST')
        self.assertIn('txn123', call_args[0][1])

    def test_set_duo_push_approved_no_urgid(self):
        """Should skip transactions that have no urgid"""
        self.duo._get_push_transactions = MagicMock(return_value=[
            {'other_field': 'value'}
        ])
        self.duo._generate_push_signature = MagicMock(return_value='Basic sig')
        self.duo.set_duo_push_approved()
        self.duo._api.request.assert_not_called()


if __name__ == '__main__':
    unittest.main()
