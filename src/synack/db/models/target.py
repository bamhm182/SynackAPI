"""db/models/target.py

Database Model for the Target item
"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from .category import Category
from .organization import Organization

Base = declarative_base()


class Target(Base):
    __tablename__ = 'targets'
    slug = sa.Column(sa.VARCHAR(20), primary_key=True)
    category = sa.Column(sa.INTEGER, sa.ForeignKey(Category.id))
    organization = sa.Column(sa.VARCHAR(20), sa.ForeignKey(Organization.slug))
    average_payout = sa.Column(sa.REAL, default=0.0)
    codename = sa.Column(sa.VARCHAR(100))
    date_updated = sa.Column(sa.INTEGER, default=0)
    end_date = sa.Column(sa.INTEGER, default=0)
    is_active = sa.Column(sa.BOOLEAN, default=False)
    is_new = sa.Column(sa.BOOLEAN, default=False)
    is_registered = sa.Column(sa.BOOLEAN, default=True)
    is_updated = sa.Column(sa.BOOLEAN, default=False)
    last_submitted = sa.Column(sa.INTEGER, default=0)
    start_date = sa.Column(sa.INTEGER, default=0)
    vulnerability_discovery = sa.Column(sa.BOOLEAN, default=False)
