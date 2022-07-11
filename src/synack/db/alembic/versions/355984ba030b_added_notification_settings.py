"""Added Notification Settings

Revision ID: 355984ba030b
Revises: 0c1ac7be711c
Create Date: 2022-07-10 15:06:58.823545

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '355984ba030b'
down_revision = '0c1ac7be711c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.add_column(sa.Column('scratchspace_dir', sa.VARCHAR(250), server_default='~/Scratchspace'))
        batch_op.add_column(sa.Column('slack_url', sa.VARCHAR(500), server_default=''))
        batch_op.add_column(sa.Column('smtp_email_from', sa.VARCHAR(250), server_default=''))
        batch_op.add_column(sa.Column('smtp_email_to', sa.VARCHAR(250), server_default=''))
        batch_op.add_column(sa.Column('smtp_password', sa.VARCHAR(250), server_default=''))
        batch_op.add_column(sa.Column('smtp_port', sa.INTEGER, server_default='465'))
        batch_op.add_column(sa.Column('smtp_server', sa.VARCHAR(250), server_default=''))
        batch_op.add_column(sa.Column('smtp_starttls', sa.BOOLEAN, server_default='t'))
        batch_op.add_column(sa.Column('smtp_username', sa.VARCHAR(250), server_default=''))


def downgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.drop_column('scratchspace_dir')
        batch_op.drop_column('slack_url')
        batch_op.drop_column('smtp_from_email')
        batch_op.drop_column('smtp_password')
        batch_op.drop_column('smtp_port')
        batch_op.drop_column('smtp_server')
        batch_op.drop_column('smtp_to_email')
        batch_op.drop_column('smtp_starttls')
        batch_op.drop_column('smtp_username')
