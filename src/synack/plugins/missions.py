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

    def get_approved_missions(self):
        """Get a list of missions currently approved"""
        return self.get_missions("APPROVED")

    def get_available_missions(self):
        """Get a list of missions currently available"""
        return self.get_missions("PUBLISHED")

    def get_claimed_missions(self):
        """Get a list of all missions you currently have"""
        return self.get_missions("CLAIMED")

    def get_invisible_missions(self):
        """Return targets with invisible missions

        Sometimes a condition will arise in which the
        sidebar states there are missions, but there are not.
        These missions are associated with a specific target.
        If this happens, we can use this to easily determine
        which target has the mission and submit a ticket.
        """
        ret = []
        self.targets.get_registered_summary()
        for t in self.db.targets:
            count = self.get_missions_count("PUBLISHED", t.slug)
            if count >= 1:
                missions = self.get_missions("PUBLISHED", 1, 1, count, t.slug)
                if len(missions) == 0:
                    ret.append(t.codename)
        return ret

    def get_in_review_missions(self):
        """Get a list of missions currently in review"""
        return self.get_missions("FOR_REVIEW")

    def get_missions_count(self, status="PUBLISHED", listing_uids=None):
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

    def get_missions_summary(self, missions):
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
                elapsed = (utc - claimed_on).seconds
                time = m['maxCompletionTimeInSecs'] - elapsed
                if time < ret['time'] or ret['time'] == 0:
                    ret['time'] = time
            ret['count'] = ret['count'] + 1
            ret['value'] = ret['value'] + m['payout']['amount']
        return ret

    def get_missions(self, status="PUBLISHED",
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
                new = self.get_missions(status,
                                        max_pages,
                                        page+1,
                                        per_page)
                ret.extend(new)
            return ret

    def do_claim_mission(self, mission):
        """Try to claim a single mission

        Arguments:
        mission -- A single mission
        """
        return self.do_interact_mission(mission, "CLAIM")

    def do_release_mission(self, mission):
        """Try to release a single mission

        Arguments:
        missions -- A single mission
        """
        return self.do_interact_mission(mission, "DISCLAIM")

    def do_interact_mission(self, mission, action):
        """Interact with single mission

        Arguments:
        mission -- A single mission
        """
        data = {
            "type": action
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
            "claimed": True if res.status_code == 201 else False
        }

    def do_upload_evidences(self, mission):
        """Upload a template to a mission

        Arguments:
        mission -- A single mission
        """
        template = self.templates.get_template(mission)
        if template:
            curr = self.get_evidences(mission)
            safe = True
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

    def get_evidences(self, mission):
        """Download the evidences for a single mission

        Arguments:
        mission -- A single mission
        """
        res = self.api.request('GET',
                               'tasks/v2/tasks/' +
                               mission['id'] +
                               '/evidences')
        if res.status_code == 200:
            ret = res.json()
            ret["title"] = mission["title"]
            ret["asset"] = mission["assetTypes"][0]
            ret["type"] = mission["taskType"]
            ret["structuredResponse"] = mission["validResponses"][1]["value"]

            return ret

    def do_sort_missions(self, missions, sort="payout-high"):
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
