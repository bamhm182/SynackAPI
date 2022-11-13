"""plugins/targets.py

Functions related to handling and checking targets
"""

import ipaddress

from urllib.parse import urlparse
from .base import Plugin


class Targets(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Db', 'Scratchspace']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

    def build_codename_from_slug(self, slug):
        """Return a codename for a target given its slug

        Arguments:
        slug -- Slug of desired target
        """
        codename = 'NONE'
        targets = self.db.find_targets(slug=slug)
        if not targets:
            self.get_registered_summary()
            targets = self.db.find_targets(slug=slug)
        if targets:
            codename = targets[0].codename
        return codename

    def build_scope_host_db(self, slug, scope):
        """Return a Host Scope that can be ingested into the Database"""
        ret = list()
        for asset in scope:
            for ip in [str(ip) for ip in ipaddress.ip_network(asset)]:
                ret.append({
                    'target': slug,
                    'ip': ip
                })
        return ret

    def build_scope_web_burp(self, scope):
        """Return a Burp Suite scope given retrieved web scope"""
        ret = {'target': {'scope': {'advanced_mode': 'true', 'exclude': [], 'include': []}}}
        for asset in scope:
            state = 'include' if asset['status'] == 'in' else 'exclude'
            raw = urlparse(asset['raw_url'])
            for item in asset['rules']:
                item = item['rule'].strip('.*')
                url = urlparse(item)
                if len(url.netloc) == 0:
                    url = urlparse(raw.scheme + '://' + item)
                ret['target']['scope'][state].append({
                    'enabled': True if url.hostname else False,
                    'scheme': url.scheme if url.scheme else 'any',
                    'host': url.hostname,
                    'file': url.path
                })
        return ret

    def build_scope_web_db(self, scope):
        """Return a Web Scope that can be ingested into the Database"""
        ret = list()
        for asset in scope:
            if asset.get('status') == 'in':
                for owner in asset.get('owners'):
                    ret.append({
                        "target": owner.get('owner_uid'),
                        "urls": [{
                            "url": asset.get('raw_url')
                        }]
                    })
        return ret

    def build_scope_web_urls(self, scope):
        """Return a list of the raw urls gived a retrieved web scope"""
        ret = {"in": list(), "out": list()}
        for asset in scope:
            if asset.get('status') == 'in':
                ret["in"].append(asset["raw_url"])
            else:
                ret["out"].append(asset["raw_url"])
        return ret

    def build_slug_from_codename(self, codename):
        """Return a slug for a target given its codename"""
        slug = None
        targets = self.db.find_targets(codename=codename)
        if not targets:
            self.get_registered_summary()
            targets = self.db.find_targets(codename=codename)
        if targets:
            slug = targets[0].slug
        return slug

    def get_assessments(self):
        """Check which assessments have been completed"""
        res = self.api.request('GET', 'assessments')
        if res.status_code == 200:
            self.db.add_categories(res.json())
            return self.db.categories

    def get_connected(self):
        """Return information about the currenly selected target"""
        res = self.api.request('GET', 'launchpoint')
        if res.status_code == 200:
            j = res.json()
            slug = j.get('slug')

            if slug == '':
                status = 'Not Connected'
            else:
                status = "Connected"

            ret = {
                "slug": slug,
                "codename": self.build_codename_from_slug(slug),
                "status": status
            }
            return ret

    def get_credentials(self, **kwargs):
        """Get Credentials for a target"""
        target = self.db.find_targets(**kwargs)[0]
        if target:
            res = self.api.request('POST',
                                   f'asset/v1/organizations/{target.organization}' +
                                   f'/owners/listings/{target.slug}' +
                                   f'/users/{self.db.user_id}' +
                                   '/credentials')
            if res.status_code == 200:
                return res.json()

    def get_query(self, status='registered', query_changes={}):
        """Get information about targets returned from a query"""
        if not self.db.categories:
            self.get_assessments()
        categories = []
        for category in self.db.categories:
            if category.passed_practical and category.passed_written:
                categories.append(category.id)
        query = {
            'filter[primary]': status,
            'filter[secondary]': 'all',
            'filter[industry]': 'all',
            'filter[category][]': categories
        }
        query.update(query_changes)
        res = self.api.request('GET', 'targets', query=query)
        if res.status_code == 200:
            self.db.add_targets(res.json(), is_registered=True)
            return res.json()

    def get_registered_summary(self):
        """Get information on your registered targets"""
        res = self.api.request('GET', 'targets/registered_summary')
        ret = []
        if res.status_code == 200:
            self.db.add_targets(res.json())
            ret = dict()
            for t in res.json():
                ret[t['id']] = t
        return ret

    def get_scope(self, **kwargs):
        """Get the scope of a target"""
        if len(kwargs) > 0:
            target = self.db.find_targets(**kwargs)
        else:
            curr = self.get_connected()
            target = self.db.find_targets(slug=curr.get('slug'))

        if target:
            target = target[0]
            categories = dict()
            for category in self.db.categories:
                categories[category.id] = category.name
            if categories[target.category].lower() == 'host':
                return self.get_scope_host(target)
            elif categories[target.category].lower() == 'web application':
                return self.get_scope_web(target)

    def get_scope_host(self, target=None, **kwargs):
        """Get the scope of a Host target"""
        if target is None:
            target = self.db.find_targets(**kwargs)
            if target:
                target = target[0]
        if target:
            res = self.api.request('GET', f'targets/{target.slug}/cidrs?page=all')
            if res.status_code == 200:
                scope = res.json()['cidrs']
                self.db.add_ips(self.build_scope_host_db(target.slug, scope))
                if self.db.use_scratchspace:
                    self.scratchspace.set_hosts_file(scope, target=target)
                return scope

    def get_scope_web(self, target=None, **kwargs):
        """Get the scope of a Web target"""
        if target is None:
            target = self.db.find_targets(**kwargs)
            if target:
                target = target[0]
        res = self.api.request('GET', f'asset/v1/organizations/{target.organization}' +
                                      f'/owners/listings/{target.slug}/webapps')
        if res.status_code == 200:
            scope = list()
            for asset in res.json():
                if target.slug in [o['owner_uid'] for o in asset['owners']]:
                    scope.append(asset)
            self.db.add_urls(self.build_scope_web_db(scope))
            if self.db.use_scratchspace:
                self.scratchspace.set_burp_file(self.build_scope_web_burp(scope), target=target)
            return scope

    def get_unregistered(self):
        """Get slugs of all unregistered targets"""
        return self.get_query(status='unregistered')

    def get_upcoming(self):
        """Get slugs and upcoming start dates of all upcoming targets"""
        query_changes = {
            'sorting[field]': 'upcomingStartDate',
            'sorting[direction]': 'asc'
        }
        return self.get_query(status='upcoming', query_changes=query_changes)

    def set_connected(self, target=None, **kwargs):
        """Connect to a target"""
        slug = None
        if target:
            slug = target.slug
        elif len(kwargs) == 0:
            slug = ''
        else:
            target = self.db.find_targets(**kwargs)
            if target:
                slug = target[0].slug

        if slug is not None:
            res = self.api.request('PUT', 'launchpoint', data={'listing_id': slug})
            if res.status_code == 200:
                return self.get_connected()

    def set_registered(self, targets=None):
        """Register all unregistered targets"""
        if targets is None:
            targets = self.get_unregistered()
        data = '{"ResearcherListing":{"terms":1}}'
        ret = []
        for t in targets:
            res = self.api.request('POST',
                                   f'targets/{t["slug"]}/signup',
                                   data=data)
            if res.status_code == 200:
                ret.append(t)
        if len(targets) >= 15:
            ret.extend(self.set_registered())
        return ret
