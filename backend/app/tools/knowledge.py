from typing import Any


class KnowledgeTool:
    """Local stand-in for the future Bedrock Knowledge Base."""

    async def search(self, query: str) -> list[dict[str, Any]]:
        normalized = query.lower()
        if "latency" in normalized or "slow" in normalized or "checkout" in normalized:
            return [
                {
                    "title": "Checkout high-latency runbook",
                    "summary": (
                        "Check p95 latency, recent configuration/deployment changes, "
                        "and slow database or downstream calls before forming a root-cause hypothesis."
                    ),
                }
            ]
        return []
