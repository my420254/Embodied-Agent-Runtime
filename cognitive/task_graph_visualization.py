from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from typing import Any

from interfaces.contracts import TaskGraph, TaskGraphEdge, TaskGraphNode


@dataclass(frozen=True)
class TaskGraphVisualization:
    """Debug-friendly TaskGraph view for traces and architecture reviews."""

    task_graph_id: str
    goal: str
    stats: dict[str, int]
    policy: dict[str, Any]
    nodes: tuple[dict[str, Any], ...]
    edges: tuple[dict[str, Any], ...]
    missing_facts: tuple[str, ...]
    mermaid: str
    graphviz_dot: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "format": "task_graph_visualization.v1",
            "task_graph_id": self.task_graph_id,
            "goal": self.goal,
            "stats": dict(self.stats),
            "policy": dict(self.policy),
            "nodes": [dict(node) for node in self.nodes],
            "edges": [dict(edge) for edge in self.edges],
            "missing_facts": list(self.missing_facts),
            "mermaid": self.mermaid,
            "graphviz_dot": self.graphviz_dot,
        }


def visualize_task_graph(graph: TaskGraph, *, include_data: bool = False) -> TaskGraphVisualization:
    """Build a compact JSON view plus Mermaid and GraphViz render strings."""

    return TaskGraphVisualization(
        task_graph_id=graph.task_graph_id,
        goal=graph.goal,
        stats={
            "nodes": len(graph.nodes),
            "edges": len(graph.edges),
            "missing_facts": len(graph.missing_facts),
        },
        policy={
            "max_hops": graph.max_hops,
            "node_budget": graph.node_budget,
            "edge_budget": graph.edge_budget,
            "relation_allowlist": list(graph.relation_allowlist),
            "phase_view": graph.phase_view,
        },
        nodes=tuple(_node_payload(node, include_data=include_data) for node in graph.nodes),
        edges=tuple(_edge_payload(edge, include_data=include_data) for edge in graph.edges),
        missing_facts=graph.missing_facts,
        mermaid=task_graph_to_mermaid(graph),
        graphviz_dot=task_graph_to_graphviz_dot(graph),
    )


def task_graph_to_mermaid(graph: TaskGraph) -> str:
    node_aliases = _node_aliases(graph)
    lines = ["flowchart TD"]
    if not node_aliases:
        lines.append(f'  empty["{_escape_mermaid_label(graph.goal)}"]')
        return "\n".join(lines)

    for node in graph.nodes:
        alias = node_aliases[node.node_id]
        label = _escape_mermaid_label(_display_label(node))
        lines.append(f'  {alias}["{label}"]')

    for edge in graph.edges:
        source_alias = node_aliases.get(edge.source_id, _synthetic_alias("source", edge.source_id))
        target_alias = node_aliases.get(edge.target_id, _synthetic_alias("target", edge.target_id))
        relation = _escape_mermaid_label(edge.relation)
        lines.append(f'  {source_alias} -- "{relation}" --> {target_alias}')

    if graph.missing_facts:
        lines.append('  missing["missing_facts"]')
        for index, fact in enumerate(graph.missing_facts, start=1):
            alias = f"missing_{index}"
            lines.append(f'  {alias}["{_escape_mermaid_label(fact)}"]')
            lines.append(f"  missing -.-> {alias}")

    return "\n".join(lines)


def task_graph_to_graphviz_dot(graph: TaskGraph) -> str:
    node_aliases = _node_aliases(graph)
    lines = ["digraph TaskGraph {", "  rankdir=LR;"]
    if not node_aliases:
        lines.append(f'  empty [label="{_escape_dot_label(graph.goal)}"];')
        lines.append("}")
        return "\n".join(lines)

    for node in graph.nodes:
        alias = node_aliases[node.node_id]
        label = _escape_dot_label(_display_label(node))
        shape = _dot_shape_for(node.node_type)
        lines.append(f'  {alias} [label="{label}", shape={shape}];')

    for edge in graph.edges:
        source_alias = node_aliases.get(edge.source_id, _synthetic_alias("source", edge.source_id))
        target_alias = node_aliases.get(edge.target_id, _synthetic_alias("target", edge.target_id))
        label = _escape_dot_label(edge.relation)
        lines.append(f'  {source_alias} -> {target_alias} [label="{label}"];')

    if graph.missing_facts:
        lines.append('  missing [label="missing_facts", shape=note];')
        for index, fact in enumerate(graph.missing_facts, start=1):
            alias = f"missing_{index}"
            lines.append(f'  {alias} [label="{_escape_dot_label(fact)}", shape=note];')
            lines.append(f"  missing -> {alias} [style=dashed];")

    lines.append("}")
    return "\n".join(lines)


def _node_payload(node: TaskGraphNode, *, include_data: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": node.node_id,
        "type": node.node_type,
        "label": node.label,
        "source": node.source,
        "evidence_ids": list(node.evidence_ids),
    }
    if include_data:
        payload["data"] = _json_safe(node.data)
    return payload


def _edge_payload(edge: TaskGraphEdge, *, include_data: bool) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "source": edge.source_id,
        "target": edge.target_id,
        "relation": edge.relation,
        "source_system": edge.source,
        "evidence_ids": list(edge.evidence_ids),
    }
    if include_data:
        payload["data"] = _json_safe(edge.data)
    return payload


def _node_aliases(graph: TaskGraph) -> dict[str, str]:
    return {node.node_id: f"n{index}" for index, node in enumerate(graph.nodes, start=1)}


def _display_label(node: TaskGraphNode) -> str:
    return f"{node.node_type}: {node.label or node.node_id}"


def _dot_shape_for(node_type: str) -> str:
    return {
        "goal": "box",
        "cognitive_skill": "component",
        "constraint": "diamond",
        "scene_instance": "ellipse",
    }.get(node_type, "oval")


def _synthetic_alias(prefix: str, value: str) -> str:
    digest = sha1(value.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{digest}"


def _escape_mermaid_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "<br/>")


def _escape_dot_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(child) for child in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
