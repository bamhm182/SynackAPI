"""Added IP/Port tables

Revision ID: deb7dd07212c
Revises: 649443e08834
Create Date: 2022-05-23 00:26:08.257745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'deb7dd07212c'
down_revision = '649443e08834'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ips',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('ip', sa.VARCHAR(40)),
                    sa.Column('target', sa.VARCHAR(20), sa.ForeignKey('targets.slug')))
    op.create_table('ports',
                    sa.Column('id', sa.INTEGER, autoincrement=True, primary_key=True),
                    sa.Column('ip', sa.VARCHAR(40), sa.ForeignKey('ips.id')),
                    sa.Column('port', sa.INTEGER),
                    sa.Column('protocol', sa.VARCHAR(10)),
                    sa.Column('source', sa.VARCHAR(50)),
                    sa.Column('open', sa.BOOLEAN, server_default='f'),
                    sa.Column('service', sa.VARCHAR(200), server_default=''),
                    sa.Column('updated', sa.INTEGER, server_default='0'),
                    sa.Column('url', sa.VARCHAR(200), server_default=''),
                    sa.Column('screenshot_url', sa.VARCHAR(1000), server_default=''))


def downgrade():
    op.drop_table('ips')
    op.drop_table('ports')
