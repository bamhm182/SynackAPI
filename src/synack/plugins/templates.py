"""plugins/templates.py

This contains the Templates class
"""

import re
from pathlib import Path

from .base import Plugin


class Templates(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Alerts', 'Db', 'Targets']:
            setattr(self,
                    '_'+plugin.lower(),
                    self._registry.get(plugin)(self._state))

    def build_filepath(self, mission, generic_ok=False):
        f = self._state.template_dir
        f = f / self.build_safe_name(mission['taskType'])
        if mission.get('asset'):
            f = f / self.build_safe_name(mission['asset'])
        else:
            f = f / self.build_safe_name(mission['assetTypes'][0])
        f.mkdir(parents=True, exist_ok=True)
        generic = f / 'generic.txt'
        specific = f / (self.build_safe_name(mission['title']) + '.txt')
        if not specific.exists() and generic.exists() and generic_ok:
            return str(generic)
        return str(specific)

    def build_replace_variables(self, text, target=None, **kwargs):
        """Replaces known variables within text"""
        if target is None:
            target = self._db.find_targets(**kwargs)
            if target:
                target = target[0]

        if target:
            text = text.replace("{{ TARGET_CODENAME }}", str(target.codename))
        return text

    def build_safe_name(self, name):
        """Simplify a name to use for a file path"""
        name = self._alerts.sanitize(name)
        name = name.lower()
        name = re.sub('[^a-z0-9]', '_', name)
        return re.sub('_+', '_', name)

    def build_sections(self, path, include_extras=False):
        ret = dict()
        reg = r"\[\[\[(.+?)(?=\]\]\])\]\]\](.+?)(?=\[\[\[)"
        with open(path, 'r') as fp:
            text = fp.read()
            sections = re.findall(reg, text, flags=re.DOTALL)
            for s in sections:
                ret[s[0].strip()] = s[1].strip()
        if not include_extras:
            necessary_keys = [
                'structuredResponse',
                'introduction',
                'testing_methodology',
                'conclusion'
            ]
            ret = {k: v for k, v in ret.items() if k in necessary_keys}
        return ret

    def get_file(self, mission, include_extras=False):
        """Get a template file from disk and return its sections"""
        path = self.build_filepath(mission, generic_ok=True)
        if Path(path).exists():
            return self.build_sections(path, include_extras)

    def set_file(self, evidences, mission=dict(), clobber=False):
        """Save a template json to disk

        Arguments:
        template -- A template object from missions.get_evidences
        """
        path = self.build_filepath(evidences)
        if not Path(path).exists() or clobber:
            out_list = list()
            for k, v in evidences.items():
                out_list.append(f'\n[[[{k}]]]\n{v}\n')
                if k == 'intruduction':
                    out_list.append('THIS IS A DOWNLOADED TEMPLATE!')
                    out_list.append('ENSURE THERE IS NO SENSITIVE INFORMATION,')
                    out_list.append('THEN DELETE THIS WARNING!\n')
            out_list.append('[[[END]]]')
            with open(path, 'w') as fp:
                fp.write('\n'.join(out_list))
            return path
