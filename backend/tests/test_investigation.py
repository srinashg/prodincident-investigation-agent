import pytest

from app.schemas import IncidentRequest
from app.services.investigation import InvestigationService


class FakeTelemetryTool:
    async def get_checkout_telemetry(self):
        return {
            "request_count": 20,
            "error_rate_percent": 0.0,
            "p95_latency_ms": 4000.0,
        }


class FakeRecentChangeTool:
    async def get_recent_changes(self):
        return [
            {
                "summary": "CHECKOUT_PROCESSING_DELAY_MS changed from 50 to 4000."
            }
        ]


class FakeKnowledgeTool:
    async def search(self, query: str):
        return [
            {
                "title": "Checkout high-latency runbook",
                "summary": "Check p95 latency and recent configuration changes.",
            }
        ]


@pytest.mark.asyncio
async def test_high_latency_investigation_is_evidence_backed():
    service = InvestigationService(
        telemetry_tool=FakeTelemetryTool(),
        recent_change_tool=FakeRecentChangeTool(),
        knowledge_tool=FakeKnowledgeTool(),
    )

    report = await service.investigate(
        IncidentRequest(symptom="Checkout latency increased to 4 seconds")
    )

    assert report.confidence == 0.95
    assert "4000 ms" in report.likely_cause
    assert {item.source for item in report.evidence} >= {
        "local telemetry",
        "recent changes",
    }
    assert len(report.tool_timeline) == 3
