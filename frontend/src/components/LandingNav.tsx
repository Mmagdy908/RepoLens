"use client";

/**
 * LandingNav — top navigation bar for the landing page (/).
 *
 * Layout:
 *   Left  — inline SVG lens/eye logo + "RepoLens" wordmark
 *   Right — light/dark theme toggle (Sun / Moon icon from lucide-react)
 *
 * The bar starts transparent and gains a frosted-glass blur when the user
 * scrolls down past 10 px.
 */

import { useEffect, useState } from "react";
import ThemeToggle from "./ThemeToggle";

export default function LandingNav() {
  const [scrolled, setScrolled] = useState(false);

  // Detect scroll to toggle backdrop blur
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav      className={[
        "fixed inset-x-0 top-0 z-50 flex items-center justify-between px-6 py-4 transition-all duration-300",
        scrolled
          ? "bg-white/80 backdrop-blur-md shadow-md dark:bg-slate-900/80"
          : "bg-transparent",
      ].join(" ")}
    >
      {/* ── Logo + wordmark ── */}
      <div className="flex items-center gap-2.5 select-none">
        {/* Inline SVG lens/eye icon */}
        <svg
          width="28"
          height="28"
          viewBox="0 0 28 28"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          {/* Outer circle (lens frame) */}
          <circle cx="14" cy="14" r="11" stroke="#6366f1" strokeWidth="2.2" />
          {/* Inner iris */}
          <circle cx="14" cy="14" r="5.5" fill="#6366f1" opacity="0.85" />
          {/* Pupil highlight */}
          <circle cx="15.8" cy="12.2" r="1.6" fill="white" opacity="0.6" />
          {/* Cross-hair tick marks */}
          <line
            x1="14"
            y1="1"
            x2="14"
            y2="4.5"
            stroke="#6366f1"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
          <line
            x1="14"
            y1="23.5"
            x2="14"
            y2="27"
            stroke="#6366f1"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
          <line
            x1="1"
            y1="14"
            x2="4.5"
            y2="14"
            stroke="#6366f1"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
          <line
            x1="23.5"
            y1="14"
            x2="27"
            y2="14"
            stroke="#6366f1"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
        </svg>        <span className="text-xl font-semibold tracking-tight text-indigo-900 dark:text-white">
          RepoLens
        </span></div>

      {/* ── Theme toggle ── */}
      <ThemeToggle />
    </nav>
  );
}
