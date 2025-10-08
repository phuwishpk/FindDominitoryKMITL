"""add deleted_at to owner

Revision ID: a1b2c3d4e5f6
Revises: f2a9b7a1c8d3
Create Date: 2025-10-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f2a9b7a1c8d3' # <--สำคัญ: ให้แก้เป็น ID ของ migration ล่าสุดก่อนหน้าไฟล์นี้
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('owners', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('owners', schema=None) as batch_op:
        batch_op.drop_column('deleted_at')