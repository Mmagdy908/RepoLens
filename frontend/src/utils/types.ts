/**
 * Shared TypeScript interfaces for RepoLens frontend.
 *
 * These mirror the Pydantic models defined in backend/app/models/ — keep them
 * in sync when the backend schemas change.
 */

// ---------------------------------------------------------------------------
// Ingestion & session types
// ---------------------------------------------------------------------------

/** A single file discovered during repo ingestion. Mirrors backend FileNode. */
export interface FileNode {
  path: string;
  size_bytes: number;
  token_count: number;
  language: string | null;
  is_binary: boolean;
}

/** Lightweight session metadata stored in the frontend after ingestion. */
export interface SessionState {
  session_id: string;
  repo_url: string | null;
  file_tree: FileNode[];
  token_count: number;
  token_budget: number;
}

/** Response returned by POST /api/ingest and POST /api/ingest/upload. */
export interface IngestResponse {
  session_id: string;
  file_tree: FileNode[];
  token_count: number;
  token_budget: number;
}

// ---------------------------------------------------------------------------
// Chat types
// ---------------------------------------------------------------------------

/** A single message in the chat history. */
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  /** Accumulated reasoning/thinking text shown in the collapsible block. */
  thinking?: string;
  /** True while the assistant is still streaming its reply. */
  streaming?: boolean;
}

// ---------------------------------------------------------------------------
// SSE event types (discriminated union)
// ---------------------------------------------------------------------------

/** A step label emitted while the agent is calling a tool. */
export interface SseStepEvent {
  type: "step";
  content: string;
}

/** A reasoning/thinking token (reserved for future use). */
export interface SseThinkingEvent {
  type: "thinking";
  chunk: string;
}

/** A final-answer token streamed from the agent node. */

export interface SseChunkEvent {
  type: "chunk";
  content: string;
}

/** Emitted once when the stream is complete. */
export interface SseDoneEvent {
  type: "done";
}

/** Emitted when an unhandled exception occurs on the backend. */
export interface SseErrorEvent {
  type: "error";
  detail: string;
}

/** Discriminated union of all SSE event shapes emitted by POST /api/chat. */
export type SseEvent =
  | SseStepEvent
  | SseThinkingEvent
  | SseChunkEvent
  | SseDoneEvent
  | SseErrorEvent;
