import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import EvaluationResult, IncidentReport, IncidentRequest
from app.services.evaluation import EvaluationService
from app.services.investigation import InvestigationService
from app.tools.changes import RecentChangeTool
from app.tools.common import ToolUnavailableError
from app.tools.knowledge import KnowledgeTool
from app.tools.scenario import ScenarioTool
from app.tools.telemetry import TelemetryTool

SIMULATOR_BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://localhost:8001")

telemetry_tool = TelemetryTool(SIMULATOR_BASE_URL)
recent_change_tool = RecentChangeTool(SIMULATOR_BASE_URL)
knowledge_tool = KnowledgeTool()
scenario_tool = ScenarioTool(SIMULATOR_BASE_URL)

investigation_service = InvestigationService(
    telemetry_tool=telemetry_tool,
    recent_change_tool=recent_change_tool,
    knowledge_tool=knowledge_tool,
)
evaluation_service = EvaluationService(
    investigation_service=investigation_service,
    scenario_tool=scenario_tool,
)

app = FastAPI(
    title="Production Incident Investigation API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/investigations", response_model=IncidentReport)
async def investigate(request: IncidentRequest) -> IncidentReport:
    try:
        return await investigation_service.investigate(request)
    except ToolUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/evaluations/high-latency", response_model=EvaluationResult)
async def evaluate_high_latency() -> EvaluationResult:
    try:
        return await evaluation_service.evaluate_high_latency()
    except ToolUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
