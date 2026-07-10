from datetime import date, datetime, time
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Text, Time, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class InteractionType(StrEnum):
    MEETING = "meeting"
    CALL = "call"
    EMAIL = "email"
    FIELD_VISIT = "field_visit"


class InteractionSentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class HcpInteraction(Base):
    __tablename__ = "hcp_interactions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    hcp_name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    interaction_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    interaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    interaction_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    attendees: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    topics_discussed: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    materials_shared: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    samples_distributed: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    sentiment: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    outcomes: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_actions: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
