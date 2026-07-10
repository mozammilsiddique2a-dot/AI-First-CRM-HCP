import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8001/api/v1"


def request(method: str, path: str, payload: dict | None = None) -> tuple[int, dict | None]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=90) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else None
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        return exc.code, json.loads(body) if body else None


def chat(message: str, conversation_id: str | None = None) -> dict:
    status, body = request(
        "POST",
        "/hcp-assistant/chat",
        {"message": message, "conversation_id": conversation_id},
    )
    if status != 200:
        raise AssertionError(f"chat expected HTTP 200, got HTTP {status}: {body}")
    required_keys = {
        "tool_used",
        "success",
        "data",
        "assistant_response",
        "conversation_id",
        "conversation_history",
    }
    if set(body.keys()) != required_keys:
        raise AssertionError(f"unexpected response keys: {sorted(body.keys())}")
    if not isinstance(body["data"], dict):
        raise AssertionError("data must be an object")
    print(f"{body['tool_used']}=success:{body['success']}")
    return body


def cleanup(interaction_id: str | None) -> None:
    if not interaction_id:
        return
    status, _ = request("DELETE", f"/hcp-interactions/{interaction_id}")
    if status not in {204, 404}:
        raise AssertionError(f"cleanup expected HTTP 204 or 404, got HTTP {status}")
    print(f"cleanup=HTTP {status}")


def main() -> None:
    interaction_id: str | None = None
    conversation_id: str | None = None

    try:
        logged = chat(
            "Log an HCP interaction. Met Dr. LangGraph Verification on 2026-07-10 at "
            "10:30 AM for a meeting. Discussed CardioPlus efficacy and shared the "
            "CardioPlus brochure. No samples were distributed. Sentiment was positive. "
            "Outcome: doctor requested clinical evidence. Follow-up: send product brochure "
            "and schedule next visit."
        )
        if logged["tool_used"] != "log_interaction" or not logged["success"]:
            raise AssertionError(f"log_interaction failed: {logged}")
        interaction_id = logged["data"]["id"]
        conversation_id = logged["conversation_id"]

        searched = chat(
            "Search interaction history for Dr. LangGraph Verification about CardioPlus.",
            conversation_id,
        )
        if searched["tool_used"] != "search_interaction_history" or not searched["success"]:
            raise AssertionError(f"search_interaction_history failed: {searched}")
        if searched["data"]["count"] < 1:
            raise AssertionError("search did not find the logged interaction")

        summarized = chat(
            "Summarize these meeting notes: Dr. LangGraph Verification asked about CardioPlus "
            "efficacy, wanted phase III evidence, and agreed to a follow-up discussion next week.",
            conversation_id,
        )
        if summarized["tool_used"] != "summarize_interaction" or not summarized["success"]:
            raise AssertionError(f"summarize_interaction failed: {summarized}")

        suggested = chat(
            "Suggest follow-up actions for Dr. LangGraph Verification after a positive CardioPlus meeting.",
            conversation_id,
        )
        if suggested["tool_used"] != "suggest_follow_up_actions" or not suggested["success"]:
            raise AssertionError(f"suggest_follow_up_actions failed: {suggested}")

        edited = chat(
            f"Update interaction {interaction_id}: change sentiment to neutral and follow_up_actions "
            "to send clinical evidence next Friday.",
            conversation_id,
        )
        if edited["tool_used"] != "edit_interaction" or not edited["success"]:
            raise AssertionError(f"edit_interaction failed: {edited}")
        if edited["data"]["sentiment"] != "neutral":
            raise AssertionError("edit did not update sentiment to neutral")
    finally:
        cleanup(interaction_id)


if __name__ == "__main__":
    main()

