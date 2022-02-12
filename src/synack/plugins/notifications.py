"""plugins/notifications.py

Functions used to handle notifications on the Synack Platform
"""

from .base import Plugin


class Notifications(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def get(self):
        """Get a list of recent notifications"""
        res = self.api.notifications('GET',
                                     'notifications?meta=1')
        if res.status_code == 200:
            return res.json()

    def get_unread_count(self):
        """Get the number of unread notifications"""
        token = self.db.notifications_token
        query = {
            "authorization_token": token
        }
        res = self.api.notifications('GET',
                                     'notifications/unread_count',
                                     query=query)
        if res.status_code == 200:
            return res.json()
