"""test_missions.py

Tests for the Synack Missions APIs

NOTE: ALL potentially sensitive variables in the mock returned variable are 100% FAKE. I am not about to leak data here.
Additionally, values SHOULD, but may not represent exactly what real data would look like. I am only testing types
"""

import datetime
import os
import pprint
import random
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

from src import synack
from unittest.mock import MagicMock

mission = {
    "attackTypes": [
        ["Bad Juju"]
    ],
    "assetTypes": [["web"]],
    "assignee": [None, "wfugmlu"],
    "batchId": ["f4e56dc9-1e95-4abf-ba84-d24f7ee71a1b"],
    "campaignName": ["Some Missions - Security Vulns"],
    "campaignUid": ["1c6b09d2-df24-4c6e-898c-f28c1a3a84cf"],
    "canEditResponse": [True],
    "categories": [["Some Category"]],
    "claimedOn": ["2022-01-10T01:25:45.123Z"],
    "completedOn": ["2022-01-10T02:21:16.416Z"],
    "createdBy": [""],
    "createdOn": ["2021-11-15T15:25:42.456Z"],
    "credits": [0],
    "cwe": [["456"]],
    "deactivatedOn": [None, "2021-11-15T15:15:15.123Z"],
    "definitionId": ["5f532406-8f04-49bb-a64d-57fb59a31c3c"],
    "description": ["This is the description of the mission"],
    "hasBeenViewed": [True],
    "id": ["a6cd7e86-0855-4a9d-b9ff-d12ce79d5402"],
    "isAssigneeCurrentUser": [True],
    "listingCodename": ["MURTLETURTLE"],
    "listingUid": ["wjlrtpug"],
    "maxCompletionTimeInSecs": [86400],
    "modifiedBy": [""],
    "modifiedOn": ["2022-01-22T04:12:26Z"],
    "organizationCodename": ["Some Company"],
    "organizationUid": ["flypgvjt"],
    "pausedDurationInSecs": [0],
    "payout": [{
        "amount": [100],
        "currency": ["USD"]
    }],
    "position": [0],
    "publishedOn": ["2022-01-10T01:25:44.975Z"],
    "response": [""],
    "responseType": ["YES_NO"],
    "reviewedOn": ["2022-01-10T16:15:14.123Z"],
    "reviewer": [""],
    "scope": ["Some scope definition"],
    "status": ["APPROVED"],
    "structuredResponse": ["no"],
    "sv": [["123"]],
    "taskGroup": [""],
    "taskTemplateUid": ["d3141e91-d1be-46d9-864d-94640219afe7"],
    "taskType": ["MISSION"],
    "title": ["Some Mission"],
    "validResponses": [[
        {
            "label": "No - customer will see this mission marked as 'Passed'",
            "value": "no"
        }
    ]],
    "validatedOn": ["2022-01-10T15:16:17.123Z"],
    "version": [22],
}

class MissionsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ans = input("These tests run against the live Synack API to easily identify changes.\n" +
                    "If you are sure you intend to run these, enter 'yes': ")
        if ans != 'yes' and ans != 'y':
            exit()
        cls.h = synack.Handler()

    def test_mission_parameters(self):
        """Should have the same mission parameters"""
        ret = self.h.missions.get_approved_missions()
        for m in ret:
            pp = pprint.pformat(m)
            for k in m.keys():
                types = [type(v) for v in mission[k]]
                self.assertTrue(type(m[k]) in types, f"{k} : Real={m[k]} : Mock={mission[k]}")
            self.assertTrue(m["assetTypes"][0] in ["web", "host", "mobile"])
            self.assertTrue(type(m["assetTypes"][0]) in [str])
            self.assertTrue(type(m["validResponses"][0]) in [dict])
            self.assertTrue(type(m["validResponses"][0]["label"]) in [str])
            self.assertTrue(type(m["validResponses"][0]["value"]) in [str])
            self.assertTrue(type(m["payout"]["amount"]) in [int])
            self.assertTrue(type(m["payout"]["currency"]) in [str])

            prop_count = len(mission.keys())

            if m["taskType"] in ["MISSION"]:
                prop_count -= len(["sv", "cwe", "categories"])
                if m.get('categories'):
                    self.assertTrue(type(m["categories"][0]) in [str])
                    prop_count += len(["categories"]) 
                self.assertEqual(prop_count, len(m.keys()), pp)
            elif m["taskType"] in ["SV2M"]:
                prop_count -= len(["attackTypes", "categories"])
                self.assertTrue(type(m["sv"][0]) in [str])
                self.assertTrue(type(m["cwe"][0]) in [str])
                self.assertEqual(prop_count, len(m.keys()), pp)
