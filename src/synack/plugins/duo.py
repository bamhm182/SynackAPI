"""plugins/duo.py

Functions related to handling Duo Security Multi-Factor Authentication.
"""

from .base import Plugin

import base64
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import datetime
import email.utils
import json
import pyotp
import re
import time
import urllib.parse


class Duo(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Db', 'Utils']:
            setattr(self,
                    '_'+plugin.lower(),
                    self._registry.get(plugin)(self._state))

        self._akey = None
        self._auth_url = None
        self._authkey = None
        self._authn_evaluation = None
        self._available_auth_method_types = ''
        self._base_url = None
        self._can_opt_out_of_push = False
        self._device = None
        self._factor = None
        self._grant_token = None
        self._hotp = None
        self._ikey = None
        self._pkey = None
        self._progress_token = None
        self._push_txid = None
        self._referrer = None
        self._req_trace_group = None
        self._session_vars = None
        self._status = None
        self._sid = None
        self._txid = None
        self._ukey = None
        self._xsrf = None

    def _browser_features(self):
        return json.dumps({
            'touch_supported': False,
            'platform_authenticator_status': 'unavailable',
            'webauthn_supported': True,
            'screen_resolution_height': 1529,
            'screen_resolution_width': 2446,
            'screen_color_depth': 24,
            'is_uvpa_available': False,
            'client_capabilities_uvpa': False
        }, separators=(',', ':'))

    def _build_headers(self, overrides=None):
        headers = {
            'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Linux"',
            'Referrer': self._referrer,
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document'
        }
        headers.update(overrides if overrides else dict())
        return headers

    def _configure_hotp(self):
        secret = input('OTP Secret: ').strip()
        count = input('OTP Count: ').strip()
        self._db.otp_secret = secret
        self._db.otp_count = int(count)

    def configure_mfa(self):
        """Configure MFA interactively, choosing between Duo Push virtual device or HOTP"""
        choice = input('MFA Type (push/hotp): ').strip().lower()
        if choice == 'push':
            self._configure_push()
        else:
            self._configure_hotp()

    def _configure_push(self):
        choice = input('Setup Type (new/existing): ').strip().lower()
        if choice == 'new':
            code = input('Duo Activation Code: ').strip()
            self.get_duo_push_values(code)
        else:
            self._db.duo_akey = input('Duo AKey: ').strip()
            self._db.duo_pkey = input('Duo PKey: ').strip()
            self._db.duo_host = input('Duo Host: ').strip()
            rsa_input = input('Duo RSA Private Key (PEM or base64): ').strip()
            try:
                key = RSA.import_key(rsa_input)
                pem = key.export_key('PEM').decode('utf-8')
            except (ValueError, IndexError, TypeError):
                decoded = base64.b64decode(rsa_input)
                key = RSA.import_key(decoded)
                pem = key.export_key('PEM').decode('utf-8')
            self._db.duo_rsa_key = pem

    def _generate_push_signature(self, method, path, now, data):
        rsa_key = RSA.import_key(self._db.duo_rsa_key)
        message = (now + '\n' + method + '\n' + self._db.duo_host.lower() + '\n' +
                   path + '\n' + urllib.parse.urlencode(data)).encode('ascii')
        h = SHA512.new(message)
        signature = pkcs1_15.new(rsa_key).sign(h)
        auth = ('Basic ' + base64.b64encode(
            (self._db.duo_pkey + ':' + base64.b64encode(signature).decode('ascii')).encode('ascii')
        ).decode('ascii'))
        return auth

    def get_duo_push_values(self, code):
        """Register SynackAPI as a virtual Duo device using a Duo activation code"""
        code_part, host_part = map(lambda x: x.strip('<>'), code.split('-'))
        missing_padding = len(host_part) % 4
        if missing_padding:
            host_part += '=' * (4 - missing_padding)
        host = base64.b64decode(host_part.encode('ascii')).decode('ascii')
        rsa_key = RSA.import_key(self._db.duo_rsa_key)
        params = {
            'customer_protocol': '1',
            'pubkey': rsa_key.publickey().export_key('PEM').decode('ascii'),
            'pkpush': 'rsa-sha512',
            'jailbroken': 'false',
            'architecture': 'arm64',
            'region': 'US',
            'app_id': 'com.duosecurity.duomobile',
            'full_disk_encryption': 'true',
            'passcode_status': 'true',
            'platform': 'Android',
            'app_version': '4.111.0',
            'app_build_number': '4111000',
            'version': '16',
            'manufacturer': 'unknown',
            'language': 'en',
            'model': 'Browser Extension',
            'security_patch_level': '2026-04-01'
        }
        url = f'https://{host}/push/v2/activation/{code_part}?{urllib.parse.urlencode(params)}'
        res = self._api.request('POST', url)
        if res.status_code == 200:
            response = res.json().get('response', {})
            self._db.duo_akey = response.get('akey', '')
            self._db.duo_pkey = response.get('pkey', '')
            self._db.duo_host = host

    def _get_grant_token(self):
        headers = {
            'X-Csrf-Token': self._xsrf
        }
        data = {
            'progress_token': self._progress_token
        }
        res = self._api.login('POST',
                              'authenticate',
                              data=data,
                              headers=headers)
        if res.status_code == 200:
            self._grant_token = res.json().get('grant_token')

    def get_grant_token(self, auth_url):
        """Get Grant Token from Duo Security via HOTP passcode or Duo Push"""
        self._auth_url = auth_url
        self._get_session_variables()
        if self._akey and self._authkey:
            self._post_browser_event({
                'context': {
                    'current_view': 'index',
                    'view_history': '',
                    'message': 'Browser event',
                    'platform_authenticator_status': 'unavailable',
                    'platform_id': 'unknown',
                    'req-trace-group': self._req_trace_group
                },
                'name': 'platform info',
                'level': 'info'
            })
            self._get_prompt_payload()
            self._post_browser_event({
                'context': {
                    'current_view': 'pre_authn_init',
                    'view_history': 'pre_authn_init',
                    'message': 'Browser event',
                    'card_name': 'PreAuthnInitializationCard',
                    'akey': self._akey,
                    'authn_result': {'status': 'unperformed'},
                    'ikey': self._ikey,
                    'platform_authenticator_status': 'unavailable',
                    'platform_id': 'unknown',
                    'ukey': self._ukey,
                    'auth_flow': 'mfa'
                },
                'name': 'card_visit',
                'level': 'info'
            })
            self._get_prompt_initialization()
            self._post_browser_event({
                'context': {
                    'current_view': 'device_health',
                    'view_history': 'pre_authn_init,device_health',
                    'message': 'Browser event',
                    'card_name': 'DeviceHealthCard',
                    'akey': self._akey,
                    'authn_result': {'status': 'unperformed'},
                    'ikey': self._ikey,
                    'platform_authenticator_status': 'unavailable',
                    'platform_id': 'unknown',
                    'ukey': self._ukey,
                    'auth_flow': 'mfa'
                },
                'name': 'card_visit',
                'level': 'info'
            })
            self._post_browser_event({
                'context': {
                    'current_view': 'pre_authn_eval',
                    'view_history': 'pre_authn_init,device_health,pre_authn_eval',
                    'message': 'Browser event',
                    'card_name': 'PreAuthnEvaluationCard',
                    'akey': self._akey,
                    'authn_result': {'status': 'unperformed'},
                    'ikey': self._ikey,
                    'platform_authenticator_status': 'unavailable',
                    'platform_id': 'unknown',
                    'ukey': self._ukey,
                    'auth_flow': 'mfa'
                },
                'name': 'card_visit',
                'level': 'info'
            })
            self._get_prompt_evaluation()
            if self._pkey:
                self._get_prompt_push_txid()
            if self._push_txid:
                self._post_browser_event({
                    'context': {
                        'current_view': 'duo_push',
                        'view_history': 'pre_authn_init,device_health,pre_authn_eval,duo_push',
                        'message': 'Browser event',
                        'card_name': 'DuoPushCard',
                        'active_auth_method': {'id': 'DUO_PUSH', 'authenticator_key': self._pkey},
                        'akey': self._akey,
                        'authn_result': {'status': 'unperformed'},
                        'available_auth_method_types': self._available_auth_method_types,
                        'can_opt_out_of_push': self._can_opt_out_of_push,
                        'ikey': self._ikey,
                        'platform_authenticator_status': 'unavailable',
                        'platform_id': 'unknown',
                        'ukey': self._ukey,
                        'auth_flow': 'mfa'
                    },
                    'name': 'card_visit',
                    'level': 'info'
                })
                self._get_prompt_push_status()
            if self._status == 'SUCCESS':
                self._get_prompt_remember_me()
                self._post_browser_event({
                    'context': {
                        'current_view': 'auth_success',
                        'view_history': 'pre_authn_init,device_health,pre_authn_eval,duo_push,auth_success',
                        'message': 'Browser event',
                        'card_name': 'SuccessCard',
                        'active_auth_method': {'id': 'DUO_PUSH', 'authenticator_key': self._pkey},
                        'akey': self._akey,
                        'authn_result': {'status': 'success', 'evaluation': self._authn_evaluation},
                        'available_auth_method_types': self._available_auth_method_types,
                        'can_opt_out_of_push': self._can_opt_out_of_push,
                        'ikey': self._ikey,
                        'platform_authenticator_status': 'unavailable',
                        'platform_id': 'unknown',
                        'ukey': self._ukey,
                        'auth_flow': 'mfa'
                    },
                    'name': 'card_visit',
                    'level': 'info'
                })
                self._get_prompt_finalize()
                return self._grant_token
        else:
            self._set_session_variables()
            self._set_session_variables()  # Yes, this needs to be called twice...
            self._get_txid()
            if self._txid:
                self._get_status()
            if self._status == 'SUCCESS':
                self._get_oidc_exit()
                if self._progress_token:
                    self._get_grant_token()
                return self._grant_token

    def _get_mfa_details(self):
        if self._state.otp_secret and not self._db.duo_akey:
            self._device = 'null'
            self._hotp = pyotp.HOTP(s=self._state.otp_secret).generate_otp(int(self._state.otp_count))
            self._factor = 'Passcode'
            return

        headers = {
            'Referer': f'{self._base_url}/frame/v4/auth/prompt?sid={self._sid}',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'X-Xsrftoken': self._xsrf
        }
        query = {
            'post_auth_action': 'OIDC_EXIT',
            'browser_features': json.dumps({
                 'touch_supported': 'false',
                 'platform_authenticator_status': 'unavailable',
                 'webauthn_supported': 'true'
             }, separators=(',', ':')),
            'sid': self._sid
        }
        res = self._api.request('GET', f'{self._base_url}/frame/v4/auth/prompt/data', headers=headers, query=query)
        if res.status_code == 200:
            device_key = ''
            for method in res.json().get('response', {}).get('auth_method_order', []):
                if method.get('factor', '') == 'Duo Push':
                    device_key = method.get('deviceKey', '')
                    break

            for phone in res.json().get('response', {}).get('phones', []):
                if phone.get('key', '') == device_key:
                    self._device = phone.get('index', '')
                    self._factor = 'Duo Push'

    def _get_oidc_exit(self):
        headers = {
            'Referer': f'{self._base_url}/frame/v4/auth/prompt?sid={self._sid}',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'X-Xsrftoken': self._xsrf
        }
        data = {
            'sid': self._sid,
            'txid': self._txid,
            'factor': self._factor,
            'device_key': self._device,
            '_xsrf': self._xsrf,
            'dampen_choice': 'false'
        }
        res = self._api.request('POST', f'{self._base_url}/frame/v4/oidc/exit', headers=headers, data=data)
        if res.status_code == 200:
            try:
                self._grant_token = re.search('grant_token=([^&]*)', res.url).group(1)
            except AttributeError:
                self._progress_token = re.search('token=([^&]*)', res.url).group(1)
                self._xsrf = self._utils.get_html_tag_value('csrf-token', res.text)

    def _get_prompt_evaluation(self):
        query = {
            'authkey': self._authkey,
            'browser_features': self._browser_features(),
            'local_trust_choice': 'undecided'
        }
        res = self._api.request('GET',
                                f'{self._base_url}/prompt/{self._akey}/pre_authn/evaluation',
                                query=query)
        if res.status_code == 200:
            response = res.json().get('response', {})
            self._can_opt_out_of_push = response.get('can_opt_out_of_push', False)
            factors = (response
                       .get('available_unified_auth_factors', {})
                       .get('factors', []))
            self._available_auth_method_types = ','.join(f.get('factor_type', '') for f in factors)
            for factor in factors:
                if factor.get('factor_type') == 'push':
                    self._pkey = factor.get('device_info', {}).get('pkey', '')
                    break

    def _get_prompt_finalize(self):
        res = self._api.request('GET',
                                f'{self._base_url}/prompt/{self._akey}/auth/finalize_auth',
                                query={'authkey': self._authkey})
        if res.status_code == 200:
            exit_url = res.json().get('response', {}).get('url', '')
            if exit_url:
                final = self._api.request('GET', exit_url)
                grant_match = re.search(r'grant_token=([^&]*)', final.url)
                if grant_match:
                    self._grant_token = grant_match.group(1)

    def _get_prompt_initialization(self):
        client_hints = base64.b64encode(json.dumps({
            'brands': [
                {'brand': 'Chromium', 'version': '131'},
                {'brand': 'Not_A Brand', 'version': '24'}
            ],
            'fullVersionList': [],
            'mobile': False,
            'platform': 'Linux',
            'platformVersion': '',
            'uaFullVersion': ''
        }).encode()).decode()
        query = {
            'authkey': self._authkey,
            'is_ipad': 'false',
            'client_hints': client_hints
        }
        self._api.request('GET',
                          f'{self._base_url}/prompt/{self._akey}/pre_authn/initialization',
                          query=query)

    def _get_prompt_payload(self):
        query = {
            'authkey': self._authkey,
            'browser_features': self._browser_features()
        }
        res = self._api.request('GET',
                                f'{self._base_url}/prompt/{self._akey}/auth/payload',
                                query=query)
        if res.status_code == 200:
            response = res.json().get('response', {})
            self._ikey = response.get('ikey', '')
            self._ukey = response.get('ukey', '')

    def _get_prompt_push_status(self):
        query = {
            'authkey': self._authkey,
            'push_txid': self._push_txid,
            'saw_good_news': 'false'
        }
        for i in range(10):
            res = self._api.request('GET',
                                    f'{self._base_url}/prompt/{self._akey}/auth/factors/push/status',
                                    query=query)
            if res.status_code == 200:
                result = res.json().get('response', {}).get('result', {})
                status_enum = res.json().get('response', {}).get('status_enum', -1)
                result_str = result.get('result', 'UNKNOWN') if isinstance(result, dict) else str(result)
                if result_str == 'SUCCESS':
                    authn_eval = (res.json().get('response', {})
                                  .get('result', {})
                                  .get('auth_result', {})
                                  .get('authn_evaluation', {}))
                    self._authn_evaluation = {
                        'is_allowed': authn_eval.get('is_allowed', True),
                        'auth_method_type': authn_eval.get('auth_method_type', 'push'),
                        'authenticator_key': authn_eval.get('authenticator_key', self._pkey),
                        'status_enum': authn_eval.get('status_enum', 5),
                        'request_browser_trust': authn_eval.get('request_browser_trust', False)
                    }
                    self._status = 'SUCCESS'
                    break
                elif status_enum == 15:
                    self.set_duo_push_approved()
                elif status_enum in [6, 7]:
                    break
            time.sleep(5)

    def _get_prompt_push_txid(self):
        data = {
            'authkey': self._authkey,
            'pkey': self._pkey
        }
        res = self._api.request('POST',
                                f'{self._base_url}/prompt/{self._akey}/auth/factors/push/auth',
                                data=data)
        if res.status_code == 200:
            self._push_txid = res.json().get('response', {}).get('push_txid', '')

    def _get_prompt_remember_me(self):
        headers = {
            'Accept': '*/*',
            'Origin': self._base_url,
            'Referer': f'{self._base_url}/prompt/{self._akey}?authkey={self._authkey}&req_trace_group={self._req_trace_group}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Duo-Req-Trace-Group': self._req_trace_group
        }
        self._api.request('POST',
                          f'{self._base_url}/prompt/{self._akey}/auth/remember_me',
                          headers=headers,
                          data={'authkey': self._authkey})

    def _get_push_transactions(self):
        now = email.utils.format_datetime(datetime.datetime.utcnow())
        path = '/push/v2/device/transactions'
        data = {
            'akey': self._db.duo_akey,
            'fips_status': '1',
            'hsm_status': 'true',
            'pkpush': 'rsa-sha512'
        }
        signature = self._generate_push_signature('GET', path, now, data)
        res = self._api.request('GET', f'https://{self._db.duo_host}{path}',
                                query=data,
                                headers={'Authorization': signature, 'x-duo-date': now,
                                         'host': self._db.duo_host})
        if res.status_code == 200:
            return res.json().get('response', {}).get('transactions', [])
        return []

    def _get_session_variables(self):
        self._referrer = f'https://login.{self._state.synack_domain}/'
        res = self._api.request('GET', self._auth_url, headers=self._build_headers())
        if res.status_code == 200:
            base_url_match = re.search('(https.*duo[^.]*.com)/', res.url)
            if not base_url_match:
                return
            self._base_url = base_url_match.group(1)
            self._referrer = res.url
            # New synack.com / duosecurity.com prompt-based flow
            prompt_match = re.search(r'/prompt/([^/?]+)\?authkey=([^&]+)', res.url)
            if prompt_match:
                self._akey = prompt_match.group(1)
                self._authkey = prompt_match.group(2)
                trace_match = re.search(r'req_trace_group=([^&]+)', res.url)
                if trace_match:
                    self._req_trace_group = trace_match.group(1)
                return
            # Old synack.us / duofederal.com frameless v4 flow
            sid_match = re.search('sid=([^&]*)', res.url)
            if not sid_match:
                return
            self._sid = sid_match.group(1)
            self._xsrf = self._utils.get_html_tag_value('_xsrf', res.text)

            client_hints = base64.b64encode(json.dumps({
                'brands': [
                    {'brand': 'Chromium', 'version': '131'},
                    {'brand': 'Not_A Brand', 'version': '24'}
                ],
                'fullVersionList': [],
                'mobile': False,
                'platform': 'Linux',
                'platformVersion': '',
                'uaFullVersion': ''
            }).encode()).decode()

            analysis_feature = self._utils.get_html_tag_value('has_session_trust_analysis_feature', res.text)

            self._session_vars = {
                'tx': self._utils.get_html_tag_value('tx', res.text),
                'parent': self._utils.get_html_tag_value('parent', res.text),
                '_xsrf': self._xsrf,
                'version': self._utils.get_html_tag_value('version', res.text),
                'akey': self._utils.get_html_tag_value('akey', res.text),
                'has_session_trust_analysis_feature': analysis_feature,
                'session_trust_extension_id': self._utils.get_html_tag_value('session_trust_extension_id', res.text),
                'java_version': self._utils.get_html_tag_value('java_version', res.text),
                'flash_version': self._utils.get_html_tag_value('flash_version', res.text),
                'screen_resolution_width': '3422',
                'screen_resolution_height': '1465',
                'extension_instance_key': '',
                'color_depth': '24',
                'has_touch_capability': 'false',
                'ch_ua_error': '',
                'client_hints': client_hints,
                'is_cef_browser': 'false',
                'is_ipad_os': 'false',
                'is_ie_compatibility_mode': '',
                'is_user_verifying_platform_authenticator_available': 'false',
                'user_verifying_platform_authenticator_available_error': '',
                'acting_ie_version': '',
                'react_support': 'false',
                'react_support_error_message': ''
            }

    def _get_status(self):
        headers = {
            'Referrer': f'{self._base_url}/frame/v4/auth/prompt?sid={self._sid}',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'X-Xsrftoken': self._xsrf
        }
        data = {
            'txid': self._txid,
            'sid': self._sid
        }
        for i in range(5):
            res = self._api.request('POST', f'{self._base_url}/frame/v4/status', headers=headers, data=data)
            if res.status_code == 200:
                status_enum = res.json().get('response', {}).get('status_enum', -1)
                message_enum = res.json().get('message_enum', -1)
                self._status = res.json().get('response', {}).get('result', 'UNKNOWN')
                if status_enum == 5 or self._status == 'SUCCESS':  # Valid Code
                    break
                elif status_enum == 6:  # Push Notification Declined (Normal)
                    break
                elif status_enum == 7:  # Push Notification Declined (Suspicious Login)
                    break
                elif status_enum == 11:  # Bad Code (or Future Code by 20+)
                    print("Bad OTP Code Sent")
                    print(res)
                    print(res.json())
                    break
                elif status_enum == 13:  # Awaiting Push Notification
                    if self._db.duo_akey:
                        self.set_duo_push_approved()
                elif status_enum == 15:  # Push Notification MFA Blocked
                    break
                elif status_enum == 44:  # Prior Code
                    self._db.otp_count += 5
                    break
                elif status_enum == 56:  # Push Notification Sent
                    self.set_duo_push_approved()
                elif message_enum == 57:  # Bad Request
                    print('Your Request was bad!')
                    break
                else:  # IDK
                    print('Something went wrong!')
                    print(res)
                    print(res.json())
                    break
            time.sleep(5)

    def _get_txid(self):
        """Sends Push Notification or Submits HOTP"""
        headers = {
            'Referrer': f'{self._base_url}/frame/v4/auth/prompt?sid={self._sid}',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'X-Xsrftoken': self._xsrf
        }

        self._get_mfa_details()

        if self._device and self._factor:
            data = {
                'device': self._device,
                'factor': self._factor,
                'postAuthDestination': 'OIDC_EXIT',
                'browser_features': json.dumps({
                     'touch_supported': 'false',
                     'platform_authenticator_status': 'unavailable',
                     'webauthn_supported': 'true'
                 }, separators=(',', ':')),
                'sid': self._sid
            }

            if self._state.otp_secret:
                data['passcode'] = self._hotp

            res = self._api.request('POST',
                                    f'{self._base_url}/frame/v4/prompt',
                                    headers=self._build_headers(headers),
                                    data=data)
            if res.status_code == 200:
                self._txid = res.json().get('response', {}).get('txid', '')
                if self._state.otp_secret:
                    self._db.otp_count += 1

    def _post_browser_event(self, body):
        headers = {
            'Accept': '*/*',
            'Origin': self._base_url,
            'Referer': f'{self._base_url}/prompt/{self._akey}?authkey={self._authkey}&req_trace_group={self._req_trace_group}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Duo-Req-Trace-Group': self._req_trace_group
        }
        self._api.request('POST',
                          f'{self._base_url}/prompt/{self._akey}/auth/browser_events',
                          headers=headers,
                          query={'authkey': self._authkey},
                          data=body)

    def set_duo_push_approved(self, attempts=10, approvals=1, sleep=5):
        """Approve pending Duo push transactions for the registered virtual device"""
        acted = []
        attempt = 0
        while attempts == 0 or attempt < attempts:
            for transaction in self._get_push_transactions():
                txid = transaction.get('urgid', '')
                if not txid:
                    continue
                now = email.utils.format_datetime(datetime.datetime.utcnow())
                path = f'/push/v2/device/transactions/{txid}'
                data = {
                    'akey': self._db.duo_akey,
                    'answer': 'approve',
                    'fips_status': '1',
                    'hsm_status': 'true',
                    'pkpush': 'rsa-sha512'
                }
                signature = self._generate_push_signature('POST', path, now, data)
                self._api.request('POST', f'https://{self._db.duo_host}{path}',
                                  data=data,
                                  headers={'Authorization': signature, 'x-duo-date': now,
                                           'host': self._db.duo_host, 'txId': txid,
                                           'Content-Type': 'application/x-www-form-urlencoded'})
                acted.append(transaction)
                if approvals != 0 and len(acted) >= approvals:
                    return acted
            attempt += 1
            if attempts == 0 or attempt < attempts:
                time.sleep(sleep)
        return acted

    def _set_session_variables(self):
        headers = {
            'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Linux"',
            'Referer': self._referrer,
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Dest': 'document',
            'Accept': ';'.join([
                'text/html,application/xhtml+xml,application/xml',
                'q=0.9,image/avif,image/webp,image/apng,*/*',
                'q=0.8,application/signed-exchange',
                'v=b3;q=0.7'
             ]),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        res = self._api.request('POST', self._referrer, headers=headers, data=self._session_vars)
        if res.status_code == 200:
            self._referrer = res.url
