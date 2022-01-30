"""plugins/auth.py

Functions related to handling and checking authentication.
"""

import pyotp
import re


class Auth:
    def __init__(self, handler):
        self.handler = handler

    def gen_otp(self):
        """Generate and return a TOTP code."""
        secret = self.handler.db.otp_secret
        totp = pyotp.TOTP(secret)
        totp.digits = 7
        totp.interval = 10
        totp.issuer = 'synack'
        return totp.now()

    def check_api_token(self):
        """Check to see if the api token exists and is valid."""
        user = self.handler.users.get_profile()
        if user:
            self.handler.api.session.headers.update({
                'user_id': user.get('user_id')
            })
        return True if user else False

    def get_login_progress_token(self, csrf):
        """Get progress token from email and password login"""
        headers = {
            'X-Csrf-Token': csrf
        }
        data = {
            'email': self.handler.db.email,
            'password': self.handler.db.password
        }
        res = self.handler.api.login('POST',
                                     'authenticate',
                                     headers=headers,
                                     data=data)
        if res.status_code == 200:
            return res.json().get("progress_token")

    def get_login_grant_token(self, csrf, progress_token):
        """Get grant token from authy totp verification"""
        headers = {
            'X-Csrf-Token': csrf
        }
        data = {
            "authy_token": self.gen_otp(),
            "progress_token": progress_token
        }
        res = self.handler.api.login('POST',
                                     'authenticate',
                                     headers=headers,
                                     data=data)
        if res.status_code == 200:
            return res.json().get("grant_token")

    def get_api_token(self):
        """Log in to get a new API token."""
        csrf = self.get_login_csrf()
        progress_token = None
        grant_token = None
        if csrf:
            progress_token = self.get_login_progress_token(csrf)
        if progress_token:
            grant_token = self.get_login_grant_token(csrf, progress_token)
        if grant_token:
            url = 'https://platform.synack.com/'
            headers = {
                'X-Requested-With': 'XMLHttpRequest'
            }
            query = {
                "grant_token": grant_token
            }
            res = self.handler.api.request('GET',
                                           url + 'token',
                                           headers=headers,
                                           query=query)
            if res.status_code == 200:
                j = res.json()
                self.handler.db.api_token = j.get('access_token')
                return j.get('access_token')

    def get_notifications_token(self):
        """Request a new Notification Token"""
        res = self.handler.api.request('GET', 'users/notifications_token')
        if res.status_code == 200:
            j = res.json()
            self.handler.db.notifications_token = j['token']
            return j['token']

    def get_login_csrf(self):
        """Get the CSRF Token from the login page"""
        res = self.handler.api.request('GET', 'https://login.synack.com')
        m = re.search('<meta name="csrf-token" content="([^"]*)"',
                      res.text)
        return m.group(1)

    def write_login_script(self):
        script = '''
        (function() {
          setTimeout(()=>{
            const loc = window.location;
            if (loc.href.startsWith("https://login.synack.com/")) {
              loc.replace("https://platform.synack.com");
            }
          },5000);
          sessionStorage.setItem("shared-session-com.synack.accessToken",
                                 "''' + self.handler.db.api_token + '''");
        })();
        '''
        with open(self.handler.db.config_dir / 'login.js', 'w') as fp:
            fp.write(script)

        return script
