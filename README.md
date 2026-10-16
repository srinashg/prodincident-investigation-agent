# AI Production Incident Investigator

An AI agent that investigates simulated production incidents in a checkout/order API.

The local MVP gathers telemetry, recent configuration changes, and troubleshooting guidance, then produces an evidence-backed incident diagnosis. The first deterministic scenario is a checkout request path whose latency increases to about 4 seconds because a deliberately slow payment dependency actually delays real checkout requests.

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
                 |
                 v
        Slow payment dependency
```

The evaluation path configures the high-latency scenario, sends real concurrent checkout requests through the simulator, measures their actual elapsed time, then runs the same investigation logic and compares the report with the expected root cause/evidence.

## Repository Structure

```text
backend/     FastAPI investigation API, local tools, orchestrator, evaluation harness
frontend/    Next.js incident console
simulator/   Tiny checkout/order API and deliberately slow dependency
```

## Implemented MVP

- Tiny checkout/order API simulator
- One deterministic high-latency incident (~4 seconds)
- Real checkout requests that wait on a deliberately slow payment dependency
- Measured checkout duration and payment-dependency duration
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

For the quickest end-to-end test, choose a simulated checkout latency and click **Run simulated latency scenario**. The harness configures the dependency delay, generates 20 real checkout requests concurrently, records their measured latency, and then evaluates the investigation result.

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

The first incident now produces measured telemetry from real delayed checkout requests. AWS integration is intentionally deferred until this local path is tested and understandable end-to-end.
