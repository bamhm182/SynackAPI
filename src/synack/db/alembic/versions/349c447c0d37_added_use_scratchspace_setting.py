"""Added Use Scratchspace Setting

Revision ID: 349c447c0d37
Revises: 355984ba030b
Create Date: 2022-07-11 00:12:58.206627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '349c447c0d37'
down_revision = '355984ba030b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.add_column(sa.Column('use_scratchspace', sa.BOOLEAN, server_default='f'))


def downgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.drop_column('use_scratchspace')
