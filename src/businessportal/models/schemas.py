from typing import Literal

from pydantic import BaseModel


class RoiDashboardResponse(BaseModel):
    total_tasks_completed: int
    estimated_hours_saved: float
    roi_status: str

class HitlApprovalRequest(BaseModel):
    approver_id: str
    decision: Literal["Approve", "Reject"]
    reason: str

class HitlApprovalResponse(BaseModel):
    approval_id: str
    status: str
    message: str
