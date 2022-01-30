"""plugins/users.py

Functions dealing with users
"""

import json


class Users:
    def __init__(self, handler):
        self.handler = handler

    def get_profile(self, slug="me"):
        """Get a user's profile"""
        res = self.handler.api.request('GET', f'profiles/{slug}')
        if res.status_code == 200:
            return res.json()
