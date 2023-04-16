"""plugins/targets.py

Functions related to handling and checking targets
"""

import ipaddress
import re

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
        ret = {'target': {'scope': {'advanced_mode': 'true', 'exclude': list(), 'include': list()}}}

        for asset in scope:
            state = 'include' if asset.get('status') == 'in' else 'exclude'
            raw = urlparse(asset.get('location', ''))
            item = asset.get('rule', '').strip('.*')
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
        sorting = dict()

        for item in scope:
            if item.get('status') == 'in':
                slug = item.get('listing')
                sorting[slug] = sorting.get(slug, list())
                sorting[slug].append({'url': item.get('location')})

        ret = list()

        for slug, urls in sorting.items():
            ret.append({
                'target': slug,
                'urls': urls
            })

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

    def get_assets(self, target=None, asset_type=None, host_type=None, active='true',
                   scope=['in', 'discovered'], sort='location', sort_dir='asc',
                   page=None, organization_uid=None, **kwargs):
        """Get the assets (scope) of a target"""
        if target is None:
            if len(kwargs) > 0:
                target = self.db.find_targets(**kwargs)
            else:
                curr = self.get_connected()
                target = self.db.find_targets(slug=curr.get('slug'))

        if type(scope) == str:
            scope = [scope]

        if target:
            if type(target) is list and len(target) > 0:
                target = target[0]
            queries = list()

            queries.append(f'listingUid%5B%5D={target.slug}')
            if organization_uid is not None:
                queries.append(f'organizationUid%5B%5D={organization_uid}')
            if asset_type is not None:
                queries.append(f'assetType%5B%5D={asset_type}')
            if host_type is not None:
                queries.append(f'hostType%5B%5D={host_type}')
            for item in scope:
                queries.append(f'scope%5B%5D={item}')
            if sort is not None:
                queries.append(f'sort%5B%5D={sort}')
            if active is not None:
                queries.append(f'active={active}')
            if sort_dir is not None:
                queries.append(f'sortDir={sort_dir}')
            if page is not None:
                queries.append(f'page={page}')

            res = self.api.request('GET', f'asset/v2/assets?{"&".join(queries)}')
            if res.status_code == 200:
                if self.db.use_scratchspace:
                    self.scratchspace.set_assets_file(res.text, target=target)
                return res.json()

    def get_attachments(self, target=None, **kwargs):
        """Get the attachments of a target."""
        if target is None:
            if len(kwargs) == 0:
                kwargs = {'codename': self.get_connected().get('codename')}
            target = self.db.find_targets(**kwargs)
            if target:
                target = target[0]
        res = self.api.request('GET', f'targets/{target.slug}/resources')
        if res.status_code == 200:
            return res.json()

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

    def get_connections(self, target=None, **kwargs):
        """Get the connection details of a target."""
        if target is None:
            if len(kwargs) == 0:
                kwargs = {'codename': self.get_connected().get('codename')}
            target = self.db.find_targets(**kwargs)
            if target:
                target = target[0]
        res = self.api.request('GET', "listing_analytics/connections", query={"listing_id": target.slug})
        if res.status_code == 200:
            return res.json()["value"]

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

    def get_scope(self, add_to_db=False, **kwargs):
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
                return self.get_scope_host(target, add_to_db=add_to_db)
            elif categories[target.category].lower() in ['web application', 'mobile']:
                return self.get_scope_web(target, add_to_db=add_to_db)

    def get_scope_host(self, target=None, add_to_db=False, **kwargs):
        """Get the scope of a Host target"""
        if target is None:
            targets = self.db.find_targets(**kwargs)
            if targets:
                target = next(iter(targets), None)

        scope = set()

        if target:
            assets = self.get_assets(target=target, active='true', asset_type='host', host_type='cidr')
            for asset in assets:
                if asset.get('active'):
                    try:
                        ipaddress.IPv4Network(asset.get('location'))
                        scope.add(asset.get('location'))
                    except ipaddress.AddressValueError:
                        # Not actually an IP
                        pass

            scope.discard(None)

            if len(scope) > 0:
                if add_to_db:
                    self.db.add_ips(self.build_scope_host_db(target.slug, scope))
                if self.db.use_scratchspace:
                    self.scratchspace.set_hosts_file(scope, target=target)

        return scope

    def get_scope_web(self, target=None, add_to_db=False, **kwargs):
        """Get the scope of a Web target"""
        if target is None:
            targets = self.db.find_targets(**kwargs)
            if targets:
                target = next(iter(targets), None)

        scope = list()

        if target:
            assets = self.get_assets(target=target, active='true', asset_type='webapp')
            for asset in assets:
                if asset.get('active'):
                    location = next(iter(re.split(r' \(', asset.get('location', ''))))
                    for listing in asset.get('listings', []):
                        status = listing.get('scope')
                        listing = listing.get('listingUid')
                        for rule in asset.get('scopeRules', []):
                            scope.append({
                                'status': status,
                                'listing': listing,
                                'location': location,
                                'rule': rule.get('rule')
                            })

            if len(scope) > 0:
                if add_to_db:
                    self.db.add_urls(self.build_scope_web_db(scope))
                if self.db.use_scratchspace:
                    self.scratchspace.set_web_file(self.build_scope_web_burp(scope), target=target)

        return scope

    def get_submissions(self, target=None, status="accepted", **kwargs):
        """Get the details of previously submitted vulnerabilities from the analytics of a target."""
        if status not in ["accepted", "rejected", "in_queue"]:
            return []
        if target is None:
            if len(kwargs) == 0:
                kwargs = {'codename': self.get_connected().get('codename')}
            target = self.db.find_targets(**kwargs)
            if target:
                target = target[0]
        query = {"listing_id": target.slug, "status": status}
        res = self.api.request('GET', "listing_analytics/categories", query=query)
        if res.status_code == 200:
            return res.json()["value"]

    def get_submissions_summary(self, target=None, hours_ago=None, **kwargs):
        """Get a summary of the submission analytics of a target."""
        if target is None:
            if len(kwargs) == 0:
                kwargs = {'codename': self.get_connected().get('codename')}
            target = self.db.find_targets(**kwargs)
            if target:
                target = target[0]
        query = {"listing_id": target.slug}
        if hours_ago:
            query["period"] = f"{hours_ago}h"
        res = self.api.request('GET', "listing_analytics/submissions", query=query)
        if res.status_code == 200:
            return res.json()["value"]

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
