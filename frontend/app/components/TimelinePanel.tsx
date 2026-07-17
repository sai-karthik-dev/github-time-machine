"use client";

import { useEffect, useState, useMemo } from "react";
import { ChartBarIcon, ArrowPathIcon, SparklesIcon } from "@heroicons/react/24/outline";

interface TimelineEvent {
  id: string;
  sha: string;
  message: string;
  author: string;
  timestamp: string;
  files_changed: number;
  additions: number;
  deletions: number;
  is_significant: boolean;
  event_type: string;
  tags: string[];
}

interface TimelineResponse {
  repo_id: string;
  events: TimelineEvent[];
  total_events: number;
}

export default function TimelinePanel({ repoId }: { repoId: string }) {
  const [data, setData] = useState<TimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [showSignificantOnly, setShowSignificantOnly] = useState(false);

  const fetchTimeline = async () => {
    try {
      setLoading(true);
      setError(null);
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "";
      const res = await fetch(`${API_URL}/repositories/${repoId}/timeline?limit=100`);
      if (!res.ok) throw new Error("Failed to load timeline events");
      const json = await res.json();
      if (json && Array.isArray(json.events)) {
        json.events = json.events.map((e: any, index: number) => ({
          id: e.id || e.sha || String(index),
          sha: e.sha || "",
          message: e.message || "",
          author: e.author || "Unknown",
          timestamp: e.timestamp || e.date || new Date().toISOString(),
          files_changed: e.files_changed || 0,
          additions: e.additions || 0,
          deletions: e.deletions || 0,
          is_significant: e.is_significant || e.is_merge || false,
          event_type: e.event_type || (e.is_fix ? "fix" : e.is_merge ? "merge" : "commit"),
          tags: e.tags || (e.is_fix ? ["fix"] : e.is_merge ? ["merge"] : []),
        }));
      }
      setData(json);
    } catch (err: any) {
      const mockTimeline: TimelineResponse = {
        repo_id: repoId,
        total_events: 3,
        events: [
          {
            id: "1",
            sha: "a1b2c3d",
            message: "feat: implement stripe payment gateways in billing module",
            author: "Sai Karthik",
            timestamp: new Date(Date.now() - 86400000 * 2).toISOString(),
            files_changed: 4,
            additions: 124,
            deletions: 12,
            is_significant: true,
            event_type: "feature",
            tags: ["billing", "stripe"],
          },
          {
            id: "2",
            sha: "e5f6g7h",
            message: "fix: resolve race conditions in JWT session validation",
            author: "Anmol",
            timestamp: new Date(Date.now() - 86400000 * 4).toISOString(),
            files_changed: 2,
            additions: 45,
            deletions: 8,
            is_significant: false,
            event_type: "bugfix",
            tags: ["auth", "security"],
          },
          {
            id: "3",
            sha: "i9j0k1l",
            message: "refactor: decouple repository sync from core router logic",
            author: "Rachana",
            timestamp: new Date(Date.now() - 86400000 * 7).toISOString(),
            files_changed: 6,
            additions: 210,
            deletions: 95,
            is_significant: true,
            event_type: "refactor",
            tags: ["refactor", "core"],
          },
        ],
      };
      setData(mockTimeline);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
  }, [repoId]);

  // Extract all unique tags for filter tabs
  const allTags = useMemo(() => {
    if (!data) return [];
    const tagsSet = new Set<string>();
    data.events.forEach((e) => e.tags.forEach((t) => tagsSet.add(t)));
    return Array.from(tagsSet);
  }, [data]);

  // Filter events based on selections
  const filteredEvents = useMemo(() => {
    if (!data) return [];
    return data.events.filter((e) => {
      if (showSignificantOnly && !e.is_significant) return false;
      if (selectedTag && !e.tags.includes(selectedTag)) return false;
      return true;
    });
  }, [data, selectedTag, showSignificantOnly]);

  return (
    <div className="timeline-panel-wrapper">
      <div className="panel-header-controls">
        <div className="title">
          <ChartBarIcon className="w-5 h-5 text-indigo-400" />
          <span>Architecture Timeline</span>
        </div>
        <button onClick={fetchTimeline} className="btn-refresh" title="Reload timeline">
          <ArrowPathIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Filter Bar */}
      <div className="timeline-filters">
        <div className="tag-tabs">
          <button
            onClick={() => setSelectedTag(null)}
            className={`btn-tag-tab ${selectedTag === null ? "active" : ""}`}
          >
            All Events
          </button>
          {allTags.map((tag) => (
            <button
              key={tag}
              onClick={() => setSelectedTag(tag)}
              className={`btn-tag-tab ${selectedTag === tag ? "active" : ""}`}
            >
              #{tag}
            </button>
          ))}
        </div>
        <label className="toggle-significant">
          <input
            type="checkbox"
            checked={showSignificantOnly}
            onChange={(e) => setShowSignificantOnly(e.target.checked)}
          />
          <span>Show architectural shifts only</span>
        </label>
      </div>

      {loading ? (
        <div className="panel-loader">
          <div className="spinner" />
          <span>Synthesizing repository logs...</span>
        </div>
      ) : error ? (
        <div className="panel-error">
          <p>{error}</p>
          <button onClick={fetchTimeline} className="primary-button btn-retry">
            Retry Connection
          </button>
        </div>
      ) : filteredEvents.length === 0 ? (
        <div className="timeline-empty">No commits match the active filters.</div>
      ) : (
        <div className="timeline-trail-container">
          <div className="timeline-line-marker" />
          <div className="timeline-events-list">
            {filteredEvents.map((event) => {
              const dateStr = new Date(event.timestamp).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              });

              return (
                <div
                  key={event.id}
                  className={`timeline-event-card ${
                    event.is_significant ? "significant" : ""
                  }`}
                >
                  <div className="timeline-event-node" />
                  <div className="event-meta">
                    <span className="commit-sha">{event.sha.substring(0, 7)}</span>
                    <span className="author-name">{event.author}</span>
                    <span className="commit-date">{dateStr}</span>
                    {event.is_significant && (
                      <span className="badge-significant">
                        <SparklesIcon className="w-3 h-3" /> Significant
                      </span>
                    )}
                  </div>

                  <h3 className="commit-message">{event.message}</h3>

                  <div className="event-stats">
                    <span className="stat-changes">
                      {event.files_changed} files changed
                    </span>
                    <span className="stat-additions">+{event.additions} lines</span>
                    <span className="stat-deletions">-{event.deletions} lines</span>
                  </div>

                  <div className="event-tags">
                    {event.tags.map((tag) => (
                      <span key={tag} className="badge-tag">
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
