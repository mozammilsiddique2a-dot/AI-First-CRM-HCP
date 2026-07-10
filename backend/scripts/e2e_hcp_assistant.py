import json
import os
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import UUID

from sqlalchemy import text

from app.db.session import SessionLocal
from app.domains.hcp.models.interaction import HcpInteraction


BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:8001/api/v1")
ROOT_URL = BASE_URL.removesuffix("/api/v1")
LOG_INPUT = (
    "Met Dr. Sharma today at 3 PM. We discussed CardioMax efficacy. Shared product brochure. "
    "He responded positively and requested a follow-up meeting next Friday."
)
EDIT_BY_NAME_INPUT = "Change the follow-up for Dr. Sharma to Monday at 11 AM."


class E2EFailure(AssertionError):
    pass


def request(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=120) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else None
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            parsed: Any = json.loads(body) if body else None
        except json.JSONDecodeError:
            parsed = body
        return exc.code, parsed


def chat(message: str, conversation_id: str | None = None) -> tuple[int, dict[str, Any]]:
    status, body = request(
        "POST",
        "/hcp-assistant/chat",
        {"message": message, "conversation_id": conversation_id},
    )
    if not isinstance(body, dict):
        raise E2EFailure(f"Expected JSON object response for chat, got status={status}, body={body!r}")
    return status, body


def assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise E2EFailure(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(condition: bool, label: str) -> None:
    if not condition:
        raise E2EFailure(label)


def db_count() -> int:
    with SessionLocal() as db:
        return db.query(HcpInteraction).count()


def db_get(interaction_id: str) -> HcpInteraction:
    with SessionLocal() as db:
        row = db.get(HcpInteraction, UUID(interaction_id))
        if row is None:
            raise E2EFailure(f"Database row was not found: {interaction_id}")
        db.expunge(row)
        return row


def alembic_versions() -> list[str]:
    with SessionLocal() as db:
        return list(db.execute(text("select version_num from alembic_version")).scalars())


def main() -> None:
    results: list[str] = []
    before_count = db_count()
    versions = alembic_versions()
    assert_true(bool(versions), "Alembic migration version is missing")
    results.append(f"alembic_versions={versions}")

    for path in ["/health", "/openapi.json"]:
        status, body = request("GET", path)
        assert_equal(status, 200, path)
        assert_true(body is not None, f"{path} returned empty body")
        results.append(f"{path}=HTTP 200")

    with urlopen(f"{ROOT_URL}/docs", timeout=30) as docs_response:
        assert_equal(docs_response.status, 200, "/docs")
    results.append("/docs=HTTP 200")

    status, logged = chat(LOG_INPUT)
    assert_equal(status, 200, "log HTTP status")
    assert_equal(logged["tool_used"], "log_interaction", "log tool")
    assert_equal(logged["success"], True, "log success")
    for key in ["id", "hcp_name", "topics_discussed", "sentiment", "follow_up_actions"]:
        assert_true(key in logged["data"], f"log structured data missing {key}")
    created_id = logged["data"]["id"]
    row = db_get(created_id)
    assert_equal(row.hcp_name, "Dr. Sharma", "created row hcp_name")
    assert_true("CardioMax" in row.topics_discussed, "created row topics")
    results.append(f"log_interaction_created={created_id}")

    status, edited_name = chat(EDIT_BY_NAME_INPUT, logged["conversation_id"])
    assert_equal(status, 200, "edit by name HTTP status")
    assert_equal(edited_name["tool_used"], "edit_interaction", "edit by name tool")
    assert_equal(edited_name["success"], True, "edit by name success")
    assert_equal(edited_name["data"]["id"], created_id, "edit by name targets latest created row")
    assert_equal(db_get(created_id).follow_up_actions, "Monday at 11 AM", "edit by name persisted")
    results.append("edit_by_hcp_name=Monday at 11 AM")

    edit_by_id_input = f"Edit interaction {created_id} and change follow-up to Tuesday at 4 PM."
    status, edited_id = chat(edit_by_id_input, edited_name["conversation_id"])
    assert_equal(status, 200, "edit by id HTTP status")
    assert_equal(edited_id["tool_used"], "edit_interaction", "edit by id tool")
    assert_equal(edited_id["success"], True, "edit by id success")
    assert_equal(edited_id["data"]["id"], created_id, "edit by id targets created row")
    assert_equal(db_get(created_id).follow_up_actions, "Tuesday at 4 PM", "edit by id persisted")
    results.append("edit_by_interaction_id=Tuesday at 4 PM")

    status, searched = chat("Show interaction history for Dr. Sharma.", edited_id["conversation_id"])
    assert_equal(status, 200, "search HTTP status")
    assert_equal(searched["tool_used"], "search_interaction_history", "search tool")
    item_ids = {item["id"] for item in searched["data"].get("items", [])}
    assert_true(created_id in item_ids, "search returned created record")
    results.append("search_history=created_record_returned")

    status, summarized = chat("Summarize the interaction with Dr. Sharma.", searched["conversation_id"])
    assert_equal(status, 200, "summarize HTTP status")
    assert_equal(summarized["tool_used"], "summarize_interaction", "summarize tool")
    assert_true(bool(summarized["data"].get("summary")), "summary text missing")
    assert_true("action_items" in summarized["data"], "summary action_items missing")
    results.append("summarize_interaction=summary_and_action_items")

    status, suggested = chat("Suggest next actions for Dr. Sharma.", summarized["conversation_id"])
    assert_equal(status, 200, "suggest HTTP status")
    assert_equal(suggested["tool_used"], "suggest_follow_up_actions", "suggest tool")
    assert_true(bool(suggested["data"].get("recommended_actions")), "recommendations missing")
    results.append("suggest_follow_up_actions=recommendations_returned")

    empty_status, empty_body = chat("")
    assert_equal(empty_status, 422, "empty input validation status")
    assert_true("detail" in empty_body, "empty validation body missing detail")
    results.append("empty_input=HTTP 422_no_500")

    status, vague = chat("Hello")
    assert_equal(status, 200, "vague input HTTP status")
    assert_equal(vague["tool_used"], "clarify_request", "vague input tool")
    assert_equal(vague["success"], False, "vague input success false")
    assert_true("Please share" in vague["assistant_response"], "vague clarification missing")
    results.append("vague_input=clarification")

    after_count = db_count()
    assert_equal(after_count, before_count + 1, "duplicate unintended records")
    results.append(f"db_count_before={before_count} after={after_count}")

    print(json.dumps({"created_interaction_id": created_id, "passed": results}, indent=2))


if __name__ == "__main__":
    main()
