# Phase 1 — Progress Tracker- [x] **T1.6** — Create `backend/requirements.txt` with all Phase 1 deps using `backend/requirements.in` and pip-compile

      _fastapi, uvicorn[standard], langgraph, langchain-core, openai, python-dotenv, python-multipart, gitpython, tiktoken, pathspec. Python ≥ 3.14._

> **Plan source**: `docs/phase1-plan.md`  
> **Features source**: `docs/features.md` §Phase 1  
> **Last updated**: 2026-02-21

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

- [x] **T1.6** — Create `backend/requirements.txt` with all Phase 1 deps using `backend/requirements.in` and pip-compile
      _fastapi, uvicorn[standard], langgraph, langchain-core, openai, python-dotenv, python-multipart, gitpython, tiktoken, pathspec. Python ≥ 3.14._

- [x] **T1.7** — Scaffold Next.js frontend project  
       _Run `docker compose run --rm frontend npx create-next-app@latest . --typescript --tailwind --app --src-dir --no-git --import-alias "@/*"` inside the container. Verify `tsconfig.json` is created with `"strict": true`. All generated files must be `.tsx`/`.ts` — delete any `.js`/`.jsx` files if created._

- [x] **T1.8** — Create `.devcontainer/devcontainer.json`  
       _Point at `docker-compose.yml`, set service to `backend`. Enables VS Code Dev Containers for IntelliSense._

- [x] **T1.9** — Create `backend/app/__init__.py` and `backend/app/main.py` boilerplate  
       _Minimal FastAPI app so uvicorn can boot: `app = FastAPI()` + a single `GET /` returning `{"status": "ok"}`. No business logic. This is the minimum needed to verify the backend Dockerfile works._

- [x] **T1.10** — Verify frontend boilerplate boots in Docker  
       _Confirm `frontend/src/app/page.tsx`, `layout.tsx`, `globals.css`, `tsconfig.json`, `next.config.ts`, `tailwind.config.ts`, and `postcss.config.js` all exist. These are the minimum files Next.js needs to start._

- [ ] **T1.11** — Smoke test: `docker compose up` boots both containers cleanly  
       _Verify: `docker compose up` starts without errors. Backend logs show uvicorn running on port 8000. Frontend logs show Next.js ready on port 3000._

---

## Milestone 2 — FastAPI Backend Skeleton (Feature 1.7)

- [ ] **T2.1** — Create `backend/app/__init__.py` (empty)

- [ ] **T2.2** — Create `backend/app/main.py`  
       _FastAPI app instance, CORS middleware (allow `http://localhost:3000`), include all routers._

- [ ] **T2.3** — Create `backend/app/api/health.py`  
       _`GET /api/health` → `{"status": "ok", "service": "repolens-backend"}`._

- [ ] **T2.4** — Create `backend/app/models/session.py`  
       _Pydantic v2 models: `FileNode`, `SessionState`, `SessionSummary`._

- [ ] **T2.5** — Create `backend/app/models/ingest.py`  
       _`IngestRequest(url: str | None, ...)`, `IngestResponse(session_id, file_tree, token_count, token_budget)`._

- [ ] **T2.6** — Create `backend/app/models/chat.py`  
       _`ChatRequest(session_id, message)`, `ChatResponse(content, role)`._

- [ ] **T2.7** — Create `backend/app/api/sessions.py`  
       _`POST /api/sessions`, `GET /api/sessions/{id}`, `DELETE /api/sessions/{id}`. In-memory `dict` store._

- [ ] **T2.8** — Create `backend/app/api/ingest.py` (stub)  
       _`POST /api/ingest` — accepts `IngestRequest` (URL) or `UploadFile` (zip). Returns stub `IngestResponse` for now._

- [ ] **T2.9** — Create `backend/app/api/chat.py` (stub)  
       _`POST /api/chat` — accepts `ChatRequest`. Returns stub `StreamingResponse` echoing the message._

- [ ] **T2.10** — Smoke test: `GET /api/health` returns 200 inside container  
       _Run: `docker compose exec backend curl http://localhost:8000/api/health`_

---

## Milestone 3 — Repo Ingestion Engine (Feature 1.1)

- [ ] **T3.1** — Create `backend/app/ingestion/__init__.py` (empty)

- [ ] **T3.2** — Create `backend/app/ingestion/cloner.py`  
       _`clone_from_url(url: str) -> Path`: shallow clone (`depth=1`) into `tempfile.mkdtemp()` using `gitpython`. Returns path to cloned root._

- [ ] **T3.3** — Create `backend/app/ingestion/extractor.py`  
       _`extract_zip(data: bytes) -> Path`: extract `zipfile.ZipFile` into `tempfile.mkdtemp()`. Returns root path._

- [ ] **T3.4** — Create `backend/app/ingestion/filter.py`  
       _`filter_files(root: Path) -> list[FileNode]`: walk tree, skip ignored dirs/files, detect binary files (read first 512 bytes, check for null bytes). Load `.repolensignore` if present using `pathspec` library._

- [ ] **T3.5** — Add `pathspec` to `backend/requirements.txt`, rebuild container

- [ ] **T3.6** — Create `backend/app/ingestion/token_counter.py`  
       _`count_tokens(text: str) -> int`: use `tiktoken.get_encoding("cl100k_base").encode(text)`._

- [ ] **T3.7** — Wire ingestion into `POST /api/ingest`  
       _URL path: call `clone_from_url` → `filter_files` → `count_tokens` per file → store in session. Zip path: call `extract_zip` → same pipeline._

- [ ] **T3.8** — Integration test: POST a real GitHub URL, verify file tree + token count in response

---

## Milestone 4 — Context Packing (Feature 1.2)

- [ ] **T4.1** — Create `backend/app/ingestion/packer.py`  
       _`pack_context(file_nodes: list[FileNode], root: Path, budget: int = 750_000) -> tuple[str, int]`_
      _Sort files by priority score (entry points first, generated files last). Concatenate with `=== FILE: {path} ===` headers. Stop adding when token count exceeds budget. Return `(packed_string, total_tokens)`._

- [ ] **T4.2** — Define priority scoring in `packer.py`  
       _Score rules: `main.*`, `index.*`, `app.*` → 100 pts; `*.config.*`, `*.toml`, `*.json` → 80 pts; `src/` files → 60 pts; `test*/` → 20 pts; `dist/`, `build/`, `generated/` → 5 pts._

- [ ] **T4.3** — Store `repo_context` string in `SessionState` after ingestion  
       _Update `POST /api/ingest` to call `pack_context` and store result in session._

- [ ] **T4.4** — Return `token_count` and `token_budget` in `IngestResponse`  
       _Frontend will use these to render the token usage bar._

---

## Milestone 5 — Nova Client + LangGraph Agent (Feature 1.3)

- [ ] **T5.1** — Create `backend/app/agent/__init__.py` (empty)

- [ ] **T5.2** — Create `backend/app/agent/nova_client.py`  
       _Singleton `OpenAI` client: `base_url="https://api.nova.amazon.com/v1"`, `api_key=os.environ["NOVA_API_KEY"]`._

- [ ] **T5.3** — Create `backend/app/agent/state.py`  
       _`AgentState(TypedDict)`: `session_id: str`, `repo_context: str`, `messages: list[dict]`._

- [ ] **T5.4** — Create `backend/app/agent/tools/__init__.py` (empty)

- [ ] **T5.5** — Create `backend/app/agent/tools/general_qa.py`  
       _`@tool answer_general_question(question: str) -> str`._

- [ ] **T5.6** — Create `backend/app/agent/tools/overview.py`  
       _`@tool get_project_overview() -> str`._

- [ ] **T5.7** — Create `backend/app/agent/tools/tech_stack.py`  
       _`@tool get_tech_stack() -> str`._

- [ ] **T5.8** — Create `backend/app/agent/tools/architecture.py`  
       _`@tool get_architecture_summary() -> str`._

- [ ] **T5.9** — Create `backend/app/agent/tools/file_explain.py`  
       _`@tool get_file_explanation(file_path: str) -> str`._

- [ ] **T5.10** — Create `backend/app/agent/tools/folder_explain.py`  
       _`@tool get_folder_explanation(folder_path: str) -> str`._

- [ ] **T5.11** — Create `backend/app/agent/graph.py`  
       _Build `StateGraph(AgentState)`. Add `agent` node (calls Nova with all tools bound). Add `tools` node (executes selected tool). Add edges with `should_continue` conditional. Compile once as `compiled_graph = graph.compile()` module-level._

- [ ] **T5.12** — Wire agent into `POST /api/chat`  
       _Load session → build initial state with `repo_context` + message → invoke `compiled_graph` → return non-streaming response first (streaming in T5.13)._

- [ ] **T5.13** — Implement SSE streaming in `POST /api/chat`  
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

> All frontend files must be **TypeScript** (`.ts` for pure logic, `.tsx` for components/pages). No `any` types. All props must have explicit interfaces. `tsconfig.json` must have `"strict": true`.

- [ ] **T8.1** — Create `src/lib/types.ts`  
       _TypeScript interfaces (no `any`): `FileNode`, `SessionState`, `IngestResponse`, `ChatMessage`. Export all types._

- [ ] **T8.2** — Create `src/lib/api.ts`  
       _Typed API wrapper: `ingestRepo(url: string): Promise<IngestResponse>`, `ingestZip(file: File): Promise<IngestResponse>`, `sendMessage(sessionId: string, message: string): AsyncGenerator<string>` (SSE consumer). Import types from `./types`._

- [ ] **T8.3** — Create `src/components/TokenUsageBar.tsx`  
       _Props interface: `{ used: number; budget: number }`. Renders a Tailwind progress bar. No `any`._

- [ ] **T8.4** — Create `src/components/RepoInputPanel.tsx`  
       _Props interface: `{ onIngest: (response: IngestResponse) => void }`. URL input + "Analyze" button + zip drag-and-drop. Calls `api.ingestRepo()` / `api.ingestZip()`. Shows loading state._

- [ ] **T8.5** — Create `src/components/FileExplorer.tsx`  
       _Props interface: `{ fileTree: FileNode[]; onFileClick: (path: string) => void }`. Tree view of ingested files._

- [ ] **T8.6** — Create `src/components/QuickActions.tsx`  
       _Props interface: `{ onAction: (prompt: string) => void }`. Chip buttons: "Give me an overview", "Show architecture diagram", "What's the tech stack?", "Find design flaws", "Identify security issues"._

- [ ] **T8.7** — Create `src/components/DiagramBlock.tsx`  
       _Props interface: `{ source: string }`. Dynamic import `mermaid` (browser-only). Renders SVG in `useEffect`. Copy source + download SVG buttons._

- [ ] **T8.8** — Create `src/components/ChatMessage.tsx`  
       _Props interface: `{ message: ChatMessage }`. Renders a single message bubble. Splits content into text and Mermaid blocks. Passes Mermaid blocks to `DiagramBlock`._

- [ ] **T8.9** — Create `src/components/ChatInput.tsx`  
       _Props interface: `{ onSend: (message: string) => void; disabled: boolean }`. Textarea (auto-resize) + send button. Disabled while streaming._

- [ ] **T8.10** — Create `src/components/ChatWindow.tsx`  
       _Props interface: `{ messages: ChatMessage[] }`. Scrollable list of `ChatMessage` components. Auto-scrolls to bottom on new message._

- [ ] **T8.11** — Create `src/components/AppShell.tsx`  
       _No props (top-level). Three-column layout: FileExplorer sidebar | ChatWindow | (future: details pane). Holds all session state via `useState<SessionState | null>`._

- [ ] **T8.12** — Update `src/app/page.tsx`  
       _Renders `<AppShell>`. File must remain `.tsx`._

- [ ] **T8.13** — Update `src/app/layout.tsx`  
       _Dark mode support via Tailwind `dark` class. Inter font. File must remain `.tsx`._

- [ ] **T8.14** — End-to-end smoke test in browser  
       _Paste GitHub URL → ingestion shows file tree + token bar → send "What does this project do?" → see streamed response → ask for architecture diagram → see Mermaid rendered inline._

---

## Phase 1 Completion Checklist

- [ ] All tasks above marked `[x]`
- [ ] `docker compose up` starts cleanly from a fresh clone (no local state)
- [ ] Golden demo path works end-to-end (see `docs/phase1-plan.md` §Definition of Done)
- [ ] No `.env` secrets committed to git
- [ ] `docs/phase1-plan.md` updated with any deviations from the original plan
- [ ] Ready to start Phase 2
