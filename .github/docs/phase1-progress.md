# Phase 1 — Progress Tracker

> **Plan source**: `.github/docs/phase1-plan.md`  
> **Features source**: `.github/docs/features.md` §Phase 1  
> **Last updated**: 2026-02-24

Legend: `[ ]` Not started · `[~]` In progress · `[x]` Done · `[!]` Blocked

---

## Milestone 1 — Docker Setup (Feature 1.8)

> All subsequent work happens inside Docker. This milestone must be 100% done before anything else.

- [x] **T1.1** — Create `backend/Dockerfile`  
       _Base: `python:3.14-slim`. Copy `requirements.txt`. Run `pip install --no-cache-dir -r requirements.txt`. Set `CMD` to `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`._

- [x] **T1.2** — Create `frontend/Dockerfile`  
       _Base: `node:20-alpine`. Copy `package.json` + `package-lock.json`. Run `npm ci`. Set `CMD` to `npm run dev`._

- [x] **T1.3** — Create `docker-compose.yml` (dev)  
       _Services: `backend` (port 8000, bind-mount `./backend`, env_file `.env`) and `frontend` (port 3000, bind-mount `./frontend`, anonymous volume for `node_modules`, env_file `.env`)._

- [x] **T1.4** — Create `docker-compose.prod.yml`  
       _Multi-stage builds for both services. No bind mounts. `NEXT_PUBLIC_API_URL` build arg for frontend._

- [x] **T1.5** — Create `.env.example`  
       _Document all required vars: `NOVA_API_KEY`, `NEXT_PUBLIC_API_URL=http://localhost:8000`._

- [x] **T1.6** — Create `backend/requirements.txt` with all Phase 1 deps  
       _fastapi, uvicorn[standard], langgraph, langchain-core, openai, python-dotenv, python-multipart, gitpython, tiktoken, pathspec. Python ≥ 3.14._

- [x] **T1.7** — Scaffold Next.js frontend project  
       _Run `docker compose run --rm frontend npx create-next-app@14 . --typescript --tailwind --app --src-dir --no-git --import-alias "@/*"` inside the container._

- [x] **T1.8** — Create `.devcontainer/devcontainer.json`  
       _Point at `docker-compose.yml`, set service to `backend`. Enables VS Code Dev Containers for IntelliSense._

- [x] **T1.9** — Smoke test: `docker compose up` boots both containers cleanly  
       _Verify: backend logs show uvicorn running, frontend logs show Next.js ready._

---

## Milestone 2 — FastAPI Backend Skeleton (Feature 1.7)

- [x] **T2.1** — Create `backend/app/__init__.py` (empty)

- [x] **T2.2** — Create `backend/app/main.py`  
       _FastAPI app instance, CORS middleware (allow `http://localhost:3000`), include all routers._

- [x] **T2.3** — Create `backend/app/api/health.py`  
       _`GET /api/health` → `{"status": "ok", "service": "repolens-backend"}`._

- [x] **T2.4** — Create `backend/app/models/session.py`  
       _Pydantic v2 models: `FileNode`, `SessionState`, `SessionSummary`._

- [x] **T2.5** — Create `backend/app/models/ingest.py`  
       _`IngestRequest(url: str | None, ...)`, `IngestResponse(session_id, file_tree, token_count, token_budget)`._

- [x] **T2.6** — Create `backend/app/models/chat.py`  
       _`ChatRequest(session_id, message)`, `ChatResponse(content, role)`._

- [x] **T2.7** — Create `backend/app/api/sessions.py`  
       _`POST /api/sessions`, `GET /api/sessions/{id}`, `DELETE /api/sessions/{id}`. In-memory `dict` store._

- [x] **T2.8** — Create `backend/app/api/ingest.py` (stub)  
       _`POST /api/ingest` — accepts `IngestRequest` (URL) or `UploadFile` (zip). Returns stub `IngestResponse` for now._

- [x] **T2.9** — Create `backend/app/api/chat.py` (stub)  
       _`POST /api/chat` — accepts `ChatRequest`. Returns stub `StreamingResponse` echoing the message._

- [x] **T2.10** — Smoke test: `GET /api/health` returns 200 inside container  
       _Run: `docker compose exec backend curl http://localhost:8000/api/health`_

---

## Milestone 3 — Repo Ingestion Engine (Feature 1.1)

- [x] **T3.1** — Create `backend/app/ingestion/__init__.py` (empty)

- [x] **T3.2** — Create `backend/app/ingestion/cloner.py`  
       _`clone_from_url(url: str) -> Path`: shallow clone (`depth=1`) into `tempfile.mkdtemp()` using `gitpython`. Returns path to cloned root._

- [x] **T3.3** — Create `backend/app/ingestion/extractor.py`  
       _`extract_zip(data: bytes) -> Path`: extract `zipfile.ZipFile` into `tempfile.mkdtemp()`. Returns root path._

- [x] **T3.4** — Create `backend/app/ingestion/filter.py`  
       _`filter_files(root: Path) -> list[FileNode]`: walk tree, skip ignored dirs/files, detect binary files (read first 512 bytes, check for null bytes). Load `.repolensignore` if present using `pathspec` library._

- [x] **T3.5** — Add `pathspec` to `backend/requirements.txt`, rebuild container

- [x] **T3.6** — Create `backend/app/ingestion/token_counter.py`  
       _`count_tokens(text: str) -> int`: use `tiktoken.get_encoding("cl100k_base").encode(text)`._

- [x] **T3.7** — Wire ingestion into `POST /api/ingest`  
       _URL path: call `clone_from_url` → `filter_files` → `count_tokens` per file → store in session. Zip path: call `extract_zip` → same pipeline._  
       ℹ️ Split into two routes: `POST /api/ingest` (JSON + URL) and `POST /api/ingest/upload` (multipart zip) — FastAPI cannot mix a Pydantic body with UploadFile on the same function.

- [x] **T3.8** — Integration test: POST a real GitHub URL, verify file tree + token count in response  
       ℹ️ Both endpoints verified via Postman.

---

## Milestone 4 — Context Packing (Feature 1.2)

- [x] **T4.1** — Create `backend/app/ingestion/packer.py`  
       _`pack_context(file_nodes: list[FileNode], root: Path, budget: int = 750_000) -> tuple[str, int]`_
      _Sort files by priority score (entry points first, generated files last). Concatenate with `=== FILE: {path} ===` headers. Stop adding when token count exceeds budget. Return `(packed_string, total_tokens)`._

- [x] **T4.2** — Define priority scoring in `packer.py`  
       _Score rules: `main.*`, `index.*`, `app.*` → 100 pts; `*.config.*`, `*.toml`, `*.json` → 80 pts; `src/` files → 60 pts; `test*/` → 20 pts; `dist/`, `build/`, `generated/` → 5 pts._

- [x] **T4.3** — Store `repo_context` string in `SessionState` after ingestion  
       _Update `POST /api/ingest` to call `pack_context` and store result in session._

- [x] **T4.4** — Return `token_count` and `token_budget` in `IngestResponse`  
       _Frontend will use these to render the token usage bar._

---

## Milestone 5 — Nova Client + LangGraph Agent (Feature 1.3)

- [x] **T5.1** — Create `backend/app/agent/__init__.py` (empty)

- [x] **T5.2** — Create `backend/app/agent/nova_client.py`  
       _Singleton `OpenAI` client: `base_url="https://api.nova.amazon.com/v1"`, `api_key=os.environ["NOVA_API_KEY"]`._

- [x] **T5.3** — Create `backend/app/agent/state.py`  
       _`AgentState(TypedDict)`: `session_id: str`, `repo_context: str`, `messages: list[dict]`._

- [x] **T5.4** — Create `backend/app/agent/tools/__init__.py` (empty)

- [x] **T5.5** — Create `backend/app/agent/tools/general_qa.py`  
       _`@tool answer_general_question(question: str) -> str`._

- [x] **T5.6** — Create `backend/app/agent/tools/overview.py`  
       _`@tool get_project_overview() -> str`._

- [x] **T5.7** — Create `backend/app/agent/tools/tech_stack.py`  
       _`@tool get_tech_stack() -> str`._

- [x] **T5.8** — Create `backend/app/agent/tools/architecture.py`  
       _`@tool get_architecture_summary() -> str`._

- [x] **T5.9** — Create `backend/app/agent/tools/file_explain.py`  
       _`@tool get_file_explanation(file_path: str) -> str`._

- [x] **T5.10** — Create `backend/app/agent/tools/folder_explain.py`  
       _`@tool get_folder_explanation(folder_path: str) -> str`._

- [x] **T5.11** — Create `backend/app/agent/graph.py`  
       _Build `StateGraph(AgentState)`. Add `agent` node (calls Nova with all tools bound). Add `tools` node (executes selected tool). Add edges with `should_continue` conditional. Compile once as `compiled_graph = graph.compile()` module-level._

- [x] **T5.12** — Wire agent into `POST /api/chat`  
       _Load session → build initial state with `repo_context` + message → invoke `compiled_graph` → return non-streaming response first (streaming in T5.13)._

- [x] **T5.13** — Implement SSE streaming in `POST /api/chat`  
       _Replace with `StreamingResponse`. Use `graph.astream_events()`. Filter `on_chat_model_stream`. Yield `data: {chunk}\n\n` SSE format._

- [ ] **T5.14** — Integration test: send "What does this project do?" via API, verify streamed Nova response

---

## Milestone 6 — Diagram Tools (Feature 1.4)

- [ ] **T6.1** — Create `backend/app/agent/tools/diagram_architecture.py`  
       _`@tool generate_architecture_diagram(focus: str = "") -> str`: prompt Nova to return only a Mermaid `graph TD` block. Strip everything but the fence._

- [ ] **T6.2** — Create `backend/app/agent/tools/diagram_sequence.py`  
       _`@tool generate_sequence_diagram(flow: str) -> str`: prompt for `sequenceDiagram`._

- [ ] **T6.3** — Create `backend/app/agent/tools/diagram_component.py`  
       _`@tool generate_component_diagram() -> str`: prompt for component `graph`._

- [ ] **T6.4** — Register all diagram tools in `graph.py`

---

## Milestone 7 — Design Analysis Tools (Feature 1.5)

- [ ] **T7.1** — Create `backend/app/agent/tools/design_flaws.py`  
       _`@tool find_design_flaws() -> str`: structured markdown report with 🔴/🟡/🟢 sections._

- [ ] **T7.2** — Create `backend/app/agent/tools/tech_debt.py`  
       _`@tool get_tech_debt_summary() -> str`._

- [ ] **T7.3** — Create `backend/app/agent/tools/security.py`  
       _`@tool get_security_concerns() -> str`._

- [ ] **T7.4** — Register all analysis tools in `graph.py`

---

## Milestone 8 — Next.js Frontend (Feature 1.6)

- [ ] **T8.1** — Create `src/lib/types.ts`  
       _TypeScript interfaces: `FileNode`, `SessionState`, `IngestResponse`, `ChatMessage`._

- [ ] **T8.2** — Create `src/lib/api.ts`  
       _`ingestRepo()`, `ingestZip()`, `sendMessage()` (SSE consumer returning `AsyncGenerator<string>`)._

- [ ] **T8.3** — Create `src/components/TokenUsageBar.tsx`  
       _Props: `used: number`, `budget: number`. Renders a Tailwind progress bar._

- [ ] **T8.4** — Create `src/components/RepoInputPanel.tsx`  
       _URL text input + "Analyze" button + zip drag-and-drop zone. Calls `api.ingestRepo()` / `api.ingestZip()`. Shows loading state._

- [ ] **T8.5** — Create `src/components/FileExplorer.tsx`  
       _Tree view from `SessionState.file_tree`. Click on a file → dispatches "Explain this file: {path}" message._

- [ ] **T8.6** — Create `src/components/QuickActions.tsx`  
       _Chip buttons: "Give me an overview", "Show architecture diagram", "What's the tech stack?", "Find design flaws", "Identify security issues"._

- [ ] **T8.7** — Create `src/components/DiagramBlock.tsx`  
       _Detects Mermaid fence. Dynamic imports `mermaid`. Renders SVG in `useEffect`. Copy source + download SVG buttons._

- [ ] **T8.8** — Create `src/components/ChatMessage.tsx`  
       _Renders a single message bubble. Splits content into text segments and Mermaid blocks. Passes Mermaid blocks to `DiagramBlock`._

- [ ] **T8.9** — Create `src/components/ChatInput.tsx`  
       _Textarea (auto-resize) + send button. Disabled while streaming._

- [ ] **T8.10** — Create `src/components/ChatWindow.tsx`  
       _Scrollable list of `ChatMessage` components. Auto-scrolls to bottom on new message._

- [ ] **T8.11** — Create `src/components/AppShell.tsx`  
       _Three-column layout: FileExplorer sidebar | ChatWindow | (future: details pane). Holds session state via `useState`._

- [ ] **T8.12** — Update `src/app/page.tsx`  
       _Renders `<AppShell>`. Handles top-level session state._

- [~] **T8.13** — Update `src/app/layout.tsx`  
  _Dark mode support via Tailwind `dark` class. Inter font._  
  ⚠️ `layout.tsx` exists and has `suppressHydrationWarning` + Inter via CSS. Still needs `class="dark"` on `<html>` for Tailwind dark mode to work.

- [ ] **T8.14** — End-to-end smoke test in browser  
       _Paste GitHub URL → ingestion shows file tree + token bar → send "What does this project do?" → see streamed response → ask for architecture diagram → see Mermaid rendered inline._

---

## Phase 1 Completion Checklist

- [ ] All tasks above marked `[x]`
- [ ] `docker compose up` starts cleanly from a fresh clone (no local state)
- [ ] Golden demo path works end-to-end (see `.github/docs/phase1-plan.md` §Definition of Done)
- [ ] No `.env` secrets committed to git
- [ ] `.github/docs/phase1-plan.md` updated with any deviations from the original plan
- [ ] Ready to start Phase 2
