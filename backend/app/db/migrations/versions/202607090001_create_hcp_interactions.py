"""create hcp interactions

Revision ID: 202607090001
Revises:
Create Date: 2026-07-09 00:01:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202607090001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "hcp_interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hcp_name", sa.Text(), nullable=False),
        sa.Column("interaction_type", sa.Text(), nullable=False),
        sa.Column("interaction_date", sa.Date(), nullable=False),
        sa.Column("attendees", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("topics_discussed", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("materials_shared", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("samples_distributed", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("sentiment", sa.Text(), nullable=False),
        sa.Column("outcomes", sa.Text(), nullable=True),
        sa.Column("follow_up_actions", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hcp_interactions_hcp_name", "hcp_interactions", ["hcp_name"])
    op.create_index("ix_hcp_interactions_interaction_date", "hcp_interactions", ["interaction_date"])
    op.create_index("ix_hcp_interactions_interaction_type", "hcp_interactions", ["interaction_type"])
    op.create_index("ix_hcp_interactions_sentiment", "hcp_interactions", ["sentiment"])


def downgrade() -> None:
    op.drop_index("ix_hcp_interactions_sentiment", table_name="hcp_interactions")
    op.drop_index("ix_hcp_interactions_interaction_type", table_name="hcp_interactions")
    op.drop_index("ix_hcp_interactions_interaction_date", table_name="hcp_interactions")
    op.drop_index("ix_hcp_interactions_hcp_name", table_name="hcp_interactions")
    op.drop_table("hcp_interactions")

