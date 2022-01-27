"""plugins/db.py

Manipulates/Reads the database and provides it to other plugins
"""

from pathlib import Path
import yaml


class Db:
    def __init__(self, handler, config_dir, template_dir):
        self.config_dir = Path(config_dir).expanduser()
        self.config_file = self.config_dir / 'config'

        self._api_token = None
        self._assessments = None
        self._known_targets = None
        self._notifications_token = None

        self.email = None
        self.otp_secret = None
        self.password = None
        self.proxies = None
        self.template_dir = None
        self.use_proxies = None

        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.read()
        self.update()

    @property
    def api_token(self):
        return self._api_token

    @api_token.setter
    def api_token(self, api_token):
        self._api_token = api_token
        self.update()

    @property
    def assessments(self):
        return self._assessments

    @assessments.setter
    def assessments(self, assessments):
        self._assessments = assessments
        self.update()

    @property
    def known_targets(self):
        return self._known_targets

    @known_targets.setter
    def known_targets(self, known_targets):
        self._known_targets = known_targets
        self.update()

    @property
    def notifications_token(self):
        return self._notifications_token

    @notifications_token.setter
    def notifications_token(self, notifications_token):
        self._notifications_token = notifications_token
        self.update()

    def read(self):
        config = dict()
        if self.config_file.is_file():
            with open(self.config_file, 'r') as fp:
                y = yaml.safe_load(fp)
                if type(y) == dict:
                    config = y

        self.load(config)

    def load(self, config):
        if config.get('email'):
            self.email = config['email']
        else:
            self.email = input('Synack Email: ')

        if config.get('password'):
            self.password = config['password']
        else:
            self.password = input('Synack Password: ')

        if config.get('otp_secret'):
            self.otp_secret = config['otp_secret']
        else:
            self.otp_secret = input('Synack OTP Secret: ')

        self._api_token = config.get('api_token', "")
        self.assessments = config.get('assessments', [])
        self.known_targets = config.get('known_targets', [])
        self.notifications_token = config.get('notifications_token', "")
        self.proxies = config.get('proxies', {
            'http': 'http://127.0.0.1:8080',
            'https': 'http://127.0.0.1:8080'
        })
        td = Path(config.get('template_dir', '~/Templates')).expanduser()
        self.template_dir = td
        self.tempalte_dir = self.template_dir.expanduser()
        self.use_proxies = config.get('use_proxies', False)

    def update(self):
        config = {
            "api_token": self._api_token,
            "assessments": self._assessments,
            "email": self.email,
            "known_targets": self._known_targets,
            "notifications_token": self._notifications_token,
            "otp_secret": self.otp_secret,
            "password": self.password,
            "proxies": self.proxies,
            "template_dir": str(self.template_dir),
            "use_proxies": self.use_proxies,
        }
        with open(self.config_file, 'w') as fp:
            fp.write(yaml.safe_dump(config))
