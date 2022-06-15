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
from synack.db.models import IP
from synack.db.models import Organization
from synack.db.models import Port
from synack.db.models import Url

from .base import Plugin


class Db(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sqlite_db = self.state.config_dir / 'synackapi.db'

        self.set_migration()

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

    def add_ips(self, results, session=None):
        close = False
        if session is None:
            session = self.Session()
            close = True
        q = session.query(IP)
        for result in results:
            filt = sa.and_(
                IP.ip.like(result.get('ip')),
                IP.target.like(result.get('target'))
            )
            db_ip = q.filter(filt).first()
            if not db_ip:
                db_ip = IP(
                    ip=result.get('ip'),
                    target=result.get('target'))
                session.add(db_ip)
        if close:
            session.commit()
            session.close()

    def add_organizations(self, targets, session=None):
        close = False
        if session is None:
            session = self.Session()
            close = True
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
        if close:
            session.commit()
            session.close()

    def add_ports(self, results):
        self.add_ips(results)
        session = self.Session()
        q = session.query(Port)
        ips = session.query(IP)
        for result in results:
            ip = ips.filter_by(ip=result.get('ip'))
            if ip:
                ip = ip.first()
                for port in result.get('ports', []):
                    filt = sa.and_(
                        Port.port.like(port.get('port')),
                        Port.protocol.like(port.get('protocol')),
                        Port.ip.like(ip.id),
                        Port.source.like(result.get('source')))
                    db_port = q.filter(filt)
                    if not db_port:
                        db_port = Port(
                            port=port.get('port'),
                            protocol=port.get('protocol'),
                            service=port.get('service'),
                            ip=ip.id,
                            source=result.get('source'),
                            open=port.get('open'),
                            updated=port.get('updated')
                        )
                    else:
                        db_port = db_port.first()
                        db_port.service = port.get('service', db_port.service)
                        db_port.open = port.get('open', db_port.open)
                        db_port.updated = port.get('updated', db_port.updated)
                    session.add(db_port)
        session.commit()
        session.close()

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

    def add_urls(self, results, **kwargs):
        self.add_ips(results)
        session = self.Session()
        q = session.query(Url)
        ips = session.query(IP)
        for result in results:
            ip = ips.filter_by(ip=result.get('ip'))
            if ip:
                ip = ip.first()
                for url in result.get('urls', []):
                    filt = sa.and_(
                        Url.url.like(url.get('url')),
                        Url.ip.like(ip.id))
                    db_url = q.filter(filt)
                    if not db_url:
                        db_url = Url(
                            ip=ip.id,
                            url=url.get('url'),
                            screenshot_url=url.get('screenshot_url'),
                        )
                    else:
                        db_url = db_url.first()
                        db_url.ip = ip.id
                        db_url.url = url.get('url')
                        db_url.screenshot_url = url.get('screenshot_url')
                    session.add(db_url)
        session.commit()
        session.close()

    def find_targets(self, **kwargs):
        session = self.Session()
        targets = session.query(Target).filter_by(**kwargs).all()
        session.expunge_all()
        session.close()
        return targets

    def find_ports(self, port=None, protocol=None, source=None, ip=None, **kwargs):
        session = self.Session()
        query = session.query(Port)
        if port:
            query = query.filter_by(port=port)
        if protocol:
            query = query.filter_by(protocol=protocol)
        if source:
            query = query.filter_by(source=source)

        query = query.join(IP)
        if ip:
            query = query.filter_by(ip=ip)

        query = query.join(Target)
        if kwargs:
            query = query.filter_by(**kwargs)

        ports = query.all()

        ips = dict()
        for port in ports:
            ips[port.ip] = ips.get(port.ip, list())
            ips[port.ip].append({
                "port": port.port,
                "protocol": port.protocol,
                "service": port.service,
                "source": port.source,
                "open": port.open,
                "updated": port.updated,
            })

        ret = list()
        for ip_id in ips.keys():
            ip = session.query(IP).filter_by(id=ip_id).first()
            ret.append({
                "ip": ip.ip,
                "target": ip.target,
                "ports": ips[ip_id]
            })

        session.expunge_all()
        session.close()
        return ret

    def find_ips(self, ip=None, **kwargs):
        session = self.Session()
        query = session.query(IP)

        if ip:
            query = query.filter_by(ip=ip)

        query = query.join(Target)
        if kwargs:
            query = query.filter_by(**kwargs)

        ips = query.all()

        session.expunge_all()
        session.close()

        ret = list()
        for ip in ips:
            ret.append({
                "ip": ip.ip,
                "target": ip.target
            })

        return ret

    def find_urls(self, url=None, ip=None, **kwargs):
        session = self.Session()
        query = session.query(Url)
        if url:
            query = query.filter_by(url=url)

        query = query.join(IP)
        if ip:
            query = query.filter_by(ip=ip)

        query = query.join(Target)
        if kwargs:
            query = query.filter_by(**kwargs)

        urls = query.all()

        ips = dict()
        for url in urls:
            ips[url.ip] = ips.get(url.ip, list())
            ips[url.ip].append({
                'url': url.url,
                'screenshot_url': url.screenshot_url,
            })

        ret = list()
        for ip_id in ips.keys():
            ip = session.query(IP).filter_by(id=ip_id).first()
            ret.append({
                "ip": ip.ip,
                "target": ip.target,
                "urls": ips[ip_id]
            })

        session.expunge_all()
        session.close()
        return ret

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
    def ports(self):
        session = self.Session()
        ports = session.query(Port).all()
        session.close()
        return ports

    @property
    def ips(self):
        session = self.Session()
        ips = session.query(IP).all()
        session.close()
        return ips

    @property
    def urls(self):
        session = self.Session()
        urls = session.query(Url).all()
        session.close()
        return urls

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
            if not ret:
                ret = input("Synack Email: ")
                self.email = ret
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
            if not ret:
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
            if not ret:
                ret = input("Synack Password: ")
                self.password = ret
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
