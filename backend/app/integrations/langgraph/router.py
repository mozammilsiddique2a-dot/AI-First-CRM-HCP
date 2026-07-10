import logging
from typing import Any

from app.integrations.langgraph.state import HcpAgentState
from app.integrations.langgraph.tools import HcpAgentTools

logger = logging.getLogger(__name__)


class HcpIntentRouter:
    def __init__(self, tools: HcpAgentTools) -> None:
        self._tools = tools

    def route(self, state: HcpAgentState) -> dict[str, Any]:
        routing = self._tools.classify_intent(
            state["user_message"],
            state.get("conversation_history", []),
        )
        selected_tool = routing.get("selected_tool", "suggest_follow_up_actions")
        logger.info("LangGraph router selected tool: %s", selected_tool)
        return {
            "selected_tool": selected_tool,
            "extracted_entities": routing.get("entities", {}),
        }

