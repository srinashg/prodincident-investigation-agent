from typing import Any

import httpx

from app.tools.common import ToolUnavailableError


class RecentChangeTool:
    def __init__(self, simulator_base_url: str) -> None:
        self.simulator_base_url = simulator_base_url.rstrip("/")

    async def get_recent_changes(self) -> list[dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.simulator_base_url}/api/changes")
                response.raise_for_status()
                payload = response.json()
                return payload.get("changes", [])
        except httpx.HTTPError as exc:
            raise ToolUnavailableError(
                "Recent deployment/configuration changes are unavailable."
            ) from exc
