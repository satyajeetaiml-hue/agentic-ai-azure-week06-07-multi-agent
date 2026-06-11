"""Weeks 6-7 — Multi-Agent Orchestration Patterns.

Loan Underwriting Pipeline: sequential intake -> concurrent credit-risk + compliance
-> underwriter handoff, with human-in-the-loop approval. Run:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI, HTTPException

from app.service import (
    ApproveRequest,
    UnderwriteRequest,
    UnderwriteRun,
    get_run,
    get_settings,
    resume_underwriting,
    run_underwriting,
)

settings = get_settings()
app = FastAPI(title="Weeks 6-7 — Multi-Agent (Loan Underwriting)", version="0.2.0")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "week": "6-7", "backend": "foundry" if settings.use_foundry else "mock"}


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "service": "agentic-ai-azure-week06-07-multi-agent",
        "endpoint": "/api/v1/underwrite",
        "backend": "foundry" if settings.use_foundry else "mock",
        "docs": "/docs",
    }


@app.post("/api/v1/underwrite", response_model=UnderwriteRun, tags=["week06-07"])
async def underwrite(payload: UnderwriteRequest) -> UnderwriteRun:
    """Start the underwriting pipeline. May complete or pause for human approval."""
    return await run_underwriting(payload)


@app.get("/api/v1/runs/{run_id}", response_model=UnderwriteRun, tags=["week06-07"])
def run_status(run_id: str) -> UnderwriteRun:
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run


@app.post("/api/v1/runs/{run_id}/approve", response_model=UnderwriteRun, tags=["week06-07"])
def approve(run_id: str, payload: ApproveRequest) -> UnderwriteRun:
    """Human-in-the-loop resume for runs that are awaiting_approval."""
    run = resume_underwriting(run_id, payload)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run
