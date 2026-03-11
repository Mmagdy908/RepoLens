import Link from "next/link";
import React from "react";
import LandingNav from "@/components/LandingNav";

const FEATURE_PILLS = [
  { icon: "🔍", label: "Architecture" },
  { icon: "🛡️", label: "Security" },
  { icon: "🧹", label: "Tech Debt" },
  { icon: "⚡", label: "Instant Answers" },
];

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-hidden hero-gradient text-white dark:text-white">
      {/* ── Ambient radial glow blobs ── */}
      <div
        aria-hidden
        className="pointer-events-none absolute -top-40 -left-40 h-[600px] w-[600px] rounded-full bg-indigo-600/20 dark:bg-indigo-600/20 blur-3xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -bottom-40 -right-40 h-[500px] w-[500px] rounded-full bg-violet-700/20 dark:bg-violet-700/20 blur-3xl"
      />

      {/* ── Navigation ── */}
      <LandingNav />

      {/* ── Hero content ── */}
      <div className="relative flex min-h-screen flex-col items-center justify-center px-6 pt-24 pb-16 text-center">
        {" "}
        {/* Badge */}
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-indigo-500/40 bg-indigo-500/10 px-4 py-1.5 text-sm font-medium text-indigo-700 dark:text-indigo-300">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse" />
          Powered by Amazon Nova 2 Lite
        </div>
        {/* Headline */}
        <h1 className="max-w-3xl text-5xl font-bold leading-tight tracking-tight text-slate-900 dark:text-white sm:text-6xl lg:text-7xl">
          Understand any{" "}
          <span className="bg-gradient-to-r from-indigo-600 via-violet-500 to-indigo-400 bg-clip-text text-transparent dark:from-indigo-400 dark:via-violet-400 dark:to-indigo-300">
            codebase
          </span>
          , instantly.
        </h1>
        {/* Subtitle */}
        <p className="mt-6 max-w-xl text-lg leading-relaxed text-slate-700 dark:text-slate-300 sm:text-xl">
          Drop in a GitHub URL or zip file. RepoLens reads your entire repo and
          answers architectural questions, generates diagrams, finds design
          flaws, and more — in seconds.
        </p>
        {/* CTA */}
        <Link
          href="/chat"
          className="mt-10 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-8 py-4 text-base font-semibold text-white shadow-lg shadow-indigo-900/40 transition-all duration-200 hover:bg-indigo-500 hover:shadow-indigo-800/50 hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900"
        >
          Analyze a Repo
          <span aria-hidden>→</span>
        </Link>
        {/* Feature pills */}{" "}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-2">          {FEATURE_PILLS.map(({ icon, label }, i) => (
            <React.Fragment key={label}>
              <span
                className="inline-flex items-center gap-1.5 rounded-full border border-indigo-300/60 bg-white/40 px-4 py-1.5 text-sm font-medium text-indigo-800 backdrop-blur-sm dark:border-slate-600/60 dark:bg-slate-800/60 dark:text-slate-300"
              >
                <span>{icon}</span>
                {label}
              </span>              {i < FEATURE_PILLS.length - 1 && (
                <span
                  className="text-indigo-400/60 dark:text-slate-600 select-none"
                >
                  ·
                </span>
              )}
            </React.Fragment>
          ))}
        </div>
        {/* Subtle scroll hint */}
        <p className="mt-16 text-xs text-slate-500 dark:text-slate-500 tracking-widest uppercase">
          No sign-up required
        </p>
      </div>
    </main>
  );
}
