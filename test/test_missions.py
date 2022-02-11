"""test_missions.py

Tests for the plugins/missions.py Missions Class
"""

import datetime
import os
import random
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class MissionsTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.missions = synack.plugins.Missions(self.state)
        self.missions.api = MagicMock()
        self.missions.db = MagicMock()
        self.missions.targets = MagicMock()
        self.missions.templates = MagicMock()

    def test_get_available(self):
        """Should request PUBLISHED missions"""
        self.missions.get_list = MagicMock()
        self.missions.get_list.return_value = ['one', 'two']
        self.assertEqual(['one', 'two'],
                         self.missions.get_available())
        self.missions.get_list.assert_called_with("PUBLISHED")

    def test_get_approved(self):
        """Should request APPROVED missions"""
        self.missions.get_list = MagicMock()
        self.missions.get_list.return_value = ['one', 'two']
        self.assertEqual(['one', 'two'], self.missions.get_approved())
        self.missions.get_list.assert_called_with("APPROVED")

    def test_get_claimed(self):
        """Should request CLAIMED missions"""
        self.missions.get_list = MagicMock()
        self.missions.get_list.return_value = ['one', 'two']
        self.assertEqual(['one', 'two'], self.missions.get_claimed())
        self.missions.get_list.assert_called_with("CLAIMED")

    def test_get_invisible(self):
        """Should try to get invisible missions"""
        self.missions.db.targets = [
            synack.db.models.Target(slug="34uhweow", codename="SOMEGUY"),
            synack.db.models.Target(slug="8935h3r4", codename="SOMEGAL")
        ]
        self.missions.targets.get_registered_summary = MagicMock()
        count_calls = [
            unittest.mock.call("PUBLISHED", "34uhweow"),
            unittest.mock.call("PUBLISHED", "8935h3r4")
        ]
        self.missions.get_count = MagicMock()
        self.missions.get_count.side_effect = [1, 1]

        self.missions.get_list = MagicMock()
        self.missions.get_list.side_effect = [[], ["real_mission"]]

        self.assertEqual(["SOMEGUY"], self.missions.get_invisible())
        self.missions.get_count.has_calls(count_calls)

    def test_get_in_review(self):
        """Should request FOR_REVIEW missions"""
        self.missions.get_list = MagicMock()
        self.missions.get_list.return_value = ['one', 'two']
        self.assertEqual(['one', 'two'],
                         self.missions.get_in_review())
        self.missions.get_list.assert_called_with("FOR_REVIEW")

    def test_get_count(self):
        """Should get the current number of published missions"""
        self.missions.api.request.return_value.status_code = 204
        self.missions.api.request.return_value.headers = {
            'x-count': 5
        }
        query = {
            "status": "PUBLISHED",
            "viewed": "false"
        }
        self.assertEqual(5, self.missions.get_count())
        self.missions.api.request.assert_called_with("HEAD",
                                                     "tasks/v1/tasks",
                                                     query=query)

    def test_get_count_status_uid(self):
        """Should get the current number of STATUS missions on TARGET"""
        self.missions.api.request.return_value.status_code = 204
        self.missions.api.request.return_value.headers = {
            'x-count': 10
        }
        query = {
            "status": "CLAIMED",
            "viewed": "false",
            "listingUid": "u4fh8"
        }
        self.assertEqual(10,
                         self.missions.get_count("CLAIMED", "u4fh8"))
        self.missions.api.request.assert_called_with("HEAD",
                                                     "tasks/v1/tasks",
                                                     query=query)

    def test_do_summarize(self):
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

        self.assertEqual(ret, self.missions.do_summarize(m))

    def test_get_list_defaults(self):
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
        self.missions.api.request.return_value.status_code = 200
        self.missions.api.request.return_value.json.return_value = ret
        self.assertEqual(ret, self.missions.get_list())
        self.missions.api.request.assert_called_with("GET",
                                                     "tasks/v2/tasks",
                                                     query=query)

    def test_get_list_mixup(self):
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
        self.missions.api.request.return_value.status_code = 200
        self.missions.api.request.return_value.json.return_value = ret
        self.assertEqual(ret,
                         self.missions.get_list("CLAIMED", 1, 2, 5,
                                                "49fh48g7"))
        self.missions.api.request.assert_called_with("GET",
                                                     "tasks/v2/tasks",
                                                     query=query)

    def test_get_list_multi_page(self):
        """Should get a list missions across multiple pages"""
        q1 = {
            "status": "CLAIMED",
            "perPage": 5,
            "page": 2,
            "viewed": "true",
            "listingUids": "49fh48g7"
        }
        self.missions.api.request.return_value.status_code = 200
        self.missions.api.request.return_value.json.side_effect = [
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
                         self.missions.get_list(max_pages=2,
                                                per_page=1))
        self.missions.api.request.has_calls(calls)
        self.assertEqual(2, self.missions.api.request.call_count)

    def test_do_interact(self):
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
        self.missions.api.request.return_value.status_code = 201
        self.assertEqual(ret, self.missions.do_interact(m, "CLAIM"))
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
        self.missions.api.request.has_calls(calls)

    def test_do_sort(self):
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

        self.assertEqual(ret, self.missions.do_sort(m))

    def test_do_sort_payout_low(self):
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

        self.assertEqual(ret, self.missions.do_sort(m, "payout-low"))

    def test_do_sort_shuffle(self):
        """Should sort by payout low"""
        m = [
            {"payout": {"amount": 10}},
            {"payout": {"amount": 40}},
            {"payout": {"amount": 30}},
            {"payout": {"amount": 20}},
            {"payout": {"amount": 50}},
        ]
        random.shuffle = MagicMock()
        self.missions.do_sort(m, "shuffle")
        random.shuffle.assert_called_with(m)

    def test_do_sort_reverse(self):
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

        self.assertEqual(ret, self.missions.do_sort(m, "reverse"))

    def test_do_claim(self):
        """Should send a CLAIM to do_interact"""
        self.missions.do_interact = MagicMock()
        self.missions.do_interact.return_value = ["ret"]
        self.assertEqual(["ret"], self.missions.do_claim(["yup"]))
        self.missions.do_interact.assert_called_with(["yup"], "CLAIM")

    def test_do_release(self):
        """Should send a DISCLAIM to do_interact"""
        self.missions.do_interact = MagicMock()
        self.missions.do_interact.return_value = ["ret"]
        self.assertEqual(["ret"], self.missions.do_release(["nope"]))
        self.missions.do_interact.assert_called_with(["nope"],
                                                     "DISCLAIM")

    def test_do_upload_evidences_safe(self):
        """Should replace current text with template if < 20 characters"""
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
        self.missions.templates.get_template = MagicMock()
        self.missions.templates.get_template.return_value = template
        self.missions.get_evidences = MagicMock()
        self.missions.get_evidences.return_value = curr
        self.missions.api.request = MagicMock()
        self.missions.api.request.return_value.status_code = 200
        self.missions.api.request.return_value.json.return_value = {}
        path = 'tasks/v2/tasks/2uthgr/evidences'
        self.missions.do_upload_evidences(mission)
        self.missions.api.request.assert_called_with('PATCH', path,
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
        self.missions.templates.get_template = MagicMock()
        self.missions.templates.get_template.return_value = template
        self.missions.get_evidences = MagicMock()
        self.missions.get_evidences.return_value = curr
        self.missions.api.request = MagicMock()
        self.missions.api.request.return_value.status_code = 200
        self.missions.api.request.return_value.json.return_value = {}
        self.missions.do_upload_evidences(mission)
        self.missions.api.request.assert_not_called()

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
        self.missions.api.request = MagicMock()
        self.missions.api.request.return_value.status_code = 200
        self.missions.api.request.return_value.json.return_value = {}
        path = "tasks/v2/tasks/eugtgowery8t/evidences"
        self.assertEqual(ret, self.missions.get_evidences(m))
        self.missions.api.request.assert_called_with("GET", path)
