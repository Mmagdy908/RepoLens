"use client";

/**
 * ThemeToggle — standalone light/dark mode toggle button.
 *
 * - Reads initial theme from `localStorage("theme")` after mount (avoids SSR mismatch).
 * - Falls back to "dark" when no value is stored.
 * - Toggles `class="dark"` on `document.documentElement`.
 * - Persists the chosen theme to `localStorage("theme")`.
 * - Renders a `Sun` icon when dark mode is active (click → switch to light).
 * - Renders a `Moon` icon when light mode is active (click → switch to dark).
 */

import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

export default function ThemeToggle() {
  // undefined while not yet mounted — prevents hydration mismatch
  const [dark, setDark] = useState<boolean | undefined>(undefined);

  // Read persisted preference once after hydration
  useEffect(() => {
    const stored = localStorage.getItem("theme");
    const isDark = stored !== "light";
    setDark(isDark);
    // Ensure the DOM class matches the stored value
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, []);

  function toggleTheme() {
    const next = !dark;
    setDark(next);
    if (next) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }

  // Don't render the button until we know the current theme (avoids flash)
  if (dark === undefined) {
    return <div className="h-9 w-9" aria-hidden />;
  }

  return (
    <button
      onClick={toggleTheme}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}      className="flex h-9 w-9 items-center justify-center rounded-full transition-colors text-indigo-600 hover:bg-indigo-100 dark:text-slate-300 dark:hover:bg-slate-700/60"
    >
      {dark ? <Sun size={18} /> : <Moon size={18} className="text-indigo-700" />}
    </button>
  );
}
