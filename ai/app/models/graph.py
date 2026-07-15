"""
Graph-related response models for the Knowledge Graph visualization.
Shaped to work with react-force-graph / d3-force on the frontend.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class GraphNode(BaseModel):
    """A node in the knowledge graph (file or function)."""
    id: str
    label: str
    type: str  # "file" | "function" | "commit"
    path: Optional[str] = None
    language: Optional[str] = None
    complexity: float = 0.0
    churn: int = 0  # number of commits touching this node
    size: float = 1.0  # visual size hint


class GraphEdge(BaseModel):
    """An edge connecting two nodes."""
    source: str  # node id
    target: str  # node id
    type: str  # EdgeType value
    weight: float = 1.0
    label: Optional[str] = None


class GraphSlice(BaseModel):
    """A subgraph slice returned by the graph API."""
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    total_nodes: int = 0
    total_edges: int = 0
    depth: int = 1
