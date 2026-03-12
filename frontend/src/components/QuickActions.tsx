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
  colorClass: string;
}

const ACTIONS: Action[] = [
  {
    label: "Give me an overview",
    prompt: "Give me an overview of this project.",
    icon: <BookOpen size={13} />,
    colorClass:
      "bg-emerald-50 border-blue-200 hover:bg-blue-100 hover:border-blue-300 hover:text-blue-700",
  },
  {
    label: "Show architecture diagram",
    prompt: "Show me the architecture diagram.",
    icon: <GitBranch size={13} />,
    colorClass:
      "bg-emerald-50 border-violet-200 hover:bg-violet-100 hover:border-violet-300 hover:text-violet-700",
  },
  {
    label: "What's the tech stack?",
    prompt: "What's the tech stack used in this project?",
    icon: <Layers size={13} />,
    colorClass:
      "bg-emerald-50 border-emerald-200 hover:bg-emerald-100 hover:border-emerald-300 hover:text-emerald-700",
  },
  {
    label: "Find design flaws",
    prompt: "Find the design flaws in this codebase.",
    icon: <Bug size={13} />,
    colorClass:
      "bg-emerald-50 border-amber-200 hover:bg-amber-100 hover:border-amber-300 hover:text-amber-700",
  },
  {
    label: "Security audit",
    prompt: "Give me a security audit of this codebase.",
    icon: <ShieldAlert size={13} />,
    colorClass:
      "bg-emerald-50 border-rose-200 hover:bg-rose-100 hover:border-rose-300 hover:text-rose-700",
  },
  {
    label: "Tech debt report",
    prompt: "Give me a tech debt summary for this project.",
    icon: <Wrench size={13} />,
    colorClass:
      "bg-emerald-50 border-sky-200 hover:bg-sky-100 hover:border-sky-300 hover:text-sky-700",
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
      <p className="px-1 text-[10px] font-semibold uppercase tracking-widest text-slate-800 dark:text-slate-500">
        Quick Actions
      </p>
      <div className="flex flex-col gap-1">
        {ACTIONS.map((action) => (
          <button
            key={action.label}
            onClick={() => onSendMessage(action.prompt)}
            disabled={disabled}
            className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-left text-xs text-slate-900 transition disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700 dark:bg-slate-800/50 dark:text-slate-300 dark:hover:border-indigo-500/60 dark:hover:bg-indigo-950/40 dark:hover:text-indigo-300 ${action.colorClass}`}
          >
            <span className="shrink-0 text-slate-500 dark:text-slate-400">
              {action.icon}
            </span>
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
}
