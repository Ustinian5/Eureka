from __future__ import annotations

from pathlib import Path

from backend.app.models import EvidenceCard, LoadedReport, ReportRecord, TraceEvent
from backend.app.storage.database import connect_database, create_schema, initialize_database


class ReportRepository:
    def __init__(self, db_path: str | Path = "data/eureka.db"):
        self.db_path = db_path
        self._memory_connection = None
        if str(db_path) == ":memory:":
            self._memory_connection = connect_database(db_path)
            create_schema(self._memory_connection)
        else:
            initialize_database(db_path)

    def save_report(self, report: ReportRecord, traces: list[TraceEvent], evidence: list[EvidenceCard]) -> int:
        connection = self._connection()
        cursor = connection.execute(
            """
            INSERT INTO reports (title, page_url, user_query, provider, model, route, final_report, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report.title,
                report.page_url,
                report.user_query,
                report.provider,
                report.model,
                report.route,
                report.final_report,
                report.created_at,
            ),
        )
        report_id = int(cursor.lastrowid)
        connection.executemany(
            "INSERT INTO traces (report_id, agent, content) VALUES (?, ?, ?)",
            [(report_id, item.agent, item.content) for item in traces],
        )
        connection.executemany(
            """
            INSERT INTO evidence (report_id, title, url, snippet, relevance, quote, source_type, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    report_id,
                    item.title,
                    item.url,
                    item.snippet,
                    item.relevance,
                    item.quote,
                    item.source_type,
                    item.confidence,
                )
                for item in evidence
            ],
        )
        connection.commit()
        return report_id

    def list_reports(self) -> list[ReportRecord]:
        rows = self._connection().execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
        return [_report_from_row(row) for row in rows]

    def get_report(self, report_id: int) -> LoadedReport:
        connection = self._connection()
        row = connection.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
        if row is None:
            raise KeyError(f"Report {report_id} not found")
        trace_rows = connection.execute("SELECT * FROM traces WHERE report_id = ? ORDER BY id", (report_id,)).fetchall()
        evidence_rows = connection.execute("SELECT * FROM evidence WHERE report_id = ? ORDER BY id", (report_id,)).fetchall()
        return LoadedReport(
            report=_report_from_row(row),
            traces=[TraceEvent(agent=item["agent"], content=item["content"]) for item in trace_rows],
            evidence=[
                EvidenceCard(
                    title=item["title"],
                    url=item["url"],
                    snippet=item["snippet"],
                    relevance=item["relevance"],
                    quote=item["quote"],
                    source_type=item["source_type"],
                    confidence=float(item["confidence"]),
                )
                for item in evidence_rows
            ],
        )

    def delete_report(self, report_id: int) -> None:
        self._connection().execute("DELETE FROM reports WHERE id = ?", (report_id,))
        self._connection().commit()

    def _connection(self):
        if self._memory_connection is not None:
            return self._memory_connection
        return connect_database(self.db_path)


def _report_from_row(row) -> ReportRecord:
    return ReportRecord(
        id=row["id"],
        title=row["title"],
        page_url=row["page_url"],
        user_query=row["user_query"],
        provider=row["provider"],
        model=row["model"],
        route=row["route"],
        final_report=row["final_report"],
        created_at=row["created_at"],
    )
