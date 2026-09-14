import pytest
from starlette.testclient import TestClient
from backend.main import app
from backend.app.models.db import init_db
import asyncio


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    asyncio.run(init_db())


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AgentOps Observatory" in data["service"]


def test_version_endpoint():
    client = TestClient(app)
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "schema_version" in data
    assert "redaction_policy_version" in data


def test_ingest_event_api():
    client = TestClient(app)
    payload = {
        "run_id": "api-test-run-001",
        "source": "agent",
        "actor": "tester",
        "tool_or_model_name": "search_web",
        "tool_name": "search_web",
        "arguments_redacted": {"query": "weather in Paris with secret sk-proj-1234567890abcdef1234567890abcdef"},
        "status": "success",
        "duration_ms": 150.0
    }
    response = client.post("/events", json=payload, headers={"Idempotency-Key": "idemp-001"})
    assert response.status_code in [200, 201]
    res_data = response.json()
    assert res_data["status"] in ["ingested", "duplicate_ignored"]
    assert res_data["run_id"] == "api-test-run-001"
    assert "current_hash" in res_data
