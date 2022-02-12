"""db/models/organization.py

Database Model for the Organization items
"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Organization(Base):
    __tablename__ = 'organizations'
    slug = sa.Column(sa.VARCHAR(20), primary_key=True)
