"""test_db.py

Tests for the plugins/db.py Db class
"""

import alembic.command
import alembic.config
import os
import sys
import pathlib
import unittest

from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../src')))

import synack  # noqa: E402


class DbTestCase(unittest.TestCase):
    def setUp(self):
        self.state = synack._state.State()
        self.state._db = MagicMock()
        self.db = synack.plugins.Db(self.state)

    def test_add_categories(self):
        self.db.Session = MagicMock()
        cats = [{
            "category_id": 10,
            "category_name": "Some Cool Cat",
            "passed": True
        }]
        query = self.db.Session.return_value.query

        self.db.add_categories(cats)

        query.assert_called_with(synack.db.models.Category)
        query.return_value.filter_by.assert_called_with(id=10)
        query.return_value.filter_by.return_value.first.assert_called_with()
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_add_categories_empty_db(self):
        self.db.Session = MagicMock()
        cats = [{
            'category_id': 10,
            'category_name': 'Some Cool Cat',
            'passed': True
        }]
        query = self.db.Session.return_value.query
        query.return_value.filter_by.return_value.first.return_value = None

        self.db.add_categories(cats)

        query.assert_called_with(synack.db.models.Category)
        query.return_value.filter_by.assert_called_with(id=10)
        self.db.Session.return_value.add.assert_called()
        query.return_value.filter_by.return_value.first.assert_called_with()
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_ips_batch_flush(self, mock_insert):
        """Should flush in batches when more than 15000 IPs"""
        self.db.Session = MagicMock()
        session = self.db.Session.return_value
        results = [{'ip': f'10.{i // 65025}.{(i // 255) % 255}.{i % 255}', 'target': f'tgt{i}'}
                   for i in range(15001)]
        self.db.add_ips(results)
        session.execute.assert_called()
        session.commit.assert_called_with()
        session.close.assert_called_with()

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_ips_existing_ips(self, mock_insert):
        """Should upsert IPs using on_conflict_do_nothing"""
        self.db.Session = MagicMock()
        results = [
            {
                "ip": "1.1.1.1",
                "target": "7gh33tjf72",
                "source": "nmap",
                "ports": [
                    {
                        "port": "443",
                        "protocol": "tcp",
                        "service": "Super Apache NGINX Deluxe",
                    },
                    {
                        "port": "53",
                        "protocol": "udp",
                        "service": "DNS"
                    }
                ]
            }
        ]
        to_insert = [
            {'ip': '1.1.1.1', 'target': '7gh33tjf72'}
        ]
        self.db.add_ips(results)
        mock_insert.assert_called_with(synack.db.models.IP)
        mock_insert.return_value.values.assert_called_with(to_insert)
        mock_insert.return_value.values.return_value.on_conflict_do_nothing.assert_called_with(
            index_elements=['ip', 'target'],
        )
        stmt = mock_insert.return_value.values.return_value.on_conflict_do_nothing.return_value
        self.db.Session.return_value.execute.assert_called_with(stmt)
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_ips_new_ips(self, mock_insert):
        """Should not commit or close when session is provided externally"""
        results = [
            {
                "ip": "1.1.1.1",
                "target": "7gh33tjf72",
                "source": "nmap",
                "ports": [
                    {
                        "port": "443",
                        "protocol": "tcp",
                        "service": "Super Apache NGINX Deluxe",
                    },
                    {
                        "port": "53",
                        "protocol": "udp",
                        "service": "DNS"
                    }
                ]
            }
        ]
        mock_session = MagicMock()
        to_insert = [{'ip': '1.1.1.1', 'target': '7gh33tjf72'}]
        self.db.add_ips(results, mock_session)
        mock_insert.assert_called_with(synack.db.models.IP)
        mock_insert.return_value.values.assert_called_with(to_insert)
        mock_insert.return_value.values.return_value.on_conflict_do_nothing.assert_called_with(
            index_elements=['ip', 'target'])
        stmt = mock_insert.return_value.values.return_value.on_conflict_do_nothing.return_value
        mock_session.execute.assert_called_with(stmt)
        mock_session.commit.assert_not_called()
        mock_session.close.assert_not_called()

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_organizations(self, mock_insert):
        """Should update Organizations table if organization.slug provided"""
        mock_session = MagicMock()
        targets = [{
            "organization": {"slug": "qweqwe"}
        }]
        self.db.add_organizations(targets, mock_session)
        mock_insert.assert_called_with(synack.db.models.Organization)
        mock_insert.return_value.values.assert_called_with([{'slug': 'qweqwe'}])
        mock_insert.return_value.values.return_value.on_conflict_do_nothing.assert_called_with(
            index_elements=['slug'])
        stmt = mock_insert.return_value.values.return_value.on_conflict_do_nothing.return_value
        mock_session.execute.assert_called_with(stmt)

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_organizations_dict_targets(self, mock_insert):
        """Should handle dict of targets"""
        mock_session = MagicMock()
        targets = {'t1': {'organization': {'slug': 'qweqwe'}}}
        self.db.add_organizations(targets, mock_session)
        mock_insert.assert_called_with(synack.db.models.Organization)
        mock_insert.return_value.values.assert_called_with([{'slug': 'qweqwe'}])

    def test_add_organizations_no_session(self):
        """Should create and destroy a db session if not provided"""
        self.db.Session = MagicMock()
        targets = [{
            "organization": {"slug": "qweqwe"}
        }]
        self.db.Session.return_value.query.return_value.filter_by.return_value.first.return_value = None
        self.db.add_organizations(targets)
        self.db.Session.assert_called()
        self.db.Session.return_value.commit.assert_called()
        self.db.Session.return_value.close.assert_called()

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_organizations_organization_id(self, mock_insert):
        """Should update Organizations table if organization_id provided"""
        mock_session = MagicMock()
        targets = [{
            "organization_id": "asdasd"
        }]
        self.db.add_organizations(targets, mock_session)
        mock_insert.assert_called_with(synack.db.models.Organization)
        mock_insert.return_value.values.assert_called_with([{'slug': 'asdasd'}])
        mock_insert.return_value.values.return_value.on_conflict_do_nothing.assert_called_with(
            index_elements=['slug'])
        stmt = mock_insert.return_value.values.return_value.on_conflict_do_nothing.return_value
        mock_session.execute.assert_called_with(stmt)

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_organizations_str_organization(self, mock_insert):
        """Should handle string organization slug directly"""
        mock_session = MagicMock()
        targets = [{'organization': 'my_org_slug'}]
        self.db.add_organizations(targets, mock_session)
        mock_insert.return_value.values.assert_called_with([{'slug': 'my_org_slug'}])

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_ports_batch_flush(self, mock_insert):
        """Should flush in batches when more than 15000 ports"""
        self.db.Session = MagicMock()
        self.db.add_ips = MagicMock()
        mock_ip = MagicMock()
        mock_ip.ip = '1.1.1.1'
        mock_ip.id = 1
        self.db.Session.return_value.query.return_value.all.return_value = [mock_ip]
        result = {
            'ip': '1.1.1.1',
            'target': 'tgt',
            'source': 'nmap',
            'ports': [{'port': str(i), 'protocol': 'tcp', 'service': f'svc{i}'} for i in range(15001)]
        }
        self.db.add_ports([result])
        self.db.Session.return_value.execute.assert_called()
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_ports_new(self, mock_insert):
        """Should add port if new"""
        self.db.Session = MagicMock()
        self.db.add_ips = MagicMock()
        results = [
            {
                "ip": "1.1.1.1",
                "target": "7gh33tjf72",
                "source": "nmap",
                "ports": [
                    {
                        "port": "443",
                        "protocol": "tcp",
                        "service": "Super Apache NGINX Deluxe",
                    },
                    {
                        "port": "53",
                        "protocol": "udp",
                        "service": "DNS plz AXFR me"
                    }
                ]
            }
        ]
        mock_ip = MagicMock()
        mock_ip.ip = "1.1.1.1"
        mock_ip.id = 42
        self.db.Session.return_value.query.return_value.all.return_value = [mock_ip]
        self.db.add_ports(results)

        expected_ports = [
            {'port': '443', 'protocol': 'tcp', 'service': 'Super Apache NGINX Deluxe',
             'ip': 42, 'source': 'nmap', 'open': None, 'updated': None},
            {'port': '53', 'protocol': 'udp', 'service': 'DNS plz AXFR me',
             'ip': 42, 'source': 'nmap', 'open': None, 'updated': None}
        ]
        mock_insert.assert_called_with(synack.db.models.Port)
        mock_insert.return_value.values.assert_called_with(expected_ports)
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()
        self.db.add_ips.assert_called_with(results, self.db.Session.return_value)

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_ports_update(self, mock_insert):
        """Should update ports if existing"""
        self.db.Session = MagicMock()
        self.db.add_ips = MagicMock()
        results = [
            {
                "ip": "1.1.1.1",
                "target": "7gh33tjf72",
                "source": "nmap",
                "ports": [
                    {
                        "port": "443",
                        "protocol": "tcp",
                        "service": "Super Apache NGINX Deluxe",
                        "open": True,
                        "updated": 1654969137
                    },
                    {
                        "port": "53",
                        "protocol": "udp",
                        "service": "DNS"
                    }
                ]
            }
        ]
        mock_ip = MagicMock()
        mock_ip.ip = "1.1.1.1"
        mock_ip.id = 42
        self.db.Session.return_value.query.return_value.all.return_value = [mock_ip]
        self.db.add_ports(results)

        expected_ports = [
            {'port': '443', 'protocol': 'tcp', 'service': 'Super Apache NGINX Deluxe',
             'ip': 42, 'source': 'nmap', 'open': True, 'updated': 1654969137},
            {'port': '53', 'protocol': 'udp', 'service': 'DNS',
             'ip': 42, 'source': 'nmap', 'open': None, 'updated': None}
        ]
        mock_insert.assert_called_with(synack.db.models.Port)
        mock_insert.return_value.values.assert_called_with(expected_ports)
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()
        self.db.add_ips.assert_called_with(results, self.db.Session.return_value)

    def test_add_targets(self):
        """Should update Targets table"""
        self.db.Session = MagicMock()

        targets = [{
            "organization": {"slug": "qweqwe"},
            "category": {"id": 10}
        }, {
            "organization_id": "qwewqe",
            "category": {"id": 10}
        }]

        self.db.add_targets(targets, is_registered=True)
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_targets_dict(self, mock_insert):
        """Should handle dict of targets and insert matching orgs"""
        self.db.Session = MagicMock()
        self.db.add_organizations = MagicMock()
        session = self.db.Session.return_value
        session.query.return_value.all.return_value = [('orgslug',)]
        targets = {'t1': {'organization': {'slug': 'orgslug'}, 'category': {'id': 10}}}
        self.db.add_targets(targets)
        mock_insert.assert_called_with(synack.db.models.Target)
        session.execute.assert_called()
        session.commit.assert_called_with()
        session.close.assert_called_with()

    def test_add_targets_empty_db(self):
        """Should update Targets table with new Target"""
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.filter_by.return_value.first.return_value = None

        targets = [{
            "organization": {"slug": "qweqwe"},
            "category": {"id": 10}
        }, {
            "organization_id": "qwewqe",
            "category": {"id": 10}
        }]

        self.db.add_targets(targets)
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_targets_str_organization(self, mock_insert):
        """Should handle string organization and int category"""
        self.db.Session = MagicMock()
        self.db.add_organizations = MagicMock()
        session = self.db.Session.return_value
        session.query.return_value.all.return_value = [('orgslug',)]
        targets = [{'organization': 'orgslug', 'category': 10}]
        self.db.add_targets(targets)
        mock_insert.assert_called_with(synack.db.models.Target)
        session.execute.assert_called()

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_urls_new(self, mock_insert):
        """Should add url if new"""
        self.db.Session = MagicMock()
        self.db.add_ips = MagicMock()
        results = [
            {
                "ip": "1.1.1.1",
                "urls": [
                    {
                        "url": "https://www.google.com",
                        "screenshot_url": "https://imgur.com/219hi4"
                    },
                    {
                        "url": "https://www.ebay.com",
                        "screenshot_url": "file:///tmp/qwh82938.jpg"
                    }
                ]
            }
        ]
        mock_ip = MagicMock()
        mock_ip.ip = "1.1.1.1"
        mock_ip.id = 42
        self.db.Session.return_value.query.return_value.all.return_value = [mock_ip]
        self.db.add_urls(results)

        expected_urls = [
            {'url': 'https://www.google.com', 'screenshot_url': 'https://imgur.com/219hi4'},
            {'url': 'https://www.ebay.com', 'screenshot_url': 'file:///tmp/qwh82938.jpg'}
        ]
        mock_insert.assert_called_with(synack.db.models.Url)
        mock_insert.return_value.values.assert_called_with(expected_urls)
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()
        self.db.add_ips.assert_called_with(results, self.db.Session.return_value)

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_urls_no_ip(self, mock_insert):
        """Should be fine if IP isn't included"""
        self.db.Session = MagicMock()
        self.db.add_ips = MagicMock()
        results = [
            {
                "urls": [
                    {
                        "url": "https://www.google.com",
                        "screenshot_url": "https://imgur.com/219hi4"
                    },
                    {
                        "url": "https://www.ebay.com",
                        "screenshot_url": "file:///tmp/qwh82938.jpg"
                    }
                ]
            }
        ]
        self.db.Session.return_value.query.return_value.all.return_value = []
        self.db.add_urls(results)

        mock_insert.assert_not_called()
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()
        self.db.add_ips.assert_called_with(results, self.db.Session.return_value)

    @patch('synack.plugins.db.sqlite_insert')
    def test_add_url_update(self, mock_insert):
        """Should update urls if existing"""
        self.db.Session = MagicMock()
        self.db.add_ips = MagicMock()
        results = [
            {
                "ip": "1.1.1.1",
                "urls": [
                    {
                        "url": "https://www.google.com",
                        "screenshot_url": "https://imgur.com/219hi4"
                    },
                    {
                        "url": "https://www.ebay.com",
                        "screenshot_url": "file:///tmp/qwh82938.jpg"
                    }
                ]
            }
        ]
        mock_ip = MagicMock()
        mock_ip.ip = "1.1.1.1"
        mock_ip.id = 42
        self.db.Session.return_value.query.return_value.all.return_value = [mock_ip]
        self.db.add_urls(results)

        expected_urls = [
            {'url': 'https://www.google.com', 'screenshot_url': 'https://imgur.com/219hi4'},
            {'url': 'https://www.ebay.com', 'screenshot_url': 'file:///tmp/qwh82938.jpg'}
        ]
        mock_insert.assert_called_with(synack.db.models.Url)
        mock_insert.return_value.values.assert_called_with(expected_urls)
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()
        self.db.add_ips.assert_called_with(results, self.db.Session.return_value)

    def test_api_token(self):
        """Should set and get the api_token from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = '123'
        self.assertEqual('123', self.db.api_token)
        self.db.get_config.assert_called_with('api_token')

        self.db.api_token = '456'
        self.db.set_config.assert_called_with('api_token', '456')

    def test_categories(self):
        """Should pull the categories from the database"""
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.all.return_value = 'ret'

        self.assertEqual('ret', self.db.categories)

        self.db.Session.assert_called_with()
        query.assert_called_with(synack.db.models.Category)
        query.return_value.all.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_debug(self):
        """Should pull debug from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = False

        self.assertEqual(False, self.db.debug)
        self.db.get_config.assert_called_with("debug")

        self.db.debug = True
        self.db.set_config.assert_called_with('debug', True)

    def test_duo_akey(self):
        """Should get and set duo_akey from the database"""
        self.db.get_config = MagicMock(return_value='akey123')
        self.db.set_config = MagicMock()
        self.assertEqual('akey123', self.db.duo_akey)
        self.db.duo_akey = 'akey123'
        self.db.set_config.assert_called_with('duo_akey', 'akey123')

    def test_duo_host(self):
        """Should get and set duo_host from the database"""
        self.db.get_config = MagicMock(return_value='api.duo.com')
        self.db.set_config = MagicMock()
        self.assertEqual('api.duo.com', self.db.duo_host)
        self.db.duo_host = 'api.duo.com'
        self.db.set_config.assert_called_with('duo_host', 'api.duo.com')

    def test_duo_pkey(self):
        """Should get and set duo_pkey from the database"""
        self.db.get_config = MagicMock(return_value='pkey123')
        self.db.set_config = MagicMock()
        self.assertEqual('pkey123', self.db.duo_pkey)
        self.db.duo_pkey = 'pkey123'
        self.db.set_config.assert_called_with('duo_pkey', 'pkey123')

    @patch('synack.plugins.db.RSA')
    def test_duo_rsa_key(self, mock_rsa):
        """Should auto-generate and store RSA key when none exists"""
        self.db.get_config = MagicMock(return_value=None)
        self.db.set_config = MagicMock()
        mock_key = MagicMock()
        mock_rsa.generate.return_value = mock_key
        mock_key.export_key.return_value = b'FAKE_PEM'
        result = self.db.duo_rsa_key
        mock_rsa.generate.assert_called_with(2048)
        self.db.set_config.assert_called_with('duo_rsa_key', 'FAKE_PEM')
        self.assertEqual('FAKE_PEM', result)

    def test_duo_rsa_key_setter(self):
        """Should set duo_rsa_key in the database"""
        self.db.set_config = MagicMock()
        self.db.duo_rsa_key = 'MY_PEM'
        self.db.set_config.assert_called_with('duo_rsa_key', 'MY_PEM')

    def test_email(self):
        """Should pull email from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = "1@2.com"

        self.assertEqual("1@2.com", self.db.email)

    def test_email_prompt(self):
        """Should ask the user for email if none"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = None

        with patch("builtins.input") as mock_input:
            mock_input.return_value = '1@2.com'
            self.assertEqual('1@2.com', self.db.email)
            mock_input.assert_called_with('Synack Email: ')
        self.db.get_config.assert_called_with("email")
        self.db.set_config.assert_called_with("email", "1@2.com")

    def test_find_ips(self):
        """Should return a list of IPs"""
        self.db.Session = MagicMock()

        self.db.Session.return_value.query.return_value.join.return_value.all.return_value = [
            synack.db.models.IP(ip='1.2.3.4', target='487egfue'),
            synack.db.models.IP(ip='4.3.2.1', target='487egfue')
        ]

        returned = self.db.find_ips()
        expected = [
            {'ip': '1.2.3.4', 'target': '487egfue'},
            {'ip': '4.3.2.1', 'target': '487egfue'}
        ]
        self.assertTrue(returned, expected)
        self.db.Session.assert_called()
        self.db.Session.return_value.expunge_all.assert_called()
        self.db.Session.return_value.close.assert_called()

    def test_find_ips_filters(self):
        """Should apply filters to IPs search"""
        self.db.Session = MagicMock()

        self.db.Session.return_value.query.return_value.join.return_value.all.return_value = []

        self.db.find_ips(ip='1.2.3.4', codename='SLEEPYPUPPY')
        self.db.Session.return_value.query.return_value.filter_by.assert_called_with(ip='1.2.3.4')
        self.db.Session.return_value.query.return_value.filter_by.return_value.join.return_value. \
            filter_by.assert_called_with(codename='SLEEPYPUPPY')

        self.db.Session.assert_called()
        self.db.Session.return_value.expunge_all.assert_called()
        self.db.Session.return_value.close.assert_called()

    def test_find_ports(self):
        """Should return a list of Ports"""
        self.db.Session = MagicMock()

        self.db.Session.return_value.query.return_value.join.return_value.join.return_value.all.return_value = [
            synack.db.models.Port(ip='1', port='443', protocol='tcp'),
            synack.db.models.Port(ip='1', port='53', protocol='udp')
        ]

        returned = self.db.find_ports()
        expected = [
            {'ip': '1.2.3.4', 'target': '487egfue', 'ports': {'port': '443', 'protocol': 'tcp'}},
            {'ip': '4.3.2.1', 'target': '487egfue', 'ports': {'port': '53', 'protocol': 'udp'}}
        ]
        self.assertTrue(returned, expected)
        self.db.Session.assert_called()
        self.db.Session.return_value.expunge_all.assert_called()
        self.db.Session.return_value.close.assert_called()

    def test_find_ports_filter_by_protocol(self):
        """Should apply source filters to Ports search"""
        self.db.Session = MagicMock()

        self.db.Session.return_value.query.return_value.join.return_value.all.return_value = []

        self.db.find_ports(protocol='tcp')
        self.db.Session.return_value.query.return_value.filter_by.assert_called_with(protocol='tcp')
        self.db.Session.assert_called()
        self.db.Session.return_value.expunge_all.assert_called()
        self.db.Session.return_value.close.assert_called()

    def test_find_ports_filter_by_source(self):
        """Should apply source filters to Ports search"""
        self.db.Session = MagicMock()

        self.db.Session.return_value.query.return_value.join.return_value.all.return_value = []

        self.db.find_ports(source='nmap')
        self.db.Session.return_value.query.return_value.filter_by.assert_called_with(source='nmap')
        self.db.Session.assert_called()
        self.db.Session.return_value.expunge_all.assert_called()
        self.db.Session.return_value.close.assert_called()

    def test_find_ports_filters(self):
        """Should apply filters to Ports search"""
        self.db.Session = MagicMock()

        self.db.Session.return_value.query.return_value.join.return_value.all.return_value = []

        self.db.find_ports(port=25, ip='1.2.3.4', codename='SLEEPYPUPPY')
        self.db.Session.return_value.query.return_value.filter_by.assert_called_with(port=25)
        self.db.Session.return_value.query.return_value.filter_by.return_value.join.return_value. \
            filter_by.assert_called_with(ip='1.2.3.4')
        self.db.Session.return_value.query.return_value.filter_by.return_value.join.return_value. \
            filter_by.return_value.join.return_value.filter_by.assert_called_with(codename='SLEEPYPUPPY')

        self.db.Session.assert_called()
        self.db.Session.return_value.expunge_all.assert_called()
        self.db.Session.return_value.close.assert_called()

    def test_find_targets(self):
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.filter.return_value.all.return_value = 'ret'

        self.assertEqual('ret', self.db.find_targets(codename='SLOPPYFISH'))

        self.db.Session.assert_called_with()
        query.assert_called_with(synack.db.models.Target)
        query.return_value.filter.assert_called()
        query.return_value.filter.return_value.all.assert_called_with()
        self.db.Session.return_value.expunge_all.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_find_targets_like(self):
        """Should apply like filter when like=True"""
        self.db.Session = MagicMock()
        self.db.Session.return_value.query.return_value.filter.return_value.all.return_value = []
        self.db.find_targets(codename='FISH', like=True)
        self.db.Session.return_value.query.return_value.filter.assert_called()

    def test_find_targets_or(self):
        """Should apply OR filter when or=True"""
        self.db.Session = MagicMock()
        self.db.Session.return_value.query.return_value.filter.return_value.all.return_value = []
        self.db.find_targets(codename='FISH', **{'or': True})
        self.db.Session.return_value.query.return_value.filter.assert_called()

    def test_find_urls(self):
        """Should return a list of Urls"""
        self.db.Session = MagicMock()

        self.db.Session.return_value.query.return_value.join.return_value.join.return_value.all.return_value = [
            synack.db.models.Url(ip='1', url='https://www.google.com', screenshot_url='file:///tmp/qiuwe.png'),
            synack.db.models.Url(ip='2', url='https://www.ebay.com', screenshot_url='file:///tmp/uo932g8.png')
        ]

        returned = self.db.find_urls()
        expected = [
            {
                'ip': '1.2.3.4',
                'target': '487egfue',
                'urls': [{'url': 'https://www.ebay.com', 'screenshot_url': 'file:///tmp/uo932g8.png'}]
            },
            {
                'ip': '4.3.2.1',
                'target': '487egfue',
                'urls': [{'url': 'https://www.google.com', 'screenshot_url': 'file:///tmp/qiuwe.png'}]
            }
        ]
        self.assertTrue(returned, expected)
        self.db.Session.assert_called()
        self.db.Session.return_value.expunge_all.assert_called()
        self.db.Session.return_value.close.assert_called()

    def test_find_urls_filters(self):
        """Should apply filters to Urls search"""
        self.db.Session = MagicMock()

        self.db.Session.return_value.query.return_value.join.return_value.all.return_value = []

        self.db.find_urls(url='https://www.google.com', ip='1.2.3.4', codename='SLEEPYPUPPY')
        self.db.Session.return_value.query.return_value.filter_by.assert_called_with(url='https://www.google.com')
        self.db.Session.return_value.query.return_value.filter_by.return_value.join.return_value. \
            filter_by.assert_called_with(ip='1.2.3.4')
        self.db.Session.return_value.query.return_value.filter_by.return_value.join.return_value. \
            filter_by.return_value.join.return_value.filter_by.assert_called_with(codename='SLEEPYPUPPY')

        self.db.Session.assert_called()
        self.db.Session.return_value.expunge_all.assert_called()
        self.db.Session.return_value.close.assert_called()

    def test_foreign_keys_on(self):
        mock = MagicMock()
        self.db._fk_pragma_on_connect(mock, None)
        mock.execute.assert_called_with('pragma foreign_keys=ON')

    def test_get_config(self):
        self.db.Session = MagicMock()
        config = synack.db.models.Config(password='test')
        query = self.db.Session.return_value.query
        query.return_value.filter_by.return_value.first.return_value = config

        self.assertEqual('test', self.db.get_config('password'))

        query.assert_called_with(synack.db.models.Config)
        query.return_value.filter_by.assert_called_with(id=1)
        query.return_value.filter_by.return_value.first.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_get_config_empty_db(self):
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        mock_config = MagicMock()
        mock_config.password = None
        query.return_value.filter_by.return_value.first.side_effect = [None, mock_config]

        self.db.get_config('password')

        query.assert_called_with(synack.db.models.Config)
        query.return_value.filter_by.assert_called_with(id=1)
        self.db.Session.return_value.add.assert_called()
        self.db.Session.return_value.commit.assert_called()
        self.db.Session.return_value.close.assert_called_with()

    def test_http_proxy(self):
        """Should set and get the http_proxy from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "123"

        self.db.http_proxy = "123"
        self.db.set_config.assert_called_with("http_proxy", "123")
        self.assertEqual("123", self.db.http_proxy)
        self.db.get_config.assert_called_with("http_proxy")

    def test_https_proxy(self):
        """Should set and get the https_proxy from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "123"

        self.db.https_proxy = "123"
        self.db.set_config.assert_called_with("https_proxy", "123")
        self.assertEqual("123", self.db.https_proxy)
        self.db.get_config.assert_called_with("https_proxy")

    def test_ips(self):
        """Should get all ips from the database"""
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.all.return_value = 'ips'

        self.assertEqual('ips', self.db.ips)
        query.assert_called_with(synack.db.models.IP)
        query.return_value.all.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_notifications_token(self):
        """Should pull notifications_token from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = "123"

        self.assertEqual("123", self.db.notifications_token)
        self.db.get_config.assert_called_with("notifications_token")
        self.db.notifications_token = "123"
        self.db.set_config.assert_called_with("notifications_token", "123")

    def test_otp_count(self):
        """Should pull otp_count from the database"""
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = 5

        self.assertEqual(5, self.db.otp_count)
        self.db.get_config.assert_called_with("otp_count")

    def test_otp_count_none(self):
        """Should return None without prompting when otp_count is unset"""
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = None

        with patch("builtins.input") as mock_input:
            self.assertIsNone(self.db.otp_count)
            mock_input.assert_not_called()

    def test_otp_count_set(self):
        """Should set otp_count in the database"""
        self.db.set_config = MagicMock()
        self.db.otp_count = 5
        self.db.set_config.assert_called_with('otp_count', 5)

    def test_otp_secret(self):
        """Should pull otp_secret from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = "ABCDEFGH"

        self.assertEqual("ABCDEFGH", self.db.otp_secret)

    def test_otp_secret_none(self):
        """Should return None without prompting when otp_secret is unset"""
        self.db.get_config = MagicMock()
        self.db.get_config.return_value = None

        with patch("builtins.input") as mock_input:
            self.assertIsNone(self.db.otp_secret)
            mock_input.assert_not_called()
        self.db.get_config.assert_called_with("otp_secret")

    def test_otp_secret_set(self):
        """Should set otp_secret in the database"""
        self.db.set_config = MagicMock()
        self.db.otp_secret = 'SECRET123'
        self.db.set_config.assert_called_with('otp_secret', 'SECRET123')

    def test_password(self):
        """Should pull password from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = "password1234"

        self.assertEqual("password1234", self.db.password)

    def test_password_prompt(self):
        """Should ask the user for password if none"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = None

        with patch("builtins.input") as mock_input:
            mock_input.return_value = 'password1234'
            self.assertEqual('password1234', self.db.password)
            mock_input.assert_called_with('Synack Password: ')
        self.db.get_config.assert_called_with("password")
        self.db.set_config.assert_called_with("password", "password1234")

    def test_ports(self):
        """Should get all ports from the database"""
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.all.return_value = 'ports'

        self.assertEqual('ports', self.db.ports)
        query.assert_called_with(synack.db.models.Port)
        query.return_value.all.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_proxies(self):
        """Should get http_proxy and https_proxy and return them in a dict"""
        self.db.get_config = MagicMock()
        self.db.get_config.side_effect = [
            'http://localhost:8080',
            'https://localhost:8080'
        ]

        ret = {
            'http': 'http://localhost:8080',
            'https': 'https://localhost:8080'
        }
        calls = [
            unittest.mock.call('http_proxy'),
            unittest.mock.call('https_proxy')
        ]

        self.assertEqual(ret, self.db.proxies)
        self.db.get_config.assert_has_calls(calls)

    def test_remove_targets(self):
        self.db.Session = MagicMock()
        self.db.remove_targets()
        query = self.db.Session.return_value.query
        self.db.Session.assert_called_with()
        query.assert_called_with(synack.db.models.Target)
        query.return_value.filter_by.assert_called_with()
        query.return_value.filter_by.return_value.delete.assert_called_with()
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_remove_targets_specific(self):
        self.db.Session = MagicMock()
        self.db.remove_targets(codename="BADCAT")
        query = self.db.Session.return_value.query
        self.db.Session.assert_called_with()
        query.assert_called_with(synack.db.models.Target)
        query.return_value.filter_by.assert_called_with(codename="BADCAT")
        query.return_value.filter_by.return_value.delete.assert_called_with()
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_scratchspace_dir(self):
        """Should pull scratchspace dir from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = '/tmp'
        self.db.scratchspace_dir

        self.assertEqual(pathlib.Path('/tmp'), self.db.scratchspace_dir)
        self.db.get_config.assert_called_with('scratchspace_dir')
        self.db.scratchspace_dir = '/tmp'
        self.db.set_config.assert_called_with('scratchspace_dir', '/tmp')

    def test_set_config(self):
        self.db.Session = MagicMock()
        config = synack.db.models.Config(password='test')
        query = self.db.Session.return_value.query
        query.return_value.filter_by.return_value.first.return_value = config

        self.db.set_config('password', 'bacon')

        self.assertEqual('bacon', config.password)
        query.assert_called_with(synack.db.models.Config)
        query.return_value.filter_by.assert_called_with(id=1)
        query.return_value.filter_by.return_value.first.assert_called_with()
        self.db.Session.assert_called_with()
        self.db.Session.return_value.commit.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_set_config_empty_db(self):
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.filter_by.return_value.first.return_value = None

        self.db.set_config('password', 'test1234')

        query.assert_called_with(synack.db.models.Config)
        self.db.Session.return_value.add.assert_called()

    def test_set_migration(self):
        db_dir = pathlib.Path(__file__).parent.parent / 'src/synack/db'
        conf_dir = pathlib.Path('~/.config/synack').expanduser().resolve()
        mock = MagicMock()
        calls = [
            unittest.mock.call('script_location', str(db_dir / 'alembic')),
            unittest.mock.call('version_locations',
                               str(db_dir / 'alembic/versions')),
            unittest.mock.call('path_separator', 'os'),
            unittest.mock.call('sqlalchemy.url',
                               'sqlite:///' + str(conf_dir / 'synackapi.db')),
        ]
        with patch.object(alembic.config, 'Config') as mock_config:
            mock_config.return_value = mock
            with patch.object(alembic.command, 'upgrade') as mock_upgrade:
                self.db.set_migration()
                mock_config.return_value.set_main_option.assert_has_calls(calls)
                mock_upgrade.assert_called_with(mock, 'head')

    def test_slack_app_token(self):
        """Should get and set slack_app_token from the database"""
        self.db.get_config = MagicMock(return_value='xapp-123')
        self.db.set_config = MagicMock()
        self.assertEqual('xapp-123', self.db.slack_app_token)
        self.db.slack_app_token = 'xapp-123'
        self.db.set_config.assert_called_with('slack_app_token', 'xapp-123')

    def test_slack_app_token_prompt(self):
        """Should prompt for slack_app_token when unset"""
        self.db.get_config = MagicMock(return_value=None)
        self.db.set_config = MagicMock()
        with patch('builtins.input', return_value='xapp-456') as mock_input:
            result = self.db.slack_app_token
        mock_input.assert_called_with('Slack App Token: ')
        self.assertEqual('xapp-456', result)

    def test_slack_channel(self):
        """Should get and set slack_channel from the database"""
        self.db.get_config = MagicMock(return_value='#general')
        self.db.set_config = MagicMock()
        self.assertEqual('#general', self.db.slack_channel)
        self.db.slack_channel = '#general'
        self.db.set_config.assert_called_with('slack_channel', '#general')

    def test_slack_channel_prompt(self):
        """Should prompt for slack_channel when unset"""
        self.db.get_config = MagicMock(return_value=None)
        self.db.set_config = MagicMock()
        with patch('builtins.input', return_value='#random') as mock_input:
            result = self.db.slack_channel
        mock_input.assert_called_with('Slack Channel: ')
        self.assertEqual('#random', result)

    def test_slack_url(self):
        """Should set and get the slack_url from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "https://slack.com"

        self.db.slack_url = "https://slack.com"
        self.db.set_config.assert_called_with("slack_url", "https://slack.com")
        self.assertEqual("https://slack.com", self.db.slack_url)
        self.db.get_config.assert_called_with("slack_url")

    def test_smtp_email_from(self):
        """Should set and get the smtp_email_from from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "1@2.com"

        self.db.smtp_email_from = "1@2.com"
        self.db.set_config.assert_called_with("smtp_email_from", "1@2.com")
        self.assertEqual("1@2.com", self.db.smtp_email_from)
        self.db.get_config.assert_called_with("smtp_email_from")

    def test_smtp_email_to(self):
        """Should set and get the smtp_email_to from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "2@2.com"

        self.db.smtp_email_to = "2@2.com"
        self.db.set_config.assert_called_with("smtp_email_to", "2@2.com")
        self.assertEqual("2@2.com", self.db.smtp_email_to)
        self.db.get_config.assert_called_with("smtp_email_to")

    def test_smtp_password(self):
        """Should set and get the smtp_password from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "password123"

        self.db.smtp_password = "password123"
        self.db.set_config.assert_called_with("smtp_password", "password123")
        self.assertEqual("password123", self.db.smtp_password)
        self.db.get_config.assert_called_with("smtp_password")

    def test_smtp_port(self):
        """Should set and get the smtp_port from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "123"

        self.db.smtp_port = "123"
        self.db.set_config.assert_called_with("smtp_port", "123")
        self.assertEqual("123", self.db.smtp_port)
        self.db.get_config.assert_called_with("smtp_port")

    def test_smtp_server(self):
        """Should set and get the smtp_server from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "smtp.email.com"

        self.db.smtp_server = "smtp.email.com"
        self.db.set_config.assert_called_with("smtp_server", "smtp.email.com")
        self.assertEqual("smtp.email.com", self.db.smtp_server)
        self.db.get_config.assert_called_with("smtp_server")

    def test_smtp_starttls(self):
        """Should set and get the smtp_starttls from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = True

        self.db.smtp_starttls = True
        self.db.set_config.assert_called_with("smtp_starttls", True)
        self.assertEqual(True, self.db.smtp_starttls)
        self.db.get_config.assert_called_with("smtp_starttls")

    def test_smtp_username(self):
        """Should set and get the smtp_username from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "user5"

        self.db.smtp_username = "user5"
        self.db.set_config.assert_called_with("smtp_username", "user5")
        self.assertEqual("user5", self.db.smtp_username)
        self.db.get_config.assert_called_with("smtp_username")

    def test_synack_domain(self):
        """Should get and set synack_domain from the database"""
        self.db.get_config = MagicMock(return_value='synack.us')
        self.db.set_config = MagicMock()
        self.assertEqual('synack.us', self.db.synack_domain)
        self.db.synack_domain = 'synack.us'
        self.db.set_config.assert_called_with('synack_domain', 'synack.us')

    def test_targets(self):
        """Should get all targets from the database"""
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.all.return_value = 'tgts'

        self.assertEqual('tgts', self.db.targets)
        query.assert_called_with(synack.db.models.Target)
        query.return_value.all.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_template_dir(self):
        """Should pull template dir from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = '/tmp'
        self.db.template_dir

        self.assertEqual(pathlib.Path('/tmp'), self.db.template_dir)
        self.db.get_config.assert_called_with('template_dir')
        self.db.template_dir = '/tmp'
        self.db.set_config.assert_called_with('template_dir', '/tmp')

    def test_urls(self):
        """Should get all urls from the database"""
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.all.return_value = 'urls'

        self.assertEqual('urls', self.db.urls)
        query.assert_called_with(synack.db.models.Url)
        query.return_value.all.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_use_proxies(self):
        """Should set and get use_proxies from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = True

        self.db.use_proxies = True
        self.db.set_config.assert_called_with("use_proxies", True)
        self.assertEqual(True, self.db.use_proxies)

    def test_user_id(self):
        """Should set and get the user_id from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "qwe"

        self.db.user_id = "qwe"
        self.db.set_config.assert_called_with("user_id", "qwe")
        self.assertEqual("qwe", self.db.user_id)
        self.db.get_config.assert_called_with("user_id")

    def test_use_scratchspace(self):
        """Should set and get use_scratchspace from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = True

        self.db.use_scratchspace = True
        self.db.set_config.assert_called_with("use_scratchspace", True)
        self.assertEqual(True, self.db.use_scratchspace)
