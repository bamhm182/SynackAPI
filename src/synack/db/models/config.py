"""db/models/Config.py

Database Model for the Config item
"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Config(Base):
    __tablename__ = 'config'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    api_token = sa.Column(sa.VARCHAR(200), default='')
    debug = sa.Column(sa.BOOLEAN, default=False)
    email = sa.Column(sa.VARCHAR(150), default='')
    http_proxy = sa.Column(sa.VARCHAR(50), default='http://localhost:8080')
    https_proxy = sa.Column(sa.VARCHAR(50), default='http://localhost:8080')
    login = sa.Column(sa.BOOLEAN, default=True)
    notifications_token = sa.Column(sa.VARCHAR(1000), default='')
    otp_secret = sa.Column(sa.VARCHAR(50), default='')
    password = sa.Column(sa.VARCHAR(150), default='')
    scratchspace_dir = sa.Column(sa.VARCHAR(250), default='~/Scratchspace')
    slack_url = sa.Column(sa.VARCHAR(500), default='')
    smtp_email_from = sa.Column(sa.VARCHAR(250), default='')
    smtp_password = sa.Column(sa.VARCHAR(250), default='')
    smtp_port = sa.Column(sa.INTEGER, default=465)
    smtp_server = sa.Column(sa.VARCHAR(250), default='')
    smtp_email_to = sa.Column(sa.VARCHAR(250), default='')
    smtp_username = sa.Column(sa.VARCHAR(250), default='')
    smtp_starttls = sa.Column(sa.BOOLEAN, default=True)
    template_dir = sa.Column(sa.VARCHAR(250), default='~/Templates')
    user_id = sa.Column(sa.VARCHAR(20), default='')
    use_proxies = sa.Column(sa.BOOLEAN, default=False)
    use_scratchspace = sa.Column(sa.BOOLEAN, default=False)
