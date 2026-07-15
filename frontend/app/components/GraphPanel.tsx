"use client";

import { useEffect, useState, useMemo } from "react";
import { CubeTransparentIcon, ArrowPathIcon } from "@heroicons/react/24/outline";
import FileHealthBadge from "./FileHealthBadge";

interface GraphNode {
  id: string;
  label: string;
  type: string;
  path?: string;
  language?: string;
  complexity: number;
  churn: number;
  size: number;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
  weight: number;
  label?: string;
}

interface GraphSlice {
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_nodes: number;
  total_edges: number;
}

export default function GraphPanel({ repoId }: { repoId: string }) {
  const [data, setData] = useState<GraphSlice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [depth, setDepth] = useState(2);

  const fetchGraph = async () => {
    try {
      setLoading(true);
      setError(null);
      const url = `http://localhost:8001/repos/${repoId}/graph?depth=${depth}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to load dependency graph");
      const json = await res.json();
      setData(json);
      if (json.nodes.length > 0) {
        setSelectedNode(json.nodes[0]);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load graph");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, [repoId, depth]);

  // Position nodes mathematically in an SVG viewport (custom circle layout to look clean & ordered)
  const layout = useMemo(() => {
    if (!data) return { nodes: [], edges: [] };
    const width = 800;
    const height = 450;
    const cx = width / 2;
    const cy = height / 2;

    const files = data.nodes.filter((n) => n.type === "file");
    const functions = data.nodes.filter((n) => n.type === "function");

    const positions: Record<string, { x: number; y: number }> = {};

    // Position files in an outer circle
    const fileRadius = 180;
    files.forEach((file, index) => {
      const angle = (index / files.length) * 2 * Math.PI;
      positions[file.id] = {
        x: cx + fileRadius * Math.cos(angle),
        y: cy + fileRadius * Math.sin(angle),
      };
    });

    // Position functions in an inner circle relative to their parent file if possible, or scattered
    const functionRadius = 90;
    functions.forEach((fn, index) => {
      // Find parent file containment edge
      const containmentEdge = data.edges.find(
        (e) => e.target === fn.id && e.type === "CONTAINS"
      );
      if (containmentEdge && positions[containmentEdge.source]) {
        const parentPos = positions[containmentEdge.source];
        // Pull function nodes slightly inward from their parent file nodes
        const dx = cx - parentPos.x;
        const dy = cy - parentPos.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        positions[fn.id] = {
          x: parentPos.x + (dx / dist) * 55 + (Math.random() - 0.5) * 15,
          y: parentPos.y + (dy / dist) * 55 + (Math.random() - 0.5) * 15,
        };
      } else {
        const angle = (index / functions.length) * 2 * Math.PI;
        positions[fn.id] = {
          x: cx + functionRadius * Math.cos(angle),
          y: cy + functionRadius * Math.sin(angle),
        };
      }
    });

    const renderedNodes = data.nodes.map((node) => ({
      ...node,
      x: positions[node.id]?.x || cx + (Math.random() - 0.5) * 100,
      y: positions[node.id]?.y || cy + (Math.random() - 0.5) * 100,
    }));

    const renderedEdges = data.edges
      .map((edge) => {
        const start = positions[edge.source];
        const end = positions[edge.target];
        if (!start || !end) return null;
        return {
          ...edge,
          x1: start.x,
          y1: start.y,
          x2: end.x,
          y2: end.y,
        };
      })
      .filter((e) => e !== null) as Array<GraphEdge & { x1: number; y1: number; x2: number; y2: number }>;

    return { nodes: renderedNodes, edges: renderedEdges };
  }, [data]);

  return (
    <div className="graph-panel-wrapper">
      <div className="panel-header-controls">
        <div className="title">
          <CubeTransparentIcon className="w-5 h-5 text-sky-400" />
          <span>Interactive Code Graph</span>
        </div>
        <div className="controls">
          <div className="depth-selector">
            <span className="label">Traversal Depth:</span>
            {[1, 2, 3].map((d) => (
              <button
                key={d}
                onClick={() => setDepth(d)}
                className={`btn-toggle-small ${depth === d ? "active" : ""}`}
              >
                {d}
              </button>
            ))}
          </div>
          <button onClick={fetchGraph} className="btn-refresh" title="Reload graph">
            <ArrowPathIcon className="w-4 h-4" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="panel-loader">
          <div className="spinner" />
          <span>Traversing files & dependencies...</span>
        </div>
      ) : error ? (
        <div className="panel-error">
          <p>{error}</p>
          <button onClick={fetchGraph} className="primary-button btn-retry">
            Retry Connection
          </button>
        </div>
      ) : (
        <div className="graph-workspace-grid">
          {/* SVG Dependency Visualizer */}
          <div className="graph-canvas-container">
            <svg viewBox="0 0 800 450" className="dependency-svg-canvas">
              <defs>
                <marker
                  id="arrow"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M0,0 L10,5 L0,10 z" fill="#4b5d7d" />
                </marker>
                <filter id="glow-file" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              {/* Draw Edges */}
              {layout.edges.map((edge, index) => {
                const isSelected =
                  selectedNode &&
                  (edge.source === selectedNode.id || edge.target === selectedNode.id);
                return (
                  <line
                    key={`${edge.source}-${edge.target}-${index}`}
                    x1={edge.x1}
                    y1={edge.y1}
                    x2={edge.x2}
                    y2={edge.y2}
                    className={`graph-edge-path ${
                      edge.type === "CONTAINS" ? "contains-path" : ""
                    } ${isSelected ? "highlighted-edge" : ""}`}
                    markerEnd={edge.type !== "CONTAINS" ? "url(#arrow)" : undefined}
                    strokeDasharray={edge.type === "CONTAINS" ? "3,3" : undefined}
                  />
                );
              })}

              {/* Draw Nodes */}
              {layout.nodes.map((node) => {
                const isSelected = selectedNode?.id === node.id;
                const color = node.type === "file" ? "#0ea5e9" : "#a855f7"; // cyan for files, purple for functions
                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x},${node.y})`}
                    className="graph-node-group"
                    onClick={() => setSelectedNode(node)}
                  >
                    <circle
                      r={node.type === "file" ? 8 + node.size : 6}
                      fill={color}
                      className={`graph-node-circle ${isSelected ? "selected" : ""}`}
                      filter={isSelected ? "url(#glow-file)" : undefined}
                    />
                    <text
                      y={node.type === "file" ? -15 : 12}
                      className={`graph-node-text ${isSelected ? "selected-text" : ""}`}
                    >
                      {node.label}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Sidebar Inspector */}
          {selectedNode && (
            <div className="graph-inspector-panel">
              <div className="inspector-header">
                <span className="small-caps">{selectedNode.type.toUpperCase()}</span>
                <h2>{selectedNode.label}</h2>
                {selectedNode.type === "file" && selectedNode.path && (
                  <div className="mt-2">
                    <FileHealthBadge repoId={repoId} path={selectedNode.path} showLabel={true} />
                  </div>
                )}
              </div>
              <div className="inspector-metrics">
                <div className="metric-box">
                  <span className="label">Complexity</span>
                  <span className="value">{selectedNode.complexity}</span>
                </div>
                {selectedNode.type === "file" && (
                  <div className="metric-box">
                    <span className="label">Git Churn</span>
                    <span className="value">{selectedNode.churn} edits</span>
                  </div>
                )}
              </div>
              {selectedNode.path && (
                <div className="inspector-row">
                  <span className="label">Path</span>
                  <span className="value code-text">{selectedNode.path}</span>
                </div>
              )}
              {selectedNode.language && (
                <div className="inspector-row">
                  <span className="label">Language</span>
                  <span className="value">{selectedNode.language}</span>
                </div>
              )}
              <div className="inspector-relationships">
                <h3>Connections</h3>
                <div className="relationship-list">
                  {layout.edges
                    .filter((e) => e.source === selectedNode.id || e.target === selectedNode.id)
                    .map((edge, idx) => {
                      const otherNodeId =
                        edge.source === selectedNode.id ? edge.target : edge.source;
                      const otherNodeName =
                        layout.nodes.find((n) => n.id === otherNodeId)?.label || otherNodeId;
                      const isIncoming = edge.target === selectedNode.id;

                      return (
                        <div key={idx} className="relationship-item">
                          <span className="badge-relationship">{edge.type}</span>
                          <span>
                            {isIncoming ? "← from" : "→ to"}{" "}
                            <strong>{otherNodeName}</strong>
                          </span>
                        </div>
                      );
                    })}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
