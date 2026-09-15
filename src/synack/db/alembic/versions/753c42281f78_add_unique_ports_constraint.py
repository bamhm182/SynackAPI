"""add unique ports constraint

Revision ID: 753c42281f78
Revises: c2e6de9ffc5e
Create Date: 2025-01-26 05:07:23.252004

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '753c42281f78'
down_revision = 'c2e6de9ffc5e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ports') as batch_op:
        batch_op.create_unique_constraint('uq_port', ['port', 'protocol', 'ip', 'source'])


def downgrade():
    with op.batch_alter_table('ports') as batch_op:
        batch_op.drop_constraint('uq_port', type_='unique')
