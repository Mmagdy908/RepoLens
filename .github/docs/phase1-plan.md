# Phase 1 — Core Foundation: Implementation Plan

> **Source**: `docs/features.md` §Phase 1  
> **Goal**: A fully working end-to-end demo covering the golden demo path.  
> **Timeline**: Week 1 (Days 1–7)  
> **Status**: 🟡 Planning

---

## What We Are Building

A monorepo with two Dockerized services that together deliver the golden demo path:

```
User pastes GitHub URL
  → Backend clones repo, filters files, packs into context
  → LangGraph agent receives user question + full repo context
  → Nova 2 Lite reasons and responds (streamed)
  → Frontend renders answer + any Mermaid diagrams inline
```

---

## Feature Breakdown

### 1.8 Docker Setup ← BUILD FIRST (everything else depends on it)

**What**: Two containers (`backend`, `frontend`) orchestrated by Docker Compose with hot reload. `.env` file at repo root injected into both containers.

**Backend container**:
- Base image: `python:3.14-slim`
- Copy `requirements.txt` and run `pip install --no-cache-dir -r requirements.txt`
- Mount `./backend` as a volume
- Run: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

**Frontend container**:
- Base image: `node:20-alpine`
- Install deps at image build time (`npm ci`)
- Mount `./frontend` as a volume; `node_modules` stays in the container (anonymous volume)
- Run: `npm run dev`

**Files to create**:
- `backend/Dockerfile`
- `backend/requirements.txt`
- `frontend/Dockerfile`
- `docker-compose.yml` (dev, with bind mounts + hot reload)
- `docker-compose.prod.yml` (multi-stage production build)
- `.env.example`
- `.devcontainer/devcontainer.json`
- Updated `README.md`

---

### 1.7 FastAPI Backend Skeleton

**What**: Minimal FastAPI app with CORS, health check, and session CRUD. No business logic yet — just the skeleton all other features plug into.

**Routes**:
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Liveness check |
| `POST` | `/api/sessions` | Create a new session, returns `session_id` |
| `GET` | `/api/sessions/{session_id}` | Get session state |
| `DELETE` | `/api/sessions/{session_id}` | Delete a session |
| `POST` | `/api/ingest` | (stub) Accepts URL or file, will run ingestion |
| `POST` | `/api/chat` | (stub) Accepts message, will run agent |

**Pydantic models** (`backend/app/models/`):
- `session.py` — `SessionState`, `SessionSummary`, `FileNode`
- `ingest.py` — `IngestRequest`, `IngestResponse`
- `chat.py` — `ChatRequest`, `ChatResponse`

**Files to create/update**:
- `backend/app/main.py`
- `backend/app/api/health.py`
- `backend/app/api/sessions.py`
- `backend/app/api/ingest.py` (stub)
- `backend/app/api/chat.py` (stub)
- `backend/app/models/session.py`
- `backend/app/models/ingest.py`
- `backend/app/models/chat.py`
- `backend/requirements.txt` (deps: fastapi, uvicorn, langgraph, langchain-core, openai, python-dotenv, python-multipart, gitpython, tiktoken)

---

### 1.1 Repo Ingestion Engine

**What**: Given a GitHub URL or uploaded zip, clone/extract the repo, walk all files, apply filters, build a file tree, and store result in session state.

**Logic** (`backend/app/ingestion/`):
- `cloner.py` — `clone_from_url(url) → Path`: use `gitpython` to shallow-clone into a temp dir
- `extractor.py` — `extract_zip(file_bytes) → Path`: extract zip into a temp dir
- `filter.py` — `filter_files(root: Path) → list[FileNode]`: walk tree, apply ignore rules
  - Always ignore: `.git/`, `node_modules/`, `dist/`, `build/`, `__pycache__/`, `*.lock`, `*.png`, `*.jpg`, `*.svg`, `*.ico`, `*.woff`, binary files
  - Respect `.repolensignore` if present (same syntax as `.gitignore`)
- `token_counter.py` — `count_tokens(text: str) → int`: use `tiktoken` with `cl100k_base` encoding

**Wires into**:
- `POST /api/ingest` — calls cloner/extractor, then filter, stores `file_tree` in session

---

### 1.2 Context Packing & Token Management

**What**: Take the filtered file list and produce a single packed string to inject into the LLM context.

**Logic** (`backend/app/ingestion/packer.py`):
- `pack_context(file_nodes: list[FileNode], root: Path) → tuple[str, int]`
- Format each file as:
  ```
  === FILE: path/to/file.py ===
  <file contents>
  ```
- Count tokens as files are added; stop at 750k token budget
- Priority order if truncation needed: entry points (main, index, app) → configs → source files → tests → generated
- Return `(packed_string, token_count)`

---

### 1.3 Agentic Q&A Engine (LangGraph)

**What**: A LangGraph `StateGraph` with a ReAct-style agent that receives a user message + repo context, selects a tool, calls Nova 2 Lite, and streams back the response.

**Agent structure** (`backend/app/agent/`):
- `state.py` — `AgentState(TypedDict)`: `session_id`, `repo_context`, `messages`, `tool_calls`
- `graph.py` — compile the `StateGraph` once at startup; expose `compiled_graph`
- `nova_client.py` — singleton `OpenAI` client pointed at `api.nova.amazon.com/v1`

**Tools** (`backend/app/agent/tools/`):
- `general_qa.py` — `answer_general_question(question: str) → str`
- `overview.py` — `get_project_overview() → str`
- `tech_stack.py` — `get_tech_stack() → str`
- `architecture.py` — `get_architecture_summary() → str`
- `file_explain.py` — `get_file_explanation(file_path: str) → str`
- `folder_explain.py` — `get_folder_explanation(folder_path: str) → str`

**Streaming**: `POST /api/chat` uses `StreamingResponse` + `graph.astream_events()`, filters `on_chat_model_stream` events, yields SSE chunks.

---

### 1.4 Architecture Diagram Generation

**What**: Additional tools the agent can call to produce Mermaid diagram code. The frontend detects Mermaid fences in the response and renders them.

**Tools** (`backend/app/agent/tools/`):
- `diagram_architecture.py` — `generate_architecture_diagram(focus: str = "") → str` → returns full Mermaid `graph TD` block
- `diagram_sequence.py` — `generate_sequence_diagram(flow: str) → str` → returns Mermaid `sequenceDiagram` block
- `diagram_component.py` — `generate_component_diagram() → str` → returns Mermaid `graph` block

**Frontend**: detect ` ```mermaid ` fences in chat messages, render via `mermaid.render()` in a `useEffect`.

---

### 1.5 Design Analysis Tools

**What**: Tools the agent can call to produce structured analysis reports.

**Tools** (`backend/app/agent/tools/`):
- `design_flaws.py` — `find_design_flaws() → str`
- `tech_debt.py` — `get_tech_debt_summary() → str`
- `security.py` — `get_security_concerns() → str`

**Output format**: each tool returns a markdown report with severity sections: `🔴 Critical`, `🟡 Warning`, `🟢 Suggestion`.

---

### 1.6 Chat UI (Next.js Frontend)

**What**: The full browser interface. Built with Next.js 14 App Router + Tailwind CSS.

**Pages & layout**:
- `src/app/layout.tsx` — root layout (fonts, dark mode class)
- `src/app/page.tsx` — main page: renders `<AppShell>`

**Components** (`src/components/`):
- `AppShell.tsx` — top-level layout: sidebar + main chat area
- `RepoInputPanel.tsx` — URL input + zip upload + drag-and-drop; calls `POST /api/ingest`
- `FileExplorer.tsx` — tree view of ingested files; click → asks agent about that file
- `TokenUsageBar.tsx` — progress bar showing token budget usage
- `ChatWindow.tsx` — scrollable message list
- `ChatMessage.tsx` — renders one message; detects Mermaid blocks → passes to `DiagramBlock`
- `DiagramBlock.tsx` — dynamically imports `mermaid`, renders SVG, shows copy/download buttons
- `ChatInput.tsx` — textarea + send button + quick-action chips
- `QuickActions.tsx` — pre-defined prompt chips: "Overview", "Architecture", "Tech Stack", "Design Flaws"

**API client** (`src/lib/api.ts`):
- `ingestRepo(url: string): Promise<IngestResponse>`
- `ingestZip(file: File): Promise<IngestResponse>`
- `sendMessage(sessionId: string, message: string): AsyncGenerator<string>` — consumes SSE stream

**Types** (`src/lib/types.ts`):
- All API shapes: `SessionState`, `IngestResponse`, `ChatMessage`, `FileNode`

---

## Dependencies

### Backend (`backend/requirements.txt`)
```
fastapi>=0.110
uvicorn[standard]>=0.29
langgraph>=0.1
langchain-core>=0.2
openai>=1.30
python-dotenv>=1.0
python-multipart>=0.0.9
gitpython>=3.1
tiktoken>=0.7
pathspec>=0.12
```

### Frontend (`frontend/package.json`)
```json
"dependencies": {
  "next": "14",
  "react": "^18",
  "react-dom": "^18",
  "mermaid": "^10",
  "react-syntax-highlighter": "^15"
},
"devDependencies": {
  "typescript": "^5",
  "@types/node": "^20",
  "@types/react": "^18",
  "tailwindcss": "^3",
  "autoprefixer": "^10",
  "postcss": "^8"
}
```

---

## Build Order (critical path)

```
1. Docker setup (backend + frontend containers boot cleanly)
   ↓
2. FastAPI skeleton (health check passes at localhost:8000/api/health)
   ↓
3. Repo ingestion engine (cloner + filter + token counter)
   ↓
4. Context packer
   ↓
5. Nova client + LangGraph agent skeleton (single tool, no streaming)
   ↓
6. All 6 Q&A tools + 3 diagram tools + 3 analysis tools
   ↓
7. Streaming (SSE end-to-end)
   ↓
8. Next.js frontend (UI wired to all backend endpoints)
```

---

## Definition of Done for Phase 1

- [ ] `docker compose up` starts both services with no errors
- [ ] `GET /api/health` returns `{"status": "ok"}`
- [ ] Pasting a GitHub URL ingests the repo and returns a file tree + token count
- [ ] Asking "What does this project do?" returns a streamed answer referencing actual code
- [ ] Asking "Show me the architecture diagram" returns a rendered Mermaid diagram in the UI
- [ ] Asking "Find design flaws" returns a categorized report
- [ ] Dark/light mode toggle works
- [ ] Token usage bar updates after ingestion
