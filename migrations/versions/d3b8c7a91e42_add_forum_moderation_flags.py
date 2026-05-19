"""add forum moderation flags

Revision ID: d3b8c7a91e42
Revises: c4a2f1d9e6b7
Create Date: 2026-05-18 17:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d3b8c7a91e42"
down_revision = "c4a2f1d9e6b7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("forum_threads", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.create_index(batch_op.f("ix_forum_threads_is_hidden"), ["is_hidden"], unique=False)

    with op.batch_alter_table("forum_replies", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.create_index(batch_op.f("ix_forum_replies_is_hidden"), ["is_hidden"], unique=False)


def downgrade():
    with op.batch_alter_table("forum_replies", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_forum_replies_is_hidden"))
        batch_op.drop_column("is_hidden")

    with op.batch_alter_table("forum_threads", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_forum_threads_is_hidden"))
        batch_op.drop_column("is_hidden")
