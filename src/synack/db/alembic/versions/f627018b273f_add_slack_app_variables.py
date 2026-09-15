"""add slack app variables

Revision ID: f627018b273f
Revises: 349c447c0d37
Create Date: 2025-01-06 20:44:52.383303

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f627018b273f'
down_revision = '349c447c0d37'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.add_column(sa.Column('slack_app_token', sa.VARCHAR(100), server_default=''))
        batch_op.add_column(sa.Column('slack_channel', sa.VARCHAR(100), server_default=''))


def downgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.drop_column('slack_app_token')
        batch_op.drop_column('slack_channel')
