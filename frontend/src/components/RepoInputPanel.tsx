"use client";

import { useRef, useState } from "react";
import { Upload, Link, Loader2 } from "lucide-react";
import { ingestRepo, ingestZip } from "@/lib/api";
import type { IngestResponse } from "@/lib/types";
import TokenUsageBar from "@/components/TokenUsageBar";

interface RepoInputPanelProps {
  onIngested: (result: IngestResponse) => void;
}

export default function RepoInputPanel({ onIngested }: RepoInputPanelProps) {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IngestResponse | null>(null);
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleUrlSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!url.trim() || loading) return;
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await ingestRepo(url.trim(), setStatus);
      setResult(data);
      onIngested(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingestion failed.");
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleZipFile(file: File) {
    if (loading) return;
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await ingestZip(file, setStatus);
      setResult(data);
      onIngested(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }

  function handleFileInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleZipFile(file);
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    setDragging(true);
  }

  function handleDragLeave() {
    setDragging(false);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleZipFile(file);
  }

  return (
    <div className="w-full space-y-4 rounded-xl border border-slate-700 bg-slate-800/60 p-5 backdrop-blur">
      {/* URL input */}
      <form onSubmit={handleUrlSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <Link
            size={15}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
            disabled={loading}
            className="w-full rounded-lg border border-slate-600 bg-slate-900 py-2 pl-9 pr-3 text-sm text-slate-100 placeholder-slate-500 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="flex min-w-[100px] items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 size={14} className="animate-spin" />
              <span>Analyzing…</span>
            </>
          ) : (
            "Analyze"
          )}
        </button>
      </form>

      {/* Zip drag-and-drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !loading && fileInputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center gap-1.5 rounded-lg border-2 border-dashed px-4 py-5 text-sm transition ${
          dragging
            ? "border-indigo-400 bg-indigo-950/40 text-indigo-300"
            : "border-slate-600 text-slate-400 hover:border-slate-500 hover:text-slate-300"
        } ${loading ? "pointer-events-none opacity-50" : ""}`}
      >
        <Upload size={18} />
        <span>
          Drop a <strong>.zip</strong> archive here, or click to browse
        </span>
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip"
          className="hidden"
          onChange={handleFileInputChange}
        />
      </div>

      {/* Status line shown while loading */}
      {loading && status && (
        <p className="flex items-center gap-2 text-xs text-slate-400">
          <Loader2 size={12} className="animate-spin" />
          {status}
        </p>
      )}

      {/* Error message */}
      {error && (
        <p className="rounded-lg border border-red-700 bg-red-950/40 px-3 py-2 text-xs text-red-400">
          {error}
        </p>
      )}

      {/* Token usage bar shown after successful ingestion */}
      {result && !loading && (
        <TokenUsageBar used={result.token_count} budget={result.token_budget} />
      )}
    </div>
  );
}
