import logging
from uuid import uuid4

from fastapi import APIRouter, status

from app.api.deps import HcpInteractionServiceDep
from app.domains.hcp.schemas.interaction import HcpAssistantRequest, HcpAssistantResponse
from app.integrations.langgraph.graph import HcpLangGraphAgent
from app.integrations.langgraph.state import ConversationMessage

logger = logging.getLogger(__name__)
router = APIRouter()

_conversation_store: dict[str, list[ConversationMessage]] = {}
_MAX_HISTORY_MESSAGES = 20


@router.post(
    "/chat",
    response_model=HcpAssistantResponse,
    status_code=status.HTTP_200_OK,
)
def chat_with_hcp_agent(
    payload: HcpAssistantRequest,
    service: HcpInteractionServiceDep,
) -> HcpAssistantResponse:
    conversation_id = payload.conversation_id or str(uuid4())
    history = _conversation_store.get(conversation_id, [])

    logger.info("Handling HCP assistant message for conversation_id=%s", conversation_id)
    agent = HcpLangGraphAgent(service)
    result = agent.invoke(user_message=payload.message, conversation_history=history)

    updated_history = result["conversation_history"][-_MAX_HISTORY_MESSAGES:]
    _conversation_store[conversation_id] = updated_history

    return HcpAssistantResponse(
        tool_used=result["tool_used"],
        success=result["success"],
        data=result["data"],
        assistant_response=result["assistant_response"],
        conversation_id=conversation_id,
        conversation_history=updated_history,
    )

