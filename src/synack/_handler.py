"""handler.py

Defines the handler class and generally sets up the project.
"""

import importlib


class Handler:
    def __init__(self, config_dir='~/.config/synack/',
                 template_dir='~/Templates', debug=False, login=True):
        self.db = self.import_plugin("db")\
            .Db(self, config_dir, template_dir)
        self.api = self.import_plugin("api")\
            .Api(self)
        self.auth = self.import_plugin("auth")\
            .Auth(self)
        self.compat = self.import_plugin("compat")
        self.debug = self.import_plugin("debug")\
            .Debug(self, debug)
        self.missions = self.import_plugin("missions")\
            .Missions(self)
        self.notifications = self.import_plugin("notifications")\
            .Notifications(self)
        self.targets = self.import_plugin("targets")\
            .Targets(self)
        self.templates = self.import_plugin("templates")\
            .Templates(self)
        self.transactions = self.import_plugin("transactions")\
            .Transactions(self)

        if login and not self.auth.check_api_token():
            self.auth.get_api_token()

    @staticmethod
    def import_plugin(name):
        return importlib.import_module(f"synack.plugins.{name}")
