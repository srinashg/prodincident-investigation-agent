import httpx

from app.tools.common import ToolUnavailableError


class ScenarioTool:
    """Developer/test-only tool used by the evaluation harness."""

    def __init__(self, simulator_base_url: str) -> None:
        self.simulator_base_url = simulator_base_url.rstrip("/")

    async def seed_high_latency(self, latency_seconds: float) -> dict[str, object]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.simulator_base_url}/api/scenarios/high-latency/seed",
                    json={"latency_seconds": latency_seconds},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise ToolUnavailableError(
                "The high-latency evaluation scenario could not be seeded."
            ) from exc
