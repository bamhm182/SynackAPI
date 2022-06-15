"""test_Targets.py

Tests for the Targets Plugin
"""

import os
import sys
import unittest

from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402
from synack.db.models import Category, Target  # noqa: E402


class TargetsTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.targets = synack.plugins.Targets(self.state)
        self.targets.api = MagicMock()
        self.targets.db = MagicMock()
        self.maxDiff = None

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
        cat1 = synack.db.models.Category()
        self.targets.api.request.return_value.status_code = 200
        self.targets.api.request.return_value.json.return_value = assessments
        self.targets.db.categories = [cat1]
        self.assertEqual([cat1], self.targets.get_assessments())
        self.targets.db.add_categories.assert_called_with(assessments)

    def test_build_scope_web_burp(self):
        """Should build a Burp Suite Scope given a Synack API Scope"""
        scope = [
            {
                'raw_url': 'https://good.stuff.com',
                'status': 'in',
                'rules': [
                    {'rule': '*.stuff.com/*'},
                    {'rule': 'https://super.stuff.com/'},
                ]
            },
            {
                'raw_url': 'http://evil.stuff.com',
                'status': 'out',
                'rules': [
                    {'rule': '*.evil.stuff.com/login/*'},
                ]
            }
        ]
        expected = {
            'target': {
                'scope': {
                    'advanced_mode': 'true',
                    'exclude': [
                        {
                            'enabled': True,
                            'scheme': 'http',
                            'host': 'evil.stuff.com',
                            'file': '/login/'
                        }
                    ],
                    'include': [
                        {
                            'enabled': True,
                            'scheme': 'https',
                            'host': 'stuff.com',
                            'file': '/'
                        },
                        {
                            'enabled': True,
                            'scheme': 'https',
                            'host': 'super.stuff.com',
                            'file': '/'
                        }
                    ]
                }
            }
        }
        self.assertEqual(expected, self.targets.build_scope_web_burp(scope))

    def test_build_scope_web_urls(self):
        """Should build dictionaries of Web Application URLs given a Synack API Scope"""
        scope = [
            {
                'raw_url': 'https://good.stuff.com',
                'status': 'in'
            },
            {
                'raw_url': 'https://bad.stuff.com',
                'status': 'out'
            }
        ]
        expected = {
            'in': ['https://good.stuff.com'],
            'out': ['https://bad.stuff.com']
        }
        self.assertEqual(expected, self.targets.build_scope_web_urls(scope))

    def test_build_slug_from_codename(self):
        """Should return a slug for a given codename"""
        ret_targets = [Target(slug="qwerty")]
        self.targets.db.find_targets.return_value = ret_targets
        self.assertEqual("qwerty",
                         self.targets.build_slug_from_codename("qwerty"))
        self.targets.db.find_targets.assert_called_with(codename="qwerty")

    def test_build_slug_from_codename_no_targets(self):
        """Should update the targets if empty"""
        self.targets.db.find_targets.side_effect = [
            [],
            [Target(slug="qwerty")]
        ]
        calls = [
            unittest.mock.call(codename="CHONKEYMONKEY"),
            unittest.mock.call(codename="CHONKEYMONKEY")
        ]
        self.targets.get_registered_summary = MagicMock()

        slug = self.targets.build_slug_from_codename("CHONKEYMONKEY")
        self.assertEqual("qwerty", slug)
        self.targets.db.find_targets.assert_has_calls(calls)
        self.targets.get_registered_summary.assert_called_with()

    def test_build_codename_from_slug(self):
        """Should return a codename for a given slug"""
        ret_targets = [Target(codename="SLOPPYSLUG")]
        self.targets.db.find_targets.return_value = ret_targets
        self.assertEqual("SLOPPYSLUG",
                         self.targets.build_codename_from_slug("qwfars"))
        self.targets.db.find_targets.assert_called_with(slug="qwfars")

    def test_build_codename_from_slug_no_targets(self):
        """Should update the targets if empty"""
        self.targets.db.find_targets.side_effect = [
            [],
            [Target(codename="SLOPPYSLUG")]
        ]
        calls = [
            unittest.mock.call(slug="qwfars"),
            unittest.mock.call(slug="qwfars")
        ]
        self.targets.get_registered_summary = MagicMock()
        self.assertEqual("SLOPPYSLUG",
                         self.targets.build_codename_from_slug("qwfars"))
        self.targets.db.find_targets.assert_has_calls(calls)
        self.targets.get_registered_summary.assert_called_with()

    def test_get_connected(self):
        """Should make a request to get the currently selected target"""
        self.targets.api.request.return_value.status_code = 200
        self.targets.api.request.return_value.json.return_value = {
            "pending_slug": "-1",
            "slug": "qwfars",
            "status": "connected"
        }
        self.targets.build_codename_from_slug = MagicMock()
        self.targets.build_codename_from_slug.return_value = "SLOPPYSLUG"
        out = {
            "slug": "qwfars",
            "codename": "SLOPPYSLUG",
            "status": "Connected"
        }
        self.assertEqual(out, self.targets.get_connected())

    def test_get_connected_pending(self):
        """Should return the pending target if one is pending"""
        self.targets.api.request.return_value.status_code = 200
        self.targets.api.request.return_value.json.return_value = {
            "pending_slug": "qwfars",
            "slug": "",
            "status": ""
        }
        self.targets.build_codename_from_slug = MagicMock()
        self.targets.build_codename_from_slug.return_value = "SLOPPYSLUG"
        out = {
            "slug": "qwfars",
            "codename": "SLOPPYSLUG",
            "status": "Connecting"
        }
        self.assertEqual(out, self.targets.get_connected())

    def test_get_scope_for_host(self):
        """Should get the scope for a Host when given Host information"""
        self.targets.get_scope_host = MagicMock()
        self.targets.get_scope_host.return_value = 'HostScope'
        tgt = Target(category=1)
        self.targets.db.find_targets.return_value = [tgt]
        self.targets.db.categories = [Category(id=1, name='Host')]
        out = self.targets.get_scope(slug='1392g78yr')
        self.targets.db.find_targets.assert_called_with(slug='1392g78yr')
        self.targets.get_scope_host.assert_called_with(tgt)
        self.assertEquals(out, 'HostScope')

    def test_get_scope_for_web(self):
        """Should get the scope for a Host when given Web information"""
        self.targets.get_scope_web = MagicMock()
        self.targets.get_scope_web.return_value = 'WebScope'
        tgt = Target(category=2)
        self.targets.db.find_targets.return_value = [tgt]
        self.targets.db.categories = [Category(id=2, name='Web Application')]
        out = self.targets.get_scope(slug='1392g78yr')
        self.targets.db.find_targets.assert_called_with(slug='1392g78yr')
        self.targets.get_scope_web.assert_called_with(tgt)
        self.assertEquals(out, 'WebScope')

    def test_get_scope_host(self):
        """Should get the scope for a Host"""
        ips = ['1.1.1.1/32', '2.2.2.2/32']
        self.targets.api.request.return_value.status_code = 200
        self.targets.api.request.return_value.json.return_value = {
            'cidrs': ips
        }
        self.targets.db.find_targets.return_value = [Target(slug='213h89h3', codename='SASSYSQUIRREL')]
        out = self.targets.get_scope_host(codename='SASSYSQUIRREL')
        self.assertEqual(ips, out)
        self.targets.db.find_targets.assert_called_with(codename='SASSYSQUIRREL')
        self.targets.api.request.assert_called_with('GET', 'targets/213h89h3/cidrs?page=all')
        self.targets.api.request.return_value.json.assert_called()

    def test_get_scope_web(self):
        """Should get the scope for a Web Application"""
        self.targets.api.request.return_value.status_code = 200
        web_results = [{
            'web_results': 'yup these them!',
            'owners': [{
                'owner_uid': '213h89h3'
            }]
        }]
        self.targets.api.request.return_value.json.return_value = web_results
        tgt = Target(slug='213h89h3', organization='93g8eh8', codename='SASSYSQUIRREL')
        self.targets.db.find_targets.return_value = [tgt]
        out = self.targets.get_scope_web(codename='SASSYSQUIRREL')
        self.assertEqual(web_results, out)
        self.targets.db.find_targets.assert_called_with(codename='SASSYSQUIRREL')
        self.targets.api.request.assert_called_with('GET',
                                                    'asset/v1/organizations/93g8eh8/owners/listings/213h89h3/webapps')
        self.targets.api.request.return_value.json.assert_called()

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
        self.targets.api.request.return_value.status_code = 200
        self.targets.api.request.return_value.json.return_value = [t1]
        out = {
            "qwfars": t1
        }
        path = 'targets/registered_summary'
        self.assertEqual(out, self.targets.get_registered_summary())
        self.targets.api.request.assert_called_with('GET', path)

    def test_get_credentials(self):
        """Should get credentials for a given target"""
        target = Target(organization="qwewqe", slug="asdasd")
        self.targets.db.find_targets = MagicMock()
        self.targets.api = MagicMock()
        self.targets.db.find_targets.return_value = [target]
        self.targets.db.user_id = 'bobby'
        self.targets.api.request.return_value.status_code = 200
        self.targets.api.request.return_value.json.return_value = "json_return"

        url = 'asset/v1/organizations/qwewqe/owners/listings/asdasd/users/bobby/credentials'

        self.assertEqual("json_return",
                         self.targets.get_credentials(codename='SLEEPYSLUG'))
        self.targets.api.request.assert_called_with('POST', url)

    def test_get_unregistered(self):
        """Should get a list unregistered targets"""
        self.targets.db.categories = [
            Category(id=1, passed_practical=True,  passed_written=True),
            Category(id=2, passed_practical=True,  passed_written=True),
            Category(id=3, passed_practical=False, passed_written=False),
        ]
        query = {
            'filter[primary]': 'unregistered',
            'filter[secondary]': 'all',
            'filter[industry]': 'all',
            'filter[category][]': [1, 2]
        }
        self.targets.api.request.return_value.status_code = 200
        unreg = [
            {
                "codename": "SLEEPYSLUG",
                "slug": "1o2h8o"
            }
        ]
        self.targets.api.request.return_value.json.return_value = unreg
        self.assertEqual(unreg, self.targets.get_unregistered())
        self.targets.api.request.assert_called_with("GET",
                                                    "targets",
                                                    query=query)

    def test_get_unregistered_assessments_empty(self):
        """Should get a list of unregistered targets"""
        self.targets.get_assessments = MagicMock()
        self.targets.db.categories = []
        query = {
            'filter[primary]': 'unregistered',
            'filter[secondary]': 'all',
            'filter[industry]': 'all',
            'filter[category][]': []
        }
        self.targets.api.request.return_value.status_code = 200
        unreg = []
        self.targets.api.request.return_value.json.return_value = unreg
        self.assertEqual(unreg, self.targets.get_unregistered())
        self.targets.get_assessments.assert_called_with()
        self.targets.api.request.assert_called_with("GET",
                                                    "targets",
                                                    query=query)

    def test_set_registered(self):
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
        self.targets.api.request.return_value.status_code = 200
        self.assertEqual(unreg, self.targets.set_registered())
        self.targets.api.request.assert_has_calls(calls)

    def test_set_registered_many(self):
        """Should call itself again if it has determined the page was full"""
        self.targets.get_unregistered = MagicMock()
        t = {
            "codename": "SLEEPYSLUG",
            "slug": "1o2h8o"
        }
        unreg = []
        for i in range(0, 15):
            unreg.append(t)
        self.targets.get_unregistered.side_effect = [unreg, [t, t]]
        self.targets.api.request.return_value.status_code = 200
        self.assertEqual(17, len(self.targets.set_registered()))
