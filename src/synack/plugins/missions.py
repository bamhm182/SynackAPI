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
        for plugin in ['Api', 'Db', 'Targets', 'Templates']:
            setattr(self,
                    plugin.lower(),
                    self.registry.get(plugin)(self.state))

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
            "count": 0,
            "value": 0,
            "time": 0
        }
        for m in missions:
            if m.get("status") == "CLAIMED":
                utc = datetime.utcnow()
                claimed_on = datetime.strptime(m['claimedOn'],
                                               "%Y-%m-%dT%H:%M:%S.%fZ")
                elapsed = int((utc - claimed_on).total_seconds())
                time = m['maxCompletionTimeInSecs'] - elapsed
                if time < ret['time'] or ret['time'] == 0:
                    ret['time'] = time
            ret['count'] = ret['count'] + 1
            ret['value'] = ret['value'] + m['payout']['amount']
        return ret

    def get(self, status="PUBLISHED",
            max_pages=1, page=1, per_page=20, listing_uids=None):
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
        res = self.api.request('GET',
                               'tasks/v2/tasks',
                               query=query)
        if res.status_code == 200:
            ret = res.json()
            if len(ret) == per_page and page < max_pages:
                new = self.get(status,
                               max_pages,
                               page+1,
                               per_page)
                ret.extend(new)
            return ret

    def get_approved(self):
        """Get a list of missions currently approved"""
        return self.get("APPROVED")

    def get_available(self):
        """Get a list of missions currently available"""
        return self.get("PUBLISHED")

    def get_claimed(self):
        """Get a list of all missions you currently have"""
        return self.get("CLAIMED")

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
        res = self.api.request('HEAD',
                               'tasks/v1/tasks',
                               query=query)
        if res.status_code == 204:
            return int(res.headers.get('x-count', 0))

    def get_evidences(self, mission):
        """Download the evidences for a single mission

        Arguments:
        mission -- A single mission
        """
        evidences = self.api.request('GET',
                                     'tasks/v2/tasks/' +
                                     mission['id'] +
                                     '/evidences')
        if evidences.status_code == 200:
            ret = evidences.json()
            ret["title"] = mission["title"]
            ret["asset"] = mission["assetTypes"][0]
            ret["taskType"] = mission["taskType"]
            ret["structuredResponse"] = mission["validResponses"][1]["value"]

            return ret

    def get_in_review(self):
        """Get a list of missions currently in review"""
        return self.get("FOR_REVIEW")

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

    def set_evidences(self, mission, template=None):
        """Upload a template to a mission

        Arguments:
        mission -- A single mission
        """
        if template is None:
            template = self.templates.get_file(mission)
        if template:
            curr = self.get_evidences(mission)
            safe = True
            if curr:
                for f in ['introduction', 'testing_methodology',
                          'conclusion']:
                    if len(curr.get(f)) >= 20:
                        safe = False
                        break
            if safe:
                res = self.api.request('PATCH',
                                       'tasks/v2/tasks/' +
                                       mission['id'] +
                                       '/evidences',
                                       data=template)
                if res.status_code == 200:
                    ret = res.json()
                    ret["title"] = mission["title"]
                    ret["codename"] = mission["listingCodename"]
                    return ret

    def set_status(self, mission, status):
        """Interact with single mission

        Arguments:
        mission -- A single mission
        """
        data = {
            "type": status
        }
        orgId = mission["organizationUid"]
        listingId = mission["listingUid"]
        campaignId = mission["campaignUid"]
        taskId = mission["id"]
        payout = str(mission["payout"]["amount"])
        title = mission["title"]

        res = self.api.request('POST',
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
