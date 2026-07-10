import json
from datetime import date
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
        with urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else None
    except HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = json.loads(body) if body else None
        return exc.code, parsed


def assert_status(actual: int, expected: int, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected HTTP {expected}, got HTTP {actual}")
    print(f"{label}=HTTP {actual}")


def main() -> None:
    create_payload = {
        "hcp_name": "Dr. API Verification",
        "interaction_type": "meeting",
        "interaction_date": date.today().isoformat(),
        "attendees": ["Rep One", "Medical Science Liaison"],
        "topics_discussed": "Verified CRUD endpoint behavior against Neon PostgreSQL.",
        "summary": "Automated verification interaction.",
        "materials_shared": ["Verification brochure"],
        "samples_distributed": [],
        "sentiment": "positive",
        "outcomes": "Backend CRUD test passed through create step.",
        "follow_up_actions": "Delete verification record after test.",
    }

    status_code, health = request("GET", "/health")
    assert_status(status_code, 200, "health")
    print(f"health_body={health}")

    status_code, created = request("POST", "/hcp-interactions", create_payload)
    assert_status(status_code, 201, "create")
    interaction_id = created["id"]
    print(f"created_id={interaction_id}")

    status_code, listed = request("GET", "/hcp-interactions?limit=10&offset=0")
    assert_status(status_code, 200, "list")
    if not any(item["id"] == interaction_id for item in listed["items"]):
        raise AssertionError("list: created interaction was not returned")

    status_code, fetched = request("GET", f"/hcp-interactions/{interaction_id}")
    assert_status(status_code, 200, "get")
    if fetched["hcp_name"] != create_payload["hcp_name"]:
        raise AssertionError("get: fetched interaction did not match created payload")

    patch_payload = {
        "sentiment": "neutral",
        "outcomes": "Backend CRUD test passed through update step.",
    }
    status_code, updated = request("PATCH", f"/hcp-interactions/{interaction_id}", patch_payload)
    assert_status(status_code, 200, "update")
    if updated["sentiment"] != "neutral":
        raise AssertionError("update: sentiment was not updated")

    status_code, _ = request("DELETE", f"/hcp-interactions/{interaction_id}")
    assert_status(status_code, 204, "delete")

    status_code, deleted_lookup = request("GET", f"/hcp-interactions/{interaction_id}")
    assert_status(status_code, 404, "get_after_delete")
    print(f"deleted_lookup_body={deleted_lookup}")


if __name__ == "__main__":
    main()

