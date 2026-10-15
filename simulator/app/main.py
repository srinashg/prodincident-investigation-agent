import asyncio

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.state import TelemetryEvent, calculate_p95, state, utc_now

app = FastAPI(title="Checkout Incident Simulator", version="0.1.0")


class CheckoutRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    item_count: int = Field(default=1, ge=1, le=20)
    scenario: str | None = None


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/checkout")
async def checkout(request: CheckoutRequest) -> dict[str, str | int]:
    delay_ms = 4000 if request.scenario == "high-latency" else 50
    await asyncio.sleep(delay_ms / 1000)

    state.events.append(
        TelemetryEvent(
            latency_ms=float(delay_ms),
            status_code=200,
            timestamp=utc_now(),
        )
    )

    return {
        "status": "accepted",
        "customer_id": request.customer_id,
        "item_count": request.item_count,
    }


@app.post("/api/scenarios/high-latency/seed")
async def seed_high_latency() -> dict[str, str | int]:
    """Seed deterministic telemetry without forcing tests to wait for 20 real 4-second calls."""
    state.reset()

    for _ in range(20):
        state.events.append(
            TelemetryEvent(
                latency_ms=4000.0,
                status_code=200,
                timestamp=utc_now(),
            )
        )

    state.changes.append(
        {
            "timestamp": utc_now(),
            "type": "configuration",
            "summary": "CHECKOUT_PROCESSING_DELAY_MS changed from 50 to 4000.",
        }
    )

    return {"scenario": "checkout-high-latency-v1", "seeded_requests": 20}


@app.get("/api/telemetry/checkout")
async def checkout_telemetry() -> dict[str, object]:
    latencies = [event.latency_ms for event in state.events]
    errors = [event for event in state.events if event.status_code >= 500]
    request_count = len(state.events)

    return {
        "request_count": request_count,
        "error_count": len(errors),
        "error_rate_percent": (
            (len(errors) / request_count) * 100 if request_count else 0.0
        ),
        "average_latency_ms": (
            sum(latencies) / request_count if request_count else 0.0
        ),
        "p95_latency_ms": calculate_p95(latencies),
        "events": [event.__dict__ for event in state.events[-25:]],
    }


@app.get("/api/changes")
async def recent_changes() -> dict[str, object]:
    return {"changes": state.changes[-10:]}
