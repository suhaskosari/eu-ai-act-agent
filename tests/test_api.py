import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Test that the root endpoint returns 200 and correct message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "EU AI Act Compliance Agent is running"


def test_list_audits_returns_list():
    """Test that the audits list endpoint returns a list."""
    response = client.get("/api/v1/audits")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_review_rejects_invalid_decision():
    """Test that invalid decision values are rejected."""
    response = client.post(
        "/api/v1/audit/fake-id/review",
        json={"decision": "MAYBE", "comments": "test"}
    )
    assert response.status_code == 400
    assert "APPROVED or REJECTED" in response.json()["detail"]


def test_scan_with_mocked_agent():
    """Test scan endpoint with mocked LangGraph agent and database."""
    mock_result = {
        "system_name": "Test AI",
        "system_description": "A test system",
        "risk_category": "LIMITED",
        "risk_reasoning": "Test reasoning",
        "compliance_gaps": ["Gap 1", "Gap 2"],
        "audit_document": "Test audit document",
        "audit_id": "test-uuid-1234",
        "status": "PENDING_HUMAN_REVIEW",
        "agent_reasoning": ["Step 1", "Step 2"],
        "human_decision": None,
        "human_comments": None
    }

    with patch("app.api.routes.agent") as mock_agent, \
         patch("app.db.models.Base.metadata.create_all"), \
         patch("app.db.database.SessionLocal") as mock_db:

        mock_agent.invoke.return_value = mock_result
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value = mock_session

        response = client.post(
            "/api/v1/scan",
            json={
                "system_name": "Test AI",
                "system_description": "A test system"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["risk_category"] == "LIMITED"
    assert data["status"] == "PENDING_HUMAN_REVIEW"
    assert "audit_id" in data