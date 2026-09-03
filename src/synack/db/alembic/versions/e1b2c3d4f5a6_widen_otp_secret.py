"""widen otp_secret

The Duo offline-passcode seed (hotp_secret) is stored base32-encoded in
otp_secret. Duo delivers hotp_secret as a 32-character hex string whose ASCII
bytes are the HMAC key, so the base32 encoding is 56 characters, which exceeds
the original VARCHAR(50). SQLite ignores column length, but stricter backends
(Postgres/MySQL) would truncate and silently break passcode generation. Widen
the column to comfortably hold current and future seeds.

Revision ID: e1b2c3d4f5a6
Revises: b3f1d2e4c5a6
Create Date: 2026-03-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1b2c3d4f5a6'
down_revision = 'b3f1d2e4c5a6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.alter_column('otp_secret',
                              existing_type=sa.VARCHAR(50),
                              type_=sa.VARCHAR(128),
                              existing_nullable=True)


def downgrade():
    with op.batch_alter_table('config') as batch_op:
        batch_op.alter_column('otp_secret',
                              existing_type=sa.VARCHAR(128),
                              type_=sa.VARCHAR(50),
                              existing_nullable=True)
