"""plugins/notifications.py

Functions used to handle notifications on the Synack Platform
"""

from .base import Plugin


class Notifications(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Db']:
            setattr(self,
                    '_'+plugin.lower(),
                    self._registry.get(plugin)(self._state))

    def get(self):
        """Get a list of recent notifications"""
        res = self._api.notifications('GET',
                                      'notifications?meta=1')
        if res.status_code == 200:
            return res.json()

    def get_unread_count(self):
        """Get the number of unread notifications"""
        query = {
            "authorization_token": self._state.notifications_token
        }
        res = self._api.notifications('GET',
                                      'notifications/unread_count',
                                      query=query)
        if res.status_code == 200:
            return res.json()

    def set_read(self):
        """Set all notifications to read"""
        query = {
            "authorization_token": self._state.notifications_token
        }
        res = self._api.notifications('GET',
                                      'read_all',
                                      query=query)
        if res.status_code == 200:
            return res.json()
