"""add organization name

Revision ID: 8b478a84c1a6
Revises: 6f542023f57e
Create Date: 2025-02-11 13:05:40.939271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b478a84c1a6'
down_revision = '6f542023f57e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('organizations') as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(100)))


def downgrade():
    with op.batch_alter_table('organizations') as batch_op:
        batch_op.drop_column('name')
