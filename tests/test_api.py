from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from businessportal.api.endpoints import get_engine
from businessportal.main import app

client = TestClient(app)

def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_roi() -> None:
    mock_instance = MagicMock()
    mock_instance.calculate_roi = AsyncMock(return_value=(500, 1500.5, "Excellent"))
    
    app.dependency_overrides[get_engine] = lambda: mock_instance
    
    response = client.get("/v1/biz/analytics/roi")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks_completed"] == 500
    assert data["estimated_hours_saved"] == 1500.5
    assert data["roi_status"] == "Excellent"

@pytest.mark.asyncio
async def test_process_approval() -> None:
    mock_instance = MagicMock()
    mock_instance.resolve_hitl_approval = AsyncMock(return_value=True)
    
    app.dependency_overrides[get_engine] = lambda: mock_instance
    
    response = client.post("/v1/biz/approvals/app_123", json={
        "approver_id": "mgr-jane",
        "decision": "Approve",
        "reason": "Cost looks fine."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["approval_id"] == "app_123"
    assert data["status"] == "Approve"

@pytest.mark.asyncio
async def test_process_approval_not_found() -> None:
    mock_instance = MagicMock()
    mock_instance.resolve_hitl_approval = AsyncMock(return_value=False)
    
    app.dependency_overrides[get_engine] = lambda: mock_instance
    
    response = client.post("/v1/biz/approvals/app_999", json={
        "approver_id": "mgr-jane",
        "decision": "Reject",
        "reason": "Too risky."
    })
    assert response.status_code == 404
