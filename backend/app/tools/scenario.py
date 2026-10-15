import httpx

from app.tools.common import ToolUnavailableError


class ScenarioTool:
    """Developer/test-only tool used by the evaluation harness."""

    def __init__(self, simulator_base_url: str) -> None:
        self.simulator_base_url = simulator_base_url.rstrip("/")

    async def seed_high_latency(self) -> None:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.simulator_base_url}/api/scenarios/high-latency/seed"
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ToolUnavailableError(
                "The high-latency evaluation scenario could not be seeded."
            ) from exc
