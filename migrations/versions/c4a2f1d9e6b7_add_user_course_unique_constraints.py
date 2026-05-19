"""add user course unique constraints

Revision ID: c4a2f1d9e6b7
Revises: a8d8e35cfbe7, e0226d7aac27
Create Date: 2026-05-18 17:20:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "c4a2f1d9e6b7"
down_revision = ("a8d8e35cfbe7", "e0226d7aac27")
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    bind.exec_driver_sql(
        """
        DELETE FROM enrollments
        WHERE id NOT IN (
            SELECT keep_id
            FROM (
                SELECT MIN(id) AS keep_id
                FROM enrollments
                GROUP BY user_id, course_id
            ) dedup
        )
        """
    )
    bind.exec_driver_sql(
        """
        DELETE FROM certificates
        WHERE id NOT IN (
            SELECT keep_id
            FROM (
                SELECT MIN(id) AS keep_id
                FROM certificates
                GROUP BY user_id, course_id
            ) dedup
        )
        """
    )

    with op.batch_alter_table("enrollments", schema=None) as batch_op:
        batch_op.create_unique_constraint("uq_enrollments_user_course", ["user_id", "course_id"])

    with op.batch_alter_table("certificates", schema=None) as batch_op:
        batch_op.create_unique_constraint("uq_certificates_user_course", ["user_id", "course_id"])


def downgrade():
    with op.batch_alter_table("certificates", schema=None) as batch_op:
        batch_op.drop_constraint("uq_certificates_user_course", type_="unique")

    with op.batch_alter_table("enrollments", schema=None) as batch_op:
        batch_op.drop_constraint("uq_enrollments_user_course", type_="unique")
