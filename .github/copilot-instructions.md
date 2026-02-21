# RepoLens — Copilot Instructions

## What This App Does

RepoLens is an **agentic AI system** that ingests a software repository (via GitHub URL or zip upload) and acts as an expert on it. It answers architectural questions, generates Mermaid diagrams, detects design flaws, produces onboarding guides, and more — powered by **Amazon Nova 2 Lite** through a **LangGraph** multi-tool agent. Built for the AWS Amazon Nova Hackathon under the Agentic AI category.

---

## Monorepo Structure

```
repolens/                         ← repo root (this workspace)
├── .devcontainer/                ← VS Code Dev Container config
│   └── devcontainer.json         ← Points at docker-compose.yml, sets container to backend
├── backend/                      ← FastAPI + LangGraph agent (Python, pip)
│   ├── app/
│   │   ├── main.py               ← FastAPI app entry point
│   │   ├── api/                  ← Route handlers (one file per domain)
│   │   ├── agent/                ← LangGraph graph, nodes, tools
│   │   │   ├── graph.py          ← StateGraph definition
│   │   │   ├── state.py          ← AgentState TypedDict
│   │   │   └── tools/            ← One file per LangGraph tool
│   │   ├── ingestion/            ← Repo cloning, file filtering, token packing
│   │   └── models/               ← Pydantic request/response schemas
│   ├── requirements.txt          ← pip deps — edit this then rebuild the container
│   └── Dockerfile
├── frontend/                     ← Next.js 14 app router (TypeScript)
│   ├── src/
│   │   ├── app/                  ← Pages and layouts (app router)
│   │   ├── components/           ← Reusable React components
│   │   └── lib/                  ← API client, utils, types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml            ← Dev environment (hot reload)
├── docker-compose.prod.yml       ← Production build
├── .env.example                  ← All required env vars documented here
└── docs/
    └── features.md               ← Full feature spec — read this first
```

---

## Tech Stack

| Layer            | Technology                                  | Notes                                                |
| ---------------- | ------------------------------------------- | ---------------------------------------------------- |
| LLM              | Amazon Nova 2 Lite                          | Via `api.nova.amazon.com/v1` (OpenAI-compatible SDK) |
| Agent Framework  | LangGraph                                   | `langgraph` + `langchain-core` packages              |
| Backend          | FastAPI (Python ≥ 3.14)                     | `pip` + `requirements.txt` inside Docker             |
| Frontend         | Next.js 14 (TypeScript)                     | App Router, Tailwind CSS                             |
| Diagrams         | Mermaid.js                                  | Rendered client-side via `mermaid` npm package       |
| Vector Store     | ChromaDB                                    | Phase 3 only — not needed for small/medium repos     |
| Containerization | Docker + Docker Compose                     | Both dev and prod configs exist                      |
| Frontend Deploy  | Vercel                                      |                                                      |
| Backend Deploy   | Railway (dev) / Azure Container Apps (prod) |                                                      |

---

## Amazon Nova API — Critical Facts

- **Endpoint**: `https://api.nova.amazon.com/v1` (NOT AWS Bedrock endpoint)
- **SDK**: Use the standard `openai` Python package with a custom `base_url`
- **Model ID**: `nova-2-lite-v1`
- **Context window**: 1,000,000 tokens — inject entire repos directly; no RAG needed for small/medium repos
- **Multimodal**: Send files as base64 in the `file` content type block
- **System tools**: Pass `extra_body={"system_tools": ["nova_grounding"]}` to enable grounding
- **Streaming**: Use `stream=True` and iterate `response` chunks for SSE
- **Auth**: API key passed as `api_key=` to the `OpenAI()` constructor; stored in `NOVA_API_KEY` env var

```python
# Canonical client initialisation — always use this pattern
from openai import OpenAI
client = OpenAI(api_key=os.environ["NOVA_API_KEY"], base_url="https://api.nova.amazon.com/v1")
```

---

## Backend Conventions (FastAPI)

- **Package manager**: `pip` + `requirements.txt` inside Docker. To add a dependency, add the package to `backend/requirements.txt`, then rebuild the container: `docker compose build backend`.
- **Never run `pip` commands on the host machine** — all Python execution happens inside Docker.
- **Run dev server**: `docker compose up` from repo root — do NOT run uvicorn directly on the host.
- **All routes** are prefixed with `/api` and defined in `backend/app/api/`
- **Pydantic v2** for all request/response models — place in `backend/app/models/`
- **Session state** is in-memory (`dict`) keyed by `session_id` (UUID). No DB in Phase 1.
- **Streaming responses** use `StreamingResponse` with an async generator yielding SSE chunks
- **CORS** is configured to allow the Next.js dev origin (`http://localhost:3000`)
- **Error handling**: raise `HTTPException` with meaningful `detail` strings; never swallow exceptions silently
- **Environment variables**: always read via `os.environ["VAR"]` (hard fail if missing) or `os.getenv("VAR", default)` for optional ones

## LangGraph Conventions

- `AgentState` is a `TypedDict` defined in `agent/state.py`; always extend it, never redefine it
- Each tool is a `@tool`-decorated function in its own file under `agent/tools/`
- The graph is compiled once at startup and reused across requests (it is stateless by design)
- Pass `session_id` and `repo_context` (the packed codebase string) via the initial state, not as tool arguments
- For streaming, use `graph.astream_events()` and filter for `on_chat_model_stream` events

---

## Frontend Conventions (Next.js)

- **App Router** — all pages in `src/app/`, layouts in `src/app/layout.tsx`
- **TypeScript strict mode** — no `any` types; define all API response shapes in `src/lib/types.ts`
- **Tailwind CSS** for all styling — no inline styles, no CSS modules unless unavoidable
- **API calls** go through `src/lib/api.ts` — a thin typed wrapper around `fetch`; never call `fetch` directly from components
- **Streaming**: consume SSE with `EventSource` or `fetch` + `ReadableStream` in the API client
- **Mermaid rendering**: dynamically import `mermaid` (it is browser-only); call `mermaid.render()` inside a `useEffect`
- **Component naming**: PascalCase files and exports; one component per file
- **State management**: React `useState`/`useReducer` + React Context — no external state library needed

---

## Docker & Environment

> **Docker is the only supported development environment. Never create a local venv or run Python/Node directly on the host.**

### Running the app
```powershell
# Start both services with hot reload (from repo root)
docker compose up

# Rebuild after adding a new Python dependency to requirements.txt
docker compose build backend

# Rebuild after adding a new npm package to package.json
docker compose build frontend

# Run a one-off command inside a running container
docker compose exec backend python -c "print('hello')"
docker compose exec frontend npm run lint
```

### How hot reload works
- **Backend**: `./backend` is bind-mounted into the container. Uvicorn runs with `--reload`, so saving any `.py` file restarts the server automatically.
- **Frontend**: `./frontend` is bind-mounted. Next.js dev server (`npm run dev`) picks up file changes automatically. `node_modules` lives only inside the container (anonymous volume), never on the host.

### Adding dependencies
| Service | How |
|---|---|
| Backend (Python) | Add the package to `backend/requirements.txt`, then run `docker compose build backend` |
| Frontend (npm) | Run `docker compose exec frontend npm install <pkg>` **or** add to `package.json` then `docker compose build frontend` |

### Required env vars
Copy `.env.example` → `.env` at the repo root before running `docker compose up`:
- `NOVA_API_KEY` — Amazon Nova API key
- `NEXT_PUBLIC_API_URL` — Backend URL seen by the browser (default: `http://localhost:8000`)

Never commit `.env`; it is in `.gitignore`.

### Port mapping
| Service | Host port | Container port |
|---|---|---|
| Backend (FastAPI) | 8000 | 8000 |
| Frontend (Next.js) | 3000 | 3000 |

---

## Key Architectural Decisions

1. **No RAG for small/medium repos**: The 1M token context window is large enough to hold most repos whole. Only Phase 3 adds ChromaDB for repos that exceed ~750k tokens.
2. **Token budget**: Cap context at 750k tokens. Priority order for inclusion: entry points → configs → core modules → tests → generated files (dropped last).
3. **File ingestion filter** — always exclude: `node_modules/`, `.git/`, `dist/`, `build/`, `*.lock`, `*.png`, `*.jpg`, `*.svg`, binary files.
4. **Mermaid over image generation**: All diagrams are Mermaid text — lightweight, no image API costs, copy-able by users.
5. **In-memory sessions**: No database in Phase 1. Sessions are `Dict[str, SessionState]` on the FastAPI process.

---

## Development Workflow

Features are built phase by phase using three document types and a set of reusable prompt files.

### Document types (one set per phase)
| File | Purpose |
|---|---|
| `docs/phaseN-plan.md` | High-level implementation plan for the phase — what to build, file list, build order, definition of done |
| `docs/phaseN-progress.md` | Granular task checklist broken out of the plan — one task = one file/function, ~30 min of work |

### Reusable prompt files (`.github/prompts/`)
| Prompt file | When to use |
|---|---|
| `plan-next-phase.prompt.md` | To generate a plan file for the next unplanned phase |
| `break-into-tasks.prompt.md` | To break a plan file into a granular progress/task file |
| `execute-next-task.prompt.md` | To implement the single next `[ ]` task in the progress file |
| `execute-milestone.prompt.md` | To implement all tasks in a chosen milestone at once |
| `verify-progress.prompt.md` | To audit completed tasks and fix any broken ones |

### Normal working loop
```
1. Review docs/phaseN-plan.md  →  adjust if needed
2. Review docs/phaseN-progress.md  →  adjust if needed
3. Run execute-next-task  →  agent implements one task, marks [x]
4. Repeat step 3 until milestone is done
5. Run verify-progress  →  catch anything broken
6. Move to next milestone
```

### Task status legend
`[ ]` Not started · `[~]` In progress · `[x]` Done · `[!]` Blocked

---

## Existing Resources

- `docs/features.md` — full feature spec with phases, priority matrix, and 3-week timeline. **Always consult this before adding a new feature.**
- `docs/phase1-plan.md` — Phase 1 implementation plan (ready).
- `docs/phase1-progress.md` — Phase 1 task checklist (ready to execute).
- `.github/prompts/` — reusable Copilot prompt files for the dev workflow.
- `.gitignore` — already configured for Python and Node.

---

## Common Mistakes to Avoid

- ❌ Do NOT use `boto3` / AWS Bedrock SDK — the Nova API uses the OpenAI-compatible endpoint
- ❌ Do NOT run `pip` or `npm` commands directly on the host — use Docker exclusively
- ❌ Do NOT create a local `.venv` or `node_modules` on the host — these live only inside containers
- ❌ Do NOT put business logic in FastAPI route handlers — routes call agent/ingestion functions only
- ❌ Do NOT import `mermaid` at the module level in Next.js — it is browser-only, always dynamic import
- ❌ Do NOT hardcode `NOVA_API_KEY` — use environment variables exclusively
- ❌ Do NOT create new Pydantic models inline in route files — always define them in `models/`
