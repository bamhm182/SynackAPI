"""db/models/ip.py

Database Model for the IP item
"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from .target import Target

Base = declarative_base()


class IP(Base):
    __tablename__ = 'ips'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    ip = sa.Column(sa.VARCHAR(40))
    target = sa.Column(sa.VARCHAR(20), sa.ForeignKey(Target.slug))
    __table_args__ = (sa.UniqueConstraint('ip', 'target', name='uq_ip'),)
