"""plugins/debug.py

Defines the methods to increase verbosity and aid in debugging
"""

from datetime import datetime

from .base import Plugin


class Debug(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def log(self, title, message):
        if self.db.debug:
            t = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
            print(f'{t} -- {title.upper()}\n\t{message}')
