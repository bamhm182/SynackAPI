"""test_targets.py

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
        self.state._db = MagicMock()
        self.targets = synack.plugins.Targets(self.state)
        self.targets._api = MagicMock()
        self.targets._db = MagicMock()
        self.targets.scratchspace = MagicMock()
        self.maxDiff = None

    def test_build_codename_from_slug(self):
        """Should return a codename for a given slug"""
        ret_targets = [Target(codename="SLOPPYSLUG")]
        self.targets._db.find_targets.return_value = ret_targets
        self.assertEqual("SLOPPYSLUG",
                         self.targets.build_codename_from_slug("qwfars"))
        self.targets._db.find_targets.assert_called_with(slug="qwfars")

    def test_build_codename_from_slug_invalid(self):
        """Should return NONE if non-real slug"""
        self.targets._db.find_targets.return_value = []
        self.assertEqual("NONE",
                         self.targets.build_codename_from_slug("qwfars"))
        self.targets._db.find_targets.assert_called_with(slug="qwfars")

    def test_build_codename_from_slug_no_targets(self):
        """Should update the targets if empty"""
        self.targets._db.find_targets.side_effect = [
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
        self.targets._db.find_targets.assert_has_calls(calls)
        self.targets.get_registered_summary.assert_called_with()

    def test_build_scope_host_db(self):
        """Should build a scope that can be ingested into the Database given a Synack API Scope"""
        scope = [
            '10.0.0.0/31',
            '192.168.254.15'
        ]
        slug = 'b23iuub'
        expected = [
            {'target': slug, 'ip': '10.0.0.0'},
            {'target': slug, 'ip': '10.0.0.1'},
            {'target': slug, 'ip': '192.168.254.15'},
        ]
        self.assertEqual(expected, self.targets.build_scope_host_db(slug, scope))

    def test_build_scope_web_burp(self):
        """Should build a Burp Suite Scope given a Synack API Scope"""
        self.state.user_id = 'abc123'
        target = Target(codename='SLOPPYSLUG')
        scope = [
            {
                'listing': 'uqwheiuqwhe',
                'location': 'https://good.stuff.com',
                'status': 'in',
                'rule': '*.stuff.com/*',
            },
            {
                'listing': 'uqwheiuqwhe',
                'location': 'https://good.stuff.com',
                'status': 'in',
                'rule': 'https://super.stuff.com/'
            },
            {
                'listing': 'uqwheiuqwhe',
                'location': 'http://evil.stuff.com',
                'status': 'out',
                'rule': '*.evil.stuff.com/login/*'
            }
        ]
        expected = {
            'target': {
                'scope': {
                    'advanced_mode': 'true',
                    'exclude': [
                        {
                            'enabled': True,
                            'protocol': 'http',
                            'host': 'evil.stuff.com',
                            'file': '/login/'
                        }
                    ],
                    'include': [
                        {
                            'enabled': True,
                            'protocol': 'https',
                            'host': 'stuff.com',
                            'file': '/'
                        },
                        {
                            'enabled': True,
                            'protocol': 'https',
                            'host': 'super.stuff.com',
                            'file': '/'
                        }
                    ]
                }
            },
            'project_options': {'session_handling_rules': {'rules': [
                {
                    'actions': [
                        {
                            'add_if_not_present': 'true',
                            'enabled': 'true',
                            'name': 'X-Synack',
                            'type': 'set_header',
                            'value': 'abc123-SLOPPYSLUG'
                        }
                    ],
                    'description': 'Add X-Synack Header',
                    'enabled': 'true',
                    'exclude_from_scope': [],
                    'include_from_scope': [],
                    'named_params': [],
                    'restrict_scope_to_named_params': 'false',
                    'tools_scope': ['Target', 'Proxy', 'Scanner', 'Intruder', 'Repeater', 'Sequencer',
                                    'Burp AI', 'Extensions'],
                    'url_scope': 'suite',
                    'url_scope_advanced_mode': 'true'
                }
            ]}}
        }
        self.assertEqual(expected, self.targets.build_scope_web_burp(scope, target))

    def test_build_scope_web_db(self):
        """Should build a web scope that can be ingested into the Database"""
        scope = [
            {
                'listing': 'uqwheiuq',
                'location': 'https://good.stuff.com',
                'status': 'in',
                'rule': '*.good.stuff.com/*'
            },
            {
                'listing': 'uqwheiuq',
                'location': 'https://bad.stuff.com',
                'status': 'out',
                'rule': '*.bad.stuff.com/*'
            },
            {
                'listing': '21ye78r3hwe',
                'location': 'https://good.things.com',
                'status': 'in',
                'rule': '*.good.things.com/*'
            }
        ]
        expected = [
            {
                'target': 'uqwheiuq',
                'urls': [{
                    'url': 'https://good.stuff.com'
                }]
            },
            {
                'target': '21ye78r3hwe',
                'urls': [{
                    'url': 'https://good.things.com'
                }]
            }
        ]
        self.assertEqual(expected, self.targets.build_scope_web_db(scope))

    def test_build_slug_from_codename(self):
        """Should return a slug for a given codename"""
        ret_targets = [Target(slug="qwerty")]
        self.targets._db.find_targets.return_value = ret_targets
        self.assertEqual("qwerty",
                         self.targets.build_slug_from_codename("qwerty"))
        self.targets._db.find_targets.assert_called_with(codename="qwerty")

    def test_build_slug_from_codename_no_targets(self):
        """Should update the targets if empty"""
        self.targets._db.find_targets.side_effect = [
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
        self.targets._db.find_targets.assert_has_calls(calls)
        self.targets.get_registered_summary.assert_called_with()

    def test_get(self):
        """Should get a list of targets"""
        self.targets._db.categories = [
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
        self.targets._api.request.return_value.status_code = 200
        results = [
            {
                "codename": "SLEEPYSLUG",
                "slug": "1o2h8o"
            }
        ]
        self.targets._api.request.return_value.json.return_value = results
        self.assertEqual(results, self.targets.get_unregistered())
        self.targets._api.request.assert_called_with("GET",
                                                     "targets",
                                                     query=query)

    def test_get_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._db.categories = [Category(id=1, passed_practical=True, passed_written=True)]
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.get()
        self.targets._auth.get_api_token.assert_called_once()

    def test_get_assessments_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.get_assessments()
        self.targets._auth.get_api_token.assert_called_once()

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
        self.targets. _api.request.return_value.status_code = 200
        self.targets. _api.request.return_value.json.return_value = assessments
        self.targets._db.categories = [cat1]
        self.assertEqual([cat1], self.targets.get_assessments())
        self.targets._db.add_categories.assert_called_with(assessments)

    def test_get_assessments_empty(self):
        """Should get a list of unregistered targets"""
        self.targets.get_assessments = MagicMock()
        self.targets._db.categories = []
        query = {
            'filter[primary]': 'unregistered',
            'filter[secondary]': 'all',
            'filter[industry]': 'all',
            'filter[category][]': []
        }
        self.targets._api.request.return_value.status_code = 200
        results = []
        self.targets._api.request.return_value.json.return_value = results
        self.assertEqual(results, self.targets.get_unregistered())
        self.targets.get_assessments.assert_called_with()
        self.targets._api.request.assert_called_with("GET",
                                                     "targets",
                                                     query=query)

    def test_get_assets(self):
        """Should return a list of assets for a currently connected target"""
        self.targets.get_connected = MagicMock()
        self.targets.get_connected.return_value = {'codename': 'TURBULENTTORTOISE', 'slug': '327h8iw'}
        self.targets._db.find_targets.return_value = [Target(slug='327h8iw')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.text = 'rettext'
        self.targets._api.request.return_value.json.return_value = 'retjson'
        self.assertEqual('retjson', self.targets.get_assets())
        self.targets._api.request.assert_called_with('GET',
                                                     'asset/v2/assets?listingUid%5B%5D=327h8iw&scope%5B%5D=in' +
                                                     '&scope%5B%5D=discovered&sort%5B%5D=location&active=true' +
                                                     '&sortDir=asc&page=1&perPage=5000')

    def test_get_assets_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.get_assets(target=Target(slug='327h8iw'))
        self.targets._auth.get_api_token.assert_called_once()

    def test_get_assets_non_defaults(self):
        """Should return a list of assets given information to query"""
        self.targets._db.find_targets.return_value = [Target(codename='TURBULENTTORTOISE', slug='327h8iw')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.text = 'rettext'
        self.targets._api.request.return_value.json.return_value = 'retjson'
        self.assertEqual('retjson', self.targets.get_assets(codename='TURBULENTTORTOISE',
                                                            asset_type='blah',
                                                            host_type='cidr',
                                                            active='false',
                                                            scope='secret',
                                                            sort='loc',
                                                            sort_dir='desc',
                                                            page=3,
                                                            perPage=50,
                                                            organization_uid='uiehqw'))
        self.targets._api.request.assert_called_with('GET',
                                                     'asset/v2/assets?listingUid%5B%5D=327h8iw' +
                                                     '&organizationUid%5B%5D=uiehqw&assetType%5B%5D=blah' +
                                                     '&hostType%5B%5D=cidr&scope%5B%5D=secret' +
                                                     '&sort%5B%5D=loc&active=false&sortDir=desc&page=3&perPage=50')

    def test_get_attachments_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.get_attachments(target=Target(slug='u2ire'))
        self.targets._auth.get_api_token.assert_called_once()

    def test_get_attachments_current(self):
        """Should return a list of attachments based on currently selected target"""
        attachments = [
            {
                "listing_id": "12uib",
                "url": "https://www.download.com/uh1g23ri",
                "filename": "file1.txt",
                "created_at": 1667840052,
                "updated_at": 1667849178,
            }
        ]
        self.targets.get_connected = MagicMock()
        self.targets.get_connected.return_value = {'codename': 'TASTYTACO', 'slug': 'u2ire'}
        self.targets._db.find_targets = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = attachments
        self.assertEqual(self.targets.get_attachments(), attachments)
        self.targets._api.request.assert_called_with('GET', 'targets/u2ire/resources')

    def test_get_attachments_slug(self):
        """Should return a list of attachments given a slug"""
        attachments = [
            {
                "listing_id": "12uib",
                "url": "https://www.download.com/uh1g23ri",
                "filename": "file1.txt",
                "created_at": 1667840052,
                "updated_at": 1667849178,
            }
        ]
        self.targets._db.find_targets = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = attachments
        self.assertEqual(self.targets.get_attachments(slug='u2ire'), attachments)
        self.targets._api.request.assert_called_with('GET', 'targets/u2ire/resources')

    def test_get_attachments_target(self):
        """Should return a list of attachments given a Target"""
        attachments = [
            {
                "listing_id": "12uib",
                "url": "https://www.download.com/uh1g23ri",
                "filename": "file1.txt",
                "created_at": 1667840052,
                "updated_at": 1667849178,
            }
        ]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = attachments
        self.assertEqual(self.targets.get_attachments(target=Target(slug='u2ire')), attachments)
        self.targets._api.request.assert_called_with('GET', 'targets/u2ire/resources')

    def test_get_connected(self):
        """Should make a request to get the currently selected target"""
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = {
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

    def test_get_connected_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.get_connected()
        self.targets._auth.get_api_token.assert_called_once()

    def test_get_connected_disconnected(self):
        """Should report Not Connected when not connected to a target"""
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = {
            "slug": "",
            "status": "connected"
        }
        self.targets.build_codename_from_slug = MagicMock()
        self.targets.build_codename_from_slug.return_value = "NONE"
        out = {
            "slug": "",
            "codename": "NONE",
            "status": "Not Connected"
        }
        self.assertEqual(out, self.targets.get_connected())

    def test_get_connections(self):
        """Should return a summary of the lifetime and current connections given a slug"""
        connections = {
            "lifetime_connections": 200,
            "current_connections": 5
        }
        return_data = {
            "listing_id": "u2ire",
            "type": "connections",
            "value": {
                "lifetime_connections": 200,
                "current_connections": 5
            }
        }
        self.targets._db.find_targets = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = return_data
        self.assertEqual(self.targets.get_connections(slug='u2ire'), connections)
        self.targets._api.request.assert_called_with('GET', 'listing_analytics/connections',
                                                     query={"listing_id": "u2ire"})

    def test_get_connections_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.get_connections(slug='u2ire')
        self.targets._auth.get_api_token.assert_called_once()

    def test_get_connections_no_args(self):
        """Should return a summary of the lifetime and current connections if no args provided"""
        connections = {
            "lifetime_connections": 200,
            "current_connections": 5
        }
        return_data = {
            "listing_id": "u2ire",
            "type": "connections",
            "value": {
                "lifetime_connections": 200,
                "current_connections": 5
            }
        }
        self.targets._db.find_targets = MagicMock()
        self.targets.get_connected = MagicMock()
        self.targets.get_connected.return_value = {'codename': 'TIREDTIGER', 'slug': 'u2ire'}
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = return_data
        self.assertEqual(self.targets.get_connections(), connections)
        self.targets.get_connected.assert_called_with()
        self.targets._api.request.assert_called_with('GET', 'listing_analytics/connections',
                                                     query={"listing_id": "u2ire"})

    def test_get_credentials(self):
        """Should get credentials for a given target"""
        target = Target(organization="qwewqe", slug="asdasd")
        self.targets._db.find_targets = MagicMock()
        self.targets._api = MagicMock()
        self.targets._db.find_targets.return_value = [target]
        self.targets._db.user_id = 'bobby'
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = "json_return"
        self.targets._state.user_id = 'bobby'

        url = 'asset/v1/organizations/qwewqe/owners/listings/asdasd/users/bobby/credentials'

        self.assertEqual("json_return",
                         self.targets.get_credentials(codename='SLEEPYSLUG'))
        self.targets._api.request.assert_called_with('POST', url)

    def test_get_credentials_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._db.find_targets.return_value = [Target(organization='qwewqe', slug='asdasd')]
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.get_credentials(codename='SLEEPYSLUG')
        self.targets._auth.get_api_token.assert_called_once()

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
        self.targets._db.categories = [Category(id=1)]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = [t1]
        out = {
            "qwfars": t1
        }
        path = 'targets/registered_summary'
        self.assertEqual(out, self.targets.get_registered_summary())
        self.targets._api.request.assert_called_with('GET', path)

    def test_get_registered_summary_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._db.categories = [Category(id=1)]
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.get_registered_summary()
        self.targets._auth.get_api_token.assert_called_once()

    def test_get_registered_summary_no_categories(self):
        """Should call get_assessments if categories table is empty"""
        self.targets._db.categories = []
        self.targets.get_assessments = MagicMock()
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = []
        self.targets.get_registered_summary()
        self.targets.get_assessments.assert_called_once()

    def test_get_scope_for_host(self):
        """Should get the scope for a Host when given Host information"""
        self.targets.get_scope_host = MagicMock()
        self.targets.get_scope_host.return_value = 'HostScope'
        tgt = Target(category=1)
        self.targets._db.find_targets.return_value = [tgt]
        self.targets._db.categories = [Category(id=1, name='Host')]
        out = self.targets.get_scope(slug='1392g78yr')
        self.targets._db.find_targets.assert_called_with(slug='1392g78yr')
        self.targets.get_scope_host.assert_called_with(tgt)
        self.assertEqual(out, 'HostScope')

    def test_get_scope_for_web(self):
        """Should get the scope for a Host when given Web information"""
        self.targets.get_scope_web = MagicMock()
        self.targets.get_scope_web.return_value = 'WebScope'
        tgt = Target(category=2)
        self.targets._db.find_targets.return_value = [tgt]
        self.targets._db.categories = [Category(id=2, name='Web Application')]
        out = self.targets.get_scope(slug='1392g78yr')
        self.targets._db.find_targets.assert_called_with(slug='1392g78yr')
        self.targets.get_scope_web.assert_called_with(tgt)
        self.assertEqual(out, 'WebScope')

    def test_get_scope_host(self):
        """Should get the scope for a Host"""
        ips = {'1.1.1.1/32', '2.2.2.2/32'}
        self.targets.get_assets = MagicMock()
        self.targets.get_assets.return_value = [
            {
                'active': True,
                'location': '1.1.1.1/32'
            },
            {
                'active': True,
                'location': '2.2.2.2/32'
            }
        ]
        self.targets._db.find_targets.return_value = [Target(slug='213h89h3', codename='SASSYSQUIRREL')]
        out = self.targets.get_scope_host(codename='SASSYSQUIRREL')
        self.assertEqual(ips, out)
        self.targets._db.find_targets.assert_called_with(codename='SASSYSQUIRREL')

    def test_get_scope_host_current(self):
        """Should get the scope for the currenly connected Host if not specified"""
        ips = {'1.1.1.1/32', '2.2.2.2/32'}
        self.targets.get_connected = MagicMock()
        self.targets.get_connected.return_value = {'slug': '213h89h3'}
        self.targets.get_assets = MagicMock()
        self.targets.get_assets.return_value = [
            {
                'active': True,
                'location': '1.1.1.1/32'
            },
            {
                'active': True,
                'location': '2.2.2.2/32'
            }
        ]
        self.targets._db.find_targets.return_value = [Target(slug='213h89h3', codename='SASSYSQUIRREL')]
        out = self.targets.get_scope_host()
        self.assertEqual(ips, out)
        self.targets.get_connected.assert_called_with()
        self.targets._db.find_targets.assert_called_with(slug='213h89h3')

    def test_get_scope_host_not_ip(self):
        """Should get the scope for a Host"""
        ips = {'1.1.1.1/32'}
        self.targets.get_assets = MagicMock()
        self.targets.get_assets.return_value = [
            {
                'active': True,
                'location': '1.1.1.1/32'
            },
            {
                'active': True,
                'location': '8675309'
            }
        ]
        self.targets._db.find_targets.return_value = [Target(slug='213h89h3', codename='SASSYSQUIRREL')]
        out = self.targets.get_scope_host(codename='SASSYSQUIRREL')
        self.assertEqual(ips, out)
        self.targets._db.find_targets.assert_called_with(codename='SASSYSQUIRREL')

    def test_get_scope_no_provided(self):
        """Should get the scope for the currently connected target if none is specified"""
        self.targets.get_connected = MagicMock()
        self.targets.get_connected.return_value = {'slug': 'test'}
        self.targets._db.find_targets.return_value = None
        self.targets.get_scope()
        self.targets.get_connected.assert_called_with()
        self.targets._db.find_targets.assert_called_with(slug='test')

    def test_get_scope_web(self):
        """Should get the scope for a Web Application"""
        self.targets.build_scope_web_burp = MagicMock()
        self.targets.build_scope_web_burp.return_value = 'burp_web_scope'
        scope = [{
            'listing': 'uewqhuiewq',
            'location': 'https://good.things.com',
            'rule': '*.good.things.com/*',
            'status': 'in'
        }]
        self.targets.get_assets = MagicMock()
        self.targets.get_assets.return_value = [
            {
                'active': True,
                'listings': [{'listingUid': 'uewqhuiewq', 'scope': 'in'}],
                'location': 'https://good.things.com (https://good.things.com)',
                'scopeRules': [
                    {'rule': '*.good.things.com/*'}
                ]
            }
        ]
        tgt = Target(slug='213h89h3', organization='93g8eh8', codename='SASSYSQUIRREL')
        self.targets._db.find_targets.return_value = [tgt]
        self.targets._state.use_scratchspace = True
        out = self.targets.get_scope_web(codename='SASSYSQUIRREL')
        self.assertEqual(scope, out)
        self.targets.build_scope_web_burp.assert_called_with(scope, tgt)
        self.targets._db.find_targets.assert_called_with(codename='SASSYSQUIRREL')
        self.targets.get_assets.assert_called_with(target=tgt, active='true', asset_type='webapp')

    def test_get_scope_web_current(self):
        """Should get the scope for the currently connected Web Application if not specified"""
        self.targets.build_scope_web_burp = MagicMock()
        self.targets.build_scope_web_burp.return_value = 'burp_formatted_scope'
        scope = [{
            'listing': 'uewqhuiewq',
            'location': 'https://good.things.com',
            'rule': '*.good.things.com/*',
            'status': 'in'
        }]
        self.targets.get_connected = MagicMock()
        self.targets.get_connected.return_value = {'slug': '93g8eg8'}
        self.targets.get_assets = MagicMock()
        self.targets.get_assets.return_value = [
            {
                'active': True,
                'listings': [{'listingUid': 'uewqhuiewq', 'scope': 'in'}],
                'location': 'https://good.things.com (https://good.things.com)',
                'scopeRules': [
                    {'rule': '*.good.things.com/*'}
                ]
            }
        ]
        tgt = Target(slug='213h89h3', organization='93g8eh8', codename='SASSYSQUIRREL')
        self.targets._db.find_targets.return_value = [tgt]
        self.targets._state.use_scratchspace = True
        out = self.targets.get_scope_web()
        self.assertEqual(scope, out)
        self.targets.build_scope_web_burp.assert_called_with(scope, tgt)
        self.targets.get_connected.assert_called_with()
        self.targets._db.find_targets.assert_called_with(slug='93g8eg8')
        self.targets.get_assets.assert_called_with(target=tgt, active='true', asset_type='webapp')

    def test_get_submissions(self):
        """Should return the accepted vulnerabilities for a target given a slug"""
        return_data = {
            "listing_id": "u2ire",
            "type": "categories",
            "value": [{
                "categories": ["Authorization/Permissions", "Access/Privacy Control Violation"],
                "exploitable_locations": [{
                        "type": "url",
                        "value": "https://example.com/index.html",
                        "created_at": 1625643431,
                        "status": "fixed"
                    }
                ]
            }]
        }
        self.targets._db.find_targets = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = return_data
        self.assertEqual(self.targets.get_submissions(slug='u2ire'), return_data["value"])
        self.targets._api.request.assert_called_with('GET', 'listing_analytics/categories',
                                                     query={"listing_id": "u2ire", "status": "accepted"})

    def test_get_submissions_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.get_submissions(slug='u2ire')
        self.targets._auth.get_api_token.assert_called_once()

    def test_get_submissions_invalid_status(self):
        """Should return an empty dictionary if status is invalid"""
        return_data = {
            "listing_id": "u2ire",
            "type": "categories",
            "value": [{
                "categories": ["Authorization/Permissions", "Access/Privacy Control Violation"],
                "exploitable_locations": [{
                        "type": "url",
                        "value": "https://example.com/index.html",
                        "created_at": 1625643431,
                        "status": "fixed"
                    }
                ]
            }]
        }
        self.targets._db.find_targets = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = return_data
        self.assertEqual(self.targets.get_submissions(slug='u2ire', status="bad_status"), [])

    def test_get_submissions_no_slug(self):
        """Should return info on currently connected target if slug not provided"""
        return_data = {
            "listing_id": "u2ire",
            "type": "categories",
            "value": [{
                "categories": ["Authorization/Permissions", "Access/Privacy Control Violation"],
                "exploitable_locations": [{
                        "type": "url",
                        "value": "https://example.com/index.html",
                        "created_at": 1625643431,
                        "status": "fixed"
                    }
                ]
            }]
        }
        self.targets._db.find_targets = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = return_data
        self.targets.get_connected = MagicMock()
        self.targets.get_connected.return_value = {"slug": "u2ire"}
        self.assertEqual(self.targets.get_submissions(), return_data["value"])
        self.targets._api.request.assert_called_with('GET', 'listing_analytics/categories',
                                                     query={"listing_id": "u2ire", "status": "accepted"})

    def test_get_submissions_rejected(self):
        """Should return the accepted vulnerabilities for a target given a slug"""
        return_data = {
            "listing_id": "u2ire",
            "type": "categories",
            "value": [{
                "categories": ["Authorization/Permissions", "Access/Privacy Control Violation"],
                "exploitable_locations": [{
                        "type": "url",
                        "value": "https://example.com/index.html",
                        "created_at": 1625643431,
                        "status": "pending"
                    }
                ]
            }]
        }
        self.targets._db.find_targets = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = return_data
        self.assertEqual(self.targets.get_submissions(status="rejected", slug='u2ire'), return_data["value"])
        self.targets._api.request.assert_called_with('GET', 'listing_analytics/categories',
                                                     query={"listing_id": "u2ire", "status": "rejected"})

    def test_get_submissions_summary(self):
        """Should return the amount of lifetime submissions given a slug"""
        return_data = {
            "listing_id": "u2ire",
            "type": "submissions",
            "value": 35
        }
        self.targets._db.find_targets = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = return_data
        self.assertEqual(self.targets.get_submissions_summary(slug='u2ire'), 35)
        self.targets._api.request.assert_called_with('GET', 'listing_analytics/submissions',
                                                     query={"listing_id": "u2ire"})

    def test_get_submissions_summary_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.get_submissions_summary(slug='u2ire')
        self.targets._auth.get_api_token.assert_called_once()

    def test_get_submissions_summary_hours(self):
        """Should return the amount of submissions in the last x hours given a slug"""
        return_data = {
            "listing_id": "u2ire",
            "type": "submissions",
            "value": 5
        }
        self.targets._db.find_targets = MagicMock()
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = return_data
        self.assertEqual(self.targets.get_submissions_summary(hours_ago=48, slug='u2ire'), 5)
        self.targets._api.request.assert_called_with('GET', 'listing_analytics/submissions',
                                                     query={"listing_id": "u2ire", "period": "48h"})

    def test_get_submissions_summary_no_slug(self):
        """Should return the amount of lifetime submissions for current connected when no slug"""
        return_data = {
            "listing_id": "u2ire",
            "type": "submissions",
            "value": 35
        }
        self.targets._db.find_targets = MagicMock()
        self.targets.get_connected = MagicMock()
        self.targets.get_connected.return_value = {'slug': 'u2ire'}
        self.targets._db.find_targets.return_value = [Target(slug='u2ire')]
        self.targets._api.request.return_value.status_code = 200
        self.targets._api.request.return_value.json.return_value = return_data
        self.assertEqual(self.targets.get_submissions_summary(), 35)
        self.targets._api.request.assert_called_with('GET', 'listing_analytics/submissions',
                                                     query={"listing_id": "u2ire"})

    def test_get_unregistered(self):
        """Should query for unregistered targets"""
        results = [
            {'codename': 'SLEEPYSLUG', 'slug': '1283hi'}
        ]
        self.targets.get = MagicMock()
        self.targets.get.return_value = results
        self.assertEqual(results, self.targets.get_unregistered())
        self.targets.get.assert_called_with(status='unregistered')

    def test_get_upcoming(self):
        """Should query for upcoming targets"""
        results = [
            {'codename': 'SLEEPYSLUG', 'slug': '1283hi'}
        ]
        query_changes = {
            'sorting[field]': 'upcomingStartDate',
            'sorting[direction]': 'asc'
        }
        self.targets.get = MagicMock()
        self.targets.get.return_value = results
        self.assertEqual(results, self.targets.get_upcoming())
        self.targets.get.assert_called_with(status='upcoming', query_changes=query_changes)

    def test_set_connected(self):
        """Should connect to a given target provided kwargs"""
        self.targets._db.find_targets.return_value = [Target(slug='28h93iw')]
        self.targets._api.request.return_value.status_code = 200
        self.targets.get_connected = MagicMock()
        self.targets.set_connected(slug='28h93iw')
        self.targets._api.request.assert_called_with('PUT',
                                                     'launchpoint',
                                                     data={'listing_id': '28h93iw'})
        self.targets.get_connected.assert_called_with()

    def test_set_connected_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.set_connected()
        self.targets._auth.get_api_token.assert_called_once()

    def test_set_connected_disconnect(self):
        """Should disconnect from target if none specified"""
        self.targets._api.request.return_value.status_code = 200
        self.targets.get_connected = MagicMock()
        self.targets.set_connected()
        self.targets._api.request.assert_called_with('PUT',
                                                     'launchpoint',
                                                     data={'listing_id': ''})
        self.targets.get_connected.assert_called_with()

    def test_set_connected_target(self):
        """Should connect to a given target provided a target"""
        target = Target(slug='28h93iw')
        self.targets._api.request.return_value.status_code = 200
        self.targets.get_connected = MagicMock()
        self.targets.set_connected(target)
        self.targets._api.request.assert_called_with('PUT',
                                                     'launchpoint',
                                                     data={'listing_id': '28h93iw'})
        self.targets.get_connected.assert_called_with()

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
        self.targets._api.request.return_value.status_code = 200
        self.assertEqual(unreg, self.targets.set_registered())
        self.targets._api.request.assert_has_calls(calls)

    def test_set_registered_403_login(self):
        """Should call get_api_token on 403"""
        self.targets._auth = MagicMock()
        self.targets._api.request.return_value.status_code = 403
        self.state.login = True
        self.targets.set_registered([{'slug': '1o2h8o'}])
        self.targets._auth.get_api_token.assert_called_once()

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
        self.targets._api.request.return_value.status_code = 200
        self.assertEqual(17, len(self.targets.set_registered()))
