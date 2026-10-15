# AI Production Incident Investigator

An AI agent that investigates simulated production incidents in a checkout/order API.

The system will gather logs, metrics, configuration changes, and troubleshooting documentation, then generate an evidence-backed incident diagnosis.

## Planned Architecture

Next.js → FastAPI → Investigation Agent → tools → logs/metrics + knowledge base → IncidentReport

## Initial MVP

- Tiny checkout/order API
- One simulated high-latency incident
- FastAPI investigation backend
- Structured incident reports
- Local-first development before AWS deployment

## Planned Tech Stack

- Python
- FastAPI
- Next.js
- Docker
- AWS CloudWatch
- AWS Lambda
- Amazon Bedrock / AgentCore

## Status

In development
