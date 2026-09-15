"""add synack_domain

Revision ID: 1434aa7ed47c
Revises: 6814001a4ed4
Create Date: 2025-02-06 04:19:28.655055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1434aa7ed47c'
down_revision = '6814001a4ed4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.add_column(sa.Column('synack_domain', sa.VARCHAR(100), server_default='synack.com'))


def downgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.drop_column('synack_domain')
