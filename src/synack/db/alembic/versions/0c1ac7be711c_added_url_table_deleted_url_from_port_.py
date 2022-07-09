"""Added Url table/Deleted url from Port table

Revision ID: 0c1ac7be711c
Revises: deb7dd07212c
Create Date: 2022-06-15 03:14:49.327185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c1ac7be711c'
down_revision = 'deb7dd07212c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('urls',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('ip', sa.Integer, sa.ForeignKey('ips.id')),
                    sa.Column('url', sa.VARCHAR(1024), server_default=''),
                    sa.Column('screenshot_url', sa.VARCHAR(1024), server_default=''))
    with op.batch_alter_table('ports') as batch_op:
        batch_op.drop_column('url')
        batch_op.drop_column('screenshot_url')


def downgrade():
    op.drop_table('urls')
    with op.batch_alter_table('ports') as batch_op:
        batch_op.add_column(sa.Column('url', sa.VARCHAR(200), server_default=''))
        batch_op.add_column(sa.Column('screenshot_url', sa.VARCHAR(1000), server_default=''))
