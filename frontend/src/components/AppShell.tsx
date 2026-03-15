"use client";

/**
 * AppShell — two-column chat application layout.
 *
 * Left sidebar  : FileExplorer + QuickActions (collapsible on mobile)
 * Main column   : RepoInputPanel (until session exists) + ChatWindow + ChatInput
 *
 * Holds all session state:
 *   sessionId, fileTree, tokenUsed, tokenBudget, messages, isStreaming
 *
 * onSendMessage handler:
 *   1. Appends user bubble immediately.
 *   2. Appends empty assistant bubble with streaming:true.
 *   3. Iterates api.sendMessage() SSE generator.
 *      - "step"  → accumulates into bubble.thinking
 *      - "text"  → accumulates into bubble.content
 *      - "done"  → sets streaming:false
 *      - "error" → sets streaming:false, shows error in bubble
 */

import { useState, useCallback } from "react";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

import RepoInputPanel from "@/components/RepoInputPanel";
import FileExplorer from "@/components/FileExplorer";
import QuickActions from "@/components/QuickActions";
import ChatWindow from "@/components/ChatWindow";
import ChatInput from "@/components/ChatInput";

import { sendMessage } from "@/utils/api";
import type {
  ChatMessage,
  FileNode,
  IngestResponse,
  SseEvent,
} from "@/utils/types";

export default function AppShell() {
  // Session state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [tokenUsed, setTokenUsed] = useState(0);
  const [tokenBudget, setTokenBudget] = useState(750_000);

  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [inputValue, setInputValue] = useState("");

  // Sidebar
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // -------------------------------------------------------------------------
  // Ingestion callback
  // -------------------------------------------------------------------------
  function handleIngested(result: IngestResponse) {
    setSessionId(result.session_id);
    setFileTree(result.file_tree);
    setTokenUsed(result.token_count);
    setTokenBudget(result.token_budget);
    setMessages([]);
  }

  // -------------------------------------------------------------------------
  // Send message
  // -------------------------------------------------------------------------
  const handleSendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isStreaming || !sessionId) return;

      setInputValue("");

      // Append user bubble
      const userBubble: ChatMessage = { role: "user", content: trimmed };
      // Append empty assistant bubble
      const assistantBubble: ChatMessage = {
        role: "assistant",
        content: "",
        thinking: "",
        streaming: true,
      };

      setMessages((prev) => [...prev, userBubble, assistantBubble]);
      setIsStreaming(true);

      try {
        const generator = sendMessage(sessionId, trimmed);

        for await (const event of generator) {
          const ev = event as SseEvent;

          if (ev.type === "step") {
            setMessages((prev) => {
              const next = [...prev];
              const last = { ...next[next.length - 1] };
              // Append step label as a new line in thinking block
              last.thinking = last.thinking
                ? `${last.thinking}\n${ev.content}`
                : ev.content;
              next[next.length - 1] = last;
              return next;
            });
          } else if (ev.type === "chunk") {
            setMessages((prev) => {
              const next = [...prev];
              const last = { ...next[next.length - 1] };
              last.content += ev.content;
              next[next.length - 1] = last;
              return next;
            });
          } else if (ev.type === "done") {
            break;
          } else if (ev.type === "error") {
            setMessages((prev) => {
              const next = [...prev];
              const last = { ...next[next.length - 1] };
              last.content = last.content || `⚠️ Error: ${ev.detail}`;
              next[next.length - 1] = last;
              return next;
            });
            break;
          }
        }
      } catch (err) {
        setMessages((prev) => {
          const next = [...prev];
          const last = { ...next[next.length - 1] };
          last.content =
            last.content ||
            `⚠️ ${err instanceof Error ? err.message : "Unknown error"}`;
          next[next.length - 1] = last;
          return next;
        });
      } finally {
        // Mark streaming done
        setMessages((prev) => {
          const next = [...prev];
          const last = { ...next[next.length - 1] };
          last.streaming = false;
          next[next.length - 1] = last;
          return next;
        });
        setIsStreaming(false);
      }
    },
    [isStreaming, sessionId]
  );
  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------
  return (
    <div className="flex h-screen overflow-hidden bg-white text-slate-800 dark:bg-slate-900 dark:text-slate-100">
      {/* ------------------------------------------------------------------ */}
      {/* Left sidebar                                                         */}
      {/* ------------------------------------------------------------------ */}
      <aside
        className={`flex flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 transition-all duration-200 ${
          sidebarOpen ? "w-64 min-w-[16rem]" : "w-0 min-w-0 overflow-hidden"
        }`}
      >
        {sidebarOpen && (
          <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-3">
            {/* Logo / wordmark */}
            <div className="flex items-center gap-2 px-1 py-1">
              {/* Inline SVG lens icon */}
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-indigo-400"
              >
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
                <circle cx="11" cy="11" r="3" />
              </svg>{" "}
              <span className="text-sm font-semibold tracking-tight text-slate-800 dark:text-slate-100">
                RepoLens
              </span>
            </div>

            {/* File explorer */}
            <div className="flex flex-col gap-1">
              <p className="px-1 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
                Files
              </p>
              <FileExplorer files={fileTree} onFileClick={handleSendMessage} />
            </div>

            {/* Quick actions */}
            <QuickActions
              onSendMessage={handleSendMessage}
              disabled={!sessionId || isStreaming}
            />
          </div>
        )}
      </aside>

      {/* ------------------------------------------------------------------ */}
      {/* Main column                                                          */}
      {/* ------------------------------------------------------------------ */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}{" "}
        <header className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 px-4 py-2">
          <button
            onClick={() => setSidebarOpen((o) => !o)}
            title={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
            className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200 transition-colors"
          >
            {sidebarOpen ? (
              <PanelLeftClose size={16} />
            ) : (
              <PanelLeftOpen size={16} />
            )}
          </button>
          <span className="text-sm font-medium text-slate-600 dark:text-slate-300">
            {sessionId ? "Chat" : "New Analysis"}
          </span>
        </header>
        {/* Content area */}
        <div className="flex flex-1 flex-col overflow-hidden p-4 gap-4">
          {/* Repo input — shown until a session exists */}
          {!sessionId && (
            <div className="mx-auto w-full max-w-2xl">
              <RepoInputPanel onIngested={handleIngested} />
            </div>
          )}

          {/* Chat window — shown once session exists */}
          {sessionId && <ChatWindow messages={messages} />}

          {/* Chat input — shown once session exists */}
          {sessionId && (
            <div className="mx-auto w-full max-w-3xl shrink-0">
              <ChatInput
                value={inputValue}
                onChange={setInputValue}
                onSend={() => handleSendMessage(inputValue)}
                streaming={isStreaming}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
