"""add unique ips constraint

Revision ID: 6814001a4ed4
Revises: 753c42281f78
Create Date: 2025-01-26 05:19:35.150476

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '6814001a4ed4'
down_revision = '753c42281f78'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('ips') as batch_op:
        batch_op.create_unique_constraint('uq_ip', ['ip', 'target'])


def downgrade():
    with op.batch_alter_table('ips') as batch_op:
        batch_op.drop_constraint('uq_ip', type_='unique')
