"""add organization name

Revision ID: b3f1d2e4c5a6
Revises: a689d566479d
Create Date: 2026-04-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3f1d2e4c5a6'
down_revision = 'a689d566479d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('organizations') as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(100)))


def downgrade():
    with op.batch_alter_table('organizations') as batch_op:
        batch_op.drop_column('name')
