"use client";

import { useEffect, useState } from "react";
import { CommandLineIcon, ArrowPathIcon, ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import FileHealthBadge from "./FileHealthBadge";

interface DebtScore {
  path: string;
  language: string;
  churn: number;
  complexity: number;
  age_days: number;
  line_count: number;
  debt_score: number;
  risk_level: string;
}

interface HeatmapResponse {
  repo_id: string;
  scores: DebtScore[];
  average_debt: number;
  hotspot_count: number;
}

export default function HeatmapPanel({ repoId }: { repoId: string }) {
  const [data, setData] = useState<HeatmapResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<DebtScore | null>(null);

  const fetchHeatmap = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`http://localhost:8001/repos/${repoId}/heatmap`);
      if (!res.ok) throw new Error("Failed to load tech debt metrics");
      const json = await res.json();
      setData(json);
      if (json.scores.length > 0) {
        setSelectedFile(json.scores[0]);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load heatmap");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHeatmap();
  }, [repoId]);

  // Map risk levels to visual Tailwind colors
  const getRiskColors = (level: string) => {
    switch (level.toLowerCase()) {
      case "high":
        return { bg: "bg-red-500/10", border: "border-red-500/40", text: "text-red-400", blockBg: "#ef4444" };
      case "medium":
        return { bg: "bg-amber-500/10", border: "border-amber-500/40", text: "text-amber-400", blockBg: "#f59e0b" };
      default:
        return { bg: "bg-emerald-500/10", border: "border-emerald-500/30", text: "text-emerald-400", blockBg: "#10b981" };
    }
  };

  return (
    <div className="heatmap-panel-wrapper">
      <div className="panel-header-controls">
        <div className="title">
          <CommandLineIcon className="w-5 h-5 text-amber-400" />
          <span>Technical Debt Heatmap</span>
        </div>
        <button onClick={fetchHeatmap} className="btn-refresh" title="Reload metrics">
          <ArrowPathIcon className="w-4 h-4" />
        </button>
      </div>

      {loading ? (
        <div className="panel-loader">
          <div className="spinner" />
          <span>Profiling complexity and churn variables...</span>
        </div>
      ) : error ? (
        <div className="panel-error">
          <p>{error}</p>
          <button onClick={fetchHeatmap} className="primary-button btn-retry">
            Retry Connection
          </button>
        </div>
      ) : data ? (
        <div className="heatmap-grid-layout">
          {/* Summary stats */}
          <div className="heatmap-summary-row">
            <div className="summary-stat-box">
              <span className="label">Average Debt Score</span>
              <span className="value">{data.average_debt} / 100</span>
            </div>
            <div className="summary-stat-box warning">
              <span className="label">High-Risk Hotspots</span>
              <span className="value">{data.hotspot_count} files</span>
            </div>
          </div>

          <div className="heatmap-workspace-split">
            {/* Visual treemap-style blocks grid */}
            <div className="heatmap-treemap-blocks">
              {data.scores.map((score, index) => {
                const colors = getRiskColors(score.risk_level);
                // Compute block relative visual weight (scaled by lines of code)
                const relativeWidth = Math.max(10, Math.min(100, (score.line_count / 250) * 100));

                return (
                  <button
                    key={score.path}
                    onClick={() => setSelectedFile(score)}
                    className={`heatmap-block-item ${
                      selectedFile?.path === score.path ? "active" : ""
                    }`}
                    style={{
                      borderLeft: `4px solid ${colors.blockBg}`,
                      opacity: selectedFile?.path === score.path ? 1 : 0.85,
                    }}
                  >
                    <div className="block-meta">
                      <span className="block-title">{score.path.split("/").pop()}</span>
                      <span className="block-path">{score.path}</span>
                    </div>
                    <div className="block-metrics">
                      <span>{score.line_count} LOC</span>
                      <span style={{ color: colors.blockBg }} className="font-bold">
                        {score.debt_score.toFixed(1)}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Sidebar Details Panel */}
            {selectedFile && (
              <div className="heatmap-inspector-card">
                <div className="inspector-header">
                  <span className="small-caps">FILE PROFILE</span>
                  <h2>{selectedFile.path.split("/").pop()}</h2>
                  <span className="sub-path">{selectedFile.path}</span>
                  <div className="mt-3">
                    <FileHealthBadge repoId={repoId} path={selectedFile.path} showLabel={true} />
                  </div>
                </div>

                <div className="inspector-indicators">
                  {selectedFile.risk_level === "high" && (
                    <div className="alert-box-hotspot">
                      <ExclamationTriangleIcon className="w-5 h-5" />
                      <div>
                        <strong>High Risk Refactor Target</strong>
                        <p>High churn and high complexity make this module fragile.</p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="metric-bars-list">
                  <div className="metric-bar-group">
                    <div className="bar-header">
                      <span>Composite Debt Score</span>
                      <span className="font-bold">{selectedFile.debt_score.toFixed(1)}/100</span>
                    </div>
                    <div className="bar-track">
                      <div
                        className="bar-fill"
                        style={{
                          width: `${selectedFile.debt_score}%`,
                          backgroundColor: getRiskColors(selectedFile.risk_level).blockBg,
                        }}
                      />
                    </div>
                  </div>

                  <div className="metric-text-grid">
                    <div>
                      <span className="label">File Size</span>
                      <span className="value">{selectedFile.line_count} lines</span>
                    </div>
                    <div>
                      <span className="label">Complexity</span>
                      <span className="value">{selectedFile.complexity}/100</span>
                    </div>
                    <div>
                      <span className="label">Git Churn</span>
                      <span className="value">{selectedFile.churn} edits</span>
                    </div>
                    <div>
                      <span className="label">Last Touched</span>
                      <span className="value">{selectedFile.age_days} days ago</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
