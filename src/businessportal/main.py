import structlog
import uvicorn
from fastapi import FastAPI

from businessportal.api.endpoints import router as biz_router

logger = structlog.get_logger()

app = FastAPI(
    title="Business Workspace Portal",
    description="Analytics Dashboard and Human-in-the-Loop approvals for AI Agents",
    version="1.0.0"
)

app.include_router(biz_router, prefix="/v1/biz", tags=["Business Logic"])

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}

def start() -> None:
    logger.info("Starting Business Workspace Portal on 0.0.0.0:8001")
    uvicorn.run("businessportal.main:app", host="0.0.0.0", port=8001, reload=True)

if __name__ == "__main__":
    start()
