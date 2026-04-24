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

        self._auth_url = None
        self._base_url = None
        self._device = None
        self._factor = None
        self._grant_token = None
        self._hotp = None
        self._progress_token = None
        self._referrer = None
        self._session_vars = None
        self._status = None
        self._sid = None
        self._txid = None
        self._xsrf = None

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
        """Get Grant Token from Duo Security via HOTP passcode"""
        self._auth_url = auth_url
        self._get_session_variables()
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
            sid_match = re.search('sid=([^&]*)', res.url)
            base_url_match = re.search('(https.*duo[^.]*.com)/', res.url)
            if not sid_match or not base_url_match:
                return
            self._sid = sid_match.group(1)
            self._referrer = res.url
            self._base_url = base_url_match.group(1)
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
