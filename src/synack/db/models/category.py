"""db/models/category.py

Database Model for the Category items
"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    name = sa.Column(sa.VARCHAR(100))
    passed_practical = sa.Column(sa.BOOLEAN, default=False)
    passed_written = sa.Column(sa.BOOLEAN, default=False)
