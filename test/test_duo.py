"""test_Duo.py

Tests for the duo.py Duo Class
"""

import base64
import json
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

    def set_push_vars(self):
        self.duo._akey = 'test_akey'
        self.duo._authkey = 'test_authkey'
        self.duo._req_trace_group = 'rtracegroup'

    def test_browser_features(self):
        """Should return compact JSON string with browser feature flags"""
        result = self.duo._browser_features()
        parsed = json.loads(result)
        self.assertFalse(parsed['touch_supported'])
        self.assertTrue(parsed['webauthn_supported'])
        self.assertEqual(parsed['platform_authenticator_status'], 'unavailable')

    def test_build_headers(self):
        """Should return headers dict with referrer"""
        self.duo._referrer = 'https://example.com/'
        headers = self.duo._build_headers()
        self.assertEqual(headers['Referrer'], 'https://example.com/')
        self.assertIn('Sec-Ch-Ua', headers)

    def test_build_headers_with_overrides(self):
        """Should merge override headers into base headers"""
        self.duo._referrer = 'https://example.com/'
        headers = self.duo._build_headers({'X-Custom': 'value'})
        self.assertEqual(headers['X-Custom'], 'value')
        self.assertIn('Referrer', headers)

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

    @patch('synack.plugins.duo.pkcs1_15')
    @patch('synack.plugins.duo.SHA512')
    @patch('synack.plugins.duo.RSA')
    def test_generate_push_signature(self, mock_rsa, mock_sha512, mock_pkcs1_15):
        """Should generate Basic auth header using RSA signature"""
        self.duo._db.duo_rsa_key = 'fake_pem'
        self.duo._db.duo_host = 'api.duosecurity.com'
        self.duo._db.duo_pkey = 'pkey123'
        mock_key = MagicMock()
        mock_rsa.import_key.return_value = mock_key
        mock_hash = MagicMock()
        mock_sha512.new.return_value = mock_hash
        mock_signer = MagicMock()
        mock_pkcs1_15.new.return_value = mock_signer
        mock_signer.sign.return_value = b'signature_bytes'
        result = self.duo._generate_push_signature('GET', '/path', 'now', {'key': 'val'})
        self.assertTrue(result.startswith('Basic '))

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

    @patch('synack.plugins.duo.RSA')
    def test_get_duo_push_values_missing_padding(self, mock_rsa):
        """Should add base64 padding when host_part length is not a multiple of 4"""
        mock_key = MagicMock()
        mock_rsa.import_key.return_value = mock_key
        mock_key.publickey.return_value.export_key.return_value = b'fake_pubkey'
        self.duo._db.duo_rsa_key = 'fake_pem'
        self.duo._api.request.return_value.status_code = 200
        self.duo._api.request.return_value.json.return_value = {
            'response': {'akey': 'akey', 'pkey': 'pkey'}
        }
        # 'a.com' encodes to 'YS5jb20=' (8 chars); strip '=' to get 7 chars (7 % 4 == 3)
        host_part = base64.b64encode(b'a.com').decode().rstrip('=')
        self.duo.get_duo_push_values(f'CODE-{host_part}')
        self.assertEqual(self.duo._db.duo_host, 'a.com')

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

    def test_get_grant_token_private(self):
        """Should POST progress_token and set _grant_token on 200"""
        self.duo._xsrf = 'test_xsrf'
        self.duo._progress_token = 'prog_token'
        self.duo._api.login.return_value.status_code = 200
        self.duo._api.login.return_value.json.return_value = {'grant_token': 'gt123'}
        self.duo._get_grant_token()
        self.assertEqual(self.duo._grant_token, 'gt123')

    def test_get_grant_token_push(self):
        """Should complete push flow when akey and authkey are set after session setup"""

        self.duo._get_session_variables = MagicMock(side_effect=self.set_push_vars)
        self.duo._post_browser_event = MagicMock()
        self.duo._get_prompt_payload = MagicMock()
        self.duo._get_prompt_initialization = MagicMock()
        self.duo._get_prompt_evaluation = MagicMock(
            side_effect=lambda: setattr(self.duo, '_pkey', 'test_pkey'))
        self.duo._get_prompt_push_txid = MagicMock(
            side_effect=lambda: setattr(self.duo, '_push_txid', 'push_txid123'))
        self.duo.set_duo_push_approved = MagicMock()
        self.duo._get_prompt_push_status = MagicMock(
            side_effect=lambda: setattr(self.duo, '_status', 'SUCCESS'))
        self.duo._get_prompt_remember_me = MagicMock()
        self.duo._get_prompt_finalize = MagicMock()
        self.duo._grant_token = 'grant_token_push'
        result = self.duo.get_grant_token('https://duo.test/auth')
        self.assertEqual(result, 'grant_token_push')
        self.duo._get_prompt_push_txid.assert_called_once()
        self.duo._get_prompt_remember_me.assert_called_once()

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

    def test_get_oidc_exit_grant_token(self):
        """Should extract grant_token from redirect URL"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._factor = 'Duo Push'
        self.duo._device = 'phone0'
        self.duo._xsrf = 'test_xsrf'
        res = MagicMock()
        res.status_code = 200
        res.url = 'https://login.synack.us/callback?grant_token=my_token&other=stuff'
        self.duo._api.request.return_value = res
        self.duo._get_oidc_exit()
        self.assertEqual(self.duo._grant_token, 'my_token')

    def test_get_oidc_exit_progress_token(self):
        """Should extract progress_token when no grant_token in redirect URL"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._factor = 'Duo Push'
        self.duo._device = 'phone0'
        self.duo._xsrf = 'test_xsrf'
        res = MagicMock()
        res.status_code = 200
        res.url = 'https://login.synack.us/callback?token=prog_token_value'
        res.text = '<meta name="csrf-token" content="new_csrf"'
        self.duo._api.request.return_value = res
        self.duo._utils.get_html_tag_value.return_value = 'new_csrf'
        self.duo._get_oidc_exit()
        self.assertEqual(self.duo._progress_token, 'prog_token_value')
        self.assertEqual(self.duo._xsrf, 'new_csrf')

    def test_get_prompt_evaluation(self):
        """Should extract pkey and available auth method types"""
        self.duo._authkey = 'test_authkey'
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._akey = 'test_akey'
        self.duo._api.request.return_value.status_code = 200
        self.duo._api.request.return_value.json.return_value = {
            'response': {
                'can_opt_out_of_push': True,
                'available_unified_auth_factors': {
                    'factors': [
                        {'factor_type': 'push', 'device_info': {'pkey': 'pkey_abc'}}
                    ]
                }
            }
        }
        self.duo._get_prompt_evaluation()
        self.assertTrue(self.duo._can_opt_out_of_push)
        self.assertEqual(self.duo._pkey, 'pkey_abc')
        self.assertEqual(self.duo._available_auth_method_types, 'push')

    def test_get_prompt_finalize(self):
        """Should follow exit_url and extract grant_token"""
        self.duo._authkey = 'test_authkey'
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._akey = 'test_akey'
        res1 = MagicMock()
        res1.status_code = 200
        res1.json.return_value = {'response': {'url': 'https://login.synack.com/callback'}}
        res2 = MagicMock()
        res2.url = 'https://login.synack.com/callback?grant_token=final_token'
        self.duo._api.request.side_effect = [res1, res2]
        self.duo._get_prompt_finalize()
        self.assertEqual(self.duo._grant_token, 'final_token')

    def test_get_prompt_initialization(self):
        """Should make GET request to initialization endpoint"""
        self.duo._authkey = 'test_authkey'
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._akey = 'test_akey'
        self.duo._get_prompt_initialization()
        self.duo._api.request.assert_called_once()
        call_args = self.duo._api.request.call_args
        self.assertEqual(call_args[0][0], 'GET')
        self.assertIn('initialization', call_args[0][1])

    def test_get_prompt_payload(self):
        """Should extract ikey and ukey from response"""
        self.duo._authkey = 'test_authkey'
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._akey = 'test_akey'
        self.duo._api.request.return_value.status_code = 200
        self.duo._api.request.return_value.json.return_value = {
            'response': {'ikey': 'ikey123', 'ukey': 'ukey456'}
        }
        self.duo._get_prompt_payload()
        self.assertEqual(self.duo._ikey, 'ikey123')
        self.assertEqual(self.duo._ukey, 'ukey456')

    @patch('synack.plugins.duo.time.sleep')
    def test_get_prompt_push_status_blocked(self, mock_sleep):
        """Should call set_duo_push_approved on status_enum 15 and continue looping"""
        self.duo._authkey = 'test_authkey'
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._akey = 'test_akey'
        self.duo._push_txid = 'push_txid'
        self.duo._pkey = 'test_pkey'
        self.duo.set_duo_push_approved = MagicMock()
        res_blocked = MagicMock()
        res_blocked.status_code = 200
        res_blocked.json.return_value = {'response': {'result': 'PENDING', 'status_enum': 15}}
        res_success = MagicMock()
        res_success.status_code = 200
        res_success.json.return_value = {
            'response': {
                'result': {'result': 'SUCCESS', 'auth_result': {'authn_evaluation': {}}},
                'status_enum': 5
            }
        }
        self.duo._api.request.side_effect = [res_blocked, res_success]
        self.duo._get_prompt_push_status()
        self.duo.set_duo_push_approved.assert_called()
        self.assertEqual(self.duo._status, 'SUCCESS')

    @patch('synack.plugins.duo.time.sleep')
    def test_get_prompt_push_status_declined(self, mock_sleep):
        """Should break on status_enum 6 or 7"""
        self.duo._authkey = 'test_authkey'
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._akey = 'test_akey'
        self.duo._push_txid = 'push_txid'
        res = MagicMock()
        res.status_code = 200
        res.json.return_value = {'response': {'result': 'DECLINED', 'status_enum': 6}}
        self.duo._api.request.return_value = res
        self.duo._get_prompt_push_status()
        self.assertEqual(self.duo._api.request.call_count, 1)

    @patch('synack.plugins.duo.time.sleep')
    def test_get_prompt_push_status_success(self, mock_sleep):
        """Should set status to SUCCESS and break"""
        self.duo._authkey = 'test_authkey'
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._akey = 'test_akey'
        self.duo._push_txid = 'push_txid'
        self.duo._pkey = 'test_pkey'
        res = MagicMock()
        res.status_code = 200
        res.json.return_value = {
            'response': {
                'result': {
                    'result': 'SUCCESS',
                    'auth_result': {
                        'authn_evaluation': {
                            'is_allowed': True,
                            'auth_method_type': 'push',
                            'authenticator_key': 'pkey',
                            'status_enum': 5,
                            'request_browser_trust': False
                        }
                    }
                },
                'status_enum': 5
            }
        }
        self.duo._api.request.return_value = res
        self.duo._get_prompt_push_status()
        self.assertEqual(self.duo._status, 'SUCCESS')

    def test_get_prompt_push_txid(self):
        """Should POST to push/auth and set _push_txid"""
        self.duo._authkey = 'test_authkey'
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._akey = 'test_akey'
        self.duo._pkey = 'test_pkey'
        self.duo._api.request.return_value.status_code = 200
        self.duo._api.request.return_value.json.return_value = {
            'response': {'push_txid': 'push_txid_abc'}
        }
        self.duo._get_prompt_push_txid()
        self.assertEqual(self.duo._push_txid, 'push_txid_abc')

    def test_get_prompt_remember_me(self):
        """Should POST to remember_me endpoint"""
        self.duo._authkey = 'test_authkey'
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._akey = 'test_akey'
        self.duo._req_trace_group = 'rtracegroup'
        self.duo._get_prompt_remember_me()
        self.duo._api.request.assert_called_once()
        call_args = self.duo._api.request.call_args
        self.assertEqual(call_args[0][0], 'POST')
        self.assertIn('remember_me', call_args[0][1])

    def test_get_push_transactions(self):
        """Should return list of transactions on 200"""
        self.duo._generate_push_signature = MagicMock(return_value='Basic sig')
        self.duo._db.duo_akey = 'test_akey'
        self.duo._db.duo_host = 'api.duosecurity.com'
        self.duo._api.request.return_value.status_code = 200
        self.duo._api.request.return_value.json.return_value = {
            'response': {'transactions': [{'urgid': 'txn1'}]}
        }
        result = self.duo._get_push_transactions()
        self.assertEqual(result, [{'urgid': 'txn1'}])

    def test_get_push_transactions_non_200(self):
        """Should return empty list on non-200"""
        self.duo._generate_push_signature = MagicMock(return_value='Basic sig')
        self.duo._db.duo_akey = 'test_akey'
        self.duo._db.duo_host = 'api.duosecurity.com'
        self.duo._api.request.return_value.status_code = 500
        result = self.duo._get_push_transactions()
        self.assertEqual(result, [])

    def test_get_session_variables_new_flow(self):
        """Should extract akey, authkey, req_trace_group for new prompt-based flow"""
        self.duo._auth_url = 'https://duo.test/auth'
        res = MagicMock()
        res.status_code = 200
        res.url = ('https://api.duosecurity.com/prompt/akey123'
                   '?authkey=authkey456&req_trace_group=rtracegroup789')
        self.duo._api.request.return_value = res
        self.duo._get_session_variables()
        self.assertEqual(self.duo._akey, 'akey123')
        self.assertEqual(self.duo._authkey, 'authkey456')
        self.assertEqual(self.duo._req_trace_group, 'rtracegroup789')

    def test_get_session_variables_no_base_url(self):
        """Should return early when no duo base_url found in redirect"""
        self.duo._auth_url = 'https://duo.test/auth'
        res = MagicMock()
        res.status_code = 200
        res.url = 'https://someother.site/path'
        self.duo._api.request.return_value = res
        self.duo._get_session_variables()
        self.assertIsNone(self.duo._base_url)

    def test_get_session_variables_no_sid(self):
        """Should return early in old flow when no sid in URL"""
        self.duo._auth_url = 'https://duo.test/auth'
        res = MagicMock()
        res.status_code = 200
        res.url = 'https://api.duofederal.com/frame/v4/auth/prompt'
        self.duo._api.request.return_value = res
        self.duo._get_session_variables()
        self.assertIsNone(self.duo._sid)

    def test_get_session_variables_old_flow(self):
        """Should extract sid and session_vars for old frameless v4 flow"""
        self.duo._auth_url = 'https://duo.test/auth'
        res = MagicMock()
        res.status_code = 200
        res.url = 'https://api.duofederal.com/frame/v4/auth/prompt?sid=test_sid123'
        res.text = '<input name="_xsrf" value="xsrf_token"'
        self.duo._api.request.return_value = res
        self.duo._utils.get_html_tag_value.return_value = 'some_value'
        self.duo._get_session_variables()
        self.assertEqual(self.duo._sid, 'test_sid123')
        self.assertIsNotNone(self.duo._session_vars)

    @patch('synack.plugins.duo.time.sleep')
    def test_get_status_awaiting_push(self, mock_sleep):
        """Should call set_duo_push_approved on status_enum 13 when duo_akey is set"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._xsrf = 'test_xsrf'
        self.duo.set_duo_push_approved = MagicMock()
        self.duo._db.duo_akey = 'registered_akey'
        res_awaiting = MagicMock()
        res_awaiting.status_code = 200
        res_awaiting.json.return_value = {
            'response': {'status_enum': 13, 'result': 'WAITING'}, 'message_enum': -1
        }
        res_success = MagicMock()
        res_success.status_code = 200
        res_success.json.return_value = {
            'response': {'status_enum': 5, 'result': 'SUCCESS'}, 'message_enum': -1
        }
        self.duo._api.request.side_effect = [res_awaiting, res_success]
        self.duo._get_status()
        self.duo.set_duo_push_approved.assert_called()

    @patch('builtins.print')
    @patch('synack.plugins.duo.time.sleep')
    def test_get_status_bad_code(self, mock_sleep, mock_print):
        """Should print and break on status_enum 11"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._xsrf = 'test_xsrf'
        res = MagicMock()
        res.status_code = 200
        res.json.return_value = {
            'response': {'status_enum': 11, 'result': 'UNKNOWN'}, 'message_enum': -1
        }
        self.duo._api.request.return_value = res
        self.duo._get_status()
        self.assertEqual(self.duo._api.request.call_count, 1)

    @patch('builtins.print')
    @patch('synack.plugins.duo.time.sleep')
    def test_get_status_bad_request(self, mock_sleep, mock_print):
        """Should print and break on message_enum 57"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._xsrf = 'test_xsrf'
        res = MagicMock()
        res.status_code = 200
        res.json.return_value = {
            'response': {'status_enum': -1, 'result': 'UNKNOWN'}, 'message_enum': 57
        }
        self.duo._api.request.return_value = res
        self.duo._get_status()
        self.assertEqual(self.duo._api.request.call_count, 1)

    @patch('synack.plugins.duo.time.sleep')
    def test_get_status_blocked(self, mock_sleep):
        """Should break on status_enum 15"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._xsrf = 'test_xsrf'
        res = MagicMock()
        res.status_code = 200
        res.json.return_value = {
            'response': {'status_enum': 15, 'result': 'UNKNOWN'}, 'message_enum': -1
        }
        self.duo._api.request.return_value = res
        self.duo._get_status()
        self.assertEqual(self.duo._api.request.call_count, 1)

    @patch('synack.plugins.duo.time.sleep')
    def test_get_status_declined_6(self, mock_sleep):
        """Should break on status_enum 6"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._xsrf = 'test_xsrf'
        res = MagicMock()
        res.status_code = 200
        res.json.return_value = {
            'response': {'status_enum': 6, 'result': 'UNKNOWN'}, 'message_enum': -1
        }
        self.duo._api.request.return_value = res
        self.duo._get_status()
        self.assertEqual(self.duo._api.request.call_count, 1)

    @patch('synack.plugins.duo.time.sleep')
    def test_get_status_declined_7(self, mock_sleep):
        """Should break on status_enum 7"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._xsrf = 'test_xsrf'
        res = MagicMock()
        res.status_code = 200
        res.json.return_value = {
            'response': {'status_enum': 7, 'result': 'UNKNOWN'}, 'message_enum': -1
        }
        self.duo._api.request.return_value = res
        self.duo._get_status()
        self.assertEqual(self.duo._api.request.call_count, 1)

    @patch('synack.plugins.duo.time.sleep')
    def test_get_status_prior_code(self, mock_sleep):
        """Should increment otp_count by 5 and break on status_enum 44"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._xsrf = 'test_xsrf'
        self.duo._db.otp_count = 0
        res = MagicMock()
        res.status_code = 200
        res.json.return_value = {
            'response': {'status_enum': 44, 'result': 'UNKNOWN'}, 'message_enum': -1
        }
        self.duo._api.request.return_value = res
        self.duo._get_status()
        self.assertEqual(self.duo._db.otp_count, 5)
        self.assertEqual(self.duo._api.request.call_count, 1)

    @patch('synack.plugins.duo.time.sleep')
    def test_get_status_push_sent(self, mock_sleep):
        """Should call set_duo_push_approved on status_enum 56 and continue"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._xsrf = 'test_xsrf'
        self.duo.set_duo_push_approved = MagicMock()
        res_56 = MagicMock()
        res_56.status_code = 200
        res_56.json.return_value = {
            'response': {'status_enum': 56, 'result': 'WAITING'}, 'message_enum': -1
        }
        res_success = MagicMock()
        res_success.status_code = 200
        res_success.json.return_value = {
            'response': {'status_enum': 5, 'result': 'SUCCESS'}, 'message_enum': -1
        }
        self.duo._api.request.side_effect = [res_56, res_success]
        self.duo._get_status()
        self.duo.set_duo_push_approved.assert_called()

    @patch('synack.plugins.duo.time.sleep')
    def test_get_status_success(self, mock_sleep):
        """Should break on status_enum 5"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._xsrf = 'test_xsrf'
        res = MagicMock()
        res.status_code = 200
        res.json.return_value = {
            'response': {'status_enum': 5, 'result': 'SUCCESS'}, 'message_enum': -1
        }
        self.duo._api.request.return_value = res
        self.duo._get_status()
        self.assertEqual(self.duo._status, 'SUCCESS')
        self.assertEqual(self.duo._api.request.call_count, 1)

    @patch('builtins.print')
    @patch('synack.plugins.duo.time.sleep')
    def test_get_status_unknown(self, mock_sleep, mock_print):
        """Should print and break on unrecognized status"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._txid = 'test_txid'
        self.duo._xsrf = 'test_xsrf'
        res = MagicMock()
        res.status_code = 200
        res.json.return_value = {
            'response': {'status_enum': 999, 'result': 'UNKNOWN'}, 'message_enum': -1
        }
        self.duo._api.request.return_value = res
        self.duo._get_status()
        self.assertEqual(self.duo._api.request.call_count, 1)

    def test_get_txid_hotp(self):
        """Should include passcode in POST data and increment otp_count"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._xsrf = 'test_xsrf'
        self.duo._get_mfa_details = MagicMock(side_effect=lambda: [
            setattr(self.duo, '_device', 'phone0'),
            setattr(self.duo, '_factor', 'Passcode'),
            setattr(self.duo, '_hotp', '123456')
        ])
        self.state._otp_secret = 'TOPSECRET'
        self.duo._db.otp_count = 5
        self.duo._api.request.return_value.status_code = 200
        self.duo._api.request.return_value.json.return_value = {'response': {'txid': 'txid123'}}
        self.duo._get_txid()
        self.assertEqual(self.duo._txid, 'txid123')
        self.assertIn('passcode', self.duo._api.request.call_args[1]['data'])
        self.assertEqual(self.duo._db.otp_count, 6)

    def test_get_txid_no_device(self):
        """Should not POST when device or factor is not set"""
        self.duo._get_mfa_details = MagicMock()
        self.duo._device = None
        self.duo._factor = None
        self.duo._get_txid()
        self.duo._api.request.assert_not_called()

    def test_get_txid_push(self):
        """Should POST to prompt and set txid without passcode for push"""
        self.duo._base_url = 'https://duofederal.com'
        self.duo._sid = 'test_sid'
        self.duo._xsrf = 'test_xsrf'
        self.duo._get_mfa_details = MagicMock(side_effect=lambda: [
            setattr(self.duo, '_device', 'phone0'),
            setattr(self.duo, '_factor', 'Duo Push')
        ])
        self.state._otp_secret = ''
        self.duo._api.request.return_value.status_code = 200
        self.duo._api.request.return_value.json.return_value = {'response': {'txid': 'txid456'}}
        self.duo._get_txid()
        self.assertEqual(self.duo._txid, 'txid456')
        self.assertNotIn('passcode', self.duo._api.request.call_args[1]['data'])

    def test_post_browser_event(self):
        """Should POST to browser_events endpoint with correct headers"""
        self.duo._base_url = 'https://api.duosecurity.com'
        self.duo._akey = 'test_akey'
        self.duo._authkey = 'test_authkey'
        self.duo._req_trace_group = 'rtracegroup'
        body = {'name': 'test_event', 'level': 'info'}
        self.duo._post_browser_event(body)
        self.duo._api.request.assert_called_once()
        call_args = self.duo._api.request.call_args
        self.assertEqual(call_args[0][0], 'POST')
        self.assertIn('browser_events', call_args[0][1])

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
        self.duo.set_duo_push_approved(sleep=0)
        self.duo._api.request.assert_not_called()

    def test_set_session_variables(self):
        """Should POST session vars and update referrer on 200"""
        self.duo._referrer = 'https://duofederal.com/frame/v4/auth/prompt'
        self.duo._session_vars = {'key': 'val'}
        res = MagicMock()
        res.status_code = 200
        res.url = 'https://duofederal.com/frame/v4/auth/new'
        self.duo._api.request.return_value = res
        self.duo._set_session_variables()
        self.assertEqual(self.duo._referrer, 'https://duofederal.com/frame/v4/auth/new')

    def test_set_session_variables_non_200(self):
        """Should not update referrer on non-200"""
        self.duo._referrer = 'https://duofederal.com/frame/v4/auth/prompt'
        self.duo._session_vars = {'key': 'val'}
        res = MagicMock()
        res.status_code = 500
        self.duo._api.request.return_value = res
        self.duo._set_session_variables()
        self.assertEqual(self.duo._referrer, 'https://duofederal.com/frame/v4/auth/prompt')


if __name__ == '__main__':
    unittest.main()
