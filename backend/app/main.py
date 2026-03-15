from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, health, ingest, sessions, tools_usage

import os

print("FRONTEND_URL:", os.environ.get("FRONTEND_URL"))
app = FastAPI(title="RepoLens API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(tools_usage.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
