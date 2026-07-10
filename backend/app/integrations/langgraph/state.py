from typing import Any, TypedDict


class ConversationMessage(TypedDict):
    role: str
    content: str


class HcpAgentState(TypedDict):
    user_message: str
    extracted_entities: dict[str, Any]
    selected_tool: str
    tool_result: dict[str, Any]
    response: dict[str, Any]
    conversation_history: list[ConversationMessage]


class HcpAgentResult(TypedDict):
    tool_used: str
    success: bool
    data: dict[str, Any]
    assistant_response: str
    conversation_history: list[ConversationMessage]

