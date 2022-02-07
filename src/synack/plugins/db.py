"""plugins/db.py

Manipulates/Reads the database and provides it to other plugins
"""

import yaml
import alembic.config
import alembic.command
import logging
import sqlalchemy as sa

from pathlib import Path
from sqlalchemy.orm import sessionmaker
from synack.db.models import Target
from synack.db.models import Config
from synack.db.models import Category

from .base import Plugin


class Db(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sqlite_db = self.config_dir / 'synackapi.db'
        engine = sa.create_engine(f'sqlite:///{str(self.sqlite_db)}')
        self.Session = sessionmaker(bind=engine)

        if not self.sqlite_db.is_file():
            self.migrate()

    def migrate(self):
        alembic_ini = Path(__file__).parent.parent / 'db/alembic.ini'

        config = alembic.config.Config(str(alembic_ini))
        config.set_main_option('sqlalchemy.url', f'sqlite:///{str(self.sqlite_db)}')
        alembic.command.upgrade(config, 'head')

    def get_config(self, name):
        session = self.Session()
        config = session.query(Config).filter_by(id=1).first()
        if not config:
            config = Config()
            session.add(config)
        session.close()
        return getattr(config, name)

    def set_config(self, name, value):
        session = self.Session()
        config = session.query(Config).filter_by(id=1).first()
        if not config:
            config = Config()
            session.add(config)
        setattr(config, name, value)
        session.commit()
        session.close()

    def update_categories(self, categories):
        session = self.Session()
        q = session.query(Category)
        for c in categories:
            db_c = q.filter_by(id=c.get('id')).first()
            if not db_c:
                db_c = Category()
                session.add(db_c)
            db_c.id = c['category_id']
            db_c.name = c['category_name']
            db_c.passed_practical = c['practical_assessment']['passed']
            db_c.passed_written = c['written_assessment']['passed']
        session.commit()
        session.close()

    def update_targets(self, targets):
        session = self.Session()
        q = session.query(Target)
        for t in targets:
            db_t = q.filter_by(slug=t.get('slug', t.get('id'))).first()
            if not db_t:
                db_t = Target(id=t.get('slug', t.get('id')))
                session.add(db_t)
            for k in t.keys():
                setattr(db_t, k, t[k])
            db_t.category = t['category']['id']
            db_t.date_updated = t.get('dateUpdated')
            db_t.is_active = t.get('isActive')
            db_t.is_new = t.get('isNew')
            db_t.is_registered = t.get('isRegistered')
            db_t.is_updated = t.get('isUpdated')
            db_t.last_submitted = t.get('lastSubmitted')
        session.commit()
        session.close()

    def wipe_targets(self):
        session = self.Session()
        session.query(Target).delete()
        session.commit()
        session.close()

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
    def use_proxies(self):
        return self.get_config('use_proxies')

    @use_proxies.setter
    def use_proxies(self, value):
        self.set_config('use_proxies', value)

    @property
    def template_dir(self):
        return self.get_config('template_dir')

    @template_dir.setter
    def template_dir(self, value):
        self.set_config('template_dir', value)

    @property
    def notifications_token(self):
        return self.get_config('notifications_token')

    @notifications_token.setter
    def notifications_token(self, value):
        self.set_config('notifications_token', value)

    @property
    def email(self):
        return self.get_config('email')

    @email.setter
    def email(self, value):
        self.set_config('email', value)

    @property
    def password(self):
        return self.get_config('password')

    @password.setter
    def password(self, value):
        self.set_config('password', value)

    @property
    def otp_secret(self):
        return self.get_config('otp_secret')

    @otp_secret.setter
    def otp_secret(self, value):
        self.set_config('otp_secret', value)

    @property
    def config_dir(self):
        if not self.state.config_dir:
            ret = pathlib.Path(self.get_config('config_dir')).expanduser().resolve()
            self.state.config_dir = ret
        else:
            ret = self.state.config_dir
        return ret

    @config_dir.setter
    def config_dir(self, value):
        self.set_config('config_dir', value)

    @property
    def template_dir(self):
        if not self.state.template_dir:
            ret = pathlib.Path(self.get_config('template_dir')).expanduser().resolve()
            self.state.template_dir = ret
        else:
            ret = self.state.template_dir
        return ret

    @template_dir.setter
    def template_dir(self, value):
        self.set_config('template_dir', value)

    @property
    def categories(self):
        session = self.Session()
        categories = session.query(Category).all()
        session.close()
        print(categories)
        return categories

    @categories.setter
    def categories(self, value):
        self.update_categories(value)

    @property
    def debug(self):
        return self.state.debug if self.state.debug != None else self.get_config('debug')

    @debug.setter
    def debug(self, value):
        self.set_config('debug', value)
        
