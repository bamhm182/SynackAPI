"""plugins/templates.py

This contains the Templates class
"""

import re
from pathlib import Path

from .base import Plugin


class Templates(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def build_filepath(self, mission):
        f = self.db.template_dir
        f = f / self.build_safe_name(mission['taskType'])
        if mission.get('asset'):
            f = f / self.build_safe_name(mission['asset'])
        else:
            f = f / self.build_safe_name(mission['assetTypes'][0])
        f.mkdir(parents=True, exist_ok=True)
        f = f / self.build_safe_name(mission['title'])
        return str(f) + '.txt'

    @staticmethod
    def build_safe_name(name):
        """Simplify a name to use for a file path"""
        name = name.lower()
        name = re.sub('[^a-z0-9]', '_', name)
        return re.sub('_+', '_', name)

    def build_sections(self, path):
        ret = dict()
        reg = r"\[\[\[(.+?)(?=\]\]\])\]\]\](.+?)(?=\[\[\[)"
        with open(path, 'r') as fp:
            text = fp.read()
            sections = re.findall(reg, text, flags=re.DOTALL)
            for s in sections:
                ret[s[0].strip()] = s[1].strip()
        return ret

    def get_file(self, mission):
        """Get a template file from disk and return its sections"""
        path = self.build_filepath(mission)
        if Path(path).exists():
            return self.build_sections(path)

    def set_file(self, evidences):
        """Save a template json to disk

        Arguments:
        template -- A template object from missions.get_evidences
        """
        path = self.build_filepath(evidences)
        if evidences["version"] == "2" and not Path(path).exists():
            out = "\n".join([
                "[[[structuredResponse]]]\n",
                evidences["structuredResponse"],
                "\n[[[introduction]]]\n",
                "THIS IS A DOWNLOADED TEMPLATE!",
                "ENSURE THERE IS NO SENSITIVE INFORMATION,",
                "THEN DELETE THIS WARNING!\n",
                evidences["introduction"],
                "\n[[[testing_methodology]]]\n",
                evidences["testing_methodology"],
                "\n[[[conclusion]]]\n",
                evidences["conclusion"],
                "\n[[[END]]]"
            ])
            with open(path, 'w') as fp:
                fp.write(out)
            return path
