"use client";

/**
 * ChatWindow — scrollable list of ChatMessage bubbles.
 *
 * - Auto-scrolls to the bottom on new messages.
 * - Shows an empty-state placeholder when there are no messages.
 */

import { useRef, useEffect } from "react";
import { MessageSquare } from "lucide-react";
import ChatMessage from "@/components/ChatMessage";
import type { ChatMessage as ChatMessageType } from "@/lib/types";

interface ChatWindowProps {
  messages: ChatMessageType[];
}

export default function ChatWindow({ messages }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center">
        <div className="rounded-full border border-slate-200 bg-slate-100 p-4 dark:border-slate-700 dark:bg-slate-800">
          <MessageSquare size={24} className="text-slate-400 dark:text-slate-500" />
        </div>
        <p className="text-sm text-slate-400 dark:text-slate-500">
          Ask anything about your repository
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col overflow-y-auto py-4">
      {messages.map((msg, i) => (
        <ChatMessage key={i} message={msg} />
      ))}
      {/* Invisible anchor for auto-scroll */}
      <div ref={bottomRef} />
    </div>
  );
}
