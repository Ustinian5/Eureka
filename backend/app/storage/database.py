from __future__ import annotations

import sqlite3
from pathlib import Path


def connect_database(path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(path: str | Path) -> None:
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect_database(path) as connection:
        create_schema(connection)


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            page_url TEXT NOT NULL,
            user_query TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            route TEXT NOT NULL,
            final_report TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS traces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            agent TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            snippet TEXT NOT NULL,
            relevance TEXT NOT NULL,
            quote TEXT NOT NULL DEFAULT '',
            source_type TEXT NOT NULL DEFAULT 'web',
            confidence REAL NOT NULL DEFAULT 0,
            FOREIGN KEY(report_id) REFERENCES reports(id) ON DELETE CASCADE
        );
        """
    )
    _ensure_column(connection, "evidence", "quote", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(connection, "evidence", "source_type", "TEXT NOT NULL DEFAULT 'web'")
    _ensure_column(connection, "evidence", "confidence", "REAL NOT NULL DEFAULT 0")
    connection.commit()


def _ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    existing = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
