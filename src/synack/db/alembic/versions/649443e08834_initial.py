"""Initial

Revision ID: 649443e08834
Revises:
Create Date: 2022-01-31 22:43:29.235269

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '649443e08834'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('config',
                    sa.Column('id', sa.INTEGER, primary_key=True),
                    sa.Column('api_token', sa.VARCHAR(200), server_default=""),
                    sa.Column('debug', sa.BOOLEAN, server_default='f'),
                    sa.Column('email', sa.VARCHAR(150), server_default=""),
                    sa.Column('http_proxy', sa.VARCHAR(50), server_default='http://localhost:8080'),
                    sa.Column('https_proxy', sa.VARCHAR(50), server_default='http://localhost:8080'),
                    sa.Column('login', sa.BOOLEAN, server_default='f'),
                    sa.Column('template_dir', sa.VARCHAR(250), server_default='~/Templates'),
                    sa.Column('notifications_token', sa.VARCHAR(1000), server_default=""),
                    sa.Column('otp_secret', sa.VARCHAR(50), server_default=""),
                    sa.Column('password', sa.VARCHAR(150), server_default=""),
                    sa.Column('user_id', sa.VARCHAR(20), server_default=""),
                    sa.Column('use_proxies', sa.BOOLEAN, server_default='f'))

    op.create_table('categories',
                    sa.Column('id', sa.INTEGER, primary_key=True),
                    sa.Column('name', sa.VARCHAR(100)),
                    sa.Column('passed_practical', sa.BOOLEAN, server_default='f'),
                    sa.Column('passed_written', sa.BOOLEAN, server_default='f'))

    op.create_table('organizations',
                    sa.Column('slug', sa.VARCHAR(20), primary_key=True))

    op.create_table('targets',
                    sa.Column('slug', sa.VARCHAR(20), primary_key=True),
                    sa.Column('category', sa.INTEGER, sa.ForeignKey('categories.id')),
                    sa.Column('organization', sa.VARCHAR(20), sa.ForeignKey('organizations.slug')),
                    sa.Column('average_payout', sa.REAL, server_default='0.0'),
                    sa.Column('codename', sa.VARCHAR(100)),
                    sa.Column('date_updated', sa.INTEGER, default=0),
                    sa.Column('end_date', sa.INTEGER, default=0),
                    sa.Column('is_active', sa.BOOLEAN, default='f'),
                    sa.Column('is_new', sa.BOOLEAN, default='f'),
                    sa.Column('is_registered', sa.BOOLEAN, default='t'),
                    sa.Column('is_updated', sa.BOOLEAN, default='f'),
                    sa.Column('last_submitted', sa.INTEGER, default=0),
                    sa.Column('start_date', sa.INTEGER, default=0),
                    sa.Column('vulnerability_discovery', sa.BOOLEAN, default='f'),
                    sa.Column('workspace_access_missing', sa.BOOLEAN, default='f'))


def downgrade():
    op.drop_table('config')
    op.drop_table('categories')
    op.drop_table('targets')
    op.drop_table('organizations')
