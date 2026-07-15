"""
GET /repos/{repo_id}/graph — Knowledge Graph slice

Returns nodes (files/functions) and edges (calls/depends/modifies)
shaped for react-force-graph or d3-force on the frontend.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_data_provider
from app.mock.data_provider import DataProvider
from app.models.graph import GraphNode, GraphEdge, GraphSlice

router = APIRouter(prefix="/repos/{repo_id}", tags=["graph"])


def _file_id_to_label(file_id: str, files_map: dict) -> str:
    """Convert a file ID to a human-readable label."""
    if file_id in files_map:
        path = files_map[file_id].path
        return path.split("/")[-1]  # basename
    return file_id


@router.get("/graph", response_model=GraphSlice)
async def get_graph(
    repo_id: str,
    file: Optional[str] = Query(None, description="Filter by file path"),
    depth: int = Query(2, ge=1, le=5, description="Traversal depth"),
    data: DataProvider = Depends(get_data_provider),
):
    """
    Return a knowledge graph slice for the repository.
    Optionally filter by a specific file path and control traversal depth.
    """
    repo = await data.get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository '{repo_id}' not found")

    all_files = await data.get_files(repo_id)
    all_edges = await data.get_edges(repo_id)
    all_functions = await data.get_functions(repo_id)

    # Build a lookup map
    files_map = {f.id: f for f in all_files}
    functions_map = {fn.id: fn for fn in all_functions}

    # Determine which file IDs are in scope
    if file:
        seed_ids = {f.id for f in all_files if f.path == file}
        if not seed_ids:
            raise HTTPException(status_code=404, detail=f"File '{file}' not found")
    else:
        seed_ids = {f.id for f in all_files}

    # BFS traversal to collect connected nodes up to `depth`
    visited = set(seed_ids)
    frontier = set(seed_ids)

    for _ in range(depth):
        next_frontier = set()
        for edge in all_edges:
            if edge.source_id in frontier and edge.target_id not in visited:
                next_frontier.add(edge.target_id)
                visited.add(edge.target_id)
            if edge.target_id in frontier and edge.source_id not in visited:
                next_frontier.add(edge.source_id)
                visited.add(edge.source_id)
        frontier = next_frontier
        if not frontier:
            break

    # Build nodes
    nodes: list[GraphNode] = []

    for f in all_files:
        if f.id in visited:
            # Count how many commits touch this file (churn)
            churn = sum(
                1 for e in all_edges
                if e.source_id == f.id and e.edge_type.value == "MODIFIES"
            )
            nodes.append(GraphNode(
                id=f.id,
                label=f.path.split("/")[-1],
                type="file",
                path=f.path,
                language=f.language.value,
                complexity=f.complexity_score,
                churn=churn,
                size=max(1.0, f.line_count / 50),
            ))

    for fn in all_functions:
        if fn.file_id in visited:
            nodes.append(GraphNode(
                id=fn.id,
                label=fn.name,
                type="function",
                path=None,
                language=None,
                complexity=fn.complexity,
                churn=0,
                size=max(0.5, fn.complexity / 10),
            ))

    # Build edges (only between visited nodes)
    node_ids = {n.id for n in nodes}
    edges: list[GraphEdge] = []
    for e in all_edges:
        if e.source_id in node_ids and e.target_id in node_ids:
            edges.append(GraphEdge(
                source=e.source_id,
                target=e.target_id,
                type=e.edge_type.value,
                weight=e.weight,
                label=e.edge_type.value,
            ))

    # Also add file→function containment edges
    for fn in all_functions:
        if fn.id in node_ids and fn.file_id in node_ids:
            edges.append(GraphEdge(
                source=fn.file_id,
                target=fn.id,
                type="CONTAINS",
                weight=1.0,
                label="CONTAINS",
            ))

    return GraphSlice(
        nodes=nodes,
        edges=edges,
        total_nodes=len(nodes),
        total_edges=len(edges),
        depth=depth,
    )
