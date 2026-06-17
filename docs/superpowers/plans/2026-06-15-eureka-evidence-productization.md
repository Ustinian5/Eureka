# Eureka Evidence Productization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade Eureka from a complete course demo into a stronger evidence-centered research product with richer exports, examples, evaluation docs, screenshots, scripts, and CI.

**Architecture:** Add evidence scoring and citation verification agents after search and writing. Add a fetch tool to enrich evidence cards with source type, confidence, and quote snippets. Extend report APIs with PDF export, make demo research save history, and enhance Web Demo with history/export/source UI.

**Tech Stack:** Python 3.12, FastAPI, SQLite, reportlab, pypdf, unittest, vanilla HTML/CSS/JavaScript, GitHub Actions.

---

### Task 1: Evidence Quality Agents

**Files:**
- Create: `backend/app/agents/scorer.py`
- Create: `backend/app/agents/citation_verifier.py`
- Create: `backend/app/tools/fetcher.py`
- Modify: `backend/app/agents/evidence.py`
- Modify: `backend/app/agents/orchestrator.py`
- Modify: `backend/app/models.py`
- Test: `backend/tests/test_evidence_quality.py`
- Test: `backend/tests/test_fetcher.py`

- [ ] Score evidence by query overlap, URL source type, and snippet quality.
- [ ] Extract quote snippets from fetched page text or search snippets.
- [ ] Verify final report citations and add trace plus report note when citations are weak.

### Task 2: Export and History Productization

**Files:**
- Create: `backend/app/export/pdf.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/storage/database.py`
- Modify: `backend/app/storage/repositories.py`
- Test: `backend/tests/test_api_exports.py`

- [ ] Save demo research reports so offline demos populate history.
- [ ] Add `GET /api/reports/{id}/pdf`.
- [ ] Include evidence confidence, quote, and source type in saved reports.

### Task 3: Web Demo Product UI

**Files:**
- Modify: `web/index.html`
- Modify: `web/styles.css`
- Modify: `web/app.js`
- Modify: `backend/tests/test_frontend_assets.py`

- [ ] Add history sidebar.
- [ ] Add export Markdown and export PDF buttons.
- [ ] Add evidence/source cards.
- [ ] Show report id and saved state.

### Task 4: Course and Open Source Materials

**Files:**
- Create: `examples/mcp_article.txt`
- Create: `examples/ai_product_article.txt`
- Create: `examples/paper_abstract.txt`
- Create: `docs/evaluation.md`
- Create: `docs/model-products-survey.md`
- Create: `docs/design-decisions.md`
- Create: `scripts/run_tests.ps1`
- Create: `scripts/start_backend.ps1`
- Create: `scripts/build_docs.ps1`
- Create: `.github/workflows/tests.yml`
- Modify: `README.md`

- [ ] Add fixed example inputs and an evaluation matrix.
- [ ] Add model product survey covering Minimax, Zhipu, Kimi, OpenAI, Google, DeepSeek, and Qwen.
- [ ] Add design decisions explaining lightweight multi-agent orchestration.
- [ ] Add one-command scripts and GitHub Actions.

### Task 5: Visual Assets

**Files:**
- Create: `docs/screenshots/web-demo.png`
- Create: `docs/screenshots/agent-trace.png`
- Create: `docs/screenshots/demo.gif`
- Modify: `docs/report.md`
- Modify: `README.md`

- [ ] Capture Web Demo screenshot after offline demo.
- [ ] Generate a small demo GIF from screenshots.
- [ ] Regenerate `docs/report.pdf` and `docs/README.pdf`.

### Final Verification

- [ ] Run `D:\conda_envs\eureka\python.exe -B -W ignore -m unittest discover -s backend\tests -v`.
- [ ] Run `node --check extension\popup.js`, `node --check extension\content.js`, and `node --check web\app.js`.
- [ ] Verify `/health`, `/api/providers`, `/api/demo/research`, Markdown export, and PDF export.
- [ ] Verify `docs/report.pdf`, `docs/README.pdf`, screenshots, and demo GIF exist and are readable.
