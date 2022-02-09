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

    def get_template_path(self, mission):
        f = self.db.template_dir
        f = f / self.do_convert_name(mission['taskType'])
        if mission.get('asset'):
            f = f / self.do_convert_name(mission['asset'])
        else:
            f = f / self.do_convert_name(mission['assetTypes'][0])
        f.mkdir(parents=True, exist_ok=True)
        f = f / self.do_convert_name(mission['title'])
        return str(f) + '.txt'

    def get_sections_from_file(self, path):
        ret = dict()
        reg = r"\[\[\[(.+?)(?=\]\]\])\]\]\](.+?)(?=\[\[\[)"
        with open(path, 'r') as fp:
            text = fp.read()
            sections = re.findall(reg, text, flags=re.DOTALL)
            for s in sections:
                ret[s[0].strip()] = s[1].strip()
        return ret

    def get_template(self, mission):
        path = self.get_template_path(mission)
        if Path(path).exists():
            return self.get_sections_from_file(path)

    def do_save_template(self, template):
        """Save a template json to disk

        Arguments:
        template -- A template object from missions.get_evidences
        """
        path = self.get_template_path(template)
        if template["version"] == "2" and not Path(path).exists():
            out = "\n".join([
                "[[[structuredResponse]]]\n",
                template["structuredResponse"],
                "\n[[[introduction]]]\n",
                "THIS IS A DOWNLOADED TEMPLATE!",
                "ENSURE THERE IS NO SENSITIVE INFORMATION,",
                "THEN DELETE THIS WARNING!\n",
                template["introduction"],
                "\n[[[testing_methodology]]]\n",
                template["testing_methodology"],
                "\n[[[conclusion]]]\n",
                template["conclusion"],
                "\n[[[END]]]"
            ])
            with open(path, 'w') as fp:
                fp.write(out)
            return path

    @staticmethod
    def do_convert_name(name):
        """Simplify a name to use for a file path"""
        name = name.lower()
        name = re.sub('[^a-z]', '_', name)
        return re.sub('_+', '_', name)
