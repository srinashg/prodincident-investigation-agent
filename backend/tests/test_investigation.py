import pytest

from app.schemas import IncidentRequest
from app.services.investigation import InvestigationService


class FakeTelemetryTool:
    def __init__(self, p95_latency_ms: float):
        self.p95_latency_ms = p95_latency_ms

    async def get_checkout_telemetry(self):
        return {
            "request_count": 20,
            "error_rate_percent": 0.0,
            "p95_latency_ms": self.p95_latency_ms,
        }


class FakeRecentChangeTool:
    def __init__(self, changes):
        self.changes = changes

    async def get_recent_changes(self):
        return self.changes


class FakeKnowledgeTool:
    async def search(self, query: str):
        return [
            {
                "title": "Checkout high-latency runbook",
                "summary": "Check p95 latency and recent configuration changes.",
            }
        ]


def build_service(p95_latency_ms: float, changes: list[dict]) -> InvestigationService:
    return InvestigationService(
        telemetry_tool=FakeTelemetryTool(p95_latency_ms),
        recent_change_tool=FakeRecentChangeTool(changes),
        knowledge_tool=FakeKnowledgeTool(),
    )


@pytest.mark.asyncio
async def test_high_latency_with_matching_change_identifies_processing_delay():
    service = build_service(
        p95_latency_ms=6500.0,
        changes=[
            {
                "field": "CHECKOUT_PROCESSING_DELAY_MS",
                "previous_value_ms": 50,
                "new_value_ms": 6500,
                "summary": "CHECKOUT_PROCESSING_DELAY_MS changed from 50 to 6500.",
            }
        ],
    )

    report = await service.investigate(
        IncidentRequest(symptom="Checkout latency increased to 6.5 seconds")
    )

    assert report.confidence == 0.95
    assert "6500 ms" in report.likely_cause


@pytest.mark.asyncio
async def test_high_latency_without_matching_change_returns_unknown_cause():
    service = build_service(
        p95_latency_ms=4200.0,
        changes=[],
    )

    report = await service.investigate(
        IncidentRequest(symptom="Checkout latency increased to 4.2 seconds")
    )

    assert report.confidence == 0.75
    assert "does not yet identify one specific" in report.likely_cause


@pytest.mark.asyncio
async def test_normal_latency_does_not_report_high_latency_incident():
    service = build_service(
        p95_latency_ms=800.0,
        changes=[
            {
                "field": "CHECKOUT_PROCESSING_DELAY_MS",
                "previous_value_ms": 50,
                "new_value_ms": 800,
                "summary": "CHECKOUT_PROCESSING_DELAY_MS changed from 50 to 800.",
            }
        ],
    )

    report = await service.investigate(
        IncidentRequest(symptom="Checkout latency increased to 0.8 seconds")
    )

    assert report.confidence == 0.40
    assert "does not show the expected high-latency incident" in report.likely_cause
