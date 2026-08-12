import os

import asyncpg


class PostgresBizAdapter:
    def __init__(self) -> None:
        self.dsn = os.getenv("PG_DSN", "postgresql://postgres:postgres@localhost:5432/biz_db")
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.dsn)
            await self._init_db()

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()

    async def _init_db(self) -> None:
        if self.pool is None:
            return
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_analytics (
                    id SERIAL PRIMARY KEY,
                    agent_id VARCHAR(255) NOT NULL,
                    task_name VARCHAR(255) NOT NULL,
                    hours_saved FLOAT NOT NULL,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS hitl_queue (
                    approval_id VARCHAR(255) PRIMARY KEY,
                    agent_id VARCHAR(255) NOT NULL,
                    action_requested VARCHAR(255) NOT NULL,
                    status VARCHAR(50) DEFAULT 'Pending',
                    approver_id VARCHAR(255),
                    decision_reason TEXT,
                    resolved_at TIMESTAMP
                );
            """)

    async def get_total_roi(self) -> tuple[int, float]:
        await self.connect()
        if self.pool is None:
            raise RuntimeError("DB pool not initialized")
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT COUNT(*) as total_tasks, COALESCE(SUM(hours_saved), 0) as total_hours FROM agent_analytics"
            )
            return (int(row["total_tasks"]), float(row["total_hours"])) if row else (0, 0.0)

    async def process_approval(self, approval_id: str, approver_id: str, decision: str, reason: str) -> bool:
        await self.connect()
        if self.pool is None:
            raise RuntimeError("DB pool not initialized")
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE hitl_queue 
                SET status = $1, approver_id = $2, decision_reason = $3, resolved_at = CURRENT_TIMESTAMP
                WHERE approval_id = $4 AND status = 'Pending'
                """,
                decision, approver_id, reason, approval_id
            )
            return bool(result == "UPDATE 1")
