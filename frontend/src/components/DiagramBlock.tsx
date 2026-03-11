"use client";

/**
 * DiagramBlock — renders a raw Mermaid diagram string as an inline SVG.
 *
 * • mermaid is imported dynamically (browser-only).
 * • mermaid.initialize() is called once outside the component function so it
 *   runs at most once per module load, not on every render.
 * • Each render gets a unique element ID to avoid collisions when multiple
 *   diagrams appear on the same page.
 */

import { useEffect, useRef, useState, useId } from "react";
import { Copy, Download, Check } from "lucide-react";

// ---------------------------------------------------------------------------
// One-time initialisation (outside component — runs once per module load)
// ---------------------------------------------------------------------------
let mermaidInitialised = false;

async function ensureMermaidInitialised() {
  if (mermaidInitialised) return;
  const mermaid = (await import("mermaid")).default;
  mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    themeVariables: {
      // Slate / indigo dark palette
      background: "#0f172a",
      primaryColor: "#1e293b",
      primaryTextColor: "#e2e8f0",
      primaryBorderColor: "#334155",
      lineColor: "#6366f1",
      secondaryColor: "#1e293b",
      tertiaryColor: "#0f172a",
      edgeLabelBackground: "#1e293b",
      clusterBkg: "#1e293b",
      clusterBorder: "#334155",
      titleColor: "#e2e8f0",
      nodeTextColor: "#e2e8f0",
      actorBkg: "#1e293b",
      actorBorder: "#6366f1",
      actorTextColor: "#e2e8f0",
      actorLineColor: "#6366f1",
      signalColor: "#a5b4fc",
      signalTextColor: "#e2e8f0",
      labelBoxBkgColor: "#1e293b",
      labelBoxBorderColor: "#334155",
      labelTextColor: "#e2e8f0",
      loopTextColor: "#e2e8f0",
      noteBorderColor: "#6366f1",
      noteBkgColor: "#1e293b",
      noteTextColor: "#e2e8f0",
    },
  });
  mermaidInitialised = true;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

interface DiagramBlockProps {
  /** Raw Mermaid source — no surrounding ``` fences. */
  code: string;
}

let diagramCounter = 0;

export default function DiagramBlock({ code }: DiagramBlockProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<string>("");
  const [renderError, setRenderError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Stable unique ID for this diagram instance (safe in SSR + concurrent mode)
  const reactId = useId();
  // Build a DOM-safe ID (no colons)
  const diagramId = `mermaid-diagram-${reactId.replace(/:/g, "")}`;

  // Render Mermaid → SVG
  useEffect(() => {
    let cancelled = false;

    async function render() {
      try {
        await ensureMermaidInitialised();
        const mermaid = (await import("mermaid")).default;

        const { svg } = await mermaid.render(diagramId, code);

        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
          svgRef.current = svg;
          setRenderError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setRenderError(err instanceof Error ? err.message : String(err));
        }
      }
    }

    render();
    return () => {
      cancelled = true;
    };
  }, [code, diagramId]);

  // -------------------------------------------------------------------------
  // Actions
  // -------------------------------------------------------------------------

  const handleCopySource = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API not available — silently ignore
    }
  };

  const handleDownloadSvg = () => {
    const svg = svgRef.current;
    if (!svg) return;
    const blob = new Blob([svg], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "diagram.svg";
    a.click();
    URL.revokeObjectURL(url);
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="relative rounded-xl border border-slate-700 bg-slate-900 p-4 overflow-x-auto my-4">
      {/* Action buttons — top-right */}
      <div className="absolute top-2 right-2 flex gap-1 z-10">
        <button
          onClick={handleCopySource}
          title="Copy Mermaid source"
          className="flex items-center gap-1 rounded-md bg-slate-800 px-2 py-1 text-xs text-slate-400 hover:text-slate-100 hover:bg-slate-700 transition-colors border border-slate-700"
        >
          {copied ? (
            <Check size={13} className="text-green-400" />
          ) : (
            <Copy size={13} />
          )}
          <span>{copied ? "Copied!" : "Copy source"}</span>
        </button>
        <button
          onClick={handleDownloadSvg}
          title="Download SVG"
          className="flex items-center gap-1 rounded-md bg-slate-800 px-2 py-1 text-xs text-slate-400 hover:text-slate-100 hover:bg-slate-700 transition-colors border border-slate-700"
        >
          <Download size={13} />
          <span>Download SVG</span>
        </button>
      </div>

      {/* Diagram container */}
      {renderError ? (
        <pre className="text-xs text-red-400 whitespace-pre-wrap font-mono">
          {`Failed to render diagram:\n${renderError}\n\nSource:\n${code}`}
        </pre>
      ) : (
        <div
          ref={containerRef}
          className="flex justify-center [&_svg]:max-w-full [&_svg]:h-auto"
        />
      )}
    </div>
  );
}
