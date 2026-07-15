"use client";

import { useEffect, useState } from "react";

export interface FileHealthScore {
  file_path: string;
  complexity_score: number;
  churn_score: number;
  debt_score: number;
  health_status: "good" | "moderate" | "poor";
}

export default function FileHealthBadge({ repoId, path, showLabel = false }: { repoId: string; path: string; showLabel?: boolean }) {
  const [health, setHealth] = useState<FileHealthScore | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    if (!path) return;
    
    const fetchHealth = async () => {
      setLoading(true);
      try {
        const url = `http://localhost:8001/repos/${repoId}/file_health?path=${encodeURIComponent(path)}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to load health");
        const json = await res.json();
        if (mounted) setHealth(json);
      } catch (err) {
        console.error("Health badge error:", err);
      } finally {
        if (mounted) setLoading(false);
      }
    };
    
    fetchHealth();
    return () => { mounted = false; };
  }, [repoId, path]);

  if (loading || !health) return <div className="h-4 w-4 rounded-full bg-slate-700 animate-pulse inline-block" />;

  const colors = {
    good: "bg-emerald-500",
    moderate: "bg-amber-500",
    poor: "bg-rose-500"
  };

  return (
    <div className="inline-flex items-center gap-1.5" title={`Complexity: ${(health.complexity_score*100).toFixed(0)}%, Churn: ${(health.churn_score*100).toFixed(0)}%, Debt: ${(health.debt_score*100).toFixed(0)}%`}>
      <div className={`h-3 w-3 rounded-full ${colors[health.health_status] || "bg-slate-500"} shadow-sm`} />
      {showLabel && <span className="text-xs text-slate-300 font-medium capitalize">{health.health_status} Health</span>}
    </div>
  );
}
