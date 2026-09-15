"""db/models/port.py

Database Model for the Port item
"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from .ip import IP

Base = declarative_base()


class Port(Base):
    __tablename__ = 'ports'
    id = sa.Column(sa.INTEGER, autoincrement=True, primary_key=True)
    ip = sa.Column(sa.VARCHAR(40), sa.ForeignKey(IP.id))
    port = sa.Column(sa.INTEGER)
    protocol = sa.Column(sa.VARCHAR(10))
    source = sa.Column(sa.VARCHAR(50))
    open = sa.Column(sa.BOOLEAN, default=False)
    service = sa.Column(sa.VARCHAR(200), default="")
    updated = sa.Column(sa.INTEGER, default=0)
    __table_args__ = (sa.UniqueConstraint('port', 'protocol', 'ip', 'source', name='uq_port'),)
