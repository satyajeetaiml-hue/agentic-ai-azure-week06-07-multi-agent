"""Weeks 6–7 — Multi-Agent Orchestration Patterns — starter FastAPI service.

Use case: Loan Underwriting Pipeline (Banking).
See README.md for the full lab brief. Run:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Weeks 6–7 — Multi-Agent Orchestration Patterns", version="0.1.0")


class LabRequest(BaseModel):
    applicant_summary: str = Field(..., min_length=1, description="A summary of the loan applicant and request.")


@app.get("/health")
def health():
    return {"status": "ok", "week": "6-7", "use_case": "Loan Underwriting Pipeline"}


@app.get("/")
def root():
    return {
        "service": "agentic-ai-azure-week06-07-multi-agent",
        "week": "6-7",
        "endpoint": "/api/v1/underwrite",
        "docs": "/docs",
    }


@app.post("/api/v1/underwrite")
def handler(payload: LabRequest):
    """Mock handler for the Loan Underwriting Pipeline.

    TODO (lab): replace this stub with the real implementation described in
    README.md (the Azure services for this week are listed in the Tech Stack).
    """
    return {
        "week": "6-7",
        "use_case": "Loan Underwriting Pipeline",
        "received": payload.applicant_summary,
        "status": "accepted",
        "note": "Mock response — implement the real agent per README.md.",
    }
