"""add otp_count

Revision ID: c2e6de9ffc5e
Revises: f627018b273f
Create Date: 2025-01-11 22:29:05.822904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2e6de9ffc5e'
down_revision = 'f627018b273f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.add_column(sa.Column('otp_count', sa.INTEGER, server_default='0'))


def downgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.drop_column('otp_count')
