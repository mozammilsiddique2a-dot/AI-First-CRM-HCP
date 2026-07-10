import json
import logging
import re
from datetime import date, time, timedelta
from typing import Any
from uuid import UUID

from groq import BadRequestError as GroqBadRequestError, Groq
from pydantic import BaseModel, Field, ValidationError, field_validator

from app.core.config import settings
from app.domains.hcp.models.interaction import HcpInteraction
from app.domains.hcp.schemas.interaction import HcpInteractionCreate, HcpInteractionUpdate
from app.domains.hcp.services.interaction_service import HcpInteractionService
from app.integrations.langgraph import prompts
from app.shared.exceptions import BadRequestError as AppBadRequestError, ResourceNotFoundError

logger = logging.getLogger(__name__)


class LlmJsonError(RuntimeError):
    pass


class LogInteractionExtraction(BaseModel):
    hcp_name: str | None = None
    interaction_type: str | None = "meeting"
    interaction_date: date | None = None
    interaction_time: time | None = None
    attendees: list[str] = Field(default_factory=list)
    topics_discussed: str | None = None
    summary: str | None = None
    materials_shared: list[str] = Field(default_factory=list)
    samples_distributed: list[str] = Field(default_factory=list)
    sentiment: str | None = "neutral"
    outcomes: str | None = None
    follow_up_actions: str | None = None

    @field_validator("topics_discussed", "summary", "outcomes", "follow_up_actions", mode="before")
    @classmethod
    def coerce_text(cls, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, list):
            return "; ".join(str(item) for item in value if item)
        return str(value)

    @field_validator("attendees", "materials_shared", "samples_distributed", mode="before")
    @classmethod
    def coerce_list(cls, value: Any) -> list[str]:
        if value is None or value is False:
            return []
        if isinstance(value, list):
            return [str(item) for item in value if item]
        return [str(value)] if value else []

    @field_validator("interaction_date", "interaction_time", mode="before")
    @classmethod
    def coerce_null_datetime(cls, value: Any) -> Any:
        if _is_nullish(value):
            return None
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "today":
                return date.today().isoformat()
            if normalized == "yesterday":
                return (date.today() - timedelta(days=1)).isoformat()
            time_match = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)", normalized)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or "0")
                meridiem = time_match.group(3)
                if meridiem == "pm" and hour != 12:
                    hour += 12
                if meridiem == "am" and hour == 12:
                    hour = 0
                return f"{hour:02d}:{minute:02d}:00"
        return value


class EditInteractionExtraction(BaseModel):
    interaction_id: UUID | None = None
    hcp_name: str | None = None
    updates: dict[str, Any] = Field(default_factory=dict)

    @field_validator("interaction_id", "hcp_name", mode="before")
    @classmethod
    def coerce_null_scalars(cls, value: Any) -> Any:
        return None if _is_nullish(value) else value


class SearchInteractionExtraction(BaseModel):
    hcp_name: str | None = None
    interaction_date: date | None = None
    product: str | None = None
    interaction_type: str | None = None
    limit: int = Field(default=10, ge=1, le=25)

    @field_validator("hcp_name", "interaction_date", "product", "interaction_type", mode="before")
    @classmethod
    def coerce_null_filters(cls, value: Any) -> Any:
        return None if _is_nullish(value) else value


def _is_nullish(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip().lower() in {"", "null", "none"})


class InteractionSummary(BaseModel):
    summary: str
    key_discussion_points: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)


class FollowUpSuggestion(BaseModel):
    recommended_actions: list[str] = Field(default_factory=list)
    rationale: str


class HcpAgentTools:
    def __init__(self, service: HcpInteractionService) -> None:
        self._service = service
        self._client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        self._model = settings.groq_model
        self._fallback_model = settings.groq_fallback_model

    def run(self, tool_name: str, user_message: str, entities: dict[str, Any]) -> dict[str, Any]:
        logger.info("Executing LangGraph HCP tool: selected_tool=%s", tool_name)

        handlers = {
            "log_interaction": self.log_interaction,
            "edit_interaction": self.edit_interaction,
            "search_interaction_history": self.search_interaction_history,
            "summarize_interaction": self.summarize_interaction,
            "suggest_follow_up_actions": self.suggest_follow_up_actions,
            "clarify_request": self.clarify_request,
        }
        handler = handlers.get(tool_name, self.suggest_follow_up_actions)
        return handler(user_message, entities)

    def log_interaction(self, user_message: str, _: dict[str, Any]) -> dict[str, Any]:
        extracted = self._extract_json(
            system_prompt=prompts.LOG_INTERACTION_PROMPT,
            user_message=user_message,
            model=LogInteractionExtraction,
        )

        interaction_date = extracted.interaction_date or date.today()
        topics = extracted.topics_discussed or user_message
        hcp_name = extracted.hcp_name or "Unknown HCP"

        create_payload = HcpInteractionCreate(
            hcp_name=hcp_name,
            interaction_type=self._normalize_interaction_type(extracted.interaction_type),
            interaction_date=interaction_date,
            interaction_time=extracted.interaction_time,
            attendees=extracted.attendees,
            topics_discussed=topics,
            summary=extracted.summary,
            materials_shared=extracted.materials_shared,
            samples_distributed=extracted.samples_distributed,
            sentiment=self._normalize_sentiment(extracted.sentiment),
            outcomes=extracted.outcomes,
            follow_up_actions=extracted.follow_up_actions,
        )
        interaction = self._service.create_interaction(create_payload)
        data = self._interaction_to_dict(interaction)
        return self._success("log_interaction", data, self._logged_interaction_response(data))

    def edit_interaction(self, user_message: str, entities: dict[str, Any]) -> dict[str, Any]:
        extracted = self._extract_json(
            system_prompt=prompts.EDIT_INTERACTION_PROMPT,
            user_message=user_message,
            model=EditInteractionExtraction,
        )
        updates = self._clean_updates(extracted.updates, user_message=user_message, entities=entities)

        interaction_id = extracted.interaction_id or self._extract_uuid(user_message)
        if interaction_id is None:
            interaction_id = self._find_latest_interaction_id(extracted.hcp_name or entities.get("hcp_name"))
        if interaction_id is None:
            raise ResourceNotFoundError(
                "No HCP interaction could be found for the edit request. Provide an interaction id or known HCP name."
            )

        if not updates:
            raise AppBadRequestError("No editable HCP interaction fields were found in the edit request.")

        update_payload = HcpInteractionUpdate(**updates)
        updated = self._service.update_interaction(interaction_id, update_payload)
        data = self._interaction_to_dict(updated)
        return self._success(
            "edit_interaction",
            data,
            self._updated_interaction_response(data, updates),
        )

    def search_interaction_history(self, user_message: str, entities: dict[str, Any]) -> dict[str, Any]:
        extracted = self._extract_json(
            system_prompt=prompts.SEARCH_INTERACTION_PROMPT,
            user_message=user_message,
            model=SearchInteractionExtraction,
        )
        hcp_name = (
            self._infer_hcp_name(user_message)
            or self._stringify_update_value(entities.get("hcp_name"))
            or self._stringify_update_value(entities.get("hcp"))
            or extracted.hcp_name
        )
        interaction_date = (
            extracted.interaction_date if self._message_mentions_date_filter(user_message) else None
        )
        product = extracted.product if self._message_mentions_value(user_message, extracted.product) else None
        interaction_type = (
            self._normalize_interaction_type(extracted.interaction_type)
            if extracted.interaction_type
            and self._message_mentions_value(user_message, extracted.interaction_type)
            else None
        )
        interactions = self._service.search_interactions(
            limit=extracted.limit,
            hcp_name=hcp_name,
            interaction_date=interaction_date,
            product=product,
            interaction_type=interaction_type,
        )
        data = {
            "count": len(interactions),
            "items": [self._interaction_to_dict(interaction) for interaction in interactions],
        }
        return self._success("search_interaction_history", data, "Interaction history retrieved.")

    def summarize_interaction(self, user_message: str, _: dict[str, Any]) -> dict[str, Any]:
        summary = self._extract_json(
            system_prompt=prompts.SUMMARIZE_INTERACTION_PROMPT,
            user_message=user_message,
            model=InteractionSummary,
        )
        return self._success(
            "summarize_interaction",
            summary.model_dump(),
            "Interaction summary generated.",
        )

    def suggest_follow_up_actions(self, user_message: str, _: dict[str, Any]) -> dict[str, Any]:
        suggestion = self._extract_json(
            system_prompt=prompts.FOLLOW_UP_PROMPT,
            user_message=user_message,
            model=FollowUpSuggestion,
        )
        return self._success(
            "suggest_follow_up_actions",
            suggestion.model_dump(),
            "Follow-up actions suggested.",
        )

    def clarify_request(self, _: str, __: dict[str, Any]) -> dict[str, Any]:
        return self._failure(
            "clarify_request",
            {"reason": "The message did not include enough HCP interaction context."},
            (
                "Please share the HCP name and what you want to do, such as logging an "
                "interaction, editing a follow-up, searching history, summarizing notes, "
                "or suggesting next actions."
            ),
        )

    def classify_intent(self, user_message: str, conversation_history: list[dict[str, str]]) -> dict[str, Any]:
        if self._is_vague_message(user_message):
            return {
                "selected_tool": "clarify_request",
                "reason": "message is too vague",
                "entities": {},
            }

        try:
            result = self._call_json(
                system_prompt=prompts.INTENT_ROUTER_PROMPT,
                user_message=user_message,
                conversation_history=conversation_history,
            )
            selected_tool = result.get("selected_tool")
            if selected_tool in {
                "log_interaction",
                "edit_interaction",
                "search_interaction_history",
                "summarize_interaction",
                "suggest_follow_up_actions",
                "clarify_request",
            }:
                return result
        except Exception:
            logger.exception("LLM intent routing failed; falling back to keyword router")

        return self._fallback_intent(user_message)

    def _extract_json[T: BaseModel](
        self,
        *,
        system_prompt: str,
        user_message: str,
        model: type[T],
    ) -> T:
        data = self._call_json(system_prompt=system_prompt, user_message=user_message)
        try:
            return model.model_validate(data)
        except ValidationError as exc:
            logger.exception("LLM JSON validation failed for %s with data=%s", model.__name__, data)
            raise

    def _call_json(
        self,
        *,
        system_prompt: str,
        user_message: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        if self._client is None:
            raise LlmJsonError("GROQ_API_KEY is not configured.")

        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": f"{system_prompt}\nCurrent date: {date.today().isoformat()}.",
            }
        ]
        for message in conversation_history or []:
            if message.get("role") in {"user", "assistant"} and message.get("content"):
                messages.append({"role": message["role"], "content": message["content"]})
        messages.append({"role": "user", "content": user_message})

        completion = self._create_completion(messages)
        content = completion.choices[0].message.content or "{}"
        try:
            return self._parse_json_content(content)
        except json.JSONDecodeError as exc:
            logger.exception("Groq returned non-JSON content: %s", content)
            raise LlmJsonError("LLM response was not valid JSON.") from exc

    @staticmethod
    def _fallback_intent(user_message: str) -> dict[str, Any]:
        lowered = user_message.lower()
        if HcpAgentTools._is_vague_message(user_message):
            selected_tool = "clarify_request"
        elif any(word in lowered for word in ["change", "update", "edit", "modify"]):
            selected_tool = "edit_interaction"
        elif any(word in lowered for word in ["log", "record", "met ", "discussed", "shared"]):
            selected_tool = "log_interaction"
        elif any(word in lowered for word in ["search", "find", "history", "previous", "past"]):
            selected_tool = "search_interaction_history"
        elif any(word in lowered for word in ["summarize", "summary", "notes"]):
            selected_tool = "summarize_interaction"
        elif any(word in lowered for word in ["follow-up", "follow up", "next action", "recommend"]):
            selected_tool = "suggest_follow_up_actions"
        else:
            selected_tool = "log_interaction"

        return {"selected_tool": selected_tool, "reason": "keyword fallback", "entities": {}}

    @staticmethod
    def _is_vague_message(user_message: str) -> bool:
        normalized = re.sub(r"\s+", " ", user_message.strip().lower())
        return normalized in {"hello", "hi", "hey", "help", "good morning", "good afternoon", "good evening"}

    @staticmethod
    def _infer_hcp_name(user_message: str) -> str | None:
        match = re.search(
            r"\b(?:for|with|about)\s+(Dr\.?\s+[A-Z][A-Za-z]+)",
            user_message,
            flags=re.IGNORECASE,
        )
        if not match:
            return None
        value = match.group(1).strip().rstrip(".")
        return re.sub(r"^dr\.?\s+", "Dr. ", value, flags=re.IGNORECASE)

    @staticmethod
    def _message_mentions_value(user_message: str, value: str | None) -> bool:
        if not value:
            return False
        normalized_message = user_message.lower().replace("_", " ").replace("-", " ")
        normalized_value = value.lower().replace("_", " ").replace("-", " ")
        return normalized_value in normalized_message

    @staticmethod
    def _message_mentions_date_filter(user_message: str) -> bool:
        lowered = user_message.lower()
        return bool(
            re.search(r"\b\d{4}-\d{2}-\d{2}\b", lowered)
            or re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", lowered)
            or re.search(r"\b(today|yesterday|tomorrow)\b", lowered)
            or re.search(r"\bon\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lowered)
        )

    def _create_completion(self, messages: list[dict[str, str]]):
        models = [self._model]
        if self._fallback_model and self._fallback_model not in models:
            models.append(self._fallback_model)

        last_error: Exception | None = None
        for index, model in enumerate(models):
            try:
                if index > 0:
                    logger.warning("Retrying Groq request with fallback model: %s", model)
                logger.info("Sending Groq request with model=%s message_count=%s", model, len(messages))
                return self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0,
                    response_format={"type": "json_object"},
                )
            except GroqBadRequestError as exc:
                last_error = exc
                error_text = str(exc).lower()
                if "decommissioned" in error_text or "model" in error_text:
                    continue
                if "response_format" in error_text or "json" in error_text:
                    return self._client.chat.completions.create(
                        model=model,
                        messages=[
                            *messages[:-1],
                            {
                                "role": messages[-1]["role"],
                                "content": messages[-1]["content"] + "\nReturn JSON only.",
                            },
                        ],
                        temperature=0,
                    )
                raise

        if last_error:
            raise last_error
        raise LlmJsonError("No Groq model was available for completion.")

    @staticmethod
    def _parse_json_content(content: str) -> dict[str, Any]:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not match:
                raise
            parsed = json.loads(match.group(0))

        if not isinstance(parsed, dict):
            raise LlmJsonError("LLM response JSON must be an object.")
        return parsed

    @staticmethod
    def _extract_uuid(text: str) -> UUID | None:
        match = re.search(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            text,
        )
        return UUID(match.group(0)) if match else None

    def _find_latest_interaction_id(self, hcp_name: str | None) -> UUID | None:
        if not hcp_name:
            return None
        interactions = self._service.search_interactions(limit=5, hcp_name=hcp_name)
        logger.info(
            "Edit interaction lookup by hcp_name=%r matched_count=%s matched_ids=%s",
            hcp_name,
            len(interactions),
            [str(interaction.id) for interaction in interactions],
        )
        return interactions[0].id if interactions else None

    @staticmethod
    def _clean_updates(
        updates: dict[str, Any],
        *,
        user_message: str,
        entities: dict[str, Any],
    ) -> dict[str, Any]:
        allowed_fields = {
            "hcp_name",
            "interaction_type",
            "interaction_date",
            "interaction_time",
            "attendees",
            "topics_discussed",
            "summary",
            "materials_shared",
            "samples_distributed",
            "sentiment",
            "outcomes",
            "follow_up_actions",
        }
        aliases = {
            "follow_up": "follow_up_actions",
            "followup": "follow_up_actions",
            "follow_up_action": "follow_up_actions",
            "next_follow_up": "follow_up_actions",
            "follow_up_date": "follow_up_actions",
            "follow_up_time": "follow_up_actions",
        }
        text_fields = {
            "hcp_name",
            "topics_discussed",
            "summary",
            "outcomes",
            "follow_up_actions",
        }
        list_fields = {"attendees", "materials_shared", "samples_distributed"}

        cleaned: dict[str, Any] = {}
        for raw_key, value in {**entities, **updates}.items():
            key = aliases.get(raw_key, raw_key)
            if key not in allowed_fields or value is None:
                continue
            if key in text_fields:
                if key == "follow_up_actions":
                    cleaned[key] = HcpAgentTools._normalize_follow_up_update(value, user_message)
                else:
                    cleaned[key] = HcpAgentTools._stringify_update_value(value)
            elif key in list_fields:
                cleaned[key] = HcpAgentTools._normalize_string_list(value)
            else:
                cleaned[key] = value

        if "interaction_type" in cleaned:
            cleaned["interaction_type"] = HcpAgentTools._normalize_interaction_type(
                cleaned["interaction_type"]
            )
        if "sentiment" in cleaned:
            cleaned["sentiment"] = HcpAgentTools._normalize_sentiment(cleaned["sentiment"])
        return {
            key: value
            for key, value in cleaned.items()
            if not HcpAgentTools._is_empty_update_value(value)
        }

    @staticmethod
    def _is_empty_update_value(value: Any) -> bool:
        return value is None or value == "" or value == [] or value == {}

    @staticmethod
    def _normalize_follow_up_update(value: Any, user_message: str) -> str:
        phrase_match = re.search(r"\bfollow[- ]?up\b.*?\bto\s+(.+)$", user_message, flags=re.IGNORECASE)
        if phrase_match:
            return phrase_match.group(1).strip().rstrip(".")
        return HcpAgentTools._stringify_update_value(value)

    @staticmethod
    def _stringify_update_value(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            ordered_parts = [
                str(value[key]).strip()
                for key in ("date", "time", "status", "action", "description", "value")
                if value.get(key)
            ]
            if ordered_parts:
                return " ".join(ordered_parts)
            return "; ".join(
                f"{key}: {item}" for key, item in value.items() if item is not None and str(item).strip()
            )
        if isinstance(value, list):
            return "; ".join(
                HcpAgentTools._stringify_update_value(item)
                for item in value
                if HcpAgentTools._stringify_update_value(item)
            )
        return str(value).strip()

    @staticmethod
    def _normalize_string_list(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [HcpAgentTools._stringify_update_value(item) for item in value if item]
        return [HcpAgentTools._stringify_update_value(value)]

    @staticmethod
    def _normalize_interaction_type(value: str | None) -> str:
        normalized = (value or "meeting").lower().replace("-", "_").replace(" ", "_")
        aliases = {"in_person": "meeting", "virtual": "meeting", "phone": "call"}
        normalized = aliases.get(normalized, normalized)
        return normalized if normalized in {"meeting", "call", "email", "field_visit"} else "meeting"

    @staticmethod
    def _normalize_sentiment(value: str | None) -> str:
        normalized = (value or "neutral").lower().replace(" ", "_").replace("-", "_")
        if normalized in {"good", "favorable"}:
            return "positive"
        if normalized in {"bad", "unfavorable"}:
            return "negative"
        return normalized if normalized in {"positive", "neutral", "negative"} else "neutral"

    @staticmethod
    def _interaction_to_dict(interaction: HcpInteraction) -> dict[str, Any]:
        return {
            "id": str(interaction.id),
            "hcp_name": interaction.hcp_name,
            "interaction_type": interaction.interaction_type,
            "interaction_date": interaction.interaction_date.isoformat(),
            "interaction_time": interaction.interaction_time.isoformat()
            if interaction.interaction_time
            else None,
            "attendees": interaction.attendees,
            "topics_discussed": interaction.topics_discussed,
            "summary": interaction.summary,
            "materials_shared": interaction.materials_shared,
            "samples_distributed": interaction.samples_distributed,
            "sentiment": interaction.sentiment,
            "outcomes": interaction.outcomes,
            "follow_up_actions": interaction.follow_up_actions,
            "created_at": interaction.created_at.isoformat(),
            "updated_at": interaction.updated_at.isoformat(),
        }

    @staticmethod
    def _logged_interaction_response(data: dict[str, Any]) -> str:
        materials = data.get("materials_shared") or []
        materials_text = ", ".join(materials) if materials else "no materials recorded"
        follow_up = data.get("follow_up_actions") or "no follow-up action recorded"
        return (
            f"Interaction logged for {data['hcp_name']}. "
            f"Captured {data['interaction_type']} on {data['interaction_date']} at "
            f"{data.get('interaction_time') or 'unspecified time'} with "
            f"{data['sentiment']} sentiment. Topics: {data['topics_discussed']}. "
            f"Materials shared: {materials_text}. Follow-up: {follow_up}."
        )

    @staticmethod
    def _updated_interaction_response(data: dict[str, Any], updates: dict[str, Any]) -> str:
        updated_fields = ", ".join(sorted(updates))
        return (
            f"Interaction updated for {data['hcp_name']}. "
            f"Updated fields: {updated_fields}. "
            f"Current follow-up: {data.get('follow_up_actions') or 'no follow-up action recorded'}."
        )

    @staticmethod
    def _success(tool_used: str, data: dict[str, Any], assistant_response: str) -> dict[str, Any]:
        return {
            "tool_used": tool_used,
            "success": True,
            "data": data,
            "assistant_response": assistant_response,
        }

    @staticmethod
    def _failure(tool_used: str, data: dict[str, Any], assistant_response: str) -> dict[str, Any]:
        return {
            "tool_used": tool_used,
            "success": False,
            "data": data,
            "assistant_response": assistant_response,
        }
