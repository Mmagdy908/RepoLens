"use client";

import { useState, useEffect } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
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

// ---------------------------------------------------------------------------
// Prop shapes for the react-markdown component overrides
// ---------------------------------------------------------------------------
type NodeProps = { children?: React.ReactNode };
type CodeProps = { className?: string; children?: React.ReactNode };
type AnchorProps = { href?: string; children?: React.ReactNode };

// ---------------------------------------------------------------------------
// Component map passed to ReactMarkdown
// ---------------------------------------------------------------------------
const markdownComponents: Record<string, React.ComponentType<any>> = {
  // eslint-disable-line @typescript-eslint/no-explicit-any
  h1: ({ children }: NodeProps) => (
    <h1 className="mb-3 mt-4 text-lg font-bold text-slate-100 first:mt-0">
      {children}
    </h1>
  ),
  h2: ({ children }: NodeProps) => (
    <h2 className="mb-2 mt-4 text-base font-bold text-slate-100 first:mt-0">
      {children}
    </h2>
  ),
  h3: ({ children }: NodeProps) => (
    <h3 className="mb-2 mt-3 text-sm font-bold text-slate-200 first:mt-0">
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
      <code className="rounded bg-slate-700 px-1 py-0.5 font-mono text-xs text-indigo-300">
        {children}
      </code>
    );
  },
  pre: ({ children }: NodeProps) => (
    <pre className="mb-3 overflow-x-auto rounded-lg border border-slate-700 bg-slate-900 p-3 font-mono text-xs text-slate-300">
      {children}
    </pre>
  ),
  blockquote: ({ children }: NodeProps) => (
    <blockquote className="mb-2 border-l-2 border-indigo-500 pl-3 italic text-slate-400">
      {children}
    </blockquote>
  ),
  strong: ({ children }: NodeProps) => (
    <strong className="font-semibold text-slate-100">{children}</strong>
  ),
  em: ({ children }: NodeProps) => (
    <em className="italic text-slate-300">{children}</em>
  ),
  hr: () => <hr className="my-3 border-slate-700" />,
  table: ({ children }: NodeProps) => (
    <div className="mb-3 overflow-x-auto">
      <table className="w-full border-collapse text-xs">{children}</table>
    </div>
  ),
  thead: ({ children }: NodeProps) => (
    <thead className="bg-slate-700">{children}</thead>
  ),
  th: ({ children }: NodeProps) => (
    <th className="border border-slate-600 px-3 py-1.5 text-left font-semibold text-slate-200">
      {children}
    </th>
  ),
  td: ({ children }: NodeProps) => (
    <td className="border border-slate-600 px-3 py-1.5 text-slate-300">
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

function MarkdownContent({ text }: { text: string }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
      {text}
    </ReactMarkdown>
  );
}

// ---------------------------------------------------------------------------
// ThinkingBlock — collapsible reasoning section
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
    <div className="mb-2 rounded-lg border border-slate-700 bg-slate-900/60 text-sm">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-1.5 px-3 py-2 text-slate-400 transition-colors hover:text-slate-200"
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
        <div className="border-t border-slate-700 px-3 py-2 italic leading-relaxed text-slate-400 whitespace-pre-wrap">
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

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
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

  return (
    <div className="flex justify-start px-4 py-1.5">
      <div className="w-full max-w-[85%]">
        {/* Collapsible reasoning block */}
        {message.thinking && message.thinking.trim().length > 0 && (
          <ThinkingBlock text={message.thinking} streaming={streaming} />
        )}

        {/* Assistant bubble */}
        <div className="rounded-2xl rounded-tl-sm bg-slate-800 px-4 py-3 text-sm text-slate-100 shadow-md">
          {/* Waiting cursor before first token arrives */}
          {!message.content && streaming && (
            <span className="inline-block h-4 w-1 animate-pulse rounded-sm bg-indigo-400" />
          )}

          {/* Rendered markdown — ```mermaid fences become <DiagramBlock> */}
          {message.content && <MarkdownContent text={message.content} />}

          {/* Blinking cursor while streaming */}
          {streaming && message.content && (
            <span className="ml-0.5 inline-block h-4 w-1 animate-pulse rounded-sm bg-indigo-400 align-middle" />
          )}
        </div>
      </div>
    </div>
  );
}
