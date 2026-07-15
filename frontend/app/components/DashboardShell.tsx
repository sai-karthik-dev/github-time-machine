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
  UserCircleIcon,
  WrenchScrewdriverIcon,
} from "@heroicons/react/24/outline";

interface Repository {
  id: string;
  name: string;
  full_name: string;
  description: string;
  default_branch: string;
  language: string;
  total_commits: number;
  total_files: number;
}

interface DashboardShellProps {
  repo: Repository | null;
  activeTab: "graph" | "timeline" | "heatmap" | "impact" | "chat" | "refactor";
  setActiveTab: (tab: "graph" | "timeline" | "heatmap" | "impact" | "chat" | "refactor") => void;
  loading: boolean;
  error: string | null;
  children: React.ReactNode;
}

export default function DashboardShell({
  repo,
  activeTab,
  setActiveTab,
  loading,
  error,
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
    <div className="dashboard-layout">
      {/* Sidebar Navigation */}
      <aside className="dashboard-sidebar">
        <div className="sidebar-top">
          <Link href="/" className="brand">
            <span className="brand-mark">⌁</span>
            GITHUB <em>TIME MACHINE</em>
          </Link>
          <div className="sidebar-repo-card">
            {loading ? (
              <div className="repo-loader">
                <span className="pulse-dot" /> Checking Repository...
              </div>
            ) : repo ? (
              <>
                <div className="repo-title">
                  <SparklesIcon className="w-4 h-4 text-emerald-400" />
                  <span>{repo.full_name}</span>
                </div>
                <div className="repo-meta-grid">
                  <div>
                    <span className="label">Branch</span>
                    <span className="value">{repo.default_branch}</span>
                  </div>
                  <div>
                    <span className="label">Commits</span>
                    <span className="value">{repo.total_commits}</span>
                  </div>
                </div>
              </>
            ) : (
              <div className="repo-error">No Repository Selected</div>
            )}
          </div>
        </div>

        <nav className="sidebar-nav">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`sidebar-nav-item ${active ? "active" : ""}`}
              >
                <Icon className="nav-icon" />
                <div className="nav-text">
                  <span className="nav-title">{tab.name}</span>
                  <span className="nav-desc">{tab.desc}</span>
                </div>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <Link href="/login" className="back-link">
            <ArrowLeftIcon className="w-4 h-4" />
            <span>Connect New Repo</span>
          </Link>
          <div className="service-status">
            <CloudIcon className="w-4 h-4 text-emerald-400" />
            <span>AI Backend: Active</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="dashboard-main">
        {/* Header */}
        <header className="dashboard-header">
          <div className="header-info">
            <h1>
              {tabs.find((t) => t.id === activeTab)?.name}
            </h1>
            <p className="header-sub">
              {tabs.find((t) => t.id === activeTab)?.desc}
            </p>
          </div>
          <div className="header-user">
            <UserCircleIcon className="w-8 h-8 text-slate-400" />
            <span>developer@octo-labs</span>
          </div>
        </header>

        {/* Content Body */}
        <main className="dashboard-body">
          {error ? (
            <div className="dashboard-error-pane">
              <h3>Error Loading Dashboard</h3>
              <p>{error}</p>
            </div>
          ) : (
            children
          )}
        </main>
      </div>
    </div>
  );
}
