# RepoLens — Feature Documentation

> **Tagline**: _A lens over any codebase. Understand, visualize, and improve software architecture using AI._

---

## Project Overview

**RepoLens** is an agentic AI system that ingests a software repository and becomes an intelligent expert on it. It answers architectural questions, generates diagrams, detects design flaws, explains tech stacks, and guides developers — all powered by **Amazon Nova 2 Lite** via **Amazon Bedrock**.

Built for the **AWS Amazon Nova Hackathon** under the **Agentic AI** category.

---

## Tech Stack

| Layer                             | Technology                          |
| --------------------------------- | ----------------------------------- |
| **LLM**                           | Amazon Nova 2 Lite (Amazon Bedrock)          |
| **Agent Framework**               | LangGraph                                    |
| **Backend**                       | FastAPI (Python ≥ 3.14)                      |
| **Frontend**                      | Next.js 16 (TypeScript, App Router, Tailwind)|
| **Diagram Rendering**             | Mermaid.js                                   |
| **Vector Store (Phase 3+)**       | ChromaDB (local)                    |
| **Containerization**              | Docker + Docker Compose             |
| **Frontend Hosting**              | Vercel                              |
| **Backend Hosting (Dev/Staging)** | Railway                             |
| **Backend Hosting (Prod Demo)**   | Azure Container Apps                |

---

## Golden Demo Path

> This is the **end-to-end flow** that must work flawlessly for the hackathon demo.

1. User pastes a **GitHub repo URL** (or uploads a zip/folder).
2. System **ingests and indexes** the repository.
3. User asks: _"What does this project do?"_ → Gets a clear project overview.
4. User asks: _"What is the architecture?"_ → Gets a **Mermaid architecture diagram**.
5. User asks: _"What tech stack is used?"_ → Gets a structured breakdown.
6. User asks: _"What are the design flaws?"_ → Gets actionable findings.
7. User asks: _"Generate a C4 container diagram."_ → Gets a rendered C4 diagram.
8. User asks: _"How would you improve this project?"_ → Gets prioritized suggestions.

---

## Architecture Decision: Context Window vs RAG

Amazon Nova 2 Lite supports a **1,000,000 token context window**. For small-to-medium repos (the majority of real-world projects), the **entire codebase fits directly in the context window**, eliminating the need for embedding/RAG in most cases.

| Repo Size                       | Strategy                                                       |
| ------------------------------- | -------------------------------------------------------------- |
| Small / Medium (≤ ~700k tokens) | Full context injection into Nova 2 Lite                        |
| Large (> 700k tokens)           | Hybrid: smart file filtering + ChromaDB RAG fallback (Phase 3) |

---

## Development Phases

---

### Phase 1 — Core Foundation _(Week 1)_

> Goal: A working end-to-end demo that covers the golden demo path. This phase must be fully functional before moving on.

---

#### 1.1 Repo Ingestion Engine

**Description**: The system's ability to load a repository's content and prepare it for the LLM.

**Features:**

- Accept a **GitHub/GitLab repo URL** and clone it server-side.
- Accept a **zip file upload** from the user.
- Accept a **local folder path** (for development/testing).
- Traverse the repo and collect all relevant files.
- Apply a smart **file filter** to exclude noise:
  - Ignore: `node_modules/`, `.git/`, `dist/`, `build/`, `*.lock`, `*.png`, `*.jpg`, binary files, etc.
  - Configurable ignore rules (`.repolensignore` file support).
- Calculate **total token count** of the ingested content.
- Display a **file tree summary** of what was ingested.

**Why it matters**: Everything depends on clean, efficient ingestion.

---

#### 1.2 Context Packing & Token Management

**Description**: Intelligently pack the repo content into the LLM context window.

**Features:**

- Concatenate files with clear delimiters (filename headers, language hints).
- Enforce a **token budget** (max ~750k tokens for safety headroom).
- If the repo exceeds the budget: surface a warning and apply **priority-based truncation** (keep entry points, configs, main modules; drop test files, generated files last).
- Display a **token usage indicator** in the UI (e.g., "Used 342k / 1M tokens").

---

#### 1.3 Agentic Q&A Engine (LangGraph)

**Description**: The core agent that answers questions about the repo using Amazon Nova 2 Lite.

**Features:**

- LangGraph-based agent with the following **tools**:
  - `answer_general_question` — general repo Q&A.
  - `get_project_overview` — structured project summary.
  - `get_tech_stack` — identify and list technologies used.
  - `get_architecture_summary` — describe the system architecture in prose.
  - `get_file_explanation` — explain a specific file in detail.
  - `get_folder_explanation` — explain what a folder/module does.
- Maintain **conversation history** (multi-turn chat within a session).
- Stream responses to the frontend (token streaming via SSE or WebSocket).
- Agent has a **system prompt** that establishes it as a senior software architect expert.

---

#### 1.4 Architecture Diagram Generation

**Description**: Generate visual architecture diagrams as Mermaid code, rendered in the browser.

**Features:**

- `generate_architecture_diagram` tool — generates a **high-level system diagram** (Mermaid flowchart/graph).
- `generate_sequence_diagram` tool — generates a **sequence diagram** for a specific flow.
- `generate_component_diagram` tool — generates a **component relationship diagram**.
- Auto-render Mermaid diagrams inline in the chat UI.
- Allow users to **copy Mermaid source** or **download diagram as SVG/PNG**.
- Diagram **regeneration** with user-provided hints (e.g., _"focus on the auth flow"_).

---

#### 1.5 Design Analysis Tools

**Description**: The agent proactively identifies issues and improvement areas in the codebase.

**Features:**

- `find_design_flaws` tool — identifies architectural anti-patterns, tight coupling, missing abstractions, etc.
- `get_tech_debt_summary` tool — surfaces areas of technical debt.
- `get_security_concerns` tool — highlights obvious security issues (hardcoded secrets, missing auth, SQL injection risks, etc.).
- Results are presented as a **structured, categorized report** (Critical / Warning / Suggestion).

---

#### 1.6 Chat UI (Next.js Frontend)

**Description**: A clean, modern chat interface for interacting with the agent. Built with **Next.js 16 App Router**, **TypeScript (strict mode)**, and **Tailwind CSS**. All components are `.tsx` files; no `.js` or `.jsx` files are used in the frontend.

**Features:**

- **Repo input panel**: URL field + zip upload + drag-and-drop.
- **Ingestion progress indicator**: file count, token usage, status.
- **Chat interface**: message history, streaming responses, code highlighting.
- **Diagram panel**: inline Mermaid diagram rendering with copy/download buttons.
- **Quick-action buttons**: pre-defined prompts like _"Give me an overview"_, _"Show architecture diagram"_, _"Find design flaws"_.
- **File explorer sidebar**: shows the ingested file tree; click a file to ask about it.
- **Dark/Light mode** toggle.
- Responsive design (desktop-first, mobile-friendly).

---

#### 1.7 FastAPI Backend

**Description**: The backend API that bridges the frontend, LangGraph agent, and Amazon Bedrock.

**Features:**

- `POST /api/ingest` — accepts URL or file upload, runs ingestion pipeline.
- `POST /api/chat` — sends a message to the agent, returns streamed response.
- `GET /api/session/{id}` — retrieves session state (file tree, token usage, chat history).
- `DELETE /api/session/{id}` — clears a session.
- Session management (in-memory for Phase 1, can be persisted later).
- CORS configuration for Next.js frontend.
- Health check endpoint `GET /api/health`.

---

#### 1.8 Docker Setup

**Description**: Fully containerized development and production environment. **Docker is the only supported runtime — no local Python venv or Node environment is ever created on the host.**

**Features:**

- `Dockerfile` for the **FastAPI backend** — uses `python:3.14-slim`, installs `uv`, runs `uv sync` to install deps, starts uvicorn with `--reload`.
- `Dockerfile` for the **Next.js frontend** — uses `node:20-alpine`, installs npm deps at build time, starts `npm run dev`. Scaffolded with `create-next-app` using `--typescript --tailwind --app --src-dir` flags — **TypeScript strict mode is required; no plain `.js`/`.jsx` files**.
- `docker-compose.yml` for **local development**:
  - Bind-mounts `./backend` and `./frontend` for hot reload.
  - `node_modules` is an anonymous Docker volume (never written to host).
  - Both services read from a single `.env` file at the repo root.
- `docker-compose.prod.yml` for **production** multi-stage build (no bind mounts, optimized images).
- `.env.example` with all required environment variables documented.
- README with one-command startup: `docker compose up`.

**Adding dependencies (inside Docker, never on host):**
| Service | Command |
|---|---|
| Backend (Python) | `docker compose build backend` |
| Frontend (npm) | `docker compose exec frontend npm install <pkg>`, or edit `package.json` then `docker compose build frontend` |

---

### Phase 2 — Enhanced Intelligence _(Week 2)_

> Goal: Make the agent smarter, more proactive, and more impressive. Add features that differentiate RepoLens from a basic chatbot.

---

#### 2.1 C4 Model Diagram Generation

**Description**: Generate professional **C4 architecture diagrams** (the industry standard for software architecture documentation).

**Features:**

- `generate_c4_context_diagram` — Level 1: System context (actors + external systems).
- `generate_c4_container_diagram` — Level 2: Containers (apps, databases, services).
- `generate_c4_component_diagram` — Level 3: Components within a container.
- Rendered using **Mermaid C4 syntax** (natively supported).
- Interactive: user can drill down from Level 1 → Level 2 → Level 3 in the chat.

---

#### 2.2 Onboarding Guide Generation

**Description**: Auto-generate a personalized onboarding document for a new developer joining the project.

**Features:**

- `generate_onboarding_guide` tool — produces a structured markdown document covering:
  - Project purpose and goals.
  - How to set up the development environment.
  - Key modules and their responsibilities.
  - Important files to read first.
  - Common workflows (e.g., how to add a new feature, how to run tests).
  - Glossary of project-specific terms.
- Export onboarding guide as a **downloadable Markdown or PDF**.
- Customizable: user can specify their role (frontend dev, backend dev, DevOps, etc.) to get a tailored guide.

---

#### 2.3 Code Quality & Best Practices Report

**Description**: A comprehensive report on how well the codebase follows best practices.

**Features:**

- `generate_quality_report` tool covering:
  - **SOLID principles** adherence.
  - **Code duplication** detection.
  - **Test coverage** assessment (based on presence/quality of test files).
  - **Documentation quality** (missing docstrings, README completeness).
  - **Naming conventions** consistency.
  - **Dependency management** hygiene (outdated packages, circular dependencies).
- Report is formatted as a **scorecard** with ratings per category (A/B/C/D/F or 1–10).
- Exportable as PDF or Markdown.

---

#### 2.4 Dependency Graph Visualization

**Description**: Visual map of how modules/packages depend on each other.

**Features:**

- `generate_dependency_graph` tool — analyzes import statements across the codebase.
- Renders as an **interactive Mermaid graph**.
- Highlights **circular dependencies** in red.
- Identifies **most coupled** modules (high fan-in/fan-out).
- Supports multiple languages (Python imports, JS/TS imports, etc.).

---

#### 2.5 Multi-Session & Session Management

**Description**: Allow users to manage multiple repo sessions simultaneously.

**Features:**

- Session list in the sidebar (named by repo name).
- Switch between sessions without losing context.
- Rename, duplicate, or delete sessions.
- Sessions persist across browser refreshes (stored in localStorage or backend DB).

---

#### 2.6 Suggested Questions System

**Description**: AI-generated follow-up questions to guide the user's exploration.

**Features:**

- After each agent response, display **3–5 suggested follow-up questions**.
- Suggestions are contextually aware (based on the current answer and repo).
- One-click to send a suggested question.
- Helps non-technical stakeholders navigate the system.

---

#### 2.7 Repo Comparison Mode

**Description**: Load two repos and compare them side-by-side.

**Features:**

- Compare **tech stacks** between two repos.
- Compare **architectural approaches**.
- Identify what Repo B does better/worse than Repo A.
- Useful for: evaluating open-source alternatives, comparing project versions (v1 vs v2).

---

### Phase 3 — Scale & Power Features _(Week 3)_

> Goal: Handle large repos, add multimodal capabilities, and polish the product for the final demo.

---

#### 3.1 Large Repo Support (Hybrid RAG)

**Description**: Handle repos that exceed the 1M token context window using a hybrid retrieval strategy.

**Features:**

- Automatic detection when repo exceeds the token budget.
- **Smart file prioritization**: rank files by importance (entry points, configs, core modules score higher).
- **ChromaDB integration**: embed file chunks using **Amazon Titan Embeddings** (free on Bedrock) or a local model.
- **Hybrid retrieval**: semantic search to pull relevant chunks per query, then inject into context.
- Transparent UI indicator: _"Large repo mode — using selective context retrieval"_.
- Configurable chunking strategy (by file, by function, by class).

---

#### 3.2 Multimodal Input — Image & Screenshot Analysis

**Description**: Leverage Nova 2 Lite's multimodal capabilities to analyze images.

**Features:**

- User can **upload a screenshot** of an architecture diagram, ERD, or whiteboard sketch.
- Agent analyzes the image and:
  - Describes what it sees.
  - Compares it to the actual codebase.
  - Identifies discrepancies between the diagram and the code.
- User can ask: _"Does this diagram match our actual codebase?"_
- Supports: PNG, JPG, PDF screenshots.

---

#### 3.3 API Documentation Generator

**Description**: Auto-generate API documentation from the codebase.

**Features:**

- `generate_api_docs` tool — scans for REST endpoints, GraphQL schemas, gRPC definitions.
- Outputs **OpenAPI/Swagger-compatible** documentation.
- Renders an **interactive API explorer** in the UI (using Swagger UI or Redoc).
- Detects missing documentation on existing endpoints.
- Suggests improvements to API design (naming, versioning, error handling).

---

#### 3.4 Git History Intelligence

**Description**: Incorporate git history for deeper insights (requires git access).

**Features:**

- Analyze **commit patterns**: who contributes what, most-changed files.
- Identify **hotspot files** (frequently modified = likely complex/problematic).
- Summarize **recent changes** (last N commits) in plain English.
- Answer questions like: _"What changed in the last sprint?"_, _"Which files are most risky to modify?"_
- Visualize contribution heatmap per file/module.

---

#### 3.5 Architectural Decision Records (ADR) Generator

**Description**: Auto-generate ADR documents based on observed patterns in the codebase.

**Features:**

- `generate_adr` tool — infers architectural decisions from the code (e.g., _"Why was PostgreSQL chosen over MongoDB?"_).
- Generates ADRs in the standard format: Title / Status / Context / Decision / Consequences.
- Allows users to edit and export ADRs as Markdown files.
- Creates an **ADR registry** view in the UI.

---

#### 3.6 Refactoring Suggestions with Code Snippets

**Description**: Go beyond identifying problems — provide concrete, copy-pasteable refactoring suggestions.

**Features:**

- `suggest_refactoring` tool — for a specific file or module, suggests concrete code improvements.
- Shows **before/after** code diff in the UI.
- Prioritizes suggestions by impact (High/Medium/Low).
- Can be scoped: _"Refactor the authentication module"_ or _"Improve performance in src/api/routes.py"_.
- One-click **copy to clipboard** for each suggestion.

---

#### 3.7 Export & Sharing

**Description**: Allow users to export and share insights generated by RepoLens.

**Features:**

- Export full session as a **PDF report** (overview + diagrams + findings + suggestions).
- Export individual diagrams as **SVG or PNG**.
- Export onboarding guide, quality report, ADRs as **Markdown files**.
- Generate a **shareable link** to a session (read-only snapshot).
- One-click **copy report to clipboard** for pasting into Confluence, Notion, etc.

---

#### 3.8 Voice Input (Stretch Goal — Nova 2 Sonic)

**Description**: Allow users to ask questions using voice, powered by Amazon Nova 2 Sonic.

> ⚠️ Requires Nova 2 Sonic access (pending).

**Features:**

- Push-to-talk button in the chat UI.
- Voice transcription via Nova 2 Sonic.
- Agent responds with both text and **synthesized voice output**.
- Enables a fully hands-free code review experience.
- Impressive demo moment: _speak a question and hear an architectural explanation_.

---

## Feature Priority Matrix

| Feature                         | Phase | Demo Impact | Build Effort | Priority |
| ------------------------------- | ----- | ----------- | ------------ | -------- |
| Repo Ingestion Engine           | 1     | 🔴 Critical | Medium       | P0       |
| Agentic Q&A (LangGraph)         | 1     | 🔴 Critical | High         | P0       |
| Architecture Diagram Generation | 1     | 🔴 Critical | Medium       | P0       |
| Chat UI                         | 1     | 🔴 Critical | High         | P0       |
| FastAPI Backend                 | 1     | 🔴 Critical | Medium       | P0       |
| Docker Setup                    | 1     | 🟡 High     | Low          | P0       |
| Design Analysis Tools           | 1     | 🔴 Critical | Medium       | P0       |
| Context Packing                 | 1     | 🟡 High     | Medium       | P0       |
| C4 Diagram Generation           | 2     | 🔴 Critical | Low          | P1       |
| Onboarding Guide Generation     | 2     | 🔴 Critical | Low          | P1       |
| Code Quality Report             | 2     | 🟡 High     | Low          | P1       |
| Suggested Questions             | 2     | 🟡 High     | Low          | P1       |
| Dependency Graph                | 2     | 🟡 High     | Medium       | P1       |
| Multi-Session Management        | 2     | 🟢 Medium   | Medium       | P1       |
| Repo Comparison                 | 2     | 🟡 High     | High         | P2       |
| Large Repo / Hybrid RAG         | 3     | 🟢 Medium   | High         | P2       |
| Multimodal Image Analysis       | 3     | 🔴 Critical | Medium       | P1       |
| API Docs Generator              | 3     | 🟡 High     | Medium       | P2       |
| Git History Intelligence        | 3     | 🟡 High     | Medium       | P2       |
| ADR Generator                   | 3     | 🟡 High     | Low          | P2       |
| Refactoring Suggestions         | 3     | 🔴 Critical | Medium       | P2       |
| Export & Sharing                | 3     | 🟡 High     | Medium       | P2       |
| Voice Input (Nova Sonic)        | 3     | 🔴 Critical | High         | P3       |

---

## Suggested 3-Week Timeline

### Week 1 — Phase 1 (Foundation)

| Day     | Tasks                                                                                                                            |
| ------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Day 1–2 | Docker Compose setup (backend + frontend containers, hot reload, `.env`), FastAPI skeleton, Next.js skeleton, Nova API smoke test inside container |
| Day 3–4 | Repo ingestion engine (URL clone, zip upload, file filtering, token counting)                                                    |
| Day 5–6 | LangGraph agent setup + core tools (Q&A, overview, tech stack, architecture summary)                                            |
| Day 7   | Diagram generation tools (architecture, sequence, component) + Mermaid rendering in UI                                          |

### Week 2 — Phase 1 completion + Phase 2

| Day       | Tasks                                                                                   |
| --------- | --------------------------------------------------------------------------------------- |
| Day 8–9   | Design analysis tools (flaws, tech debt, security) + Chat UI polish                     |
| Day 10–11 | File explorer sidebar, quick-action buttons, streaming responses, token usage indicator |
| Day 12–13 | C4 diagrams, onboarding guide generator, code quality report                            |
| Day 14    | Suggested questions, dependency graph, multi-session management                         |

### Week 3 — Phase 3 + Polish + Deployment

| Day       | Tasks                                                                         |
| --------- | ----------------------------------------------------------------------------- |
| Day 15–16 | Multimodal image analysis, refactoring suggestions with diffs                 |
| Day 17–18 | Export & sharing (PDF, Markdown, SVG), ADR generator                          |
| Day 19–20 | Git history intelligence, large repo RAG (if time permits)                    |
| Day 21    | Final polish, deployment (Vercel + Azure Container Apps), demo recording prep |

---

## AWS & Amazon Nova Alignment

| Hackathon Category                          | How RepoLens Qualifies                                                                        |
| ------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Agentic AI** ✅ (Primary)                 | LangGraph multi-tool agent using Nova 2 Lite for complex, multi-step reasoning over codebases |
| **Multimodal Understanding** ✅ (Secondary) | Nova 2 Lite multimodal: analyze architecture diagram screenshots, compare to code             |
| **Voice AI** 🔄 (Stretch)                   | Nova 2 Sonic for voice Q&A (pending access)                                                   |

**Core Nova 2 usage:**

- `amazon.nova-lite-v1` — primary reasoning, Q&A, diagram generation, analysis
- Multimodal image input for screenshot analysis (Phase 3)
- Optional: `amazon.nova-sonic-v1` for voice (Phase 3 stretch)

---

## Project Structure (Planned)

```
repolens/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route handlers
│   │   ├── agent/          # LangGraph agent definition & tools
│   │   ├── ingestion/      # Repo cloning, parsing, token management
│   │   ├── diagrams/       # Mermaid generation utilities
│   │   └── models/         # Pydantic models
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js app router (TypeScript — .tsx/.ts only)
│   │   ├── components/     # UI components (.tsx)
│   │   └── lib/            # API client, utils, types (.ts)
│   ├── tsconfig.json       # TypeScript strict mode
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
└── docs/
    └── features.md         # This document
```

---

_Document version: 1.0 | Created: 2026-02-21 | Project: RepoLens_
