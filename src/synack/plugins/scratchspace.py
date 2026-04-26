"""plugins/scratchspace.py

This contains the Templates class
"""

import json

from .base import Plugin


class Scratchspace(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Auth', 'Db']:
            setattr(self,
                    '_'+plugin.lower(),
                    self._registry.get(plugin)(self._state))

    def build_filepath(self, filename, target=None, codename=None):
        if target:
            codename = target.codename

        if codename:
            f = self._state.scratchspace_dir
            f = f / codename
            f.mkdir(parents=True, exist_ok=True)
            f = f / filename
            return f

    def set_assets_file(self, content, target=None, codename=None):
        return self.set_file(content=content, filename='assets.txt', target=target, codename=codename)

    def set_burp_file(self, content, target=None, codename=None):
        return self.set_file(content=content, filename='burp.txt', target=target, codename=codename)

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
                    res = self._api.request('GET', attachment.get('url'))
                    if res.status_code == 200:
                        with open(dest_file, 'wb') as fp:
                            fp.write(res.content)
                            downloads.append(dest_file)
                    elif res.status_code == 403 and self._state.login:
                        self._auth.get_api_token()
        return downloads

    def set_file(self, content, filename, target=None, codename=None):
        if target or codename:
            if type(content) in [list, set]:
                content = '\n'.join(content)
            elif type(content) in [dict]:
                content = json.dumps(content)
            dest_file = self.build_filepath(filename, target=target, codename=codename)
            with open(dest_file, 'w') as fp:
                fp.write(content)
                return dest_file

    def set_hosts_file(self, content, target=None, codename=None):
        return self.set_file(content=content, filename='hosts.txt', target=target, codename=codename)
