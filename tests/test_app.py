"""Hermetic tests for the Weeks 6-7 underwriting pipeline."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_low_amount_high_score_approved():
    r = client.post(
        "/api/v1/underwrite",
        json={"applicant_summary": "Applicant: A. Lee, income $80k, requesting $20k loan, credit score 740."},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["risk"]["risk_level"] == "low"
    assert body["status"] == "completed"
    assert body["decision"] == "approved"


def test_large_amount_triggers_human_in_the_loop():
    r = client.post(
        "/api/v1/underwrite",
        json={"applicant_summary": "Applicant: J. Smith, income $95k, requesting $300k mortgage, credit score 712."},
    )
    body = r.json()
    assert body["status"] == "awaiting_approval"
    assert body["decision"] == "pending"

    # Resume via human approval.
    approved = client.post(f"/api/v1/runs/{body['run_id']}/approve", json={"approved": True}).json()
    assert approved["status"] == "completed"
    assert approved["decision"] == "approved"


def test_low_credit_score_rejected():
    r = client.post(
        "/api/v1/underwrite",
        json={"applicant_summary": "Applicant: B. Doe, income $40k, requesting $50k loan, credit score 540."},
    )
    body = r.json()
    assert body["risk"]["risk_level"] == "high"
    assert body["decision"] == "rejected"


def test_compliance_flag_rejected():
    r = client.post(
        "/api/v1/underwrite",
        json={"applicant_summary": "Applicant on watchlist, income $90k, requesting $20k, credit score 720."},
    )
    assert r.json()["decision"] == "rejected"


def test_status_polling_and_404():
    started = client.post(
        "/api/v1/underwrite",
        json={"applicant_summary": "Applicant: C. Ray, income $80k, requesting $15k, credit score 700."},
    ).json()
    polled = client.get(f"/api/v1/runs/{started['run_id']}")
    assert polled.status_code == 200
    assert polled.json()["run_id"] == started["run_id"]
    assert client.get("/api/v1/runs/RUN-DOESNOTEXIST").status_code == 404


def test_validation_rejects_empty():
    assert client.post("/api/v1/underwrite", json={"applicant_summary": ""}).status_code == 422
