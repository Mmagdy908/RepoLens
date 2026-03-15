# RepoLens 🔍

[![Deployed App](https://img.shields.io/badge/Deployed_App-Live_Demo-blue?style=for-the-badge)](https://repolens-production-e64d.up.railway.app)

**RepoLens** is an agentic AI system that ingests a software repository (via GitHub URL or zip upload) and acts as an expert on it. It answers architectural questions, generates Mermaid diagrams, detects design flaws, produces onboarding guides, and more — powered by **Amazon Nova 2 Lite** through a **LangGraph** multi-tool agent.

Built for the **AWS Amazon Nova Hackathon** under the Agentic AI category.

---

## 🚀 Features

- **Instant Codebase Understanding**: Drop in a GitHub URL or zip file. RepoLens reads your entire repo instantly.
- **Architectural Insights**: Ask high-level architectural questions and get detailed, grounded answers.
- **Dynamic Mermaid Diagrams**: Automatically generate sequence, component, and architectural diagrams.
- **Code Quality & Security**: Detect design flaws, tech debt, and potential security vulnerabilities.
- **Powered by Amazon Nova 2 Lite**: Utilizes the massive 1M token context window to ingest entire repositories without needing complex RAG for small-to-medium codebases.

---

## 🏗️ Architecture & Tech Stack

RepoLens is built as a robust, containerized monorepo with a separation of concerns between the frontend UI and the agentic backend.

### Tech Stack

| Layer               | Technology                  | Notes                                                                                          |
| ------------------- | --------------------------- | ---------------------------------------------------------------------------------------------- |
| **LLM**             | **Amazon Nova 2 Lite**      | Accessed via `api.nova.amazon.com/v1`. Utilizes the 1M context window for full-repo ingestion. |
| **Agent Framework** | **LangGraph**               | Manages the multi-tool agent state and execution flow.                                         |
| **Backend**         | **FastAPI** (Python 3.14+)  | Handles repository cloning, token packing, and LangGraph execution.                            |
| **Frontend**        | **Next.js 16** (TypeScript) | App Router, Tailwind CSS for a modern, responsive UI.                                          |
| **Diagrams**        | **Mermaid.js**              | Rendered client-side.                                                                          |
| **Infrastructure**  | **Docker & Compose**        | Fully containerized dev and prod environments.                                                 |

### How It Works

1. **Ingestion**: The backend downloads the target repository, filters out irrelevant files (e.g., `node_modules`, binaries), and packs the code into a massive context block.
2. **State Management**: LangGraph initializes an `AgentState` containing the user query, chat history, and the codebase context.
3. **Agentic Execution**: The Amazon Nova 2 Lite model decides which tools to call (e.g., `architecture`, `security`, `diagram_component`) based on the user's prompt.
4. **Streaming Delivery**: The backend streams the LLM's response back to the Next.js frontend via Server-Sent Events (SSE).

---

## 💻 How to Run Locally

> **Note**: Docker is the _only_ supported development environment. Ensure you have Docker and Docker Compose installed.

### 1. Clone the Repository

```bash
git clone https://github.com/Mmagdy908/RepoLens.git
cd repolens
```

### 2. Set Up Environment Variables

Create a `.env` file in the repository root (you can copy `.env.example` if it exists):

```bash
cp .env.example .env
```

Ensure your `.env` contains:

```env
NOVA_API_KEY=your_amazon_nova_api_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
NOVA_MODEL_ID=nova-2-lite-v1
```

### 3. Start the Application

#### Option A: Using Docker (Recommended)

Run Docker Compose to build and start both the frontend and backend services with hot-reloading enabled.

```bash
docker compose up --build
```

#### Option B: Run Manually (Without Docker)

If you prefer to run the project on your host machine:

**1. Set up and start the Backend (FastAPI)**

```bash
cd backend
cp ../.env .env  # Copy the root .env to the backend folder
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**2. Set up and start the Frontend (Next.js)**
Open a new terminal and run:

```bash
cd frontend
cp ../.env .env.local  # Copy the root .env to the frontend folder
npm install
npm run dev
```

### 4. Access the App Locally

- **App Link**: [http://localhost:3000](http://localhost:3000)

---

**Live Demo:** [https://repolens-production-e64d.up.railway.app](https://repolens-production-e64d.up.railway.app)
