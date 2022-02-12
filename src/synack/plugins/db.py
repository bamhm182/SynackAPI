"""plugins/db.py

Manipulates/Reads the database and provides it to other plugins
"""

import alembic.config
import alembic.command
import sqlalchemy as sa

from pathlib import Path
from sqlalchemy.orm import sessionmaker
from synack.db.models import Target
from synack.db.models import Config
from synack.db.models import Category
from synack.db.models import Organization

from .base import Plugin


class Db(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sqlite_db = self.state.config_dir / 'synackapi.db'
        engine = sa.create_engine(f'sqlite:///{str(self.sqlite_db)}')
        sa.event.listen(engine, 'connect', self._fk_pragma_on_connect)
        self.Session = sessionmaker(bind=engine)

    @staticmethod
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON')

    def add_categories(self, categories):
        session = self.Session()
        q = session.query(Category)
        for c in categories:
            db_c = q.filter_by(id=c.get('category_id')).first()
            if not db_c:
                db_c = Category(id=c['category_id'])
                session.add(db_c)
            db_c.name = c['category_name']
            db_c.passed_practical = c['practical_assessment']['passed']
            db_c.passed_written = c['written_assessment']['passed']
        session.commit()
        session.close()

    def add_organizations(self, targets, session):
        q = session.query(Organization)
        for t in targets:
            if t.get('organization'):
                slug = t['organization']['slug']
            else:
                slug = t.get('organization_id')
            db_o = q.filter_by(slug=slug).first()
            if not db_o:
                db_o = Organization(slug=slug)
                session.add(db_o)

    def add_targets(self, targets, **kwargs):
        session = self.Session()
        self.add_organizations(targets, session)
        q = session.query(Target)
        for t in targets:
            if t.get('organization'):
                org_slug = t['organization']['slug']
            else:
                org_slug = t.get('organization_id')
            slug = t.get('slug', t.get('id'))
            db_t = q.filter_by(slug=slug).first()
            if not db_t:
                db_t = Target(slug=slug)
                session.add(db_t)
            for k in t.keys():
                setattr(db_t, k, t[k])
            db_t.category = t['category']['id']
            db_t.organization = org_slug
            db_t.date_updated = t.get('dateUpdated')
            db_t.is_active = t.get('isActive')
            db_t.is_new = t.get('isNew')
            db_t.is_registered = t.get('isRegistered')
            db_t.is_updated = t.get('isUpdated')
            db_t.last_submitted = t.get('lastSubmitted')
            for k in kwargs.keys():
                setattr(db_t, k, kwargs[k])
        session.commit()
        session.close()

    def find_targets(self, **kwargs):
        session = self.Session()
        targets = session.query(Target).filter_by(**kwargs).all()
        session.expunge_all()
        session.close()
        return targets

    def get_config(self, name=None):
        session = self.Session()
        config = session.query(Config).filter_by(id=1).first()
        if not config:
            config = Config()
            session.add(config)
        session.close()
        return getattr(config, name) if name else config

    def remove_targets(self, **kwargs):
        session = self.Session()
        session.query(Target).filter_by(**kwargs).delete()
        session.commit()
        session.close()

    def set_config(self, name, value):
        session = self.Session()
        config = session.query(Config).filter_by(id=1).first()
        if not config:
            config = Config()
            session.add(config)
        setattr(config, name, value)
        session.commit()
        session.close()

    def set_migration(self):
        db_folder = Path(__file__).parent.parent / 'db'

        config = alembic.config.Config()
        config.set_main_option('script_location', str(db_folder / 'alembic'))
        config.set_main_option('version_locations',
                               str(db_folder / 'alembic/versions'))
        config.set_main_option('sqlalchemy.url',
                               f'sqlite:///{str(self.sqlite_db)}')
        alembic.command.upgrade(config, 'head')

    @property
    def categories(self):
        session = self.Session()
        categories = session.query(Category).all()
        session.close()
        return categories

    @property
    def proxies(self):
        if self.state.http_proxy is None:
            http_proxy = self.get_config('http_proxy')
        else:
            http_proxy = self.state.http_proxy

        if self.state.https_proxy is None:
            https_proxy = self.get_config('https_proxy')
        else:
            https_proxy = self.state.https_proxy

        return {
            'http': http_proxy,
            'https': https_proxy
        }

    @property
    def targets(self):
        session = self.Session()
        targets = session.query(Target).all()
        session.close()
        return targets

    @property
    def api_token(self):
        return self.get_config('api_token')

    @api_token.setter
    def api_token(self, value):
        self.set_config('api_token', value)

    @property
    def debug(self):
        if self.state.debug is None:
            return self.get_config('debug')
        else:
            return self.state.debug

    @debug.setter
    def debug(self, value):
        self.state.debug = value
        self.set_config('debug', value)

    @property
    def email(self):
        if self.state.email is None:
            ret = self.get_config('email')
            if ret is None:
                ret = input("Synack Email: ")
                self.email = ret
            self.state.email = ret
            return ret
        else:
            return self.state.email

    @email.setter
    def email(self, value):
        self.state.email = value
        self.set_config('email', value)

    @property
    def http_proxy(self):
        return self.get_config('http_proxy')

    @http_proxy.setter
    def http_proxy(self, value):
        self.set_config('http_proxy', value)

    @property
    def https_proxy(self):
        return self.get_config('https_proxy')

    @https_proxy.setter
    def https_proxy(self, value):
        self.set_config('https_proxy', value)

    @property
    def notifications_token(self):
        return self.get_config('notifications_token')

    @notifications_token.setter
    def notifications_token(self, value):
        self.set_config('notifications_token', value)

    @property
    def otp_secret(self):
        if self.state.otp_secret is None:
            ret = self.get_config('otp_secret')
            if ret is None:
                ret = input("Synack OTP Secret: ")
                self.otp_secret = ret
            self.state.otp_secret = ret
            return ret
        else:
            return self.state.otp_secret

    @otp_secret.setter
    def otp_secret(self, value):
        self.state.otp_secret = value
        self.set_config('otp_secret', value)

    @property
    def password(self):
        if self.state.password is None:
            ret = self.get_config('password')
            if ret is None:
                ret = input("Synack Password: ")
                self.password = ret
            self.state.password = ret
            return ret
        else:
            return self.state.password

    @password.setter
    def password(self, value):
        self.state.password = value
        self.set_config('password', value)

    @property
    def template_dir(self):
        if self.state.template_dir is None:
            ret = Path(self.get_config('template_dir')).expanduser().resolve()
            self.state.template_dir = ret
        else:
            ret = self.state.template_dir
        return ret

    @template_dir.setter
    def template_dir(self, value):
        self.set_config('template_dir', value)

    @property
    def use_proxies(self):
        if self.state.use_proxies is None:
            return self.get_config('use_proxies')
        else:
            return self.state.use_proxies

    @use_proxies.setter
    def use_proxies(self, value):
        self.state.use_proxies = value
        self.set_config('use_proxies', value)

    @property
    def user_id(self):
        return self.get_config('user_id')

    @user_id.setter
    def user_id(self, value):
        self.set_config('user_id', value)
