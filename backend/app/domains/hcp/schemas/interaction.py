from datetime import date, datetime, time
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InteractionType(StrEnum):
    MEETING = "meeting"
    CALL = "call"
    EMAIL = "email"
    FIELD_VISIT = "field_visit"


class InteractionSentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class HcpInteractionBase(BaseModel):
    hcp_name: str = Field(..., min_length=1, max_length=255)
    interaction_type: InteractionType
    interaction_date: date
    interaction_time: time | None = None
    attendees: list[str] = Field(default_factory=list, max_length=100)
    topics_discussed: str = Field(..., min_length=1, max_length=10_000)
    summary: str | None = Field(default=None, max_length=10_000)
    materials_shared: list[str] = Field(default_factory=list, max_length=100)
    samples_distributed: list[str] = Field(default_factory=list, max_length=100)
    sentiment: InteractionSentiment
    outcomes: str | None = Field(default=None, max_length=10_000)
    follow_up_actions: str | None = Field(default=None, max_length=10_000)

    @field_validator(
        "hcp_name",
        "topics_discussed",
        "summary",
        "outcomes",
        "follow_up_actions",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return str(value).strip()

    @field_validator("attendees", "materials_shared", "samples_distributed")
    @classmethod
    def strip_list_items(cls, values: list[str]) -> list[str]:
        return [item.strip() for item in values if item.strip()]


class HcpInteractionCreate(HcpInteractionBase):
    pass


class HcpInteractionUpdate(BaseModel):
    hcp_name: str | None = Field(default=None, min_length=1, max_length=255)
    interaction_type: InteractionType | None = None
    interaction_date: date | None = None
    interaction_time: time | None = None
    attendees: list[str] | None = Field(default=None, max_length=100)
    topics_discussed: str | None = Field(default=None, min_length=1, max_length=10_000)
    summary: str | None = Field(default=None, max_length=10_000)
    materials_shared: list[str] | None = Field(default=None, max_length=100)
    samples_distributed: list[str] | None = Field(default=None, max_length=100)
    sentiment: InteractionSentiment | None = None
    outcomes: str | None = Field(default=None, max_length=10_000)
    follow_up_actions: str | None = Field(default=None, max_length=10_000)

    @field_validator(
        "hcp_name",
        "topics_discussed",
        "summary",
        "outcomes",
        "follow_up_actions",
        mode="before",
    )
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return str(value).strip()

    @field_validator("attendees", "materials_shared", "samples_distributed")
    @classmethod
    def strip_list_items(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return values
        return [item.strip() for item in values if item.strip()]


class HcpInteractionResponse(HcpInteractionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class HcpInteractionListResponse(BaseModel):
    items: list[HcpInteractionResponse]
    total: int
    limit: int
    offset: int


class HcpAssistantRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=20_000)
    conversation_id: str | None = Field(default=None, max_length=120)


class HcpAssistantResponse(BaseModel):
    tool_used: str
    success: bool
    data: dict
    assistant_response: str
    conversation_id: str
    conversation_history: list[dict[str, str]]
