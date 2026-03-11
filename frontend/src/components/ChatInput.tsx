"use client";

/**
 * ChatInput — auto-resizing textarea with Send button.
 *
 * - Grows up to 6 rows as the user types.
 * - Enter submits, Shift+Enter inserts a newline.
 * - Entire input is disabled while `streaming` is true.
 */

import { useRef, useEffect, useCallback } from "react";
import { Send } from "lucide-react";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  streaming: boolean;
  placeholder?: string;
}

export default function ChatInput({
  value,
  onChange,
  onSend,
  streaming,
  placeholder = "Ask anything about your repository…",
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize: shrink back down when value changes (e.g. after send)
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    // Cap at 6 rows worth of height (~1.5rem line-height * 6 + padding)
    const lineHeight = parseFloat(getComputedStyle(el).lineHeight) || 24;
    const maxHeight = lineHeight * 6 + 16; // 16px top+bottom padding
    el.style.height = `${Math.min(el.scrollHeight, maxHeight)}px`;
  }, [value]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (!streaming && value.trim()) onSend();
      }
    },
    [onSend, streaming, value]
  );

  const canSend = !streaming && value.trim().length > 0;

  return (
    <div className="flex items-end gap-2 rounded-xl border border-slate-700 bg-slate-800 px-3 py-2 transition focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500">
      <textarea
        ref={textareaRef}
        rows={1}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={streaming}
        placeholder={placeholder}
        className="flex-1 resize-none bg-transparent text-sm text-slate-100 placeholder-slate-500 outline-none disabled:opacity-50"
        style={{ minHeight: "1.5rem" }}
      />
      <button
        onClick={() => canSend && onSend()}
        disabled={!canSend}
        title="Send message (Enter)"
        className="mb-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40"
      >
        <Send size={13} />
      </button>
    </div>
  );
}
