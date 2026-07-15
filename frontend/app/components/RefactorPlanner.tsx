"use client";

import { useState } from "react";
import { WrenchScrewdriverIcon, SparklesIcon, DocumentDuplicateIcon } from "@heroicons/react/24/outline";

export default function RefactorPlanner({ repoId }: { repoId: string }) {
  const [plan, setPlan] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generatePlan = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`http://localhost:8001/repos/${repoId}/refactor_plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ since_days: 30 })
      });
      
      if (!res.ok) throw new Error("Failed to generate refactor plan");
      const json = await res.json();
      setPlan(json.plan);
    } catch (err: any) {
      setError(err.message || "Failed to load refactor plan");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (plan) navigator.clipboard.writeText(plan);
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800">
      <div className="panel-header-controls p-4 border-b border-slate-800 flex justify-between items-center">
        <div className="title flex items-center gap-2">
          <WrenchScrewdriverIcon className="w-5 h-5 text-fuchsia-400" />
          <span className="font-semibold text-slate-200">Refactor Planner</span>
        </div>
        <button 
          onClick={generatePlan} 
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 bg-fuchsia-600 hover:bg-fuchsia-500 disabled:bg-slate-700 text-white rounded text-sm font-medium transition-colors"
        >
          {loading ? (
            <><div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" /> Analyzing...</>
          ) : (
            <><SparklesIcon className="w-4 h-4" /> Generate Plan</>
          )}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 text-slate-300">
        {!plan && !loading && !error && (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 gap-4">
            <WrenchScrewdriverIcon className="w-16 h-16 opacity-20" />
            <p>Click "Generate Plan" to synthesize recent refactoring trends into actionable steps.</p>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-4">
            <div className="w-8 h-8 border-4 border-slate-700 border-t-fuchsia-500 rounded-full animate-spin" />
            <p>The Architect is formulating a strategy...</p>
          </div>
        )}

        {error && (
          <div className="bg-rose-900/20 border border-rose-500/30 text-rose-400 p-4 rounded-lg">
            {error}
          </div>
        )}

        {plan && !loading && (
          <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-fuchsia-500 to-indigo-500" />
            <div className="flex justify-end p-2 bg-slate-800/80 border-b border-slate-700/50">
              <button onClick={copyToClipboard} className="text-slate-400 hover:text-white p-1.5 rounded bg-slate-700/50 hover:bg-slate-600 transition-colors" title="Copy to clipboard">
                <DocumentDuplicateIcon className="w-4 h-4" />
              </button>
            </div>
            <div className="p-6 prose prose-invert max-w-none prose-pre:bg-slate-900 prose-pre:border prose-pre:border-slate-700">
              <div dangerouslySetInnerHTML={{ __html: plan.replace(/\n/g, '<br />').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
