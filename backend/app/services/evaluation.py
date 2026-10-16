from app.schemas import EvaluationResult, IncidentRequest
from app.services.investigation import InvestigationService
from app.tools.scenario import ScenarioTool


class EvaluationService:
    def __init__(
        self,
        investigation_service: InvestigationService,
        scenario_tool: ScenarioTool,
    ) -> None:
        self.investigation_service = investigation_service
        self.scenario_tool = scenario_tool

    async def evaluate_high_latency(
        self,
        latency_seconds: float = 4.0,
    ) -> EvaluationResult:
        scenario = await self.scenario_tool.seed_high_latency(latency_seconds)
        latency_ms = int(scenario["latency_ms"])

        report = await self.investigation_service.investigate(
            IncidentRequest(
                symptom=(
                    "Checkout latency increased to about "
                    f"{latency_seconds:g} seconds"
                ),
                service="checkout",
                time_window_minutes=5,
            )
        )

        root_cause_match = (
            f"{latency_ms} ms" in report.likely_cause
            and "processing delay" in report.likely_cause.lower()
        )
        evidence_sources = {item.source for item in report.evidence}
        required_evidence_found = {
            "local telemetry",
            "recent changes",
        }.issubset(evidence_sources)

        score = (float(root_cause_match) + float(required_evidence_found)) / 2.0

        return EvaluationResult(
            scenario_id=f"checkout-high-latency-{latency_ms}ms",
            passed=score == 1.0,
            root_cause_match=root_cause_match,
            required_evidence_found=required_evidence_found,
            score=score,
            report=report,
        )
