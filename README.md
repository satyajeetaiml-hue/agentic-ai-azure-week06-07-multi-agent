# Weeks 6–7 — Multi-Agent Orchestration Patterns

[![CI](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week06-07-multi-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week06-07-multi-agent/actions/workflows/ci.yml)

> **Standalone lab** from the *Agentic AI on Azure — Enterprise Master Class* (12 weeks).
> Each lab is an independent, runnable FastAPI starter. Part of the
> [course series](https://github.com/satyajeetaiml-hue?tab=repositories&q=agentic-ai-azure).

---

## 🎯 Learning goal
Implement sequential, concurrent, handoff, group-chat, and graph-based orchestration with human-in-the-loop.

## 🏢 Enterprise use case — "Loan Underwriting Pipeline" (Banking)
Intake Agent extracts application data; Credit Risk and Compliance agents run concurrently; an Underwriter agent receives a handoff and decides, with human-in-the-loop approval for edge cases. Orchestrated as a graph with aggregated, explained results.

---

## 🧪 What you'll build (lab)
1. Build the multi-agent graph using Agent Framework orchestration.
2. Implement an approval **pause/resume** with Durable Tasks.
3. Expose `/underwrite` via FastAPI with async background execution + status polling.
4. Add inter-agent communication via **A2A** and an event-driven topology.

> This starter ships with a **runnable mock** of the endpoint so you can run and test
> immediately, then progressively replace the mock with the real Azure implementation.

## 🏗️ Architect's lens
- Pattern selection: when concurrency helps (independent sub-tasks) vs. sequential dependencies.
- Human-in-the-loop checkpoints and durable state for long-running approvals.
- Inter-agent communication via **A2A** + event-driven topologies (Service Bus / Event Grid).
- Failure handling: partial results, compensation, retries.

## 🧰 Tech stack
Microsoft Agent Framework orchestration, A2A protocol, Azure Service Bus / Event Grid, Azure Durable Functions, FastAPI BackgroundTasks, Cosmos DB for run state.

---

## 🚀 Quick start

```bash
# 1. Create & activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) copy the env template — runs in MOCK mode without it
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux

# 4. Run the API
uvicorn app.main:app --reload
```

Open the interactive docs at **http://127.0.0.1:8000/docs**.

### Try the endpoint
```bash
curl -X POST http://127.0.0.1:8000/api/v1/underwrite \
  -H "Content-Type: application/json" \
  -d '{"applicant_summary": "Applicant: J. Smith, income $95k, requesting $300k mortgage, credit score 712."}'
```

### Run the tests
```bash
pytest -q
```

### Run with Docker
```bash
docker build -t agentic-ai-azure-week06-07-multi-agent .
docker run -p 8000:8000 agentic-ai-azure-week06-07-multi-agent
```

---

## 📁 Project structure
```
agentic-ai-azure-week06-07-multi-agent/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI app + the /api/v1/underwrite endpoint
├── tests/
│   └── test_smoke.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

---

## 🗺️ Where this fits
This repo covers **Weeks 6–7 — Multi-Agent Orchestration Patterns**. The full 12-week path and reference architecture
live in the master-class companion repo:
**[azure-agentic-ai-masterclass](https://github.com/satyajeetaiml-hue/azure-agentic-ai-masterclass)**.

## 📄 License
MIT — see [`LICENSE`](LICENSE).
