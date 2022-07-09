"""plugins/hydra.py

Functions dealing with hydra
"""

import json
import time

from .base import Plugin
from datetime import datetime


class Hydra(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Db']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def get_hydra(self, page=1, max_page=5, update_db=True, **kwargs):
        """Get Hydra results for target identified using kwargs (codename='x', slug='x', etc.)"""
        max_page = 1000 if max_page == 0 else max_page
        target = self.db.find_targets(**kwargs)[0]
        results = list()
        if target:
            query = {
                'page': page,
                'listing_uids': target.slug,
                'q': '+port_is_open:true'
            }
            time.sleep(page*0.01)
            res = self.api.request('GET',
                                   'hydra_search/search',
                                   query=query)
            if res.status_code == 200:
                curr_results = json.loads(res.content)
                results.extend(curr_results)
                if len(curr_results) == 10 and page < max_page:
                    results.extend(self.get_hydra(page=page+1, max_page=max_page, **kwargs))
            if update_db:
                self.db.add_ports(self.build_db_input(results))
            return results

    def build_db_input(self, results):
        """Format the Hydra output so that it can be ingested into the DB"""
        db_input = list()
        for result in results:
            ports = list()
            for port in result.get('ports').keys():
                for protocol in result['ports'][port].keys():
                    for hydra_src in result['ports'][port][protocol].keys():
                        h_src = result['ports'][port][protocol][hydra_src]
                        service = h_src.get('verified_service', {'parsed': 'unknown'})['parsed'] + \
                            ' - ' + \
                            h_src.get('product', {'parsed': 'unknown'})['parsed']
                        service = service.strip(' - ')
                        port_open = result['ports'][port][protocol][hydra_src]['open']['parsed']
                        epoch = datetime(1970, 1, 1)
                        try:
                            last_changed_dt = datetime.strptime(result['last_changed_dt'], "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            last_changed_dt = datetime.strptime(result['last_changed_dt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                        updated = int((last_changed_dt - epoch).total_seconds())

                        ports.append({
                            "port": port,
                            "protocol": protocol,
                            "service": service,
                            "open": port_open,
                            "updated": updated
                        })
            db_input.append({
                "ip": result["ip"],
                "target": result["listing_uid"],
                "source": "hydra",
                "ports": ports
            })
        return db_input
