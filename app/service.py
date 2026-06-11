"""Weeks 6-7 — Multi-Agent Orchestration: Loan Underwriting Pipeline.

Demonstrates multi-agent patterns on a runnable service:

* **Sequential + concurrent** — an intake agent runs first, then the credit-risk
  and compliance agents run **concurrently** (``asyncio.gather``).
* **Handoff** — results hand off to the underwriter agent for a decision.
* **Human-in-the-loop** — edge cases pause as ``awaiting_approval`` and are resumed
  via an approve endpoint; run state lives in a store (Cosmos DB in prod).

The pipeline is deterministic and fully offline/testable. ``FOUNDRY_PROJECT_ENDPOINT``
toggles a ``mode`` flag; the orchestration itself is the lesson.
"""

from __future__ import annotations

import asyncio
import re
import uuid
from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ── settings ────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    foundry_project_endpoint: str = ""
    foundry_model_name: str = "gpt-4o"
    hitl_amount_threshold: float = 250_000.0

    @property
    def use_foundry(self) -> bool:
        return bool(self.foundry_project_endpoint)


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ── schemas ─────────────────────────────────────────────────────────────
class UnderwriteRequest(BaseModel):
    applicant_summary: str = Field(..., min_length=1, description="Free-text loan application summary.")


class ApproveRequest(BaseModel):
    approved: bool
    note: str | None = None


class UnderwriteRun(BaseModel):
    run_id: str
    status: str  # running | awaiting_approval | completed
    decision: str  # pending | approved | rejected
    applicant: dict
    risk: dict
    compliance: dict
    steps: list[str]
    mode: str


# ── run store (Cosmos DB in prod) ───────────────────────────────────────
_RUNS: dict[str, UnderwriteRun] = {}


def get_run(run_id: str) -> UnderwriteRun | None:
    return _RUNS.get(run_id)


# ── agents ──────────────────────────────────────────────────────────────
def intake_agent(text: str) -> dict:
    name_m = re.search(r"applicant[:\s]+([A-Za-z.\- ]+?)(?:,|$)", text, re.IGNORECASE)
    score_m = re.search(r"(?:credit score|score)[^\d]*(\d{3})", text, re.IGNORECASE)
    income = _money(re.search(r"income[^\d]*\$?\s*([\d,]+)\s*(k)?", text, re.IGNORECASE))
    amount = _money(
        re.search(r"(?:requesting|loan|mortgage|amount|borrow)[^\d]*\$?\s*([\d,]+)\s*(k)?", text, re.IGNORECASE)
    )
    return {
        "name": name_m.group(1).strip() if name_m else None,
        "credit_score": int(score_m.group(1)) if score_m else None,
        "income": income,
        "amount": amount,
    }


async def credit_risk_agent(applicant: dict) -> dict:
    score = applicant.get("credit_score") or 0
    if score >= 680:
        level = "low"
    elif score >= 600:
        level = "medium"
    else:
        level = "high"
    return {"risk_level": level, "credit_score": score}


async def compliance_agent(applicant: dict, text: str) -> dict:
    flagged = any(w in text.lower() for w in ("sanction", "watchlist", "fraud"))
    return {"kyc": "pass", "aml": "flagged" if flagged else "pass", "passed": not flagged}


def underwriter_agent(applicant: dict, risk: dict, compliance: dict, threshold: float) -> tuple[str, str]:
    """Returns (status, decision)."""
    if not compliance["passed"]:
        return "completed", "rejected"
    if risk["risk_level"] == "high":
        return "completed", "rejected"
    amount = applicant.get("amount") or 0
    if risk["risk_level"] == "medium" or amount > threshold:
        return "awaiting_approval", "pending"  # human-in-the-loop
    return "completed", "approved"


def _money(m: re.Match | None) -> float | None:
    if not m:
        return None
    val = float(m.group(1).replace(",", ""))
    if m.lastindex and m.lastindex >= 2 and (m.group(2) or "").lower() == "k":
        val *= 1000
    return val


# ── orchestration ───────────────────────────────────────────────────────
async def run_underwriting(request: UnderwriteRequest) -> UnderwriteRun:
    settings = get_settings()
    steps = ["Intake agent extracting application data."]
    applicant = intake_agent(request.applicant_summary)

    steps.append("Running credit-risk + compliance agents concurrently.")
    risk, compliance = await asyncio.gather(
        credit_risk_agent(applicant),
        compliance_agent(applicant, request.applicant_summary),
    )
    steps.append(f"Risk={risk['risk_level']}, compliance_passed={compliance['passed']}.")

    status, decision = underwriter_agent(applicant, risk, compliance, settings.hitl_amount_threshold)
    steps.append(
        "Underwriter decision: human approval required."
        if status == "awaiting_approval"
        else f"Underwriter decision: {decision}."
    )

    run = UnderwriteRun(
        run_id=f"RUN-{uuid.uuid4().hex[:8].upper()}",
        status=status,
        decision=decision,
        applicant=applicant,
        risk=risk,
        compliance=compliance,
        steps=steps,
        mode="foundry" if settings.use_foundry else "mock",
    )
    _RUNS[run.run_id] = run
    return run


def resume_underwriting(run_id: str, approval: ApproveRequest) -> UnderwriteRun | None:
    run = _RUNS.get(run_id)
    if run is None or run.status != "awaiting_approval":
        return run
    run.decision = "approved" if approval.approved else "rejected"
    run.status = "completed"
    run.steps.append(f"Human approver resolved: {run.decision}" + (f" ({approval.note})" if approval.note else "."))
    return run
