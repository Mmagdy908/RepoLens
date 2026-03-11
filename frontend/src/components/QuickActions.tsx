"use client";

import {
  BookOpen,
  GitBranch,
  Layers,
  Bug,
  ShieldAlert,
  Wrench,
} from "lucide-react";

interface Action {
  label: string;
  prompt: string;
  icon: React.ReactNode;
}

const ACTIONS: Action[] = [
  {
    label: "Give me an overview",
    prompt: "Give me an overview of this project.",
    icon: <BookOpen size={13} />,
  },
  {
    label: "Show architecture diagram",
    prompt: "Show me the architecture diagram.",
    icon: <GitBranch size={13} />,
  },
  {
    label: "What's the tech stack?",
    prompt: "What's the tech stack used in this project?",
    icon: <Layers size={13} />,
  },
  {
    label: "Find design flaws",
    prompt: "Find the design flaws in this codebase.",
    icon: <Bug size={13} />,
  },
  {
    label: "Security audit",
    prompt: "Give me a security audit of this codebase.",
    icon: <ShieldAlert size={13} />,
  },
  {
    label: "Tech debt report",
    prompt: "Give me a tech debt summary for this project.",
    icon: <Wrench size={13} />,
  },
];

interface QuickActionsProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export default function QuickActions({
  onSendMessage,
  disabled = false,
}: QuickActionsProps) {
  return (
    <div className="flex flex-col gap-1.5 px-1">
      <p className="px-1 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
        Quick Actions
      </p>
      <div className="flex flex-col gap-1">
        {ACTIONS.map((action) => (
          <button
            key={action.label}
            onClick={() => onSendMessage(action.prompt)}
            disabled={disabled}
            className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-left text-xs text-slate-300 transition hover:border-indigo-500/60 hover:bg-indigo-950/40 hover:text-indigo-300 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <span className="shrink-0 text-slate-400">{action.icon}</span>
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
}
