"""plugins/duo.py

Functions related to handling Duo Security Multi-Factor Authentication.
"""

from .base import Plugin

import base64
import json
import pyotp
import re
import requests
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


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
        self._pubkey = None

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

    def get_grant_token(self, auth_url):
        """Get Grant Token from Duo Security"""
        self._auth_url = auth_url
        self._get_session_variables()
        self._set_session_variables()
        self._set_session_variables()  # Yes, this needs to be called twice...
        self._get_txid()
        if self._txid:
            # Priority 1: OTP (if configured)
            if self._state.otp_secret:
                # OTP passcode already sent in _get_txid(), just poll for status
                self._get_status()
            # Priority 2: Auto-approval (if configured) - HARD FAIL if broken
            elif self.is_configured():
                if not self.load_rsa_key():
                    raise RuntimeError(
                        "Duo Push auto-approval is enabled but RSA key failed to load"
                    )
                print("Auto-approving Duo push notification...")
                if self._state.debug:
                    print(f"Using device: {self._device}")
                    print(f"Configured duo_device: {self._state.duo_device}")
                    if self._device != self._state.duo_device:
                        print(f"WARNING: Push sent to {self._device} but credentials are for {self._state.duo_device}")
                # Wait 2 seconds before polling to give Duo time to register the push
                time.sleep(2)
                if not self.approve_pending_push(timeout=25):
                    raise RuntimeError(
                        "Duo Push auto-approval failed - check credentials or "
                        "disable auto-approval. Ensure duo_device matches the device "
                        "with extracted credentials."
                    )
                self._get_status()
            # Priority 3: Manual push (fallback)
            else:
                print("Waiting for manual Duo push approval on your device...")
                self._get_status()
        if self._status == 'SUCCESS':
            self._get_oidc_exit()
            if self._progress_token:
                self._get_grant_token()
            return self._grant_token

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

    def _get_mfa_details(self):
        if self._state.otp_secret:
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
            response_json = res.json()
            response_data = response_json.get('response', {})
            phones = response_data.get('phones', [])

            # If auto-approval credentials are configured, find the matching device
            if self.is_configured():
                # Match device by pkey
                pkey = self._state.duo_push_pkey
                for phone in phones:
                    if phone.get('key', '') == pkey:
                        self._device = phone.get('index', '')
                        self._factor = 'Duo Push'
                        # Update stored device if it doesn't match
                        if self._state.duo_device != self._device:
                            print(f"Auto-correcting duo_device from {self._state.duo_device} to {self._device}")
                            self._db.duo_device = self._device
                        return
                # If no match found, credentials are for wrong account
                print(f"WARNING: duo_push_pkey {pkey} not found in available devices")
                print("Falling back to manual device selection")

            # Check if we have a stored device preference
            if self._state.duo_device:
                # Use the stored device
                for phone in phones:
                    if phone.get('index', '') == self._state.duo_device:
                        self._device = phone.get('index', '')
                        self._factor = 'Duo Push'
                        return
                # If stored device not found, fall through to prompt

            # Prompt user to select a device
            if phones:
                print("\nAvailable Duo devices:")
                for i, phone in enumerate(phones, 1):
                    print(f"{i}. {phone.get('name', 'Unknown')} ({phone.get('index', '')})")

                while True:
                    try:
                        choice = input("\nSelect device number (or press Enter for first device): ").strip()
                        if not choice:
                            selected_phone = phones[0]
                            break
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(phones):
                            selected_phone = phones[choice_num - 1]
                            break
                        print(f"Please enter a number between 1 and {len(phones)}")
                    except ValueError:
                        print("Please enter a valid number")

                self._device = selected_phone.get('index', '')
                self._factor = 'Duo Push'
                self._db.duo_device = self._device
                return

        if not self._device or not self._factor:
            raise ValueError(
                f'Failed to determine MFA device/factor from Duo API. '
                f'HTTP {res.status_code}, device={self._device}, factor={self._factor}'
            )

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

    def _get_session_variables(self):
        self._referrer = f'https://login.{self._state.synack_domain}/'
        res = self._api.request('GET', self._auth_url, headers=self._build_headers())
        if res.status_code == 200:
            self._sid = re.search('sid=([^&]*)', res.url).group(1)
            self._referrer = res.url
            self._base_url = re.search('(https.*duo[^.]*.com)/', res.url).group(1)
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
        # Increase polling attempts from 5 to 12 (1 minute total with 5s intervals)
        for i in range(12):
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
                    pass
                elif status_enum == 15:  # Push sent, waiting for approval
                    # Continue polling for both auto-approval and manual approval
                    pass
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

    # Duo Push Auto-Approval Methods

    def is_configured(self):
        """Check if Duo push auto-approval credentials are configured"""
        return (
            self._state.duo_push_akey and
            self._state.duo_push_pkey and
            self._state.duo_push_host
        )

    def load_rsa_key(self):
        """Load RSA key from configured path"""
        if not self.is_configured():
            return False

        key_path = Path(self._state.duo_push_rsa_key_path).expanduser()
        if not key_path.exists():
            print(f"Duo RSA key not found: {key_path}")
            return False

        try:
            with open(key_path, 'rb') as f:
                self._pubkey = RSA.import_key(f.read())
            return True
        except Exception as e:
            print(f"Failed to load Duo RSA key: {e}")
            return False

    def approve_pending_push(self, timeout=30):
        """Wait for and approve a single Duo push notification"""
        if not self.is_configured():
            return False

        if not self._pubkey and not self.load_rsa_key():
            print("Cannot approve push: RSA key not available")
            return False

        print("Polling for Duo push notification...")
        start_time = time.monotonic()
        poll_interval = 2  # Poll every 2 seconds

        while time.monotonic() - start_time < timeout:
            try:
                # Poll for transactions
                transactions = self._get_transactions()
                if self._state.debug:
                    print(f"Transactions response: {transactions}")
                response_data = transactions.get('response', {})
                pending = response_data.get('transactions', [])
                current_time = response_data.get('current_time', 0)

                if self._state.debug:
                    print(f"Found {len(pending)} pending transactions")

                if pending:
                    for tx in pending:
                        tx_id = tx.get('urgid')
                        expiration = tx.get('expiration', 0)

                        if self._state.debug:
                            print(f"Transaction: {tx}")

                        # Skip expired transactions
                        if expiration and current_time and expiration <= current_time:
                            if self._state.debug:
                                print(f"Skipping expired transaction {tx_id}")
                            continue

                        if tx_id:
                            tx_summary = tx.get('summary', 'N/A')
                            print(f"Approving Duo push {tx_id[:12]}... ({tx_summary})")
                            response = self._reply_transaction(tx_id, 'approve')
                            if response.get('stat') == 'OK':
                                print("Duo push approved successfully")
                                return True
                            else:
                                print(f"Push approval returned: {response}")

                time.sleep(poll_interval)

            except Exception as e:
                print(f"Error during Duo push approval: {e}")
                return False

        return False

    def _generate_signature(self, method, path, time_str, data):
        """Generate RSA signature for Duo API request"""
        encoded_data = urlencode(sorted(data.items())) if data else ""
        message_parts = [
            time_str,
            method.upper(),
            self._state.duo_push_host.lower(),
            path,
            encoded_data,
        ]
        message = "\n".join(message_parts).encode('ascii')
        h = SHA512.new(message)
        signature = pkcs1_15.new(self._pubkey).sign(h)
        auth_string = f"{self._state.duo_push_pkey}:{base64.b64encode(signature).decode('ascii')}"
        return "Basic " + base64.b64encode(auth_string.encode('ascii')).decode('ascii')

    def _make_request(self, method, path, data):
        """Make authenticated request to Duo device API"""
        dt = datetime.now(UTC)
        # Format as RFC 2822 date for HTTP header (e.g., "Mon, 04 Nov 2025 12:34:56 GMT")
        time_str = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        signature = self._generate_signature(method, path, time_str, data)

        url = f"https://{self._state.duo_push_host}{path}"
        headers = {
            'Authorization': signature,
            'x-duo-date': time_str,
            'Host': self._state.duo_push_host,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        try:
            if method.upper() == 'GET':
                r = requests.get(url, params=data, headers=headers, timeout=10)
            else:
                r = requests.post(url, data=data, headers=headers, timeout=10)

            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Duo API request failed: {e}")
            raise

    def _get_transactions(self):
        """Get pending Duo push transactions"""
        path = "/push/v2/device/transactions"
        params = {
            'akey': self._state.duo_push_akey,
            'fips_status': '1',
            'hsm_status': 'true',
            'pkpush': 'rsa-sha512',
        }
        return self._make_request('GET', path, params)

    def _reply_transaction(self, transaction_id, answer):
        """Reply to a Duo push transaction (approve/deny)"""
        path = f"/push/v2/device/transactions/{transaction_id}"
        data = {
            'akey': self._state.duo_push_akey,
            'answer': answer,
            'fips_status': '1',
            'hsm_status': 'true',
            'pkpush': 'rsa-sha512',
        }
        return self._make_request('POST', path, data)
