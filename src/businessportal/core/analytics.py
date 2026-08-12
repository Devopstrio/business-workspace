
import structlog

from businessportal.storage.pg_adapter import PostgresBizAdapter

logger = structlog.get_logger()

class BizAnalyticsEngine:
    def __init__(self, db: PostgresBizAdapter) -> None:
        self.db = db

    async def calculate_roi(self) -> tuple[int, float, str]:
        tasks, hours = await self.db.get_total_roi()
        
        if hours > 1000:
            status = "Excellent"
        elif hours > 100:
            status = "Good"
        else:
            status = "Developing"
            
        return tasks, hours, status

    async def resolve_hitl_approval(self, approval_id: str, approver_id: str, decision: str, reason: str) -> bool:
        logger.info("Processing HITL", approval_id=approval_id, decision=decision, approver=approver_id)
        return await self.db.process_approval(approval_id, approver_id, decision, reason)
