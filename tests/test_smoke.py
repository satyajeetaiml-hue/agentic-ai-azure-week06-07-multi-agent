"""Smoke tests for Weeks 6–7 — Multi-Agent Orchestration Patterns."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_endpoint_accepts_input():
    r = client.post("/api/v1/underwrite", json={"applicant_summary": "Applicant: J. Smith, income $95k, requesting $300k mortgage, credit score 712."})
    assert r.status_code == 200


def test_endpoint_rejects_empty():
    r = client.post("/api/v1/underwrite", json={"applicant_summary": ""})
    assert r.status_code == 422
