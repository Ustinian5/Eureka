# Eureka Course Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade Eureka into a reproducible, demonstrable, multi-agent LLM research workspace suitable for a machine learning course final project.

**Architecture:** The backend becomes a lightweight multi-agent orchestrator that streams NDJSON trace/token events, supports provider presets, persists reports to SQLite, and exports Markdown. The frontend gains a local Web demo and an enhanced Chrome extension that show agent progress and final cited reports.

**Tech Stack:** Python 3.12, FastAPI, SQLite, unittest, vanilla HTML/CSS/JavaScript, Chrome Manifest V3, Markdown/PDF course documentation.

---

### Task 1: Multi-Agent Core

**Files:**
- Create: `backend/app/agents/base.py`
- Create: `backend/app/agents/context_analyst.py`
- Create: `backend/app/agents/planner.py`
- Create: `backend/app/agents/evidence.py`
- Create: `backend/app/agents/writer.py`
- Create: `backend/app/agents/critic.py`
- Create: `backend/app/agents/orchestrator.py`
- Modify: `backend/app/models.py`
- Test: `backend/tests/test_agents.py`

- [ ] Add `ResearchState`, `TraceEvent`, `EvidenceCard`, and template metadata.
- [ ] Implement agents with deterministic fallback behavior and LLM hooks.
- [ ] Stream trace events and final report tokens.

### Task 2: Provider Presets

**Files:**
- Create: `providers.yaml`
- Create: `backend/app/providers.py`
- Modify: `backend/app/config.py`
- Test: `backend/tests/test_provider_config.py`

- [ ] Parse Qwen, DeepSeek, Kimi, Zhipu, OpenAI, and custom presets.
- [ ] Keep API keys in `.env`, never in `providers.yaml`.
- [ ] Expose providers through `GET /api/providers`.

### Task 3: Persistence and Export

**Files:**
- Create: `backend/app/storage/database.py`
- Create: `backend/app/storage/repositories.py`
- Create: `backend/app/export/markdown.py`
- Test: `backend/tests/test_storage_export.py`

- [ ] Save reports, traces, and evidence cards to SQLite.
- [ ] Export a complete Markdown report with metadata and sources.
- [ ] Add report list/detail/delete API endpoints.

### Task 4: Web Demo and Extension Upgrade

**Files:**
- Create: `web/index.html`
- Create: `web/styles.css`
- Create: `web/app.js`
- Modify: `extension/popup.html`
- Modify: `extension/popup.css`
- Modify: `extension/popup.js`
- Test: `backend/tests/test_frontend_assets.py`

- [ ] Add a three-column Web demo: inputs, agent trace, report.
- [ ] Add model provider and report template selectors.
- [ ] Show NDJSON trace events and streamed report tokens.

### Task 5: Course Materials

**Files:**
- Create: `docs/report.md`
- Create: `docs/report.pdf`
- Create: `docs/demo.md`
- Create: `docs/architecture.md`
- Modify: `README.md`

- [ ] Document background, pain point, architecture, multi-agent design, provider integration, tests, and reproduction steps.
- [ ] Include Mermaid architecture diagrams.
- [ ] Generate a PDF report for submission.

### Final Verification

- [ ] Run `D:\conda_envs\eureka\python.exe -B -m unittest discover -s backend\tests -v`.
- [ ] Run `node --check extension\popup.js` and `node --check web\app.js`.
- [ ] Run FastAPI TestClient health/providers checks.
- [ ] Confirm `docs/report.pdf` exists and is readable.
