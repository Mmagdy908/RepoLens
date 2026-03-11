"use client";

import { useState, useMemo } from "react";
import {
  ChevronRight,
  ChevronDown,
  Folder,
  FolderOpen,
  FileCode,
  FileText,
  File,
  FileJson,
  Image,
} from "lucide-react";
import type { FileNode } from "@/lib/types";

// ---------------------------------------------------------------------------
// Tree-building helpers
// ---------------------------------------------------------------------------

interface TreeFolder {
  kind: "folder";
  name: string;
  fullPath: string;
  children: TreeEntry[];
}

interface TreeFile {
  kind: "file";
  name: string;
  node: FileNode;
}

type TreeEntry = TreeFolder | TreeFile;

function buildTree(files: FileNode[]): TreeEntry[] {
  const root: TreeFolder = {
    kind: "folder",
    name: "",
    fullPath: "",
    children: [],
  };

  for (const file of files) {
    const parts = file.path.replace(/\\/g, "/").split("/");
    let current = root;

    for (let i = 0; i < parts.length - 1; i++) {
      const segment = parts[i];
      let child = current.children.find(
        (c): c is TreeFolder => c.kind === "folder" && c.name === segment
      );
      if (!child) {
        child = {
          kind: "folder",
          name: segment,
          fullPath: parts.slice(0, i + 1).join("/"),
          children: [],
        };
        current.children.push(child);
      }
      current = child;
    }

    current.children.push({
      kind: "file",
      name: parts[parts.length - 1],
      node: file,
    });
  }

  // Sort: folders first, then files; alphabetically within each group
  function sortEntries(entries: TreeEntry[]): TreeEntry[] {
    return entries
      .sort((a, b) => {
        if (a.kind !== b.kind) return a.kind === "folder" ? -1 : 1;
        return a.name.localeCompare(b.name);
      })
      .map((e) =>
        e.kind === "folder" ? { ...e, children: sortEntries(e.children) } : e
      );
  }

  return sortEntries(root.children);
}

// ---------------------------------------------------------------------------
// File-type icon helper
// ---------------------------------------------------------------------------

const CODE_EXTS = new Set([
  "ts",
  "tsx",
  "js",
  "jsx",
  "py",
  "go",
  "rs",
  "java",
  "c",
  "cpp",
  "h",
  "cs",
  "rb",
  "php",
  "swift",
  "kt",
  "scala",
  "sh",
  "bash",
  "zsh",
]);
const DOC_EXTS = new Set(["md", "mdx", "txt", "rst", "adoc"]);
const IMG_EXTS = new Set(["png", "jpg", "jpeg", "gif", "svg", "webp", "ico"]);

function FileIcon({ name, isBinary }: { name: string; isBinary: boolean }) {
  const ext = name.split(".").pop()?.toLowerCase() ?? "";
  const cls = "shrink-0 text-slate-400";

  if (isBinary && IMG_EXTS.has(ext)) return <Image size={13} className={cls} />;
  if (ext === "json" || ext === "yaml" || ext === "yml" || ext === "toml")
    return <FileJson size={13} className={cls} />;
  if (CODE_EXTS.has(ext))
    return <FileCode size={13} className="shrink-0 text-indigo-400" />;
  if (DOC_EXTS.has(ext))
    return <FileText size={13} className="shrink-0 text-slate-300" />;
  return <File size={13} className={cls} />;
}

// ---------------------------------------------------------------------------
// Recursive tree node components
// ---------------------------------------------------------------------------

interface FolderNodeProps {
  entry: TreeFolder;
  depth: number;
  onFileClick: (path: string) => void;
}

function FolderNode({ entry, depth, onFileClick }: FolderNodeProps) {
  const [open, setOpen] = useState(depth < 2);

  return (
    <li>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-1.5 rounded px-1 py-0.5 text-left text-xs text-slate-300 hover:bg-slate-700/60"
        style={{ paddingLeft: `${depth * 12 + 4}px` }}
      >
        {open ? (
          <ChevronDown size={12} className="shrink-0 text-slate-400" />
        ) : (
          <ChevronRight size={12} className="shrink-0 text-slate-400" />
        )}
        {open ? (
          <FolderOpen size={13} className="shrink-0 text-yellow-400/80" />
        ) : (
          <Folder size={13} className="shrink-0 text-yellow-400/80" />
        )}
        <span className="truncate">{entry.name}</span>
      </button>

      {open && entry.children.length > 0 && (
        <ul>
          {entry.children.map((child) =>
            child.kind === "folder" ? (
              <FolderNode
                key={child.fullPath}
                entry={child}
                depth={depth + 1}
                onFileClick={onFileClick}
              />
            ) : (
              <FileNodeItem
                key={child.node.path}
                entry={child}
                depth={depth + 1}
                onFileClick={onFileClick}
              />
            )
          )}
        </ul>
      )}
    </li>
  );
}

interface FileNodeItemProps {
  entry: TreeFile;
  depth: number;
  onFileClick: (path: string) => void;
}

function FileNodeItem({ entry, depth, onFileClick }: FileNodeItemProps) {
  return (
    <li>
      <button
        onClick={() => onFileClick(entry.node.path)}
        title={entry.node.path}
        className="flex w-full items-center gap-1.5 rounded px-1 py-0.5 text-left text-xs text-slate-400 hover:bg-slate-700/60 hover:text-slate-200"
        style={{ paddingLeft: `${depth * 12 + 4 + 14}px` }}
      >
        <FileIcon name={entry.name} isBinary={entry.node.is_binary} />
        <span className="truncate">{entry.name}</span>
      </button>
    </li>
  );
}

// ---------------------------------------------------------------------------
// Public component
// ---------------------------------------------------------------------------

interface FileExplorerProps {
  files: FileNode[];
  onFileClick: (message: string) => void;
}

export default function FileExplorer({
  files,
  onFileClick,
}: FileExplorerProps) {
  const tree = useMemo(() => buildTree(files), [files]);

  if (files.length === 0) {
    return (
      <p className="px-3 py-4 text-xs text-slate-500 italic">
        No files ingested yet.
      </p>
    );
  }

  return (
    <nav aria-label="File explorer" className="overflow-y-auto">
      <ul className="space-y-0.5 py-1">
        {tree.map((entry) =>
          entry.kind === "folder" ? (
            <FolderNode
              key={entry.fullPath}
              entry={entry}
              depth={0}
              onFileClick={(path) => onFileClick(`Explain this file: ${path}`)}
            />
          ) : (
            <FileNodeItem
              key={entry.node.path}
              entry={entry}
              depth={0}
              onFileClick={(path) => onFileClick(`Explain this file: ${path}`)}
            />
          )
        )}
      </ul>
    </nav>
  );
}
