"""add unique urls constraint

Revision ID: 7f9a2b3c4d5e
Revises: e1b2c3d4f5a6
Create Date: 2026-09-15 01:30:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '7f9a2b3c4d5e'
down_revision = 'e1b2c3d4f5a6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('''
        DELETE FROM urls
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM urls
            GROUP BY ip, url
        )
    ''')
    with op.batch_alter_table('urls') as batch_op:
        batch_op.create_unique_constraint('uq_url', ['ip', 'url'])


def downgrade():
    with op.batch_alter_table('urls') as batch_op:
        batch_op.drop_constraint('uq_url', type_='unique')
