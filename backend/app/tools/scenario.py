import asyncio

import httpx

from app.tools.common import ToolUnavailableError


class ScenarioTool:
    """Developer/test-only tool used by the evaluation harness."""

    def __init__(self, simulator_base_url: str) -> None:
        self.simulator_base_url = simulator_base_url.rstrip("/")

    async def seed_high_latency(self, latency_seconds: float) -> dict[str, object]:
        try:
            timeout = httpx.Timeout(70.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                config_response = await client.post(
                    f"{self.simulator_base_url}/api/scenarios/high-latency/seed",
                    json={"latency_seconds": latency_seconds},
                )
                config_response.raise_for_status()
                scenario = config_response.json()

                async def send_checkout(index: int) -> dict[str, object]:
                    response = await client.post(
                        f"{self.simulator_base_url}/api/checkout",
                        json={
                            "customer_id": f"load-test-{index}",
                            "item_count": 1,
                        },
                    )
                    response.raise_for_status()
                    return response.json()

                results = await asyncio.gather(
                    *(send_checkout(index) for index in range(20))
                )

                scenario["generated_requests"] = len(results)
                scenario["measured_durations_ms"] = [
                    result["duration_ms"] for result in results
                ]
                return scenario
        except httpx.HTTPError as exc:
            raise ToolUnavailableError(
                "The high-latency evaluation scenario could not be generated."
            ) from exc
