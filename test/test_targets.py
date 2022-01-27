"""test_Targets.py

Tests for the _Targets.py Targets Class
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

from src import synack
from unittest.mock import MagicMock


class TargetsTestCase(unittest.TestCase):
    def setUp(self):
        synack.Handler = MagicMock()
        self.targets = synack.Targets(synack.Handler())

    def test_get_assessments_all_passed(self):
        """Should return a list of passed assessments"""
        assessments = [
            {
                "category_name": "Cat1",
                "category_id": "1",
                "written_assessment": {
                    "passed": True
                },
                "practical_assessment": {
                    "passed": True
                }
            },
            {
                "category_name": "Cat2",
                "category_id": "2",
                "written_assessment": {
                    "passed": True
                },
                "practical_assessment": {
                    "passed": True
                }
            }
        ]
        ret = [{'name': 'Cat1', 'id': '1'}, {'name': 'Cat2', 'id': '2'}]
        self.targets.handler.api.request.return_value.status_code = 200
        self.targets.handler.api.request.return_value.json.return_value = assessments
        self.assertEqual(ret, self.targets.get_assessments())

    def test_get_assessments_not_all_passed(self):
        """Should not include failed or untaken assessments"""
        assessments = [
            {
                "category_name": "Cat1",
                "category_id": "1",
                "written_assessment": {
                    "passed": False
                },
                "practical_assessment": {
                    "passed": True
                }
            },
            {
                "category_name": "Cat2",
                "category_id": "2",
                "written_assessment": {
                    "passed": True
                },
                "practical_assessment": {
                    "passed": False
                }
            }
        ]
        self.targets.handler.api.request.return_value.status_code = 200
        self.targets.handler.api.request.return_value.json.return_value = assessments
        self.assertEqual([], self.targets.get_assessments())

    def test_get_codename_from_slug(self):
        """Should return a codename for a given slug"""
        self.targets.handler.db.known_targets = {
            "qwfars": {
                "codename": "SLOPPYSLUG"
            }
        }
        self.assertEqual("SLOPPYSLUG", self.targets.get_codename_from_slug("qwfars"))

    def test_get_codename_from_slug_no_targets(self):
        """Should update the known_targets if empty"""
        self.targets.handler.db.known_targets = dict()
        self.targets.get_registered_summary = MagicMock()
        self.targets.get_registered_summary.return_value = {
            "qwfars": {
                "codename": "SLOPPYSLUG"
            }
        }
        self.assertEqual("SLOPPYSLUG", self.targets.get_codename_from_slug("qwfars"))
        self.targets.get_registered_summary.assert_called_with()

    def test_get_current_target(self):
        """Should make a request to get the currently selected target"""
        self.targets.handler.api.request.return_value.status_code = 200
        self.targets.handler.api.request.return_value.json.return_value = {
            "pending_slug": "-1",
            "slug": "qwfars",
            "status": "connected"
        }
        self.targets.get_codename_from_slug = MagicMock()
        self.targets.get_codename_from_slug.return_value = "SLOPPYSLUG"
        out = {
            "slug": "qwfars",
            "codename": "SLOPPYSLUG",
            "status": "Connected"
        }
        self.assertEqual(out, self.targets.get_current_target())

    def test_get_current_target_pending(self):
        """Should return the pending target if one is pending"""
        self.targets.handler.api.request.return_value.status_code = 200
        self.targets.handler.api.request.return_value.json.return_value = {
            "pending_slug": "qwfars",
            "slug": "",
            "status": ""
        }
        self.targets.get_codename_from_slug = MagicMock()
        self.targets.get_codename_from_slug.return_value = "SLOPPYSLUG"
        out = {
            "slug": "qwfars",
            "codename": "SLOPPYSLUG",
            "status": "Connecting"
        }
        self.assertEqual(out, self.targets.get_current_target())

    def test_get_registered_summary(self):
        """Should make a request to get basic info about registered targets"""
        t1 = {
            "id": "qwfars",
            "codename": "SLOPPYSLUG",
            "organization_id": "89yefds",
            "activated_at": 1633640638,
            "name": "Bob's Slug Hut",
            "category": {
                "id": 1,
                "name": "Web Application"
            },
            "outage_windows": [],
            "vulnerability_discovery": True
        }
        self.targets.handler.api.request.return_value.status_code = 200
        self.targets.handler.api.request.return_value.json.return_value = [t1]
        out = {
            "qwfars": t1
        }
        self.assertEqual(out, self.targets.get_registered_summary())
        self.targets.handler.api.request.assert_called_with('GET',
                                              'targets/registered_summary')

    def test_get_unregistered(self):
        """Should get a list unregistered targets"""
        self.targets.handler.db.assessments = [
            {
                "name": "web",
                "id": 1
            },
            {
                "name": "host",
                "id": 2
            }
        ]
        query = {
            'filter[primary]': 'unregistered',
            'filter[secondary]': 'all',
            'filter[industry]': 'all',
            'filter[category][]': [1,2]
        }
        self.targets.handler.api.request.return_value.status_code = 200
        unreg = [
            {
                "codename": "SLEEPYSLUG",
                "slug": "1o2h8o"
            }
        ]
        self.targets.handler.api.request.return_value.json.return_value = unreg
        self.assertEqual(unreg, self.targets.get_unregistered())
        self.targets.handler.api.request.assert_called_with("GET",
                                              "targets",
                                              query=query)

    def test_get_unregistered_assessments_empty(self):
        """Should get a list unregistered targets"""
        self.targets.get_assessments = MagicMock()
        self.targets.handler.db.assessments = [
        ]
        query = {
            'filter[primary]': 'unregistered',
            'filter[secondary]': 'all',
            'filter[industry]': 'all',
            'filter[category][]': []
        }
        self.targets.handler.api.request.return_value.status_code = 200
        unreg = []
        self.targets.handler.api.request.return_value.json.return_value = unreg
        self.assertEqual(unreg, self.targets.get_unregistered())
        self.targets.get_assessments.assert_called_with()
        self.targets.handler.api.request.assert_called_with("GET",
                                              "targets",
                                              query=query)

    def test_do_register_all(self):
        """Should register each unregistered target"""
        self.targets.get_unregistered = MagicMock()
        unreg = [
            {
                "codename": "SLEEPYSLUG",
                "slug": "1o2h8o"
            },
            {
                "codename": "SLEEPYWALRUS",
                "slug": "82h934"
            }
        ]
        calls = [
            unittest.mock.call("POST",
                               "targets/1o2h8o/signup",
                               data='{"ResearcherListing":{"terms":1}}'),
            unittest.mock.call("POST",
                               "targets/82h934/signup",
                               data='{"ResearcherListing":{"terms":1}}')
        ]
        self.targets.get_unregistered.return_value = unreg
        self.targets.handler.api.request.return_value.status_code = 200
        self.assertEqual(unreg, self.targets.do_register_all())
        self.targets.handler.api.request.assert_has_calls(calls)

    def test_do_register_all_many(self):
        """Should call itself again if it has determined the page was full"""
        self.targets.get_unregistered = MagicMock()
        t = {
            "codename": "SLEEPYSLUG",
            "slug": "1o2h8o"
        }
        unreg = []
        for i in range(0,15):
            unreg.append(t)
        self.targets.get_unregistered.side_effect = [unreg, [t, t]]
        self.targets.handler.api.request.return_value.status_code = 200
        self.assertEqual(17, len(self.targets.do_register_all()))
