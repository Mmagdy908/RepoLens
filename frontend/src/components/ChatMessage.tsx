"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { ChevronDown, ChevronRight, Loader2 } from "lucide-react";
// eslint-disable-next-line @typescript-eslint/no-require-imports
const ReactMarkdown = require("react-markdown").default as React.ComponentType<{
  children: string;
  remarkPlugins: unknown[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  components: Record<string, React.ComponentType<any>>;
}>;
// eslint-disable-next-line @typescript-eslint/no-require-imports
const remarkGfm = require("remark-gfm").default as unknown;
import React from "react";
import DiagramBlock from "./DiagramBlock";
import type { ChatMessage as ChatMessageType } from "@/lib/types";

type NodeProps = { children?: React.ReactNode };
type CodeProps = { className?: string; children?: React.ReactNode };
type AnchorProps = { href?: string; children?: React.ReactNode };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const markdownComponents: Record<string, React.ComponentType<any>> = {
  h1: ({ children }: NodeProps) => (
    <h1 className="mb-3 mt-4 text-lg font-bold text-slate-800 first:mt-0 dark:text-slate-100">
      {children}
    </h1>
  ),
  h2: ({ children }: NodeProps) => (
    <h2 className="mb-2 mt-4 text-base font-bold text-slate-800 first:mt-0 dark:text-slate-100">
      {children}
    </h2>
  ),
  h3: ({ children }: NodeProps) => (
    <h3 className="mb-2 mt-3 text-sm font-bold text-slate-700 first:mt-0 dark:text-slate-200">
      {children}
    </h3>
  ),
  p: ({ children }: NodeProps) => (
    <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
  ),
  ul: ({ children }: NodeProps) => (
    <ul className="mb-2 ml-4 list-disc space-y-1">{children}</ul>
  ),
  ol: ({ children }: NodeProps) => (
    <ol className="mb-2 ml-4 list-decimal space-y-1">{children}</ol>
  ),
  li: ({ children }: NodeProps) => (
    <li className="leading-relaxed">{children}</li>
  ),
  code: ({ className, children }: CodeProps) => {
    const language = (className ?? "").replace("language-", "");
    if (language === "mermaid") {
      return <DiagramBlock code={String(children).trim()} />;
    }
    if (className) {
      return <code className={className}>{children}</code>;
    }
    return (
      <code className="rounded bg-slate-200 px-1 py-0.5 font-mono text-xs text-indigo-700 dark:bg-slate-700 dark:text-indigo-300">
        {children}
      </code>
    );
  },
  pre: ({ children }: NodeProps) => (
    <pre className="mb-3 overflow-x-auto rounded-lg border border-slate-200 bg-slate-100 p-3 font-mono text-xs text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
      {children}
    </pre>
  ),
  blockquote: ({ children }: NodeProps) => (
    <blockquote className="mb-2 border-l-2 border-indigo-400 pl-3 italic text-slate-500 dark:border-indigo-500 dark:text-slate-400">
      {children}
    </blockquote>
  ),
  strong: ({ children }: NodeProps) => (
    <strong className="font-semibold text-slate-800 dark:text-slate-100">
      {children}
    </strong>
  ),
  em: ({ children }: NodeProps) => (
    <em className="italic text-slate-600 dark:text-slate-300">{children}</em>
  ),
  hr: () => <hr className="my-3 border-slate-200 dark:border-slate-700" />,
  table: ({ children }: NodeProps) => (
    <div className="mb-3 overflow-x-auto">
      <table className="w-full border-collapse text-xs">{children}</table>
    </div>
  ),
  thead: ({ children }: NodeProps) => (
    <thead className="bg-slate-100 dark:bg-slate-700">{children}</thead>
  ),
  th: ({ children }: NodeProps) => (
    <th className="border border-slate-200 px-3 py-1.5 text-left font-semibold text-slate-700 dark:border-slate-600 dark:text-slate-200">
      {children}
    </th>
  ),
  td: ({ children }: NodeProps) => (
    <td className="border border-slate-200 px-3 py-1.5 text-slate-600 dark:border-slate-600 dark:text-slate-300">
      {children}
    </td>
  ),
  a: ({ href, children }: AnchorProps) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-indigo-400 underline hover:text-indigo-300"
    >
      {children}
    </a>
  ),
};

function MarkdownContent({
  text,
  components,
}: {
  text: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  components: Record<string, React.ComponentType<any>>;
}) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {text}
    </ReactMarkdown>
  );
}

// ---------------------------------------------------------------------------
// ThinkingBlock
// ---------------------------------------------------------------------------
function ThinkingBlock({
  text,
  streaming,
}: {
  text: string;
  streaming: boolean;
}) {
  const [open, setOpen] = useState(streaming);
  useEffect(() => {
    if (streaming) setOpen(true);
    else setOpen(false);
  }, [streaming]);
  return (
    <div className="mb-2 rounded-lg border border-slate-200 bg-slate-50 text-sm dark:border-slate-700 dark:bg-slate-900/60">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-1.5 px-3 py-2 text-slate-500 transition-colors hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
      >
        {open ? (
          <ChevronDown size={13} className="shrink-0" />
        ) : (
          <ChevronRight size={13} className="shrink-0" />
        )}
        <span className="font-medium">🧠 Reasoning…</span>
        {streaming && (
          <span className="ml-1 inline-block h-2 w-2 animate-pulse rounded-full bg-indigo-400" />
        )}
      </button>
      {open && (
        <div className="border-t border-slate-200 px-3 py-2 italic leading-relaxed text-slate-500 whitespace-pre-wrap dark:border-slate-700 dark:text-slate-400">
          {text}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// ChatMessage
// ---------------------------------------------------------------------------
interface ChatMessageProps {
  message: ChatMessageType;
}

// Characters of raw markdown revealed per timer tick
const CHARS_PER_TICK = 6;
// ms between ticks
const TICK_MS = 100;

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const streaming = message.streaming ?? false;

  // visibleChars tracks how many characters of message.content are shown.
  // We use a ref as the source of truth inside the interval callback to avoid
  // stale closure issues, and mirror it to state only to trigger re-renders.
  const [visibleChars, setVisibleChars] = useState(() =>
    streaming ? 0 : message.content.length
  );
  const visibleRef = useRef(streaming ? 0 : message.content.length);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Sync the ref so the interval callback always reads the latest content length
  // without being recreated.
  const contentRef = useRef(message.content);
  contentRef.current = message.content;

  const visibleText = message.content.slice(0, visibleChars);
  const isRevealing = visibleChars < message.content.length || streaming;

  // Track which mermaid blocks are fully closed in the visible text
  const finishedMermaidBlocks = useMemo(() => {
    const blocks = new Set<string>();
    const regex = /```mermaid\s*([\s\S]*?)```/g;
    let match;
    while ((match = regex.exec(message.content)) !== null) {
      blocks.add(match[1].trim());
    }
    return blocks;
  }, [message.content]);

  // Track rendered state of each block to unblock "drip" effect
  const [renderedBlocks, setRenderedBlocks] = useState<Set<string>>(new Set());

  // Logic: "pausing" the reveal if we encounter a mermaid block that isn't rendered yet
  const isWaitingForRender = useMemo(() => {
    const regex = /```mermaid\s*([\s\S]*?)```/g;
    let match;
    while ((match = regex.exec(visibleText)) !== null) {
      const code = match[1].trim();
      if (!renderedBlocks.has(code)) {
        return true;
      }
    }
    return false;
  }, [visibleText, renderedBlocks]);

  // Sync the ref so the interval callback always reads the latest state
  const isWaitingRef = useRef(isWaitingForRender);
  isWaitingRef.current = isWaitingForRender;

  // Memoize components to inject state-aware logic (e.g. loading spinner for incomplete diagrams)
  const components = useMemo(() => {
    return {
      ...markdownComponents,
      code: ({ className, children }: CodeProps) => {
        const language = (className ?? "").replace("language-", "");
        if (language === "mermaid") {
          const codeContent = String(children).trim();
          // Render if fully revealed, OR if this specific block is closed
          const isComplete =
            !isRevealing || finishedMermaidBlocks.has(codeContent);

          if (isComplete) {
            return (
              <DiagramBlock
                code={codeContent}
                onRender={() => {
                  setRenderedBlocks((prev) => {
                    if (prev.has(codeContent)) return prev;
                    const next = new Set(prev);
                    next.add(codeContent);
                    return next;
                  });
                }}
              />
            );
          }
          return (
            <div className="my-4 flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-slate-300 bg-slate-50/50 py-6 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900/30 dark:text-slate-400">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Generating diagram...</span>
            </div>
          );
        }
        // Fallback for non-mermaid code
        if (className) {
          return <code className={className}>{children}</code>;
        }
        return (
          <code className="rounded bg-slate-200 px-1 py-0.5 font-mono text-xs text-indigo-700 dark:bg-slate-700 dark:text-indigo-300">
            {children}
          </code>
        );
      },
    };
  }, [finishedMermaidBlocks, isRevealing]);

  // Helper: ensure the drip interval is running
  const ensureInterval = () => {
    if (intervalRef.current !== null) return;
    intervalRef.current = setInterval(() => {
      // If we are waiting for a mermaid diagram to render, PAUSE the typewriter effect
      if (isWaitingRef.current) return;

      const target = contentRef.current.length;
      
      // If we built up a large backlog (e.g. while waiting for a diagram to render),
      // speed up the reveal so we catch up quickly instead of dripping slowly.
      const backlog = target - visibleRef.current;
      const charsToReveal = backlog > 100 ? Math.floor(backlog / 4) : CHARS_PER_TICK;
      
      const next = visibleRef.current + charsToReveal;
      if (next >= target) {
        // Reached the end of the current buffer
        visibleRef.current = target;
        setVisibleChars(target);
        // Only stop the interval if streaming has also ended
        if (!contentRef.current || !intervalRef.current) return;
        // We keep running while streaming; the streaming→false transition
        // will clear the interval after the last drain tick (see effect below).
      } else {
        visibleRef.current = next;
        setVisibleChars(next);
      }
    }, TICK_MS);
  };

  // When a new assistant message starts streaming, reset the counter and
  // kick off the interval.
  const prevStreamingRef = useRef(streaming);
  useEffect(() => {
    const wasStreaming = prevStreamingRef.current;
    prevStreamingRef.current = streaming;

    if (streaming && !wasStreaming) {
      // New stream starting — reset
      visibleRef.current = 0;
      setVisibleChars(0);
      ensureInterval();
    } else if (streaming && wasStreaming) {
      // Still streaming — new content arrived, make sure interval is alive
      ensureInterval();
    } else if (!streaming && wasStreaming) {
      // Stream just ended — keep the interval running to drain the remaining
      // buffer. It will be cleared by the cleanup effect once fully drained.
      ensureInterval();
    } else if (!streaming && !wasStreaming) {
      // Non-streaming message (e.g. history) — show immediately
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      visibleRef.current = message.content.length;
      setVisibleChars(message.content.length);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [streaming, message.content]);

  // Stop the interval once the drip has fully caught up and streaming is over
  useEffect(() => {
    if (
      !streaming &&
      visibleChars >= message.content.length &&
      intervalRef.current
    ) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, [visibleChars, streaming, message.content.length]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, []);

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

  return (
    <div className="flex justify-start px-4 py-1.5">
      <div className="w-full max-w-[85%]">
        {message.thinking && message.thinking.trim().length > 0 && (
          <ThinkingBlock text={message.thinking} streaming={streaming} />
        )}

        <div className="rounded-2xl rounded-tl-sm bg-slate-100 px-4 py-3 text-sm text-slate-800 shadow-md dark:bg-slate-800 dark:text-slate-100">
          {/* Waiting cursor before first chars arrive */}
          {!visibleText && streaming && (
            <span className="inline-block h-4 w-0.5 animate-blink rounded-sm bg-indigo-400" />
          )}

          {/* Incrementally-revealed markdown — ReactMarkdown renders at every tick */}
          {visibleText && (
            <div className="relative">
              <MarkdownContent text={visibleText} components={components} />
              {isRevealing && !isWaitingForRender && (
                <span className="inline-block h-[0.9em] w-0.5 animate-blink rounded-sm bg-indigo-400 align-middle" />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
