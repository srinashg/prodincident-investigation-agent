from dataclasses import dataclass, field
from datetime import datetime, timezone
import math


@dataclass
class TelemetryEvent:
    latency_ms: float
    status_code: int
    timestamp: str


@dataclass
class SimulatorState:
    events: list[TelemetryEvent] = field(default_factory=list)
    changes: list[dict[str, str]] = field(default_factory=list)

    def reset(self) -> None:
        self.events.clear()
        self.changes.clear()


state = SimulatorState()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def calculate_p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return float(ordered[index])
