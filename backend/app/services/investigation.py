from uuid import uuid4

from app.schemas import Evidence, IncidentReport, IncidentRequest, ToolStep
from app.tools.changes import RecentChangeTool
from app.tools.knowledge import KnowledgeTool
from app.tools.telemetry import TelemetryTool


class InvestigationService:
    """Deterministic local orchestrator that will later be replaced by the AI agent."""

    def __init__(
        self,
        telemetry_tool: TelemetryTool,
        recent_change_tool: RecentChangeTool,
        knowledge_tool: KnowledgeTool,
    ) -> None:
        self.telemetry_tool = telemetry_tool
        self.recent_change_tool = recent_change_tool
        self.knowledge_tool = knowledge_tool

    async def investigate(self, request: IncidentRequest) -> IncidentReport:
        timeline: list[ToolStep] = []
        evidence: list[Evidence] = []

        telemetry = await self.telemetry_tool.get_checkout_telemetry()
        timeline.append(
            ToolStep(
                tool="telemetry",
                status="success",
                detail="Retrieved local checkout logs and latency/error metrics.",
            )
        )
        evidence.append(
            Evidence(
                id="telemetry-1",
                source="local telemetry",
                summary=(
                    f"Across {telemetry['request_count']} checkout requests, "
                    f"p95 latency is {telemetry['p95_latency_ms']:.0f} ms and "
                    f"the error rate is {telemetry['error_rate_percent']:.1f}%."
                ),
            )
        )

        changes = await self.recent_change_tool.get_recent_changes()
        timeline.append(
            ToolStep(
                tool="recent_changes",
                status="success",
                detail="Retrieved recent simulator deployment/configuration changes.",
            )
        )
        for index, change in enumerate(changes[:3], start=1):
            evidence.append(
                Evidence(
                    id=f"change-{index}",
                    source="recent changes",
                    summary=change["summary"],
                )
            )

        knowledge = await self.knowledge_tool.search(request.symptom)
        timeline.append(
            ToolStep(
                tool="knowledge",
                status="success",
                detail="Searched the local troubleshooting runbook.",
            )
        )
        for index, document in enumerate(knowledge[:2], start=1):
            evidence.append(
                Evidence(
                    id=f"knowledge-{index}",
                    source=document["title"],
                    summary=document["summary"],
                )
            )

        p95_latency_ms = float(telemetry["p95_latency_ms"])
        processing_delay_ms = self._find_processing_delay_change(changes)

        if (
            processing_delay_ms is not None
            and p95_latency_ms >= processing_delay_ms * 0.8
        ):
            likely_cause = (
                f"The checkout processing delay was changed to {processing_delay_ms} ms, "
                "which is causing the sustained high checkout latency."
            )
            confidence = 0.95
            next_checks = [
                "Restore the checkout processing delay to its normal value.",
                "Repeat checkout requests and confirm p95 latency returns below the normal threshold.",
                "Verify no downstream dependency or database latency remains elevated.",
            ]
        elif p95_latency_ms >= 3000:
            likely_cause = (
                "Checkout requests have sustained high latency, but the available evidence "
                "does not yet identify one specific configuration or dependency as the cause."
            )
            confidence = 0.75
            next_checks = [
                "Inspect slow database and downstream dependency calls.",
                "Compare current configuration with the last known healthy version.",
            ]
        else:
            likely_cause = (
                "The available telemetry does not show the expected high-latency incident."
            )
            confidence = 0.40
            next_checks = [
                "Generate or reproduce the incident, then run the investigation again."
            ]

        return IncidentReport(
            investigation_id=str(uuid4()),
            symptom=request.symptom,
            service=request.service,
            likely_cause=likely_cause,
            confidence=confidence,
            evidence=evidence,
            tool_timeline=timeline,
            recommended_next_checks=next_checks,
        )

    @staticmethod
    def _find_processing_delay_change(changes: list[dict]) -> int | None:
        """Read the configured delay from structured recent-change evidence."""
        for change in changes:
            if change.get("field") == "CHECKOUT_PROCESSING_DELAY_MS":
                value = change.get("new_value_ms")
                if isinstance(value, (int, float)):
                    return int(value)
        return None
