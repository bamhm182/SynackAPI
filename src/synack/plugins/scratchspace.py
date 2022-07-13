"""plugins/scratchspace.py

This contains the Templates class
"""

import json

from .base import Plugin


class Scratchspace(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def build_filepath(self, filename, target=None, codename=None):
        if target:
            codename = target.codename

        if codename:
            f = self.db.scratchspace_dir
            f = f / codename
            f.mkdir(parents=True, exist_ok=True)
            f = f / filename
            return f'{f}.txt'

    def set_burp_file(self, content, target=None, codename=None):
        if target or codename:
            if type(content) == dict:
                content = json.dumps(content)
            dest_file = self.build_filepath('hosts', target=target, codename=codename)
            with open(dest_file, 'w') as fp:
                fp.write(content)
                return dest_file

    def set_hosts_file(self, content, target=None, codename=None):
        if target or codename:
            if type(content) == list:
                content = '\n'.join(content)
            dest_file = self.build_filepath('hosts', target=target, codename=codename)
            with open(dest_file, 'w') as fp:
                fp.write(content)
                return dest_file
