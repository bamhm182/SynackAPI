"""plugins/scratchspace.py

This contains the Templates class
"""

import json

from .base import Plugin


class Scratchspace(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Db']:
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
            return f

    def set_assets_file(self, content, target=None, codename=None):
        if target or codename:
            if type(content) in [list, set]:
                content = '\n'.join(content)
            dest_file = self.build_filepath('assets.txt', target=target, codename=codename)
            with open(dest_file, 'w') as fp:
                fp.write(content)
                return dest_file

    def set_burp_file(self, content, target=None, codename=None):
        if target or codename:
            if type(content) == dict:
                content = json.dumps(content)
            dest_file = self.build_filepath('burp.txt', target=target, codename=codename)
            with open(dest_file, 'w') as fp:
                fp.write(content)
                return dest_file

    def set_download_attachments(self, attachments, target=None, codename=None, prompt_overwrite=True, overwrite=True):
        downloads = list()
        for attachment in attachments:
            overwrite_current = overwrite
            if target or codename:
                dest_file = self.build_filepath(attachment.get('filename'), target=target, codename=codename)
                if prompt_overwrite and dest_file.exists():
                    ans = input(f'{attachment.get("filename")} exists. Overwrite? [y/N]: ')
                    overwrite_current = ans.lower().startswith('y')
                if overwrite_current or not dest_file.exists():
                    res = self.api.request('GET', attachment.get('url'))
                    if res.status_code == 200:
                        with open(dest_file, 'wb') as fp:
                            fp.write(res.content)
                            downloads.append(dest_file)
        return downloads

    def set_hosts_file(self, content, target=None, codename=None):
        if target or codename:
            if type(content) in [list, set]:
                content = '\n'.join(content)
            dest_file = self.build_filepath('hosts.txt', target=target, codename=codename)
            with open(dest_file, 'w') as fp:
                fp.write(content)
                return dest_file
