# Eureka Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Chrome extension and local Python backend for context-aware page summarization and deep research.

**Architecture:** The backend exposes a FastAPI streaming endpoint and keeps provider-specific LLM handling behind an OpenAI-compatible client. The Chrome extension captures the active page text with a content script, posts it to the backend, and renders streamed Markdown text in the popup.

**Tech Stack:** Python 3, FastAPI, httpx, uvicorn, unittest, Chrome Manifest V3, vanilla HTML/CSS/JavaScript.

---

### File Structure

- `backend/app/config.py`: environment-backed settings.
- `backend/app/models.py`: shared dataclasses and request/result types.
- `backend/app/llm_client.py`: OpenAI-compatible chat/completion streaming client with DeepSeek-R1 `reasoning_content` handling.
- `backend/app/intent.py`: deterministic parsing for router output and LLM-backed intent routing.
- `backend/app/search.py`: DuckDuckGo Instant Answer search client with injectable HTTP transport.
- `backend/app/workflow.py`: branch A and branch B orchestration.
- `backend/app/main.py`: FastAPI app, CORS, health check, and streaming research endpoint.
- `backend/tests/*.py`: stdlib unit tests for core behavior.
- `extension/manifest.json`: Chrome Manifest V3 permissions and entry points.
- `extension/popup.html`: popup shell.
- `extension/popup.css`: compact app UI.
- `extension/popup.js`: active-tab context capture, API call, stream rendering.
- `extension/content.js`: page text extraction.
- `.env.example`: model, search, and CORS configuration example.
- `requirements.txt`: Python runtime dependencies.
- `README.md`: updated run and architecture documentation.

### Implementation Tasks

- [ ] Write tests for intent parsing, DeepSeek streaming chunk parsing, search result normalization, workflow branch choice, and extension manifest shape.
- [ ] Run tests to confirm they fail because implementation files are missing.
- [ ] Implement backend modules with dependency injection around LLM and search.
- [ ] Add FastAPI HTTP streaming API and health endpoint.
- [ ] Implement Chrome extension popup, content script, and manifest.
- [ ] Update README and `.env.example`.
- [ ] Run unit tests and syntax checks.

### Acceptance Mapping

- Context plus optional user query is represented by `ResearchRequest`.
- Intent router emits `context_answer` for context-only work and `deep_research` for external research.
- Branch A streams a direct context answer.
- Branch B generates search keywords, calls search, merges references, and streams a cited Markdown report.
- `BASE_URL`, `API_KEY`, and `MODEL` configure any OpenAI-compatible provider.
- `reasoning_content` is parsed from streamed chunks and kept out of outbound message history.
- Chrome extension captures `document.body.innerText`, posts to backend, and renders streamed response text.
