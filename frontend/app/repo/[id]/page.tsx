"use client";

import { use, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
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
  owner: string;
  full_name?: string;
  description?: string;
  default_branch?: string;
  language?: string;
  total_commits?: number;
  total_files?: number;
  status?: string;
  github_url?: string;
  files_indexed?: number;
  commits_analyzed?: number;
}

export default function RepoDashboard({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const repoId = resolvedParams.id;
  const router = useRouter();
  const [repo, setRepo] = useState<Repository | null>(null);
  const [repos, setRepos] = useState<Repository[]>([]);
  const [activeTab, setActiveTab] = useState<"graph" | "timeline" | "heatmap" | "impact" | "chat" | "refactor">("chat");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addingRepo, setAddingRepo] = useState(false);
  const [newUrl, setNewUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://github-time-machine-production.up.railway.app";

  const fetchRepos = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/repositories/`);
      if (res.ok) {
        const data = await res.json();
        if (data.repositories) setRepos(data.repositories);
      }
    } catch {}
  }, [API_URL]);

  useEffect(() => { fetchRepos(); }, [fetchRepos]);

  useEffect(() => {
    async function fetchRepo() {
      try {
        setLoading(true); setError(null);
        const response = await fetch(`${API_URL}/repositories/${repoId}`);
        if (!response.ok) throw new Error(`Repository '${repoId}' not found`);
        setRepo(await response.json());
      } catch {
        setError("Failed to load repository");
      } finally { setLoading(false); }
    }
    fetchRepo();
  }, [repoId, API_URL]);

  const handleSubmitRepo = async () => {
    if (!newUrl.trim() || submitting) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${API_URL}/repositories/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ github_url: newUrl.trim() }),
      });
      if (res.status === 409) {
        // Repo already exists — find it in the list and navigate
        const listRes = await fetch(`${API_URL}/repositories/`);
        if (listRes.ok) {
          const listData = await listRes.json();
          const existing = (listData.repositories || []).find(
            (r: any) => r.github_url === newUrl.trim()
          );
          if (existing) {
            setNewUrl(""); setAddingRepo(false); await fetchRepos();
            router.push(`/repo/${existing.id}`);
            return;
          }
        }
        throw new Error("Repository already submitted. Refreshing list...");
      }
      if (!res.ok) throw new Error("Failed to submit");
      const created = await res.json();
      setNewUrl("");
      setAddingRepo(false);
      await fetchRepos();
      router.push(`/repo/${created.id}`);
    } catch (e: any) {
      alert(e.message || "Failed to add repository");
    } finally { setSubmitting(false); }
  };

  const handleSelectRepo = (id: string) => {
    router.push(`/repo/${id}`);
  };

  return (
    <DashboardShell
      repo={repo}
      repos={repos}
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      loading={loading}
      error={error}
      addingRepo={addingRepo}
      setAddingRepo={setAddingRepo}
      newUrl={newUrl}
      setNewUrl={setNewUrl}
      submitting={submitting}
      onSubmitRepo={handleSubmitRepo}
      onSelectRepo={handleSelectRepo}
    >
      <div className="h-full">
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
