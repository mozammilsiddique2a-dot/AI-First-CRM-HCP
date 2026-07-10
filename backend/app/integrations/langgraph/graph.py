from typing import Any

from langgraph.graph import StateGraph

from app.domains.hcp.services.interaction_service import HcpInteractionService
from app.integrations.langgraph.router import HcpIntentRouter
from app.integrations.langgraph.state import ConversationMessage, HcpAgentState
from app.integrations.langgraph.tools import HcpAgentTools


class HcpLangGraphAgent:
    def __init__(self, service: HcpInteractionService) -> None:
        self._tools = HcpAgentTools(service)
        self._router = HcpIntentRouter(self._tools)
        self._graph = self._build_graph()

    def invoke(
        self,
        *,
        user_message: str,
        conversation_history: list[ConversationMessage],
    ) -> dict[str, Any]:
        initial_state: HcpAgentState = {
            "user_message": user_message,
            "extracted_entities": {},
            "selected_tool": "",
            "tool_result": {},
            "response": {},
            "conversation_history": conversation_history,
        }
        final_state = self._graph.invoke(initial_state)
        return final_state["response"]

    def _build_graph(self):
        graph = StateGraph(HcpAgentState)
        graph.add_node("route_intent", self._route_intent)
        graph.add_node("execute_tool", self._execute_tool)
        graph.set_entry_point("route_intent")
        graph.add_edge("route_intent", "execute_tool")
        graph.set_finish_point("execute_tool")
        return graph.compile()

    def _route_intent(self, state: HcpAgentState) -> dict[str, Any]:
        return self._router.route(state)

    def _execute_tool(self, state: HcpAgentState) -> dict[str, Any]:
        tool_result = self._tools.run(
            state["selected_tool"],
            state["user_message"],
            state.get("extracted_entities", {}),
        )

        next_history = [
            *state.get("conversation_history", []),
            {"role": "user", "content": state["user_message"]},
            {"role": "assistant", "content": tool_result["assistant_response"]},
        ]
        response = {**tool_result, "conversation_history": next_history}
        next_state = {
            "tool_result": tool_result,
            "response": response,
            "conversation_history": next_history,
        }
        return next_state
