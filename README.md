# Weeks 6–7 — Multi-Agent Orchestration Patterns

[![CI](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week06-07-multi-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week06-07-multi-agent/actions/workflows/ci.yml)

> ▶️ **Run in VS Code — no Azure needed.** `pip install -r requirements.txt`, then `uvicorn app.main:app --reload` and open http://127.0.0.1:8000/docs. Runs in **mock mode** by default — no `az login`, keys, or `.env` required. Wiring real Azure (below) is optional.

> **Standalone lab** from the *Agentic AI on Azure — Enterprise Master Class*.
> Course hub: [azure-agentic-ai-masterclass](https://github.com/satyajeetaiml-hue/azure-agentic-ai-masterclass).

---

## 🎯 Learning goal
Implement sequential, **concurrent**, handoff, and **human-in-the-loop** orchestration.

## 🏢 Enterprise use case — "Loan Underwriting Pipeline" (Banking)
Intake → (Credit-Risk ‖ Compliance, concurrent) → Underwriter handoff, with human approval for edge cases.

## ✅ What this repo implements
- **Sequential + concurrent** agents — intake first, then credit-risk and compliance via `asyncio.gather`.
- **Handoff** to an underwriter agent that applies decision rules.
- **Human-in-the-loop** — large/medium-risk loans pause as `awaiting_approval`; resume via approve endpoint.
- **Run store + status polling** — every run is addressable; Cosmos DB is the prod backing store.

Fully runnable offline; no Azure required. (`FOUNDRY_PROJECT_ENDPOINT` only flips the reported mode.)

## 🚀 Quick start
```bash
python -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
```bash
# Large loan -> pauses for human approval
curl -X POST http://127.0.0.1:8000/api/v1/underwrite \
  -H "Content-Type: application/json" \
  -d '{"applicant_summary": "Applicant: J. Smith, income $95k, requesting $300k mortgage, credit score 712."}'
# -> note the run_id, then:
curl -X POST http://127.0.0.1:8000/api/v1/runs/<run_id>/approve \
  -H "Content-Type: application/json" -d '{"approved": true}'
```
Run tests: `pytest -q`

## 🔌 Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/underwrite` | Start the pipeline |
| GET | `/api/v1/runs/{run_id}` | Poll run status |
| POST | `/api/v1/runs/{run_id}/approve` | Human-in-the-loop resume |

## 🏗️ Architect's lens
- Concurrency (independent sub-tasks) vs. sequential dependencies.
- Durable state for long-running approvals; **Durable Functions / Durable Tasks** in prod.
- Inter-agent comms via **A2A** + event-driven topologies (Service Bus / Event Grid).
- Failure handling: partial results, compensation, retries.

## 🧰 Tech stack
Agent Framework orchestration, A2A, Service Bus / Event Grid, Durable Functions, FastAPI, Cosmos DB.

## 📁 Structure
```
app/service.py   # agents, orchestration (asyncio.gather), run store, HITL resume
app/main.py      # underwrite + status + approve endpoints
tests/test_app.py
```

## 🗺️ Series
Prev: [Week 5](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week05-mcp-tools) ·
Next: [Week 8 — RAG](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week08-rag-grounding) ·
[All labs](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure)

## 📄 License
MIT — see [`LICENSE`](LICENSE).

## 📊 Teaching slides

Download the **7-slide deck** for classroom use: [`agentic-ai-azure-week06-07-multi-agent.pptx`](slides/agentic-ai-azure-week06-07-multi-agent.pptx)

Prefer PDF? Download the **handout (slides + speaker notes)**: [`agentic-ai-azure-week06-07-multi-agent-handout.pdf`](slides/agentic-ai-azure-week06-07-multi-agent-handout.pdf)

> Slides: Title · Learning goal · Enterprise use case · Architecture/flow · Key concepts · Run it · Architect's takeaways.

