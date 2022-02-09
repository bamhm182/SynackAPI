"""test_targets.py

Tests for the Synack Target APIs

=== NOTE ===
ALL potentially sensitive variables here is FAKE, and NOT real API data!
Values SHOULD represent exactly what real data would look like.
Types MUST represent the exact types of real data.
"""

import sys
import os
import pprint
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402

target = {
    "averagePayout": [923.16],
    "category": [{
        "id": 1,
        "name": "Web Application"
    }],
    "codename": ["SLAPPYMONKEY"],
    "dateUpdated": [1634815246],
    "end_date": [1641564125],
    "isActive": [True],
    "isNew": [True],
    "isRegistered": [True],
    "isUpdated": [True],
    "lastSubmitted": [1638645124],
    "name": ["Some Company Asset"],
    "organization": [{
        "name": "Some Company",
        "slug": "pjflgbv"
    }],
    "outage_windows": [[
        {
            "end_date": [1635612345],
            "is_window_active": [True],
            "options": {
                "days": [[0, 6]],
                "frequency": ["recurring"]
            },
            "outage_ends_on": [1641345123],
            "outage_starts_on": [1641341000],
            "start_date": [1634894216]
        }
    ]],
    "slug": ["wfglmatfptj"],
    "srt_notes": ["Please don't do dumb things"],
    "start_date": [1634816524],
    "vulnerability_discovery": [True],
    "workspace_access_missing": [False]
}


class TargetsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ans = input("These tests run against the live Synack API " +
                    "to easily identify changes.\n" +
                    "If you are sure you intend to run these, enter 'yes': ")
        if ans != 'yes' and ans != 'y':
            exit()
        cls.h = synack.Handler()

    def test_target_list_parameters(self):
        """Should have the same target list parameters"""
        ret = self.h.targets.get_unregistered()
        for t in ret:
            pp = pprint.pformat(t)
            for k in t.keys():
                types = [type(v) for v in target[k]]
                err = f"{k} : Real={t[k]} : Mock={target[k]}"
                self.assertTrue(type(t[k]) in types, err)

            prop_count = len(target.keys())
            self.assertEqual(prop_count, len(t.keys()), pp)
