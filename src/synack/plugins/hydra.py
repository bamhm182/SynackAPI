"""plugins/hydra.py

Functions dealing with hydra
"""

# import json

from .base import Plugin
# from .db import Db


class Hydra(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def get_hydra(self, **kwargs):
        target = self.db.find_targets(**kwargs)[0]
        if target:
            query = {
                'page': '1',
                'listing_uids': target.slug,
                'q': '+port_is_open:true'
            }
            res = self.api.request('GET',
                                   'hydra_search/search',
                                   query=query)
            print(res)
            print(res.content)
            if res.status_code == 200:
                return res.content
