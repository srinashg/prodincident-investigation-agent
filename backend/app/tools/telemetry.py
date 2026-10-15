from typing import Any

import httpx

from app.tools.common import ToolUnavailableError


class TelemetryTool:
    def __init__(self, simulator_base_url: str) -> None:
        self.simulator_base_url = simulator_base_url.rstrip("/")

    async def get_checkout_telemetry(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.simulator_base_url}/api/telemetry/checkout"
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise ToolUnavailableError(
                "Checkout telemetry is unavailable from the local simulator."
            ) from exc
