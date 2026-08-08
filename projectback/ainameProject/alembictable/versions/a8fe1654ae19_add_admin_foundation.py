"""add admin foundation

Revision ID: a8fe1654ae19
Revises: 12657eb5b2af
Create Date: 2026-08-07 16:06:15.972875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8fe1654ae19'
down_revision: Union[str, None] = '12657eb5b2af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user",
        sa.Column(
            "role",
            sa.String(length=20),
            server_default=sa.text("'user'"),
            nullable=False,
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column("user", sa.Column("last_login_at", sa.DateTime(), nullable=True))

    op.create_table(
        "admin_audit_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.String(length=100), nullable=True),
        sa.Column("changes", sa.JSON(), nullable=True),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["admin_id"],
            ["user.id"],
            name=op.f("fk_admin_audit_log_admin_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_admin_audit_log")),
    )
    op.create_index(
        op.f("ix_admin_audit_log_admin_id"),
        "admin_audit_log",
        ["admin_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admin_audit_log_created_at"),
        "admin_audit_log",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_admin_audit_log_created_at"), table_name="admin_audit_log"
    )
    op.drop_index(
        op.f("ix_admin_audit_log_admin_id"), table_name="admin_audit_log"
    )
    op.drop_table("admin_audit_log")
    op.drop_column("user", "last_login_at")
    op.drop_column("user", "created_at")
    op.drop_column("user", "is_active")
    op.drop_column("user", "role")
