"""test_hydra.py

Tests for the Hydra Plugin
"""

import json
import os
import sys
import unittest


from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class HydraTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.hydra = synack.plugins.Hydra(self.state)
        self.hydra.api = MagicMock()
        self.hydra.db = MagicMock()

    def test_get_hydra(self):
        """Should get information from Hydra"""
        query = {
            'page': 1,
            'listing_uids': '87314gru',
            'q': '+port_is_open:true'
        }
        self.hydra.build_db_input = MagicMock()
        self.hydra.build_db_input.return_value = 'BuildDbInputReturn'
        self.hydra.db.find_targets.return_value = [
            synack.db.models.Target(codename='CRUSTYCRAB', slug='87314gru')
        ]
        self.hydra.api.request.return_value.status_code = 200
        content = '[{"somecontent": "content"}]'
        self.hydra.api.request.return_value.content = content
        returned = self.hydra.get_hydra(codename='CRUSTYCRAB')
        self.assertTrue(returned == json.loads(content))
        self.hydra.api.request.assert_called_with('GET',
                                                  'hydra_search/search',
                                                  query=query)
        self.hydra.build_db_input.assert_called_with(json.loads(content))
        self.hydra.db.add_ports.assert_called_with('BuildDbInputReturn')

    def test_get_hydra_no_update_db(self):
        """Should get information from Hydra without updating the DB"""
        query = {
            'page': 1,
            'listing_uids': '87314gru',
            'q': '+port_is_open:true'
        }
        self.hydra.build_db_input = MagicMock()
        self.hydra.build_db_input.return_value = 'BuildDbInputReturn'
        self.hydra.db.find_targets.return_value = [
            synack.db.models.Target(codename='CRUSTYCRAB', slug='87314gru')
        ]
        self.hydra.api.request.return_value.status_code = 200
        content = '[{"somecontent": "content"}]'
        self.hydra.api.request.return_value.content = content
        returned = self.hydra.get_hydra(codename='CRUSTYCRAB', update_db=False)
        self.assertTrue(returned == json.loads(content))
        self.hydra.api.request.assert_called_with('GET',
                                                  'hydra_search/search',
                                                  query=query)
        self.hydra.build_db_input.assert_not_called()
        self.hydra.db.add_ports.assert_not_called()

    def test_get_hydra_multipage(self):
        """Should get information from Hydra spanning multiple pages"""
        query = {
            'page': 2,
            'listing_uids': '87314gru',
            'q': '+port_is_open:true'
        }
        self.hydra.build_db_input = MagicMock()
        self.hydra.db.find_targets.return_value = [
            synack.db.models.Target(codename='CRUSTYCRAB', slug='87314gru')
        ]
        content = '[' + ','.join(['{"somecontent": "content"}' for i in range(0, 10)]) + ']'
        self.hydra.api.request.return_value.status_code = 200
        self.hydra.api.request.return_value.content = content
        returned = self.hydra.get_hydra(codename='CRUSTYCRAB', max_page=2)
        self.assertTrue(len(returned) == 20)
        self.hydra.api.request.assert_called_with('GET',
                                                  'hydra_search/search',
                                                  query=query)

    def test_build_db_input(self):
        """Should convert Hydra output into input for the DB"""
        hydra_out = [
            {
                'host_plugins': {},
                'ip': '1.1.1.1',
                'last_changed_dt': '2022-01-01T12:34:56Z',
                'listing_uid': 'owqeuhiqwe',
                'organization_profile_id': 0,
                'ports': {
                    '443': {
                        'tcp': {
                            'synack': {
                                'cpe': {
                                    'last_changed_dt': '2021-01-01T01:01:01.123456Z',
                                    'parsed': ''
                                },
                                'open': {
                                    'last_changed_dt': '2022-01-01T12:34:56Z',
                                    'parsed': True
                                },
                                'product': {
                                    'last_changed_dt': '2021-10-01T12:43:06.654321Z',
                                    'parsed': ''
                                },
                                'verified_service': {
                                    'last_changed_dt': '2021-10-01T21:43:06.654321Z',
                                    'parsed': 'unknown'
                                }
                            }
                        },
                        'udp': {}
                    }
                }
            },
            {
                'host_plugins': {},
                'ip': '1.1.1.2',
                'last_changed_dt': '2022-01-01T12:34:56.123456Z',
                'listing_uid': 'owqeuhiqwe',
                'organization_profile_id': 0,
                'ports': {
                    '443': {
                        'tcp': {
                            'synack': {
                                'cpe': {
                                    'last_changed_dt': '2021-01-01T01:01:01.123456Z',
                                    'parsed': ''
                                },
                                'open': {
                                    'last_changed_dt': '2022-01-01T12:34:56Z',
                                    'parsed': True
                                },
                                'product': {
                                    'last_changed_dt': '2021-10-01T12:43:06.654321Z',
                                    'parsed': ''
                                },
                                'verified_service': {
                                    'last_changed_dt': '2021-10-01T21:43:06.654321Z',
                                    'parsed': 'unknown'
                                }
                            }
                        },
                        'udp': {}
                    }
                }
            }
        ]

        returned = self.hydra.build_db_input(hydra_out)
        expected = [{
        }
        ]
        self.assertTrue(returned, expected)
