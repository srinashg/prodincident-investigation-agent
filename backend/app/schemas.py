from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    symptom: str = Field(min_length=3, max_length=500)
    service: str = Field(default="checkout", min_length=1, max_length=100)
    time_window_minutes: int = Field(default=5, ge=1, le=60)


class EvaluationRequest(BaseModel):
    latency_seconds: float = Field(default=4.0, gt=0, le=60)


class Evidence(BaseModel):
    id: str
    source: str
    summary: str


class ToolStep(BaseModel):
    tool: str
    status: str
    detail: str


class IncidentReport(BaseModel):
    investigation_id: str
    symptom: str
    service: str
    likely_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[Evidence]
    tool_timeline: list[ToolStep]
    recommended_next_checks: list[str]


class EvaluationResult(BaseModel):
    scenario_id: str
    passed: bool
    root_cause_match: bool
    required_evidence_found: bool
    score: float = Field(ge=0.0, le=1.0)
    report: IncidentReport
