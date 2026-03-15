/**
 * RepoLens API client.
 *
 * Thin typed wrapper around `fetch` — all backend calls go through here.
 * Never call `fetch` directly from components.
 *
 * Base URL is read from NEXT_PUBLIC_API_URL (defaults to http://localhost:8000).
 */

import type { IngestResponse, SseEvent } from "@/utils/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Ingestion
// ---------------------------------------------------------------------------

/**
 * Ingest a public GitHub repository URL.
 *
 * The `onStep` callback is called before each async stage so callers can
 * display sequential status text ("Cloning repository…" → "Ready!").
 */
export async function ingestRepo(
  url: string,
  onStep: (msg: string) => void
): Promise<IngestResponse> {
  onStep("Cloning repository…");
  const res = await fetch(`${BASE_URL}/api/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  onStep("Filtering files…");
  const data = await handleResponse<IngestResponse>(res);

  onStep("Packing context…");
  // The backend handles all three stages in one call; we advance the status
  // after the response arrives to reflect the final "Packing context…" step.

  onStep("Ready!");
  return data;
}

/**
 * Ingest a zip archive uploaded by the user.
 *
 * The `onStep` callback is called before each async stage.
 */
export async function ingestZip(
  file: File,
  onStep: (msg: string) => void
): Promise<IngestResponse> {
  onStep("Uploading archive…");
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${BASE_URL}/api/ingest/upload`, {
    method: "POST",
    body: form,
  });

  onStep("Filtering files…");
  const data = await handleResponse<IngestResponse>(res);

  onStep("Packing context…");
  onStep("Ready!");
  return data;
}

// ---------------------------------------------------------------------------
// Chat — SSE streaming
// ---------------------------------------------------------------------------

/**
 * Send a chat message and stream the agent's response as typed SSE events.
 *
 * Usage:
 * ```ts
 * for await (const event of sendMessage(sessionId, message)) {
 *   if (event.type === "text") accumulate(event.chunk);
 *   if (event.type === "done") break;
 * }
 * ```
 */
export async function* sendMessage(
  sessionId: string,
  message: string
): AsyncGenerator<SseEvent> {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (!res.ok || !res.body) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // ignore
    }
    yield { type: "error", detail } satisfies SseEvent;
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE frames are delimited by "\n\n"
    const frames = buffer.split("\n\n");
    // The last element may be an incomplete frame — keep it in the buffer.
    buffer = frames.pop() ?? "";

    for (const frame of frames) {
      // Each frame may have multiple lines; pick the one starting with "data:"
      for (const line of frame.split("\n")) {
        if (!line.startsWith("data:")) continue;
        const raw = line.slice("data:".length).trim();
        if (!raw) continue;

        let event: SseEvent;
        try {
          event = JSON.parse(raw) as SseEvent;
        } catch {
          // Malformed JSON — skip this frame
          continue;
        }

        yield event;

        if (event.type === "done" || event.type === "error") {
          reader.cancel();
          return;
        }
      }
    }
  }
}
