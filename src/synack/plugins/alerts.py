"""plugins/alerts.py

Functions to handle sending alerts to various clients
"""

import email
import datetime
import json
import requests
import smtplib

from .base import Plugin


class Alerts(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def email(self, subject='Test Alert', message='This is a test'):
        message += f'\nTime: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        msg = email.message.EmailMessage()
        msg.set_content(message)
        msg['Subject'] = subject
        msg['From'] = self.db.smtp_email_from
        msg['To'] = self.db.smtp_email_to

        if self.db.smtp_starttls:
            server = smtplib.SMTP_SSL(self.db.smtp_server, self.db.smtp_port)
        else:
            server = smtplib.SMTP(self.db.smtp_server, self.db.smtp_port)

        server.login(self.db.smtp_username, self.db.smtp_password)
        server.send_message(msg)

    def slack(self, message='This is a test'):
        requests.post(self.db.slack_url,
                      data=json.dumps({'text': message}),
                      headers={'Content-Type': 'application/json'})
