"""plugins/db.py

Manipulates/Reads the database and provides it to other plugins
"""

import alembic.config
import alembic.command
from Crypto.PublicKey import RSA
import sqlalchemy as sa

from sqlalchemy.dialects.sqlite import insert as sqlite_insert

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
        self.sqlite_db = self._state.config_dir / 'synackapi.db'

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
            db_c.passed_practical = c['passed']
            db_c.passed_written = c['passed']
        session.commit()
        session.close()

    def add_ips(self, results, session=None):
        close = False

        if session is None:
            session = self.Session()
            close = True

        ips_data = list()

        for result in results:
            if result.get('ip') and result.get('target'):
                ips_data.append({
                    'ip': result['ip'],
                    'target': result['target']
                })
                if len(ips_data) > 15000:
                    stmt = sqlite_insert(IP).values(ips_data)
                    stmt = stmt.on_conflict_do_nothing(
                        index_elements=['ip', 'target'],
                    )
                    session.execute(stmt)
                    ips_data = list()

        if ips_data:
            stmt = sqlite_insert(IP).values(ips_data)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['ip', 'target'],
            )
            session.execute(stmt)

        if close:
            session.commit()
            session.close()

    def add_organizations(self, targets, session=None):
        close = False

        if session is None:
            session = self.Session()
            close = True

        organizations_data = list()

        if isinstance(targets, dict):
            targets = [value for key, value in targets.items()]

        for target in targets:
            if isinstance(target.get('organization'), str):
                slug = target.get('organization')
            else:
                slug = target.get('organization_id', target.get('organization', {}).get('slug'))
            if slug:
                organizations_data.append({'slug': slug})

        if organizations_data:
            stmt = sqlite_insert(Organization).values(organizations_data)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['slug'],
            )
            session.execute(stmt)

        if close:
            session.commit()
            session.close()

    def add_ports(self, results):
        session = self.Session()

        self.add_ips(results, session)
        ip_map = {ip.ip: ip.id for ip in session.query(IP.ip, IP.id).all()}

        ports_data = list()

        for result in results:
            ip_id = ip_map.get(result.get('ip'))
            if ip_id:
                for port in result.get('ports', []):
                    ports_data.append({
                        'port': port.get('port'),
                        'protocol': port.get('protocol'),
                        'service': port.get('service'),
                        'ip': ip_id,
                        'source': result.get('source'),
                        'open': port.get('open'),
                        'updated': port.get('updated')
                    })
                    if len(ports_data) > 15000:
                        stmt = sqlite_insert(Port).values(ports_data)
                        stmt = stmt.on_conflict_do_update(
                            index_elements=['port', 'protocol', 'ip', 'source'],
                            set_={
                                'service': stmt.excluded.service,
                                'open': stmt.excluded.open,
                                'updated': stmt.excluded.updated
                            }
                        )
                        session.execute(stmt)
                        ports_data = list()

        if ports_data:
            stmt = sqlite_insert(Port).values(ports_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['port', 'protocol', 'ip', 'source'],
                set_={
                    'service': stmt.excluded.service,
                    'open': stmt.excluded.open,
                    'updated': stmt.excluded.updated
                }
            )
            session.execute(stmt)

        session.commit()
        session.close()

    def add_targets(self, targets, **kwargs):
        session = self.Session()

        self.add_organizations(targets, session)
        db_orgs = [org[0] for org in session.query(Organization.slug).all()]

        targets_data = list()

        if isinstance(targets, dict):
            targets = [value for key, value in targets.items()]

        for target in targets:
            if isinstance(target.get('organization'), str):
                org_slug = target.get('organization')
            else:
                org_slug = target.get('organization_id', target.get('organization', {}).get('slug'))
            if isinstance(target.get('category'), int):
                category = target.get('category')
            else:
                category = target.get('category', {}).get('id')
            if org_slug in db_orgs:
                target_data = {
                    'slug': target.get('id', target.get('slug')),
                    'codename': target.get('codename'),
                    'category': category,
                    'organization': org_slug,
                    'date_updated': target.get('dateUpdated', target.get('date_updated')),
                    'is_active': target.get('isActive', target.get('is_active')),
                    'is_new': target.get('isNew', target.get('is_new')),
                    'is_registered': target.get('isRegistered', target.get('is_registered')),
                    'last_submitted': target.get('lastSubmitted', target.get('last_submitted'))
                }
                target_data.update(kwargs)
                targets_data.append(target_data)

        if targets_data:
            stmt = sqlite_insert(Target).values(targets_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['slug'],
                set_={
                    'category': stmt.excluded.category,
                    'codename': stmt.excluded.codename,
                    'organization': stmt.excluded.organization,
                    'date_updated': stmt.excluded.date_updated,
                    'is_active': stmt.excluded.is_active,
                    'is_new': stmt.excluded.is_new,
                    'is_registered': stmt.excluded.is_registered,
                    'last_submitted': stmt.excluded.last_submitted,
                }
            )
            session.execute(stmt)

        session.commit()
        session.close()

    def add_urls(self, results):
        session = self.Session()

        self.add_ips(results, session)
        ip_map = {ip.ip: ip.id for ip in session.query(IP.ip, IP.id).all()}

        urls_data = list()

        for result in results:
            ip_id = ip_map.get(result.get('ip'))
            if ip_id:
                for url in result.get('urls', []):
                    urls_data.append({
                        'url': url.get('url'),
                        'screenshot_url': url.get('screenshot_url')
                    })

        if urls_data:
            stmt = sqlite_insert(Url).values(urls_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['ip', 'url'],
                set_={
                    'screenshot_url': stmt.excluded.screenshot_url
                }
            )
            session.execute(stmt)

        session.commit()
        session.close()

    @property
    def api_token(self):
        return self.get_config('api_token')

    @api_token.setter
    def api_token(self, value):
        self.set_config('api_token', value)

    @property
    def categories(self):
        session = self.Session()
        categories = session.query(Category).all()
        session.close()
        return categories

    @property
    def debug(self):
        return self.get_config('debug')

    @debug.setter
    def debug(self, value):
        self.set_config('debug', value)

    @property
    def duo_akey(self):
        return self.get_config('duo_akey')

    @duo_akey.setter
    def duo_akey(self, value):
        self.set_config('duo_akey', value)

    @property
    def duo_host(self):
        return self.get_config('duo_host')

    @duo_host.setter
    def duo_host(self, value):
        self.set_config('duo_host', value)

    @property
    def duo_pkey(self):
        return self.get_config('duo_pkey')

    @duo_pkey.setter
    def duo_pkey(self, value):
        self.set_config('duo_pkey', value)

    @property
    def duo_rsa_key(self):
        pem = self.get_config('duo_rsa_key')
        if not pem:
            rsa_key = RSA.generate(2048)
            pem = rsa_key.export_key('PEM').decode('utf-8')
            self.set_config('duo_rsa_key', pem)
        return pem

    @duo_rsa_key.setter
    def duo_rsa_key(self, value):
        self.set_config('duo_rsa_key', value)

    @property
    def email(self):
        ret = self.get_config('email')
        if not ret:
            ret = input('Synack Email: ')
            self.email = ret
        return ret

    @email.setter
    def email(self, value):
        self.set_config('email', value)

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

    def find_targets(self, **kwargs):
        session = self.Session()
        query = session.query(Target)

        filters = list()

        for key, value in kwargs.items():
            if hasattr(Target, key):
                if kwargs.get('like'):
                    filters.append(getattr(Target, key).like(f'%{value}%'))
                else:
                    filters.append(getattr(Target, key) == value)

        if filters:
            if kwargs.get('or'):
                query = query.filter(sa.or_(*filters))
            else:
                query = query.filter(sa.and_(*filters))

        targets = query.all()

        session.expunge_all()
        session.close()
        return targets

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
    def ips(self):
        session = self.Session()
        ips = session.query(IP).all()
        session.close()
        return ips

    @property
    def notifications_token(self):
        return self.get_config('notifications_token')

    @notifications_token.setter
    def notifications_token(self, value):
        self.set_config('notifications_token', value)

    @property
    def otp_count(self):
        ret = self.get_config('otp_count')
        if not ret:
            ret = input('Synack OTP Count: ')
            self.otp_count = int(ret)
        return ret

    @otp_count.setter
    def otp_count(self, value):
        self.set_config('otp_count', value)

    @property
    def otp_secret(self):
        ret = self.get_config('otp_secret')
        if not ret:
            ret = input('Synack OTP Secret: ')
            self.otp_secret = ret
        return ret

    @otp_secret.setter
    def otp_secret(self, value):
        self.set_config('otp_secret', value)

    @property
    def password(self):
        ret = self.get_config('password')
        if not ret:
            ret = input('Synack Password: ')
            self.password = ret
        return ret

    @password.setter
    def password(self, value):
        self.set_config('password', value)

    @property
    def ports(self):
        session = self.Session()
        ports = session.query(Port).all()
        session.close()
        return ports

    @property
    def proxies(self):
        return {
            'http': self.get_config('http_proxy'),
            'https': self.get_config('https_proxy')
        }

    def remove_targets(self, **kwargs):
        session = self.Session()
        session.query(Target).filter_by(**kwargs).delete()
        session.commit()
        session.close()

    @property
    def scratchspace_dir(self):
        return Path(self.get_config('scratchspace_dir')).expanduser().resolve()

    @scratchspace_dir.setter
    def scratchspace_dir(self, value):
        self.set_config('scratchspace_dir', str(value))

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
        config.set_main_option('path_separator', 'os')
        config.set_main_option('sqlalchemy.url',
                               f'sqlite:///{str(self.sqlite_db)}')
        alembic.command.upgrade(config, 'head')

    @property
    def slack_app_token(self):
        ret = self.get_config('slack_app_token')
        if not ret:
            ret = input('Slack App Token: ')
            self.slack_app_token = ret
        return ret

    @slack_app_token.setter
    def slack_app_token(self, value):
        self.set_config('slack_app_token', value)

    @property
    def slack_channel(self):
        ret = self.get_config('slack_channel')
        if not ret:
            ret = input('Slack Channel: ')
            self.slack_channel = ret
        return ret

    @slack_channel.setter
    def slack_channel(self, value):
        self.set_config('slack_channel', value)

    @property
    def slack_url(self):
        return self.get_config('slack_url')

    @slack_url.setter
    def slack_url(self, value):
        self.set_config('slack_url', value)

    @property
    def smtp_email_from(self):
        return self.get_config('smtp_email_from')

    @smtp_email_from.setter
    def smtp_email_from(self, value):
        self.set_config('smtp_email_from', value)

    @property
    def smtp_email_to(self):
        return self.get_config('smtp_email_to')

    @smtp_email_to.setter
    def smtp_email_to(self, value):
        self.set_config('smtp_email_to', value)

    @property
    def smtp_password(self):
        return self.get_config('smtp_password')

    @smtp_password.setter
    def smtp_password(self, value):
        self.set_config('smtp_password', value)

    @property
    def smtp_port(self):
        return self.get_config('smtp_port')

    @smtp_port.setter
    def smtp_port(self, value):
        self.set_config('smtp_port', value)

    @property
    def smtp_server(self):
        return self.get_config('smtp_server')

    @smtp_server.setter
    def smtp_server(self, value):
        self.set_config('smtp_server', value)

    @property
    def smtp_starttls(self):
        return self.get_config('smtp_starttls')

    @smtp_starttls.setter
    def smtp_starttls(self, value):
        self.set_config('smtp_starttls', value)

    @property
    def smtp_username(self):
        return self.get_config('smtp_username')

    @smtp_username.setter
    def smtp_username(self, value):
        self.set_config('smtp_username', value)

    @property
    def synack_domain(self):
        return self.get_config('synack_domain')

    @synack_domain.setter
    def synack_domain(self, value):
        self.set_config('synack_domain', value)

    @property
    def targets(self):
        session = self.Session()
        targets = session.query(Target).all()
        session.close()
        return targets

    @property
    def template_dir(self):
        return Path(self.get_config('template_dir')).expanduser().resolve()

    @template_dir.setter
    def template_dir(self, value):
        self.set_config('template_dir', value)

    @property
    def urls(self):
        session = self.Session()
        urls = session.query(Url).all()
        session.close()
        return urls

    @property
    def use_proxies(self):
        return self.get_config('use_proxies')

    @use_proxies.setter
    def use_proxies(self, value):
        self.set_config('use_proxies', value)

    @property
    def user_id(self):
        return self.get_config('user_id')

    @user_id.setter
    def user_id(self, value):
        self.set_config('user_id', value)

    @property
    def use_scratchspace(self):
        return self.get_config('use_scratchspace')

    @use_scratchspace.setter
    def use_scratchspace(self, value):
        self.set_config('use_scratchspace', value)
