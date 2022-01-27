"""test_missions.py

Tests for the plugins/missions.py Missions Class
"""

import datetime
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

from src import synack
from unittest.mock import MagicMock


class MissionsTestCase(unittest.TestCase):
    def setUp(self):
        synack.Handler = MagicMock()
        self.missions = synack.Missions(synack.Handler())

    def test_get_available_missions(self):
        """Should request PUBLISHED missions"""
        self.missions.get_missions = MagicMock()
        self.missions.get_missions.return_value = ['one', 'two']
        self.assertEqual(['one', 'two'], self.missions.get_available_missions())
        self.missions.get_missions.assert_called_with("PUBLISHED")

    def test_get_approved_missions(self):
        """Should request APPROVED missions"""
        self.missions.get_missions = MagicMock()
        self.missions.get_missions.return_value = ['one', 'two']
        self.assertEqual(['one', 'two'], self.missions.get_approved_missions())
        self.missions.get_missions.assert_called_with("APPROVED")

    def test_get_claimed_missions(self):
        """Should request CLAIMED missions"""
        self.missions.get_missions = MagicMock()
        self.missions.get_missions.return_value = ['one', 'two']
        self.assertEqual(['one', 'two'], self.missions.get_claimed_missions())
        self.missions.get_missions.assert_called_with("CLAIMED")

    def test_get_invisible_missions(self):
        """Should try to get invisible missions"""
        self.missions.handler.db.known_targets = []
        self.missions.handler.targets.get_registered_summary = MagicMock()
        self.missions.handler.targets.get_registered_summary.return_value = {
           "34uhweow": {
                "codename": "SOMEGUY",
                "id": "34uhweow"
            },
            "8935h3r4": {
                "codename": "SOMEGAL",
                "id": "8935h3r4"
            }
        }
        count_calls = [
            unittest.mock.call("PUBLISHED", "34uhweow"),
            unittest.mock.call("PUBLISHED", "8935h3r4")
        ]
        self.missions.get_missions_count = MagicMock()
        self.missions.get_missions_count.side_effect = [1,1]

        self.missions.get_missions = MagicMock()
        self.missions.get_missions.side_effect = [[], ["real_mission"]]

        self.assertEqual(["SOMEGUY"], self.missions.get_invisible_missions())
        
        self.missions.get_missions_count.has_calls(count_calls)

    def test_get_in_review_missions(self):
        """Should request FOR_REVIEW missions"""
        self.missions.get_missions = MagicMock()
        self.missions.get_missions.return_value = ['one', 'two']
        self.assertEqual(['one', 'two'], self.missions.get_in_review_missions())
        self.missions.get_missions.assert_called_with("FOR_REVIEW")

    def test_get_missions_count(self):
        """Should get the current number of published missions"""
        self.missions.handler.api.request.return_value.status_code = 204
        self.missions.handler.api.request.return_value.headers = {
            'x-count': 5
        }
        query = {
            "status": "PUBLISHED",
            "viewed": "false"
        }
        self.assertEqual(5, self.missions.get_missions_count())
        self.missions.handler.api.request.assert_called_with("HEAD",
                                              "tasks/v1/tasks",
                                              query=query)

    def test_get_missions_count_status_uid(self):
        """Should get the current number of STATUS missions on TARGET"""
        self.missions.handler.api.request.return_value.status_code = 204
        self.missions.handler.api.request.return_value.headers = {
            'x-count': 10
        }
        query = {
            "status": "CLAIMED",
            "viewed": "false",
            "listingUid": "u4fh8"
        }
        self.assertEqual(10, self.missions.get_missions_count("CLAIMED", "u4fh8"))
        self.missions.handler.api.request.assert_called_with("HEAD",
                                              "tasks/v1/tasks",
                                              query=query)

    def test_get_missions_summary(self):
        """Should summarize a list of missions"""
        ret = {
            "count": 2,
            "value": 75,
            "time": 79200
        }
        now = datetime.datetime.utcnow()
        t1 = datetime.datetime.strftime(now-datetime.timedelta(hours=2),
                                        "%Y-%m-%dT%H:%M:%S.%fZ")
        t2 = datetime.datetime.strftime(now-datetime.timedelta(hours=1),
                                        "%Y-%m-%dT%H:%M:%S.%fZ")
        m = [
            {
                "status": "CLAIMED",
                "maxCompletionTimeInSecs": 86400,
                "payout": {"amount": 50},
                "claimedOn": t1
            },
            {
                "status": "CLAIMED",
                "maxCompletionTimeInSecs": 86400,
                "payout": {"amount": 25},
                "claimedOn": t2
            }
        ]

        self.assertEqual(ret, self.missions.get_missions_summary(m))

    def test_get_missions_defaults(self):
        """Should get a list of published missions"""
        query = {
            "status": "PUBLISHED",
            "perPage": 20,
            "page": 1,
            "viewed": "true"
        }
        ret = [
            "mission_one",
            "mission_two"
        ]
        self.missions.handler.api.request.return_value.status_code = 200
        self.missions.handler.api.request.return_value.json.return_value = ret
        self.assertEqual(ret, self.missions.get_missions())
        self.missions.handler.api.request.assert_called_with("GET",
                                              "tasks/v2/tasks",
                                              query=query)
       
     
    def test_get_missions_mixup(self):
        """Should get a list of specific missions"""
        query = {
            "status": "CLAIMED",
            "perPage": 5,
            "page": 2,
            "viewed": "true",
            "listingUids": "49fh48g7"
        }
        ret = [
            "mission_one",
            "mission_two"
        ]
        self.missions.handler.api.request.return_value.status_code = 200
        self.missions.handler.api.request.return_value.json.return_value = ret
        self.assertEqual(ret, self.missions.get_missions("CLAIMED", 1, 2, 5, "49fh48g7"))
        self.missions.handler.api.request.assert_called_with("GET",
                                              "tasks/v2/tasks",
                                              query=query)
        
    def test_get_missions_multi_page(self):
        """Should get a list missions across multiple pages"""
        q1 = {
            "status": "CLAIMED",
            "perPage": 5,
            "page": 2,
            "viewed": "true",
            "listingUids": "49fh48g7"
        }
        q2 = q1
        self.missions.handler.api.request.return_value.status_code = 200
        self.missions.handler.api.request.return_value.json.side_effect = [
            ["mission_one"],
            ["mission_two"],
            ["mission_three"]
        ]
        calls = [
            unittest.mock.call("GET",
                               "tasks/v2/tasks",
                               query=q1)
        ]
        self.assertEqual(["mission_one", "mission_two"],
                          self.missions.get_missions(max_pages=2,
                                                       per_page=1))
        self.missions.handler.api.request.has_calls(calls)
        self.assertEqual(2, self.missions.handler.api.request.call_count)

    def test_do_interact_mission(self):
        """Should interact with a mission"""
        m = {
            "organizationUid": "24re7yuf",
            "listingUid": "4wr7egtu",
            "campaignUid": "27493fe8r",
            "id": "4i3eg86fyu",
            "payout": {"amount": 10},
            "title": "Some Mission"
        }
        ret = {
            "target": "4wr7egtu",
            "title": "Some Mission",
            "payout": "10",
            "claimed": True
        }
        self.missions.handler.api.request.return_value.status_code = 201
        self.assertEqual(ret, self.missions.do_interact_mission(m, "CLAIM"))
        data = {"type": "CLAIM"}
        calls = [
            unittest.mock.call('POST',
                               'tasks/v1' +
                               '/organizations/24re7yuf' +
                               '/listings/4wr7egtu' +
                               '/campaigns/27493fe8r' +
                               '/tasks/4i3eg86fyu' +
                               '/transitions',
                               data=data),
            unittest.mock.call('POST',
                               'tasks/v1' +
                               '/organizations/98y4ehru' +
                               '/listings/4298y3rehi' +
                               '/campaigns/27493fe8r' +
                               '/tasks/984yrehi' +
                               '/transitions',
                               data=data)
        ]
        self.missions.handler.api.request.has_calls(calls)

    def test_do_sort_missions(self):
        """Should sort by payout high (default)"""
        m = [
            {"payout": {"amount": 10}},
            {"payout": {"amount": 40}},
            {"payout": {"amount": 30}},
            {"payout": {"amount": 20}},
            {"payout": {"amount": 50}},
        ]
        ret = [
            {"payout": {"amount": 50}},
            {"payout": {"amount": 40}},
            {"payout": {"amount": 30}},
            {"payout": {"amount": 20}},
            {"payout": {"amount": 10}},
        ]

        self.assertEqual(ret, self.missions.do_sort_missions(m))

    def test_do_sort_missions_payout_low(self):
        """Should sort by payout low"""
        m = [
            {"payout": {"amount": 10}},
            {"payout": {"amount": 40}},
            {"payout": {"amount": 30}},
            {"payout": {"amount": 20}},
            {"payout": {"amount": 50}},
        ]
        ret = [
            {"payout": {"amount": 10}},
            {"payout": {"amount": 20}},
            {"payout": {"amount": 30}},
            {"payout": {"amount": 40}},
            {"payout": {"amount": 50}},
        ]

        self.assertEqual(ret, self.missions.do_sort_missions(m, "payout-low"))


    def test_do_sort_missions_shuffle(self):
        """Should sort by payout low"""
        m = [
            {"payout": {"amount": 10}},
            {"payout": {"amount": 40}},
            {"payout": {"amount": 30}},
            {"payout": {"amount": 20}},
            {"payout": {"amount": 50}},
        ]
        random.shuffle = MagicMock()
        self.missions.do_sort_missions(m, "shuffle")
        random.shuffle.assert_called_with(m)


    def test_do_sort_missions_reverse(self):
        """Should sort by payout low"""
        m = [
            {"payout": {"amount": 10}},
            {"payout": {"amount": 40}},
            {"payout": {"amount": 30}},
            {"payout": {"amount": 20}},
            {"payout": {"amount": 50}},
        ]
        ret = [
            {"payout": {"amount": 50}},
            {"payout": {"amount": 20}},
            {"payout": {"amount": 30}},
            {"payout": {"amount": 40}},
            {"payout": {"amount": 10}},
        ]

        self.assertEqual(ret, self.missions.do_sort_missions(m, "reverse"))


    def test_do_claim_mission(self):
        """Should send a CLAIM to do_interact_mission"""
        self.missions.do_interact_mission = MagicMock()
        self.missions.do_interact_mission.return_value = ["ret"]
        self.assertEquals(["ret"], self.missions.do_claim_mission(["yup"]))
        self.missions.do_interact_mission.assert_called_with(["yup"], "CLAIM")
        
    def test_do_release_mission(self):
        """Should send a DISCLAIM to do_interact_mission"""
        self.missions.do_interact_mission = MagicMock()
        self.missions.do_interact_mission.return_value = ["ret"]
        self.assertEquals(["ret"], self.missions.do_release_mission(["nope"]))
        self.missions.do_interact_mission.assert_called_with(["nope"], "DISCLAIM")

    def test_do_upload_evidences_safe(self):
        """Should get a template and upload it if current text is < 20 characters"""
        template = {
            "introduction": "intro",
            "testing_methodology": "test",
            "conclusion": "verdict",
            "structuredResponse": "no"
        }
        curr = {
            "introduction": "A"*19,
            "testing_methodology": "B"*19,
            "conclusion": "C"*19
        }
        mission = {
            "id": "2uthgr",
            "title": "Some Title Thing",
            "assetTypes": ["web"],
            "taskType": ["mission"],
            "validResponses": [{}, {"value": "uieth8rgyub"}],
            "listingCodename": "SLAPPYMONKEY"
        }
        self.missions.handler.templates.get_template = MagicMock()
        self.missions.handler.templates.get_template.return_value = template
        self.missions.get_evidences = MagicMock()
        self.missions.get_evidences.return_value = curr
        self.missions.handler.api.request = MagicMock()
        self.missions.handler.api.request.return_value.status_code = 200
        self.missions.handler.api.request.return_value.json.return_value = {}
        self.missions.do_upload_evidences(mission)
        self.missions.handler.api.request.assert_called_with('PATCH',
                                                             'tasks/v2/tasks/2uthgr/evidences',
                                                             data=template)

    def test_do_upload_evidences_unsafe(self):
        """Should NOT upload a template if current text is >= 20 characters"""
        template = {
            "introduction": "intro",
            "testing_methodology": "test",
            "conclusion": "verdict",
            "structuredResponse": "no"
        }
        curr = {
            "introduction": "A"*19,
            "testing_methodology": "B"*20,
            "conclusion": "C"*19
        }
        mission = {
            "id": "2uthgr",
            "title": "Some Title Thing",
            "assetTypes": ["web"],
            "taskType": ["mission"],
            "validResponses": [{}, {"value": "uieth8rgyub"}],
            "listingCodename": "SLAPPYMONKEY"
        }
        self.missions.handler.templates.get_template = MagicMock()
        self.missions.handler.templates.get_template.return_value = template
        self.missions.get_evidences = MagicMock()
        self.missions.get_evidences.return_value = curr
        self.missions.handler.api.request = MagicMock()
        self.missions.handler.api.request.return_value.status_code = 200
        self.missions.handler.api.request.return_value.json.return_value = {}
        self.missions.do_upload_evidences(mission)
        self.missions.handler.api.request.assert_not_called()


    def test_get_evidences(self):
        """Should get evidences from a mission"""
        m = {
            "id": "eugtgowery8t",
            "title": "Some Mission",
            "assetTypes": ["web"],
            "taskType": "MISSION",
            "validResponses": [{}, {"value": "uieth8rgyub"}],
        }
        ret = {
            "title": m["title"],
            "asset": "web",
            "type": "MISSION",
            "structuredResponse": "uieth8rgyub"
        }
        self.missions.handler.api.request = MagicMock()
        self.missions.handler.api.request.return_value.status_code = 200
        self.missions.handler.api.request.return_value.json.return_value = {}
        self.assertEquals(ret, self.missions.get_evidences(m))
        self.missions.handler.api.request.assert_called_with("GET",
                                                             "tasks/v2/tasks/eugtgowery8t/evidences")




        



        













