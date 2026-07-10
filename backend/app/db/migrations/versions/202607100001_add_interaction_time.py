"""add interaction time

Revision ID: 202607100001
Revises: 202607090001
Create Date: 2026-07-10 00:01:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "202607100001"
down_revision: str | None = "202607090001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("hcp_interactions", sa.Column("interaction_time", sa.Time(), nullable=True))


def downgrade() -> None:
    op.drop_column("hcp_interactions", "interaction_time")

