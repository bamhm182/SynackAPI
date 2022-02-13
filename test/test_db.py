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
        self.db = synack.plugins.Db(self.state)

    def test_api_token(self):
        """Should set and get the api_token from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "123"

        self.db.api_token = "123"
        self.db.set_config.assert_called_with("api_token", "123")
        self.assertEqual("123", self.db.api_token)
        self.db.get_config.assert_called_with("api_token")

    def test_foreign_keys_on(self):
        mock = MagicMock()
        self.db._fk_pragma_on_connect(mock, None)
        mock.execute.assert_called_with('pragma foreign_keys=ON')

    def test_set_migration(self):
        db_dir = pathlib.Path(__file__).parent.parent / 'src/synack/db'
        conf_dir = pathlib.Path('~/.config/synack').expanduser().resolve()
        mock = MagicMock()
        calls = [
            unittest.mock.call('script_location', str(db_dir / 'alembic')),
            unittest.mock.call('version_locations',
                               str(db_dir / 'alembic/versions')),
            unittest.mock.call('sqlalchemy.url',
                               'sqlite:///' + str(conf_dir / 'synackapi.db')),
        ]
        with patch.object(alembic.config, 'Config') as mock_config:
            mock_config.return_value = mock
            with patch.object(alembic.command, 'upgrade') as mock_upgrade:
                self.db.set_migration()
                mock_config.return_value.set_main_option.\
                    assert_has_calls(calls)
                mock_upgrade.assert_called_with(mock, 'head')

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

    def test_add_categories(self):
        self.db.Session = MagicMock()
        cats = [{
            "category_id": 10,
            "category_name": "Some Cool Cat",
            "practical_assessment": {
                "passed": True
            },
            "written_assessment": {
                "passed": True
            }
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
            "category_id": 10,
            "category_name": "Some Cool Cat",
            "practical_assessment": {
                "passed": True
            },
            "written_assessment": {
                "passed": True
            }
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

    def test_get_config_empty_db(self):
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.filter_by.return_value.first.return_value = None

        self.db.get_config('password')

        query.assert_called_with(synack.db.models.Config)
        query.return_value.filter_by.assert_called_with(id=1)
        query.return_value.filter_by.return_value.first.assert_called_with()
        self.db.Session.return_value.add.assert_called()
        self.db.Session.return_value.close.assert_called_with()

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

    def test_find_targets(self):
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.filter_by.return_value.all.return_value = 'ret'

        self.assertEqual('ret', self.db.find_targets(codename='SLOPPYFISH'))

        self.db.Session.assert_called_with()
        query.assert_called_with(synack.db.models.Target)
        query.return_value.filter_by.assert_called_with(codename='SLOPPYFISH')
        query.return_value.filter_by.return_value.all.assert_called_with()
        self.db.Session.return_value.expunge_all.assert_called_with()
        self.db.Session.return_value.close.assert_called_with()

    def test_user_id(self):
        """Should set and get the user_id from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = "qwe"

        self.db.user_id = "qwe"
        self.db.set_config.assert_called_with("user_id", "qwe")
        self.assertEqual("qwe", self.db.user_id)
        self.db.get_config.assert_called_with("user_id")

    def test_targets(self):
        """Should get all targets from the database"""
        self.db.Session = MagicMock()
        query = self.db.Session.return_value.query
        query.return_value.all.return_value = 'tgts'

        self.assertEqual('tgts', self.db.targets)
        query.assert_called_with(synack.db.models.Target)
        query.return_value.all.assert_called_with()
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

    def test_use_proxies(self):
        """Should set and get use_proxies from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()

        self.db.get_config.return_value = True

        self.db.use_proxies = True
        self.db.set_config.assert_called_with("use_proxies", True)
        self.assertEqual(True, self.db.use_proxies)

    def test_use_proxies_state(self):
        """State use_proxies should override database"""
        self.db.get_config = MagicMock()

        self.db.get_config.return_value = True

        self.assertEqual(True, self.db.use_proxies)

        self.db.state.use_proxies = False
        self.assertEqual(False, self.db.use_proxies)
        self.db.state.use_proxies = True
        self.assertEqual(True, self.db.use_proxies)

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
        self.db.get_config.has_calls(calls)

    def test_proxies_state(self):
        """Should pull proxies from the State over the database"""
        self.db.get_config = MagicMock()
        self.db.state.http_proxy = 'http://1.2.3.4:8080'
        self.db.state.https_proxy = 'https://4.3.2.1:8080'

        self.assertEqual(self.db.proxies, {
            'http': 'http://1.2.3.4:8080',
            'https': 'https://4.3.2.1:8080'
        })

        self.db.get_config.assert_not_called()

    def test_add_organizations(self):
        """Should update Organizations table if organization.slug provided"""
        mock = MagicMock()
        targets = [{
            "organization": {"slug": "qweqwe"}
        }]
        mock.query.return_value.filter_by.return_value.\
            first.return_value = None
        self.db.add_organizations(targets, mock)
        mock.query.assert_called_with(synack.db.models.Organization)
        mock.query.return_value.filter_by.assert_called_with(slug='qweqwe')
        mock.query.return_value.filter_by.return_value.first.\
            assert_called_with()
        mock.add.assert_called()

    def test_add_organizations_organization_id(self):
        """Should update Organizations table if organization_id provided"""
        mock = MagicMock()
        targets = [{
            "organization_id": "asdasd"
        }]
        mock.query.return_value.filter_by.return_value.\
            first.return_value = None
        self.db.add_organizations(targets, mock)
        mock.query.assert_called_with(synack.db.models.Organization)
        mock.query.return_value.filter_by.assert_called_with(slug='asdasd')
        mock.query.return_value.filter_by.return_value.first.\
            assert_called_with()
        mock.add.assert_called()

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

    def test_template_dir(self):
        """Should pull template dir from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = '/tmp'
        self.db.template_dir

        self.assertEqual(pathlib.Path('/tmp'), self.db.template_dir)
        self.assertEqual(pathlib.Path('/tmp'), self.db.state.template_dir)
        self.db.get_config.assert_called_with('template_dir')
        self.db.template_dir = '/tmp'
        self.db.set_config.assert_called_with('template_dir', '/tmp')

    def test_template_dir_state(self):
        """Should provide state template_dir over database"""
        self.db.get_config = MagicMock()
        self.db.state.template_dir = pathlib.Path('/tmp')

        self.assertEqual(pathlib.Path('/tmp'), self.db.template_dir)
        self.db.get_config.assert_not_called()

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

    def test_notifications_token(self):
        """Should pull notifications_token from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = "123"

        self.assertEqual("123", self.db.notifications_token)
        self.db.get_config.assert_called_with("notifications_token")
        self.db.notifications_token = "123"
        self.db.set_config.assert_called_with("notifications_token", "123")

    def test_email(self):
        """Should pull email from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = "1@2.com"

        self.assertEqual("1@2.com", self.db.email)

    def test_email_state(self):
        """Should pull email from the state"""
        self.db.get_config = MagicMock()
        self.db.state.email = "1@2.com"

        self.assertEqual("1@2.com", self.db.email)
        self.assertEqual("1@2.com", self.db.state.email)

    def test_email_prompt(self):
        """Should ask the user for email if none"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = None

        with patch("builtins.input") as mock_input:
            mock_input.return_value = '1@2.com'
            self.assertEqual('1@2.com', self.db.email)
            mock_input.assert_called_with('Synack Email: ')
        self.assertEqual('1@2.com', self.db.state.email)
        self.db.get_config.assert_called_with("email")
        self.db.set_config.assert_called_with("email", "1@2.com")

    def test_password(self):
        """Should pull password from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = "password1234"

        self.assertEqual("password1234", self.db.password)

    def test_password_state(self):
        """Should pull password from the state"""
        self.db.get_config = MagicMock()
        self.db.state.password = "password1234"

        self.assertEqual("password1234", self.db.password)
        self.assertEqual("password1234", self.db.state.password)

    def test_password_prompt(self):
        """Should ask the user for password if none"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = None

        with patch("builtins.input") as mock_input:
            mock_input.return_value = 'password1234'
            self.assertEqual('password1234', self.db.password)
            mock_input.assert_called_with('Synack Password: ')
        self.assertEqual('password1234', self.db.state.password)
        self.db.get_config.assert_called_with("password")
        self.db.set_config.assert_called_with("password", "password1234")

    def test_otp_secret(self):
        """Should pull otp_secret from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = "ABCDEFGH"

        self.assertEqual("ABCDEFGH", self.db.otp_secret)
        self.assertEqual("ABCDEFGH", self.db.state.otp_secret)

    def test_otp_secret_state(self):
        """Should pull otp_secret from the state"""
        self.db.get_config = MagicMock()
        self.db.state.otp_secret = "ABCDEFGH"

        self.assertEqual("ABCDEFGH", self.db.otp_secret)
        self.assertEqual("ABCDEFGH", self.db.state.otp_secret)

    def test_otp_secret_prompt(self):
        """Should ask the user for otp_secret if none"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = None

        with patch("builtins.input") as mock_input:
            mock_input.return_value = 'ABCDEFGH'
            self.assertEqual('ABCDEFGH', self.db.otp_secret)
            mock_input.assert_called_with('Synack OTP Secret: ')
        self.assertEqual('ABCDEFGH', self.db.state.otp_secret)
        self.db.get_config.assert_called_with("otp_secret")
        self.db.set_config.assert_called_with("otp_secret", "ABCDEFGH")

    def test_debug(self):
        """Should pull debug from the database"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = False

        self.assertEqual(False, self.db.debug)
        self.db.get_config.assert_called_with("debug")

        self.db.debug = True
        self.assertEqual(True, self.db.debug)
        self.assertEqual(True, self.db.state.debug)

    def test_debug_state(self):
        """Should pull debug from the State"""
        self.db.get_config = MagicMock()
        self.db.set_config = MagicMock()
        self.db.get_config.return_value = False

        self.db.state.debug = True
        self.assertEqual(True, self.db.debug)
        self.assertEqual(True, self.db.state.debug)
