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

    def test_configure_mfa_hotp(self):
        """Should store otp_secret and otp_count when user selects hotp"""
        with patch('builtins.input', side_effect=['hotp', 'SECRET123', '5']):
            self.duo.configure_mfa()
        self.assertEqual(self.duo._db.otp_secret, 'SECRET123')
        self.assertEqual(self.duo._db.otp_count, 5)

    @patch('synack.plugins.duo.RSA')
    def test_configure_mfa_push_existing(self, mock_rsa):
        """Should store push credentials directly when user selects push existing"""
        pem = '-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----'
        mock_key = MagicMock()
        mock_key.export_key.return_value = pem.encode()
        mock_rsa.import_key.return_value = mock_key
        with patch('builtins.input', side_effect=['push', 'existing', 'akey123', 'pkey123', 'api.duo.com', pem]):
            self.duo.configure_mfa()
        self.assertEqual(self.duo._db.duo_akey, 'akey123')
        self.assertEqual(self.duo._db.duo_pkey, 'pkey123')
        self.assertEqual(self.duo._db.duo_host, 'api.duo.com')
        self.assertEqual(self.duo._db.duo_rsa_key, pem)

    @patch('synack.plugins.duo.RSA')
    def test_configure_mfa_push_existing_b64(self, mock_rsa):
        """Should accept base64-encoded RSA private key and store normalized PEM"""
        pem = '-----BEGIN RSA PRIVATE KEY-----\ntest\n-----END RSA PRIVATE KEY-----'
        b64_key = base64.b64encode(pem.encode()).decode()
        mock_key = MagicMock()
        mock_key.export_key.return_value = pem.encode()
        mock_rsa.import_key.side_effect = [ValueError('invalid'), mock_key]
        with patch('builtins.input', side_effect=['push', 'existing', 'akey123', 'pkey123', 'api.duo.com', b64_key]):
            self.duo.configure_mfa()
        self.assertEqual(self.duo._db.duo_rsa_key, pem)

    def test_configure_mfa_push_new(self):
        """Should call get_duo_push_values with the activation code for a new device"""
        self.duo.get_duo_push_values = MagicMock()
        with patch('builtins.input', side_effect=['push', 'new', 'CODE-aGVsbG8=']):
            self.duo.configure_mfa()
        self.duo.get_duo_push_values.assert_called_with('CODE-aGVsbG8=')

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

    def test_get_grant_token_push(self):
        """Should complete push MFA flow and return grant_token"""
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
        result = self.duo.get_grant_token_push('https://duo.test/auth')
        self.assertEqual(result, 'expected_token')

    def test_get_grant_token_push_no_txid(self):
        """Should return None when txid is not obtained on push path"""
        self.duo._get_session_variables = MagicMock()
        self.duo._set_session_variables = MagicMock()
        self.duo._get_txid = MagicMock()
        self.duo._txid = None
        result = self.duo.get_grant_token_push('https://duo.test/auth')
        self.assertIsNone(result)

    def test_get_mfa_details_hotp(self):
        """Should use HOTP when otp_secret is set and no virtual device is registered"""
        self.state._otp_secret = 'JBSWY3DPEHPK3PXP'
        self.state._otp_count = '0'
        self.duo._db.duo_akey = ''
        self.duo._get_mfa_details()
        self.assertEqual(self.duo._factor, 'Passcode')
        self.assertEqual(self.duo._device, 'null')

    def test_get_mfa_details_push(self):
        """Should use Duo Push when no otp_secret is set"""
        self.state._otp_secret = ''
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._sid = 'test_sid'
        self.duo._xsrf = 'test_xsrf'
        self.duo._api.request.return_value.status_code = 200
        self.duo._api.request.return_value.json.return_value = {
            'response': {
                'auth_method_order': [{'factor': 'Duo Push', 'deviceKey': 'phone-abc'}],
                'phones': [{'key': 'phone-abc', 'index': 'phone0'}]
            }
        }
        self.duo._get_mfa_details()
        self.assertEqual(self.duo._factor, 'Duo Push')
        self.assertEqual(self.duo._device, 'phone0')

    def test_get_mfa_details_push_over_hotp(self):
        """Should use Duo Push over HOTP when a virtual device is registered"""
        self.state._otp_secret = 'JBSWY3DPEHPK3PXP'
        self.state._otp_count = '0'
        self.duo._db.duo_akey = 'registered_akey'
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._sid = 'test_sid'
        self.duo._xsrf = 'test_xsrf'
        self.duo._api.request.return_value.status_code = 200
        self.duo._api.request.return_value.json.return_value = {
            'response': {
                'auth_method_order': [{'factor': 'Duo Push', 'deviceKey': 'phone-abc'}],
                'phones': [{'key': 'phone-abc', 'index': 'phone0'}]
            }
        }
        self.duo._get_mfa_details()
        self.assertEqual(self.duo._factor, 'Duo Push')
        self.assertEqual(self.duo._device, 'phone0')

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
