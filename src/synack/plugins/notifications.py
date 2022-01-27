"""plugins/notifications.py

Functions used to handle notifications on the Synack Platform
"""


class Notifications:
    def __init__(self, handler):
        self.handler = handler

    def get_notifications(self):
        """Get a list of recent notifications"""
        res = self.handler.api.notifications('GET',
                                             'notifications?meta=1')
        if res.status_code == 200:
            return res.json()

    def get_unread_count(self):
        """Get the number of unread notifications"""
        token = self.handler.db.notifications_token
        query = {
            "authorization_token": token
        }
        res = self.handler.api.notifications('GET',
                                             'notifications/unread_count',
                                             query=query)
        if res.status_code == 200:
            return res.json()
