"""plugins/users.py

Functions dealing with users
"""

from .base import Plugin

class Users(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def get_profile(self, user_id="me"):
        """Get a user's profile"""
        res = self.api.request('GET', f'profiles/{user_id}')
        if res.status_code == 200:
            return res.json()
