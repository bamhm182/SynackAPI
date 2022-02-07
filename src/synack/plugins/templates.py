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

    def get_template(self, mission):
        f = self.db.template_dir
        f = f / self.do_convert_name(mission['taskType'])
        f = f / self.do_convert_name(mission['assetTypes'][0])
        f = f / self.do_convert_name(mission['title'])
        f = str(f) + '.txt'
        if Path(f).exists():
            ret = dict()
            reg = r"\[\[\[(.+?)(?=\]\]\])\]\]\](.+?)(?=\[\[\[)"
            with open(f, 'r') as fp:
                text = fp.read()
                sections = re.findall(reg, text, flags=re.DOTALL)
                for s in sections:
                    ret[s[0]] = s[1].lstrip().rstrip()
            return ret

    def do_save_template(self, template):
        """Save a template json to disk

        Arguments:
        template -- A template object from missions.get_evidences
        """
        f = self.db.template_dir
        f = f / self.do_convert_name(template['type'])
        f = f / self.do_convert_name(template['asset'])
        f.mkdir(parents=True, exist_ok=True)
        f = f / self.do_convert_name(template['title'])
        f = str(f) + '.txt'
        if template["version"] == "2" and not Path(f).exists():
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
            with open(f, 'w') as fp:
                fp.write(out)
            return f

    @staticmethod
    def do_convert_name(name):
        """Simplify a name to use for a file path"""
        name = name.lower()
        name = re.sub('[^a-z]', '_', name)
        return re.sub('_+', '_', name)
