"""plugins/alerts.py

Functions to handle sending alerts to various clients
"""

import email
import datetime
import json
import re
import requests
import smtplib
import warnings

from .base import Plugin


class Alerts(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    '_'+plugin.lower(),
                    self._registry.get(plugin)(self._state))

    def email(self, subject='Test Alert', message='This is a test'):
        message += f'\nTime: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        msg = email.message.EmailMessage()
        msg.set_content(message)
        msg['Subject'] = subject
        msg['From'] = self._state.smtp_email_from
        msg['To'] = self._state.smtp_email_to

        if self._state.smtp_starttls:
            server = smtplib.SMTP_SSL(self._state.smtp_server, self._state.smtp_port)
        else:
            server = smtplib.SMTP(self._state.smtp_server, self._state.smtp_port)

        server.login(self._state.smtp_username, self._state.smtp_password)
        server.send_message(msg)

    def sanitize(self, message):
        placeholders = dict()

        url_allowlist = [
            'https://csrc.nist.gov',
            'https://github.com/synack',
            'https://support.synack.com',
        ]

        for url in url_allowlist:
            if url in message:
                placeholder = f'__ALLOWLIST_URL_{len(placeholders)}__'
                full_url = re.search(rf'{re.escape(url)}\S*', message)
                if full_url:
                    full_url = full_url.group()
                    placeholders[placeholder] = full_url
                    message = message.replace(full_url, placeholder)

        message = re.sub(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.[0-9]{1,3}', '[IPv4]', message)
        message = re.sub(r'(?:h[tx]{1,2}ps?:\/\/)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{2,6}' +
                         r'\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\\/=]*)', '[URL]', message)
        message = re.sub(r'(?:h[xt]{1,2}ps?:\/\/)?(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}' +
                         r'\\.[a-zA-Z0-9()]{2,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)', '[URL]', message)
        message = re.sub(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{2,6}\b' +
                         r'(?:[-a-zA-Z0-9()@:%_\+.~#?&\\/=]*)', '[URL]', message)
        message = re.sub(r'(?:^|(?<=\s))(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|' +
                         r'([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|' +
                         r'([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}' +
                         r'(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|' +
                         r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:' +
                         r'((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:' +
                         r'(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}' +
                         r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}' +
                         r'(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:' +
                         r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}' +
                         r'(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(?=\s|$)', '[IPv6]', message)

        for placeholder, original in placeholders.items():
            message = message.replace(placeholder, original)

        return message

    def slack(self, message='This is a test', channel=None):
        if channel is None:
            channel = self._state.slack_channel
        warnings.filterwarnings("ignore")
        requests.post('https://slack.com/api/chat.postMessage',
                      data=json.dumps({
                          'text': message,
                          'channel': channel,
                      }),
                      headers={
                          'Authorization': f'Bearer {self._state.slack_app_token}',
                          'Content-Type': 'application/json'
                      },
                      verify=False)
