"""plugins/auth.py

Functions related to handling and checking authentication.
"""

import re
import time

from .base import Plugin


class Auth(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Db', 'Debug', 'Duo', 'Users']:
            setattr(self,
                    '_'+plugin.lower(),
                    self._registry.get(plugin)(self._state))

    def get_api_token(self, attempts=3):
        """Log in to get a new API token.

        Arguments:
        attempts -- how many times to try when login is blocked by an existing
                    session elsewhere. Synack forbids simultaneous sessions and
                    returns HTTP 400 for the authenticate call, but logging in
                    again terminates the other session, so a retry succeeds.
        """
        if self._users.get_profile():
            return self._state.api_token
        csrf = self.get_login_csrf()
        duo_auth_url = None
        grant_token = None
        if csrf:
            auth_response = self.get_authentication_response(csrf) or {}
            duo_auth_url = auth_response.get('duo_auth_url', '')
            if self._is_session_conflict(auth_response) and attempts > 1:
                self._debug.log('Existing Synack session elsewhere',
                                'Logging in here terminates it; '
                                f'retrying ({attempts - 1} left).')
                time.sleep(2)
                return self.get_api_token(attempts - 1)
        if duo_auth_url:
            has_push = self._db.duo_akey and self._db.duo_pkey and self._db.duo_host
            has_hotp = self._db.otp_secret and self._db.otp_count is not None
            if not has_push and not has_hotp:
                self._duo.configure_mfa()
                has_push = self._db.duo_akey and self._db.duo_pkey and self._db.duo_host
                has_hotp = self._db.otp_secret and self._db.otp_count is not None
            if has_push or has_hotp:
                grant_token = self._duo.get_grant_token(duo_auth_url)
        if grant_token:
            url = f'https://platform.{self._state.synack_domain}/'
            headers = {
                'X-Requested-With': 'XMLHttpRequest'
            }
            query = {
                "grant_token": grant_token
            }
            res = self._api.request('GET',
                                    url + 'token',
                                    headers=headers,
                                    query=query)
            if res.status_code == 200:
                j = res.json()
                self._db.api_token = j.get('access_token')
                self.set_login_script()
                return j.get('access_token')

    def get_authentication_response(self, csrf):
        """Get duo_auth_url from email and password login"""
        headers = {
            'X-CSRF-Token': csrf
        }
        data = {
            'email': self._state.email,
            'password': self._state.password
        }
        res = self._api.login('POST',
                              'authenticate',
                              headers=headers,
                              data=data)
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 400:
            try:
                j = res.json()
            except ValueError:
                j = {}
            if self._is_session_conflict(j):
                # An active session exists elsewhere. Synack returns 400 here,
                # but the credentials are fine -- logging in again terminates
                # the other session. Return the body so get_api_token can retry
                # WITHOUT clearing stored credentials.
                return j
            ans = input('Invalid email or password. Clear credentials? [y/N] ')
            if ans.lower().startswith('y'):
                self._db.email = ''
                self._db.password = ''
            raise ValueError('Invalid email or password.')
        elif res.status_code == 423:
            raise ValueError('Account locked. Too many failed login attempts.')

    @staticmethod
    def _is_session_conflict(response):
        """True if authenticate failed only because a session exists elsewhere.

        Synack forbids simultaneous sessions and returns HTTP 400 with a body
        like:
            {"success": false, "error": "Simultaneous Non Launchpoint and
             LaunchPoint+ sessions are not permitted. Logging in here will
             terminate your existing session ..."}
        This is distinct from bad credentials and is safe to retry.
        """
        if not isinstance(response, dict):
            return False
        error = str(response.get('error', '')).lower()
        return response.get('success') is False and (
            'session' in error or 'simultaneous' in error)

    def get_login_csrf(self):
        """Get the CSRF Token from the login page"""
        res = self._api.request('GET', f'https://login.{self._state.synack_domain}')
        m = re.search('<meta name="csrf-token" content="([^"]*)"',
                      res.text)
        return m.group(1)

    def get_notifications_token(self):
        """Request a new Notifications Token"""
        res = self._api.request('GET', 'users/notifications_token')
        if res.status_code == 200:
            j = res.json()
            self._db.notifications_token = j['token']
            return j['token']

    def set_api_token_invalid(self):
        res = self._api.request('POST', 'logout')
        if res.status_code == 200:
            self._db.api_token = ''
            return True
        return False

    def set_login_script(self):
        script = "(function() {sessionStorage.setItem('shared-session-com.synack.accessToken'" +\
            ",'" +\
            self._state.api_token +\
            "');})();" +\
            "let forceLogin = () => {" +\
            "const loc = window.location;" +\
            "if(loc.href.startsWith('https://login." + self._state.synack_domain + "/')) {" +\
            "loc.replace('https://platform." + self._state.synack_domain + "');" +\
            "}};" +\
            "(function() {" +\
            "setTimeout(forceLogin,60000);" +\
            "let btn = document.createElement('button');" +\
            "btn.addEventListener('click',forceLogin);" +\
            "btn.style = 'margin-top: 20px;';" +\
            "btn.innerText = 'SynackAPI Log In';" +\
            "btn.classList.add('btn');" +\
            "btn.classList.add('btn-blue');" +\
            "document.getElementsByClassName('onboarding-form')[0]" +\
            ".appendChild(btn)}" +\
            ")();"
        with open(self._state.config_dir / 'login.js', 'w') as fp:
            fp.write(script)

        return script
