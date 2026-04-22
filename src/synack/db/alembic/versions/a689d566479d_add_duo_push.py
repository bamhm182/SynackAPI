"""add duo push

Revision ID: a689d566479d
Revises: 1434aa7ed47c
Create Date: 2026-03-23 21:30:21.136169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a689d566479d'
down_revision = '1434aa7ed47c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.add_column(sa.Column('duo_akey', sa.VARCHAR(32), server_default=''))
        batch_op.add_column(sa.Column('duo_pkey', sa.VARCHAR(32), server_default=''))
        batch_op.add_column(sa.Column('duo_host', sa.VARCHAR(64), server_default=''))
        batch_op.add_column(sa.Column('duo_rsa_key', sa.Text(), server_default=''))


def downgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.drop_column('duo_akey')
        batch_op.drop_column('duo_pkey')
        batch_op.drop_column('duo_host')
        batch_op.drop_column('duo_rsa_key')
