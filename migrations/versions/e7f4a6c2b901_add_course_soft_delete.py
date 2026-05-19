"""add course soft delete

Revision ID: e7f4a6c2b901
Revises: d3b8c7a91e42
Create Date: 2026-05-18 18:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e7f4a6c2b901"
down_revision = "d3b8c7a91e42"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("courses", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.create_index(batch_op.f("ix_courses_is_deleted"), ["is_deleted"], unique=False)


def downgrade():
    with op.batch_alter_table("courses", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_courses_is_deleted"))
        batch_op.drop_column("is_deleted")
