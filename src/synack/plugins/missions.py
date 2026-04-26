"""plugins/missions.py

Functions related to handling, viewing, claiming, etc. missions
"""

import operator
import random

from datetime import datetime

from .base import Plugin


class Missions(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for plugin in ['Api', 'Auth', 'Db', 'Targets', 'Templates']:
            setattr(self,
                    '_'+plugin.lower(),
                    self._registry.get(plugin)(self._state))

    def build_order(self, missions, sort="payout-high"):
        """Sort a list of missions by what's desired first

        Arguments:
        missions -- A list of missions
        sort -- Criteria to sort by
                (payout-high, payout-low, random, reverse)
        """
        if sort.startswith("payout-"):
            dollar_value = dict()
            for i in range(len(missions)):
                dollar_value[i] = missions[i]["payout"]["amount"]
            reverse = True if "high" in sort else False
            sort = sorted(dollar_value.items(),
                          key=operator.itemgetter(1),
                          reverse=reverse)
            missions = [missions[t[0]] for t in sort]
        elif sort == "shuffle":
            random.shuffle(missions)
        elif sort == "reverse":
            missions.reverse()
        return missions

    def build_summary(self, missions):
        """Return a basic summary from a list of missions

        Arguments:
        missions -- List of missions from one of the get_missions functions
        """
        ret = {
            'total': {'count': 0, 'value': 0, 'time': 0}
        }
        for mission in missions:
            codename = mission.get('listingCodename', 'UNKNOWN')
            ret[codename] = ret.get(codename, {'count': 0, 'value': 0, 'time': 0, 'titles': list()})
            ret[codename]['count'] += 1
            ret[codename]['value'] += mission['payout']['amount']
            ret[codename]['titles'].append(mission['title'])
            ret['total']['count'] += 1
            ret['total']['value'] += mission['payout']['amount']

            if mission.get('status') == 'CLAIMED':
                utc = datetime.utcnow()
                try:
                    claimed_on = datetime.strptime(mission['claimedOn'],
                                                   '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    claimed_on = datetime.strptime(mission['claimedOn'],
                                                   '%Y-%m-%dT%H:%M:%SZ')
                try:
                    modified_on = datetime.strptime(mission['modifiedOn'],
                                                    '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    modified_on = datetime.strptime(mission['modifiedOn'],
                                                    '%Y-%m-%dT%H:%M:%SZ')
                report_time = claimed_on if claimed_on > modified_on else modified_on
                elapsed = int((utc - report_time).total_seconds())
                time = mission['maxCompletionTimeInSecs'] - elapsed
                if time < ret['total']['time'] or ret['total']['time'] == 0:
                    ret['total']['time'] = time
                if time < ret[codename]['time'] or ret[codename]['time'] == 0:
                    ret[codename]['time'] = time

        return ret

    def get(self, status='PUBLISHED', max_pages=1, page=1, per_page=20, listing_uids=None, **kwargs):
        """Get a list of missions given a status

        Arguments:
        status -- String matching the type of missions
                  (PUBLISHED, CLAIMED, FOR_REVIEW, APPROVED)
        max_pages -- Maximum number of pages to query
        page -- Starting page
        per_page -- Missions to return per page
                    Make sure this number is logical
                    (Bad: per_page=5000, per_page=1&max_pages=10)
        listing_uids -- A specific listing ID to check for missions
        """
        query = {
                'status': status,
                'perPage': per_page,
                'page': page,
                'viewed': "true"
        }
        if listing_uids:
            query["listingUids"] = listing_uids
        res = self._api.request('GET',
                                'tasks/v2/tasks',
                                query=query)
        if res.status_code == 200:
            ret = res.json()
            if len(ret) == per_page and page < max_pages:
                new = self.get(status=status,
                               max_pages=max_pages,
                               page=page+1,
                               per_page=per_page)
                ret.extend(new)
            return ret
        elif res.status_code == 403 and self._state.login:
            self._auth.get_api_token()
        return []

    def get_approved(self, **kwargs):
        """Get a list of missions currently approved"""
        kwargs['status'] = 'APPROVED'
        return self.get(**kwargs)

    def get_available(self, **kwargs):
        """Get a list of missions currently available"""
        kwargs['status'] = 'PUBLISHED'
        return self.get(**kwargs)

    def get_claimed(self, **kwargs):
        """Get a list of all missions you currently have"""
        kwargs['status'] = 'CLAIMED'
        return self.get(**kwargs)

    def get_count(self, status="PUBLISHED", listing_uids=None):
        """Get the number of missions currently available

        Arguments:
        status -- Status of the missions to count
        listing_uid -- Listing Id to check
        """
        query = {
            "status": status,
            "viewed": "false",
        }
        if listing_uids:
            query["listingUid"] = listing_uids
        res = self._api.request('HEAD',
                                'tasks/v1/tasks',
                                query=query)
        if res.status_code == 204:
            return int(res.headers.get('x-count', 0))
        elif res.status_code == 403 and self._state.login:
            self._auth.get_api_token()
        return 0

    def get_evidences(self, mission):
        """Download the evidences for a single mission

        Arguments:
        mission -- A single mission
        """
        res = self._api.request('GET',
                                'tasks/v2/tasks/' +
                                mission['id'] +
                                '/evidences')
        if res.status_code == 200:
            ret = res.json()
            ret["title"] = mission["title"]
            ret["asset"] = mission["assetTypes"][0]
            ret["taskType"] = mission["taskType"]
            ret["structuredResponse"] = mission["validResponses"][1]["value"]

            return ret
        elif res.status_code == 403 and self._state.login:
            self._auth.get_api_token()

    def get_in_review(self, **kwargs):
        """Get a list of missions currently in review"""
        kwargs['status'] = 'FOR_REVIEW'
        return self.get(**kwargs)

    def get_wallet_claimed(self):
        """Get Current Claimed Amount for Mission Wallet"""
        res = self._api.request('GET',
                                'tasks/v2/researcher/claimed_amount')
        if res.status_code == 200:
            return int(res.json().get('claimedAmount', '0'))
        elif res.status_code == 403 and self._state.login:
            self._auth.get_api_token()

    def get_wallet_limit(self):
        """Get Current Mission Wallet Limit"""
        res = self._api.request('GET',
                                'profiles/me')
        if res.status_code == 200:
            return int(res.json().get('claim_limit', '0'))
        elif res.status_code == 403 and self._state.login:
            self._auth.get_api_token()

    def set_claimed(self, mission):
        """Try to claim a single mission

        Arguments:
        mission -- A single mission
        """
        return self.set_status(mission, "CLAIM")

    def set_disclaimed(self, mission):
        """Try to release a single mission

        Arguments:
        missions -- A single mission
        """
        return self.set_status(mission, "DISCLAIM")

    def set_evidences(self, mission, template=None, force=False):
        """Upload a template to a mission

        Arguments:
        mission -- A single mission
        """
        if template is None:
            template = self._templates.get_file(mission)
        if template:
            curr = self.get_evidences(mission)
            safe = True
            if curr:
                for f in ['introduction', 'testing_methodology',
                          'conclusion']:
                    if len(curr.get(f)) >= 20 and not force:
                        safe = False
                        break
            if safe:
                res = self._api.request('PATCH',
                                        'tasks/v2/tasks/' +
                                        mission['id'] +
                                        '/evidences',
                                        data=template)
                if res.status_code == 200:
                    ret = res.json()
                    ret["title"] = mission["title"]
                    ret["codename"] = mission["listingCodename"]
                    return ret
                elif res.status_code == 403 and self._state.login:
                    self._auth.get_api_token()

    def set_status(self, mission, status):
        """Interact with single mission

        Arguments:
        mission -- A single mission
        """
        data = {
            "type": status
        }
        orgId = mission.get('organizationUid', 'unk')
        listingId = mission.get('listingUid', 'unk')
        campaignId = mission.get('campaignUid', 'unk')
        taskId = mission.get('id')
        payout = str(mission.get('payout', {}).get('amount', 'unk'))
        title = mission.get('title', 'unk')

        res = self._api.request('POST',
                                'tasks/v1' +
                                '/organizations/' + orgId +
                                '/listings/' + listingId +
                                '/campaigns/' + campaignId +
                                '/tasks/' + taskId +
                                '/transitions',
                                data=data)
        return {
            "target": listingId,
            "title": title,
            "payout": payout,
            "status": status,
            "success": True if res.status_code == 201 else False
        }
