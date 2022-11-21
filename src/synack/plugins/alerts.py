"""plugins/alerts.py

Functions to handle sending alerts to various clients
"""

import email
import datetime
import json
import re
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

    def sanitize(self, message):
        message = re.sub(r'[-a-zA-Z0-9@:%._+~#=\]{1,256}\.[a-zA-Z0-9()]{1,6}\b' +
                         r'([-a-zA-Z0-9()@:%_\+.~#?&//=]*)', '[REDACTED]', message)
        message = re.sub(r'(?:https?:\\/\\/)?(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}' +
                         r'\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)', '[REDACTED]', message)
        message = re.sub(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.[0-9]{1,3}', '[REDACTED]', message)
        ipv6_regex = r''.join([
            r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|',
            r'([0-9a-fA-F]{1,4}:){1,7}:|',
            r'([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|',
            r'([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|',
            r'([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|',
            r'([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|',
            r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|',
            r'[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|',
            r':((:[0-9a-fA-F]{1,4}){1,7}|:)|',
            r'fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|',
            r'::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|',
            r'(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|',
            r'(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|',
            r'([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|',
            r'(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|',
            r'(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))',
        ])
        message = re.sub(ipv6_regex, '[REDACTED]', message)
        return message

    def slack(self, message='This is a test'):
        requests.post(self.db.slack_url,
                      data=json.dumps({'text': message}),
                      headers={'Content-Type': 'application/json'})
