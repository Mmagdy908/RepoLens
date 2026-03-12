"use client";

/**
 * /chat — full app shell route.
 *
 * Renders <AppShell> which holds all session + chat state.
 * ThemeToggle is provided inside AppShell's top bar via layout.tsx dark class.
 */

import AppShell from "@/components/AppShell";
import ThemeToggle from "@/components/ThemeToggle";

export default function ChatPage() {  return (
    <div className="relative h-screen overflow-hidden bg-white dark:bg-slate-900">
      {/* Theme toggle — floated top-right over the shell */}
      <div className="absolute right-4 top-2 z-50">
        <ThemeToggle />
      </div>
      <AppShell />
    </div>
  );
}
