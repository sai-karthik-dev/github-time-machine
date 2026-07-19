"use client";

import React from "react";
import Link from "next/link";
import {
  CubeTransparentIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  CommandLineIcon,
  ChatBubbleLeftRightIcon,
  ArrowLeftIcon,
  SparklesIcon,
  CloudIcon,
  WrenchScrewdriverIcon,
  PlusIcon,
  FolderIcon,
} from "@heroicons/react/24/outline";

interface Repository {
  id: string;
  name: string;
  owner: string;
  full_name?: string;
  description?: string;
  default_branch?: string;
  language?: string;
  total_commits?: number;
  total_files?: number;
  status?: string;
  files_indexed?: number;
  commits_analyzed?: number;
}

interface DashboardShellProps {
  repo: Repository | null;
  repos: Repository[];
  activeTab: "graph" | "timeline" | "heatmap" | "impact" | "chat" | "refactor";
  setActiveTab: (tab: "graph" | "timeline" | "heatmap" | "impact" | "chat" | "refactor") => void;
  loading: boolean;
  error: string | null;
  addingRepo: boolean;
  setAddingRepo: (v: boolean) => void;
  newUrl: string;
  setNewUrl: (v: string) => void;
  submitting: boolean;
  onSubmitRepo: () => void;
  onSelectRepo: (id: string) => void;
  children: React.ReactNode;
}

export default function DashboardShell({
  repo, repos, activeTab, setActiveTab, loading, error,
  addingRepo, setAddingRepo, newUrl, setNewUrl, submitting, onSubmitRepo, onSelectRepo,
  children,
}: DashboardShellProps) {
  const tabs = [
    { id: "chat", name: "Architect's Memory", icon: ChatBubbleLeftRightIcon, desc: "AI architectural assistant" },
    { id: "graph", name: "Software DNA", icon: CubeTransparentIcon, desc: "Visual dependency graph" },
    { id: "timeline", name: "Architecture Timeline", icon: ChartBarIcon, desc: "Commit evolution scrub" },
    { id: "heatmap", name: "Technical Debt", icon: CommandLineIcon, desc: "Complexity hotspot maps" },
    { id: "impact", name: "Change Intelligence", icon: ShieldCheckIcon, desc: "Blast radius simulator" },
    { id: "refactor", name: "Refactor Planner", icon: WrenchScrewdriverIcon, desc: "Actionable refactoring steps" },
  ] as const;

  return (
    <div className="flex h-screen bg-[#0A0A0B] text-white/90 font-sans antialiased selection:bg-white selection:text-black">
      {/* Sidebar */}
      <aside className="w-72 flex-shrink-0 flex flex-col border-r border-white/[0.06] bg-[#0A0A0B]/80 backdrop-blur-sm">
        {/* Brand */}
        <div className="px-5 py-6 border-b border-white/[0.06]">
          <Link href="/" className="flex items-center gap-2 group">
            <span className="flex items-center justify-center w-7 h-7 border border-white/10 rounded text-base text-white/80 group-hover:border-white/30 transition-colors">⌁</span>
            <span className="font-mono text-[10px] font-bold tracking-[0.2em] text-white/70">
              GITHUB <span className="text-white/30 font-light">TIME MACHINE</span>
            </span>
          </Link>

          {/* Current repo card */}
          <div className="mt-5 p-3 rounded-lg border border-white/[0.04] bg-white/[0.02]">
            {loading ? (
              <div className="flex items-center gap-2 text-xs text-white/40">
                <span className="w-2 h-2 rounded-full bg-emerald-400/60 animate-pulse" />
                Loading...
              </div>
            ) : repo ? (
              <>
                <div className="flex items-center gap-2 mb-2">
                  <SparklesIcon className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-xs font-medium text-white/80 truncate">
                    {repo.owner && repo.name ? `${repo.owner}/${repo.name}` : repo.full_name || repo.name || repo.id?.slice(0, 8)}
                  </span>
                </div>
                <div className="flex gap-3 text-[10px] font-mono text-white/40">
                  <span>{repo.files_indexed ?? repo.total_files ?? 0} files</span>
                  <span>{repo.commits_analyzed ?? repo.total_commits ?? 0} commits</span>
                  {repo.status && <span className={repo.status === "completed" ? "text-emerald-400/60" : repo.status === "error" ? "text-red-400/60" : "text-amber-400/60"}>{repo.status}</span>}
                </div>
              </>
            ) : error ? (
              <div className="text-xs text-red-400/60">{error}</div>
            ) : null}
          </div>
        </div>

        {/* Repo selector */}
        <div className="px-5 py-3 border-b border-white/[0.06]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] text-white/20 font-mono tracking-widest">REPOSITORIES</span>
            <button
              onClick={() => setAddingRepo(!addingRepo)}
              className="p-1 rounded border border-white/[0.08] text-white/30 hover:text-white/60 hover:border-white/20 transition-all"
            >
              <PlusIcon className="w-3 h-3" />
            </button>
          </div>

          {addingRepo && (
            <div className="mb-2 p-2 rounded border border-emerald-400/20 bg-emerald-400/[0.03]">
              <input
                type="text"
                value={newUrl}
                onChange={e => setNewUrl(e.target.value)}
                onKeyDown={e => e.key === "Enter" && onSubmitRepo()}
                placeholder="https://github.com/user/repo"
                className="w-full bg-white/[0.03] border border-white/[0.06] rounded px-2 py-1.5 text-[10px] text-white/60 font-mono placeholder-white/15 focus:outline-none focus:border-emerald-400/30 mb-2"
              />
              <button
                onClick={onSubmitRepo}
                disabled={submitting || !newUrl.trim()}
                className="w-full py-1 rounded border border-emerald-400/20 bg-emerald-400/[0.08] text-[10px] text-emerald-400/80 font-mono tracking-wider hover:bg-emerald-400/[0.15] disabled:opacity-30 disabled:cursor-not-allowed transition-all"
              >
                {submitting ? "ANALYZING..." : "ANALYZE REPO"}
              </button>
            </div>
          )}

          <div className="max-h-32 overflow-y-auto space-y-0.5">
            {repos.map((r) => (
              <button
                key={r.id}
                onClick={() => onSelectRepo(r.id)}
                className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-left transition-all ${
                  repo?.id === r.id
                    ? "bg-emerald-400/[0.06] border border-emerald-400/15"
                    : "hover:bg-white/[0.02] border border-transparent"
                }`}
              >
                <FolderIcon className={`w-3 h-3 flex-shrink-0 ${repo?.id === r.id ? "text-emerald-400/60" : "text-white/15"}`} />
                <div className="min-w-0">
                  <div className="text-[10px] text-white/60 font-mono truncate">
                    {r.owner}/{r.name}
                  </div>
                  {r.status && (
                    <div className={`text-[8px] font-mono ${r.status === "completed" ? "text-emerald-400/50" : r.status === "error" ? "text-red-400/50" : "text-amber-400/50"}`}>
                      {r.status === "completed" ? "READY" : r.status.toUpperCase()}
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-3 px-3 space-y-0.5 overflow-y-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-left transition-all duration-150 group ${
                  active
                    ? "bg-white/[0.06] text-white border border-white/[0.08]"
                    : "text-white/40 hover:text-white/70 hover:bg-white/[0.02] border border-transparent"
                }`}
              >
                <Icon className={`w-4 h-4 flex-shrink-0 ${active ? "text-emerald-400" : "text-white/20 group-hover:text-white/40"}`} />
                <div className="min-w-0">
                  <div className="text-xs font-medium truncate">{tab.name}</div>
                  <div className="text-[10px] text-white/20 mt-0.5 font-mono tracking-wider truncate">{tab.desc}</div>
                </div>
              </button>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-white/[0.06] space-y-2">
          <Link href="/login" className="flex items-center gap-2 text-[11px] text-white/40 hover:text-white/70 transition-colors font-mono tracking-wider">
            <ArrowLeftIcon className="w-3.5 h-3.5" />
            CONNECT NEW REPO
          </Link>
          <div className="flex items-center gap-2 text-[10px] text-emerald-400/60 font-mono">
            <CloudIcon className="w-3 h-3" />
            AI BACKEND: ACTIVE
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center justify-between px-8 py-4 border-b border-white/[0.06] bg-[#0A0A0B]/60 backdrop-blur-sm">
          <div>
            <h1 className="text-sm font-medium text-white/80 font-mono tracking-wider">
              {tabs.find((t) => t.id === activeTab)?.name}
            </h1>
            <p className="text-[10px] text-white/30 mt-0.5 font-mono tracking-widest">
              {tabs.find((t) => t.id === activeTab)?.desc}
            </p>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-white/30 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400/80" />
            live · {repo?.language || repo?.owner ? `${repo?.owner || "?"}/${repo?.name || "?"}` : "—"}
          </div>
        </header>

        <main className="flex-1 overflow-auto p-6">
          {error && !repo ? (
            <div className="flex flex-col items-center justify-center h-full text-center gap-3">
              <span className="text-2xl">⌁</span>
              <p className="text-sm text-red-400/60 font-mono">{error}</p>
              <p className="text-xs text-white/20 font-mono">Select a repository from the sidebar or add a new one</p>
            </div>
          ) : (
            children
          )}
        </main>
      </div>
    </div>
  );
}
