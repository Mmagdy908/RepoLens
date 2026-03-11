"use client";

/**
 * ChatMessage — renders a single message bubble in the chat window.
 *
 * User messages: right-aligned, indigo background.
 * Assistant messages: left-aligned, slate-800 background.
 *
 * Handles:
 * - Collapsible "🧠 Reasoning…" block for the `thinking` prop.
 * - Mermaid fence detection: splits content on ```mermaid…``` blocks and
 *   passes raw Mermaid source to <DiagramBlock>; other segments are rendered
 *   as plain Markdown (bold, inline code, paragraphs).
 * - Blinking cursor while `streaming` is true.
 */

import { useState, useEffect } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import DiagramBlock from "./DiagramBlock";
import type { ChatMessage as ChatMessageType } from "@/lib/types";

// ---------------------------------------------------------------------------
// Markdown-lite renderer (no external dep)
// Handles: **bold**, `inline code`, and paragraph breaks.
// ---------------------------------------------------------------------------
function renderMarkdown(text: string): React.ReactNode[] {
  const paragraphs = text.split(/\n{2,}/);
  return paragraphs.map((para, pi) => {
    // Split on **bold** and `code` tokens
    const parts: React.ReactNode[] = [];
    const tokenRegex = /(\*\*(.+?)\*\*|`([^`]+)`)/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = tokenRegex.exec(para)) !== null) {
      if (match.index > lastIndex) {
        parts.push(para.slice(lastIndex, match.index));
      }
      if (match[2] !== undefined) {
        // **bold**
        parts.push(
          <strong key={match.index} className="font-semibold">
            {match[2]}
          </strong>
        );
      } else if (match[3] !== undefined) {
        // `inline code`
        parts.push(
          <code
            key={match.index}
            className="rounded bg-slate-700 px-1 py-0.5 font-mono text-sm text-indigo-300"
          >
            {match[3]}
          </code>
        );
      }
      lastIndex = match.index + match[0].length;
    }
    if (lastIndex < para.length) {
      parts.push(para.slice(lastIndex));
    }

    // Render single-line content without a wrapping <p> to avoid nesting issues
    return (
      <p
        key={pi}
        className="mb-2 last:mb-0 leading-relaxed whitespace-pre-wrap"
      >
        {parts}
      </p>
    );
  });
}

// ---------------------------------------------------------------------------
// Split content string into text and mermaid segments
// ---------------------------------------------------------------------------
type TextSegment = { kind: "text"; value: string };
type MermaidSegment = { kind: "mermaid"; value: string };
type Segment = TextSegment | MermaidSegment;

function splitContent(content: string): Segment[] {
  const segments: Segment[] = [];
  // Match ```mermaid ... ``` fences (multiline)
  const fenceRegex = /```mermaid\r?\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = fenceRegex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      const text = content.slice(lastIndex, match.index).trim();
      if (text) segments.push({ kind: "text", value: text });
    }
    segments.push({ kind: "mermaid", value: match[1].trim() });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < content.length) {
    const text = content.slice(lastIndex).trim();
    if (text) segments.push({ kind: "text", value: text });
  }
  return segments;
}

// ---------------------------------------------------------------------------
// ThinkingBlock — collapsible reasoning section
// ---------------------------------------------------------------------------
interface ThinkingBlockProps {
  text: string;
  streaming: boolean;
}

function ThinkingBlock({ text, streaming }: ThinkingBlockProps) {
  // Auto-expand while streaming, collapse when done
  const [open, setOpen] = useState(streaming);

  useEffect(() => {
    if (streaming) setOpen(true);
    else setOpen(false);
  }, [streaming]);

  return (
    <div className="mb-2 rounded-lg border border-slate-700 bg-slate-900/60 text-sm">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-1.5 px-3 py-2 text-slate-400 hover:text-slate-200 transition-colors"
      >
        {open ? (
          <ChevronDown size={13} className="shrink-0" />
        ) : (
          <ChevronRight size={13} className="shrink-0" />
        )}
        <span className="font-medium">🧠 Reasoning…</span>
        {streaming && (
          <span className="ml-1 inline-block h-2 w-2 rounded-full bg-indigo-400 animate-pulse" />
        )}
      </button>
      {open && (
        <div className="border-t border-slate-700 px-3 py-2 italic text-slate-400 whitespace-pre-wrap leading-relaxed">
          {text}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// ChatMessage component
// ---------------------------------------------------------------------------
interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const segments = splitContent(message.content);
  const streaming = message.streaming ?? false;

  if (isUser) {
    return (
      <div className="flex justify-end px-4 py-1.5">
        <div className="max-w-[75%] rounded-2xl rounded-tr-sm bg-indigo-600 px-4 py-3 text-sm text-white shadow-md">
          <p className="whitespace-pre-wrap leading-relaxed">
            {message.content}
          </p>
        </div>
      </div>
    );
  }

  // Assistant bubble
  return (
    <div className="flex justify-start px-4 py-1.5">
      <div className="max-w-[85%] w-full">
        {/* Thinking / reasoning block */}
        {message.thinking && message.thinking.trim().length > 0 && (
          <ThinkingBlock text={message.thinking} streaming={streaming} />
        )}

        {/* Main content bubble */}
        <div className="rounded-2xl rounded-tl-sm bg-slate-800 px-4 py-3 text-sm text-slate-100 shadow-md">
          {" "}
          {segments.length === 0 && streaming && (
            // Empty bubble while first tokens arrive
            <span className="inline-block h-4 w-1 animate-blink rounded-sm bg-indigo-400" />
          )}
          {segments.map((seg, i) => {
            if (seg.kind === "mermaid") {
              return <DiagramBlock key={i} code={seg.value} />;
            }
            return (
              <div key={i} className="prose-sm text-slate-100">
                {renderMarkdown(seg.value)}
              </div>
            );
          })}
          {/* Blinking cursor appended to last text segment while streaming */}
          {streaming && segments.length > 0 && (
            <span className="ml-0.5 inline-block h-4 w-1 animate-blink rounded-sm bg-indigo-400 align-middle" />
          )}
        </div>
      </div>
    </div>
  );
}
