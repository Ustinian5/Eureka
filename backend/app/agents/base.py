from __future__ import annotations

from typing import Protocol

from backend.app.models import ResearchState


class Agent(Protocol):
    name: str

    async def run(self, state: ResearchState) -> ResearchState: ...
