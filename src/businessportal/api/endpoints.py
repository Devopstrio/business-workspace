from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from businessportal.core.analytics import BizAnalyticsEngine
from businessportal.models.schemas import HitlApprovalRequest, HitlApprovalResponse, RoiDashboardResponse
from businessportal.storage.pg_adapter import PostgresBizAdapter

router = APIRouter()
db = PostgresBizAdapter()

def get_engine() -> BizAnalyticsEngine:
    return BizAnalyticsEngine(db)

@router.get("/analytics/roi", response_model=RoiDashboardResponse)
async def get_roi(engine: Annotated[BizAnalyticsEngine, Depends(get_engine)]) -> RoiDashboardResponse:
    tasks, hours, status = await engine.calculate_roi()
    return RoiDashboardResponse(
        total_tasks_completed=tasks,
        estimated_hours_saved=hours,
        roi_status=status
    )

@router.post("/approvals/{approval_id}", response_model=HitlApprovalResponse)
async def process_approval(
    approval_id: str, 
    req: HitlApprovalRequest, 
    engine: Annotated[BizAnalyticsEngine, Depends(get_engine)]
) -> HitlApprovalResponse:
    success = await engine.resolve_hitl_approval(approval_id, req.approver_id, req.decision, req.reason)
    if not success:
        raise HTTPException(status_code=404, detail="Approval ID not found or already resolved.")
        
    return HitlApprovalResponse(
        approval_id=approval_id,
        status=req.decision,
        message="Workflow successfully updated by Human-in-the-loop."
    )
