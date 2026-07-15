"use client";

import { use, useEffect, useState } from "react";
import DashboardShell from "../../components/DashboardShell";
import GraphPanel from "../../components/GraphPanel";
import TimelinePanel from "../../components/TimelinePanel";
import HeatmapPanel from "../../components/HeatmapPanel";
import ImpactPanel from "../../components/ImpactPanel";
import ChatPanel from "../../components/ChatPanel";
import RefactorPlanner from "../../components/RefactorPlanner";

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

export default function RepoDashboard({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const repoId = resolvedParams.id;
  const [repo, setRepo] = useState<Repository | null>(null);
  const [activeTab, setActiveTab] = useState<"graph" | "timeline" | "heatmap" | "impact" | "chat" | "refactor">("chat");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRepo() {
      try {
        setLoading(true);
        // Call local FastAPI endpoint
        const response = await fetch(`http://localhost:8001/repos/${repoId}`);
        if (!response.ok) {
          throw new Error(`Failed to load repository '${repoId}'`);
        }
        const data = await response.json();
        setRepo(data);
      } catch (err: any) {
        // Fallback to mock representation if server is not fully reachable
        setRepo({
          id: "demo",
          name: "atlas",
          full_name: "octo-labs/atlas",
          description: "Internal platform API — handles auth, billing, and team management",
          default_branch: "main",
          language: "Python",
          total_commits: 52,
          total_files: 18,
        });
      } finally {
        setLoading(false);
      }
    }
    fetchRepo();
  }, [repoId]);

  return (
    <DashboardShell
      repo={repo}
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      loading={loading}
      error={error}
    >
      <div className="dashboard-content-panel">
        {activeTab === "graph" && <GraphPanel repoId={repoId} />}
        {activeTab === "timeline" && <TimelinePanel repoId={repoId} />}
        {activeTab === "heatmap" && <HeatmapPanel repoId={repoId} />}
        {activeTab === "impact" && <ImpactPanel repoId={repoId} />}
        {activeTab === "chat" && <ChatPanel repoId={repoId} />}
        {activeTab === "refactor" && <RefactorPlanner repoId={repoId} />}
      </div>
    </DashboardShell>
  );
}
