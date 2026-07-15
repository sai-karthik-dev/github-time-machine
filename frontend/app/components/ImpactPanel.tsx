"use client";

import { useEffect, useState } from "react";
import { ShieldCheckIcon, PlayIcon, ExclamationCircleIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";

interface AffectedFile {
  path: string;
  relationship: string;
  risk_level: string;
  reason: string;
}

interface ImpactResult {
  target: string;
  change_type: string;
  risk_score: number;
  affected_files: AffectedFile[];
  suggested_tests: string[];
  ai_explanation: string;
  total_affected: number;
}

interface BugOriginResult {
  file_path: string;
  culprit_commit_sha: string | null;
  ai_explanation: string;
}

export default function ImpactPanel({ repoId }: { repoId: string }) {
  const [fileList, setFileList] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState("");
  const [changeType, setChangeType] = useState("modify");
  const [loading, setLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImpactResult | null>(null);
  const [bugOriginResult, setBugOriginResult] = useState<BugOriginResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Populate dropdown list with files from graph or files route
  useEffect(() => {
    async function loadFiles() {
      try {
        const res = await fetch(`http://localhost:8001/repos/${repoId}/graph`);
        if (res.ok) {
          const json = await res.json();
          const files = json.nodes
            .filter((n: any) => n.type === "file")
            .map((n: any) => n.path || n.label);
          setFileList(files);
          if (files.length > 0) {
            setSelectedFile(files[0]);
          }
        }
      } catch (err) {
        // Fallback to static mock files list if server is not running
        setFileList([
          "src/auth/oauth.py",
          "src/auth/middleware.py",
          "src/services/billing_service.py",
          "src/models/billing.py",
          "src/api/routes.py",
          "src/main.py",
        ]);
        setSelectedFile("src/auth/oauth.py");
      }
    }
    loadFiles();
  }, [repoId]);

  const runSimulation = async () => {
    if (!selectedFile) return;
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      setBugOriginResult(null);

      const res = await fetch(`http://localhost:8001/repos/${repoId}/impact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: selectedFile,
          change_type: changeType,
          description: `Simulated architectural alteration of ${selectedFile} module.`,
        }),
      });

      if (!res.ok) throw new Error("Impact simulation failed");
      const json = await res.json();
      setResult(json);
    } catch (err: any) {
      setError(err.message || "Failed to simulate change");
    } finally {
      setLoading(false);
    }
  };

  const runBugOrigin = async () => {
    if (!selectedFile) return;
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      setBugOriginResult(null);

      const res = await fetch(`http://localhost:8001/repos/${repoId}/bug_origin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: selectedFile }),
      });

      if (!res.ok) throw new Error("Bug origin analysis failed");
      const json = await res.json();
      setBugOriginResult(json);
    } catch (err: any) {
      setError(err.message || "Failed to analyze bug origin");
    } finally {
      setLoading(false);
    }
  };

  const getRiskLabel = (score: number) => {
    if (score >= 0.75) return { text: "CRITICAL", color: "text-red-500", border: "border-red-500" };
    if (score >= 0.4) return { text: "MEDIUM", color: "text-amber-500", border: "border-amber-500" };
    return { text: "LOW", color: "text-emerald-500", border: "border-emerald-500" };
  };

  return (
    <div className="impact-panel-wrapper">
      <div className="panel-header-controls">
        <div className="title">
          <ShieldCheckIcon className="w-5 h-5 text-emerald-400" />
          <span>Change Impact Simulator</span>
        </div>
      </div>

      {/* Inputs Form Row */}
      <div className="impact-form-card">
        <div className="form-grid">
          <div className="form-group">
            <label className="label">Target Module / File</label>
            <select
              value={selectedFile}
              onChange={(e) => setSelectedFile(e.target.value)}
              className="select-field"
            >
              {fileList.map((file) => (
                <option key={file} value={file}>
                  {file}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="label">Simulation Change Type</label>
            <div className="radio-tabs">
              {(["modify", "remove", "refactor"] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setChangeType(type)}
                  className={`btn-radio-tab ${changeType === type ? "active" : ""}`}
                >
                  {type.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-4">
          <button
            onClick={runSimulation}
            disabled={loading || !selectedFile}
            className="primary-button btn-run-impact flex-1"
          >
            {loading ? (
              <>
                <div className="spinner-small" />
                <span>Working...</span>
              </>
            ) : (
              <>
                <PlayIcon className="w-4 h-4" />
                <span>Simulate Change Impact</span>
              </>
            )}
          </button>
          
          <button
            onClick={runBugOrigin}
            disabled={loading || !selectedFile}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 disabled:bg-slate-700 text-white rounded text-sm font-medium transition-colors flex-1"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                <span>Tracing...</span>
              </>
            ) : (
              <>
                <MagnifyingGlassIcon className="w-4 h-4" />
                <span>Trace Bug Origin</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Simulator Response Details */}
      {error && (
        <div className="panel-error mt-4">
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div className="impact-results-layout">
          {/* Column Left: Blast Radius List & Risk Score */}
          <div className="results-column-left">
            <div className="risk-score-card">
              <h3>Blast Radius Risk</h3>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-4xl font-bold font-mono">
                  {(result.risk_score * 100).toFixed(0)}%
                </span>
                <div
                  className={`badge-risk ${
                    getRiskLabel(result.risk_score).color
                  }`}
                >
                  {getRiskLabel(result.risk_score).text}
                </div>
              </div>
            </div>

            <div className="blast-radius-card">
              <h3>Affected Files ({result.total_affected})</h3>
              <div className="affected-list">
                {result.affected_files.length === 0 ? (
                  <p className="empty-text">No downstream files directly call this module.</p>
                ) : (
                  result.affected_files.map((file, idx) => (
                    <div key={idx} className="affected-item">
                      <div className="item-meta">
                        <span className="path">{file.path}</span>
                        <span className="badge-rel">{file.relationship}</span>
                      </div>
                      <p className="reason">{file.reason}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            {result.suggested_tests.length > 0 && (
              <div className="suggested-tests-card">
                <h3>Suggested Verification Tests</h3>
                <div className="tests-list">
                  {result.suggested_tests.map((test, idx) => (
                    <div key={idx} className="test-item">
                      <ExclamationCircleIcon className="w-4 h-4 text-sky-400" />
                      <span>{test}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Column Right: AI Architectural Explanation */}
          <div className="results-column-right">
            <div className="ai-narrative-card">
              <h3>AI Architectural Analysis</h3>
              <div className="ai-rich-text markdown-render">
                {result.ai_explanation.split("\n").map((line, idx) => {
                  if (line.startsWith("###")) {
                    return <h4 key={idx} className="md-h4">{line.replace("###", "")}</h4>;
                  }
                  if (line.startsWith("####")) {
                    return <h5 key={idx} className="md-h5">{line.replace("####", "")}</h5>;
                  }
                  if (line.startsWith("-") || line.startsWith("*")) {
                    return <li key={idx} className="md-li">{line.substring(1)}</li>;
                  }
                  if (line.trim() === "") {
                    return <div key={idx} className="h-2" />;
                  }
                  return <p key={idx} className="md-p">{line}</p>;
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {bugOriginResult && (
        <div className="impact-results-layout mt-6">
          <div className="results-column-left">
            <div className="risk-score-card border-rose-500/30 bg-rose-500/5">
              <h3 className="text-rose-400">Culprit Commit</h3>
              <div className="flex flex-col mt-2">
                {bugOriginResult.culprit_commit_sha ? (
                  <span className="text-2xl font-bold font-mono text-slate-200">
                    {bugOriginResult.culprit_commit_sha.substring(0, 7)}
                  </span>
                ) : (
                  <span className="text-lg font-medium text-slate-400">
                    Could not identify a single commit
                  </span>
                )}
                <span className="text-sm text-slate-400 mt-1">
                  Origin of bugs in <code className="text-slate-300">{bugOriginResult.file_path}</code>
                </span>
              </div>
            </div>
          </div>

          <div className="results-column-right">
            <div className="ai-narrative-card border-rose-500/20">
              <h3 className="text-rose-400">Root Cause Analysis</h3>
              <div className="ai-rich-text markdown-render">
                {bugOriginResult.ai_explanation.split("\n").map((line, idx) => {
                  if (line.startsWith("###")) {
                    return <h4 key={idx} className="md-h4">{line.replace("###", "")}</h4>;
                  }
                  if (line.startsWith("####")) {
                    return <h5 key={idx} className="md-h5">{line.replace("####", "")}</h5>;
                  }
                  if (line.startsWith("-") || line.startsWith("*")) {
                    return <li key={idx} className="md-li">{line.substring(1)}</li>;
                  }
                  if (line.trim() === "") {
                    return <div key={idx} className="h-2" />;
                  }
                  return <p key={idx} className="md-p">{line}</p>;
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
