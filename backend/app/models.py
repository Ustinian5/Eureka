from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class ResearchRequest:
    context: str
    user_query: str = ""
    page_title: str = ""
    page_url: str = ""
    provider: str = "custom"
    template: str = "summary"


@dataclass(slots=True)
class IntentDecision:
    route: str
    reason: str = ""
    search_queries: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SearchResult:
    title: str
    url: str
    snippet: str


@dataclass(slots=True)
class ChatResponse:
    content: str
    reasoning_content: str = ""


@dataclass(slots=True)
class TraceEvent:
    agent: str
    content: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class EvidenceCard:
    title: str
    url: str
    snippet: str
    relevance: str = ""
    query: str = ""
    quote: str = ""
    source_type: str = "web"
    confidence: float = 0.0


@dataclass(slots=True)
class ResearchState:
    request: ResearchRequest
    route: str = "context_answer"
    route_reason: str = ""
    context_summary: str = ""
    key_points: list[str] = field(default_factory=list)
    sub_questions: list[str] = field(default_factory=list)
    search_queries: list[str] = field(default_factory=list)
    evidence_cards: list[EvidenceCard] = field(default_factory=list)
    draft_report: str = ""
    critique: str = ""
    final_report: str = ""
    trace: list[TraceEvent] = field(default_factory=list)

    def add_trace(self, agent: str, content: str, metadata: dict[str, str] | None = None) -> TraceEvent:
        event = TraceEvent(agent=agent, content=content, metadata=metadata or {})
        self.trace.append(event)
        return event


@dataclass(slots=True)
class ReportRecord:
    title: str
    page_url: str
    user_query: str
    provider: str
    model: str
    route: str
    final_report: str
    id: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(slots=True)
class LoadedReport:
    report: ReportRecord
    traces: list[TraceEvent]
    evidence: list[EvidenceCard]


@dataclass(frozen=True, slots=True)
class ProviderPreset:
    id: str
    name: str
    base_url: str
    model: str
    api_key_env: str


@dataclass(frozen=True, slots=True)
class ProviderCatalog:
    providers: dict[str, ProviderPreset]
