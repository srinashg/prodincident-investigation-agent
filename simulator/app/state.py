from dataclasses import dataclass, field
from datetime import datetime, timezone
import math


@dataclass
class TelemetryEvent:
    latency_ms: float
    status_code: int
    timestamp: str
    endpoint: str
    dependency: str
    dependency_duration_ms: float


@dataclass
class SimulatorState:
    events: list[TelemetryEvent] = field(default_factory=list)
    changes: list[dict[str, object]] = field(default_factory=list)
    processing_delay_ms: int = 50

    def reset(self) -> None:
        self.events.clear()
        self.changes.clear()
        self.processing_delay_ms = 50


state = SimulatorState()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def calculate_p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return float(ordered[index])
