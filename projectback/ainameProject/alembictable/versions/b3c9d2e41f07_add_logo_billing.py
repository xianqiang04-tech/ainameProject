"""add logo billing

Revision ID: b3c9d2e41f07
Revises: a8fe1654ae19
Create Date: 2026-08-08 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c9d2e41f07'
down_revision: Union[str, None] = 'a8fe1654ae19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # user_credit：新增 logo 次数账户
    op.add_column(
        "user_credit",
        sa.Column(
            "logo_balance",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.add_column(
        "user_credit",
        sa.Column(
            "logo_total_used",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )

    # package：新增套餐类型（name=起名套餐 / logo=Logo 次数包），存量回填为 name
    op.add_column(
        "package",
        sa.Column(
            "type",
            sa.String(length=20),
            server_default=sa.text("'name'"),
            nullable=False,
        ),
    )

    # user_order：冗余套餐类型快照，存量回填为 name
    op.add_column(
        "user_order",
        sa.Column(
            "package_type",
            sa.String(length=20),
            server_default=sa.text("'name'"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("user_order", "package_type")
    op.drop_column("package", "type")
    op.drop_column("user_credit", "logo_total_used")
    op.drop_column("user_credit", "logo_balance")
