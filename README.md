# AI Production Incident Investigator

An AI agent that investigates simulated production incidents in a checkout/order API.

The local MVP gathers telemetry, recent configuration changes, and troubleshooting guidance, then produces an evidence-backed incident diagnosis. The first deterministic scenario is a checkout request path whose latency increases to about 4 seconds.

## Current Architecture

```text
Next.js Incident Console
        |
        | HTTPS IncidentRequest
        v
FastAPI Investigation API
        |
        v
Local Investigation Orchestrator
   |          |           |
   v          v           v
Telemetry   Recent      Local
Tool        Changes     Runbook
   |          |
   +----- Local Checkout Simulator
```

The evaluation path starts in the Incident Console, seeds the known high-latency scenario, runs the same investigation logic, compares the report with the expected root cause/evidence, and returns a score to the console.

## Repository Structure

```text
backend/     FastAPI investigation API, local tools, orchestrator, evaluation harness
frontend/    Next.js incident console
simulator/   Tiny checkout/order API and deterministic incident telemetry
```

## Implemented MVP

- Tiny checkout/order API simulator
- One deterministic high-latency incident (~4 seconds)
- Structured local telemetry with p95 latency and error-rate metrics
- FastAPI `IncidentRequest` and `IncidentReport` models
- Read-only telemetry, recent-change, and local-knowledge tools
- Deterministic local investigation orchestrator
- Evidence IDs and tool-call timeline for traceability
- High-latency evaluation harness
- Next.js console for investigations and evaluation results

## Run Locally

Use three terminals from the repository root.

### 1. Simulator

```bash
cd simulator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### 2. Investigation backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

For the quickest end-to-end test, click **Evaluate known high-latency scenario**. The evaluation harness seeds deterministic telemetry, runs the investigation, and displays whether the expected root cause and evidence were found.

## Tests

```bash
cd backend && pytest
cd ../simulator && pytest
```

## Cloud Phase (Planned)

After the local investigation flow is reliable:

- Send application logs/metrics to Amazon CloudWatch
- Move read-only cloud investigation tools to AWS Lambda
- Replace the deterministic local orchestrator with Amazon Bedrock / AgentCore
- Move troubleshooting documents to a Bedrock Knowledge Base
- Add IAM controls, cost limits, and cloud evaluation/observability

## Planned Tech Stack

- Python / FastAPI / Pydantic
- Next.js / React / TypeScript
- AWS CloudWatch
- AWS Lambda
- Amazon Bedrock / AgentCore
- Bedrock Knowledge Bases
- Docker (later local packaging/polish phase)

## Status

Local MVP foundation implemented. AWS integration is intentionally deferred until the local flow is tested and understandable end-to-end.
