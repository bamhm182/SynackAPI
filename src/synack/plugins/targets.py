"""plugins/targets.py

Functions related to handling and checking targets
"""


class Targets:
    def __init__(self, handler):
        self.handler = handler

    def get_assessments(self):
        """Check which assessments have been completed"""
        res = self.handler.api.request('GET', 'assessments')
        if res.status_code == 200:
            ret = []
            for a in res.json():
                wpass = a['written_assessment']['passed']
                ppass = a['practical_assessment']['passed']
                if wpass and ppass:
                    ret.append({
                        'name': a['category_name'],
                        'id': a['category_id']
                    })
            self.handler.db.assessments = ret
            return ret

    def get_codename_from_slug(self, slug):
        """Return a codename for a target given its slug

        Arguments:
        slug -- Slug of desired target
        """
        target = self.handler.db.known_targets.get(slug)
        if not target:
            target = self.get_registered_summary().get(slug)
        return target.get("codename")

    def get_current_target(self):
        """Return information about the currenly selected target"""
        res = self.handler.api.request('GET', 'launchpoint')
        if res.status_code == 200:
            j = res.json()
            if j['pending_slug'] != '-1':
                slug = j['pending_slug']
                status = "Connecting"
            else:
                slug = j['slug']
                status = "Connected"
            ret = {
                "slug": slug,
                "codename": self.get_codename_from_slug(slug),
                "status": status
            }
            return ret

    def get_registered_summary(self):
        """Get information on your registered targets"""
        res = self.handler.api.request('GET', 'targets/registered_summary')
        ret = []
        if res.status_code == 200:
            ret = dict()
            for t in res.json():
                ret[t['id']] = t
            self.handler.db.known_targets = ret
        return ret

    def get_unregistered(self):
        """Get slugs of all unregistered targets"""
        if not self.handler.db.assessments:
            self.get_assessments()
        categories = [a['id'] for a in self.handler.db.assessments]
        query = {
                'filter[primary]': 'unregistered',
                'filter[secondary]': 'all',
                'filter[industry]': 'all',
                'filter[category][]': categories
        }
        res = self.handler.api.request('GET', 'targets', query=query)
        ret = []
        if res.status_code == 200:
            for t in res.json():
                ret.append({'codename': t['codename'], 'slug': t['slug']})
        return ret

    def do_register_all(self):
        """Register all unregistered targets"""
        unreg = self.get_unregistered()
        data = '{"ResearcherListing":{"terms":1}}'
        ret = []
        for t in unreg:
            res = self.handler.api.request('POST',
                                           f'targets/{t["slug"]}/signup',
                                           data=data)
            if res.status_code == 200:
                ret.append(t)
        if len(unreg) >= 15:
            ret.extend(self.do_register_all())
        return ret
