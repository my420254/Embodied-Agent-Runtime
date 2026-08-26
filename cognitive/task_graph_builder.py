from __future__ import annotations

from interfaces.contracts import (
    KGQueryResult,
    PLANNING_RELATION_ALLOWLIST,
    SceneQueryResult,
    TaskGraph,
    TaskGraphEdge,
    TaskGraphNode,
)
from interfaces.services import BrainTask


class PolicyTaskGraphBuilder:
    """Deterministic TaskGraph builder used before LLM plan generation."""

    def __init__(
        self,
        *,
        max_hops: int = 2,
        node_budget: int = 50,
        edge_budget: int = 120,
        relation_allowlist: tuple[str, ...] = PLANNING_RELATION_ALLOWLIST,
        phase_view: str = "planning",
    ) -> None:
        self.max_hops = max_hops
        self.node_budget = node_budget
        self.edge_budget = edge_budget
        self.relation_allowlist = tuple(relation_allowlist)
        self.phase_view = phase_view

    def build(self, task: BrainTask) -> TaskGraph:
        graph = TaskGraph(
            goal=task.raw_instruction,
            relation_allowlist=self.relation_allowlist,
            max_hops=self.max_hops,
            node_budget=self.node_budget,
            edge_budget=self.edge_budget,
            phase_view=self.phase_view,
        )
        goal_node = TaskGraphNode(
            node_id="goal",
            node_type="goal",
            label=task.raw_instruction,
            data={
                "max_hops": self.max_hops,
                "node_budget": self.node_budget,
                "edge_budget": self.edge_budget,
                "relation_allowlist": list(self.relation_allowlist),
                "phase_view": self.phase_view,
            },
            source="orchestrator",
        )
        return graph.add_node(goal_node)

    def enrich(self, graph: TaskGraph, kg_result: KGQueryResult, scene_result: SceneQueryResult) -> TaskGraph:
        enriched = graph
        for skill_id in kg_result.candidate_skills:
            enriched = enriched.add_node(TaskGraphNode(skill_id, "cognitive_skill", skill_id, source="kg"))

        for fact in kg_result.facts:
            subject = str(fact.get("subject", ""))
            obj = str(fact.get("object", ""))
            relation = str(fact.get("relation", ""))
            if subject:
                enriched = enriched.add_node(TaskGraphNode(subject, "kg_entity", subject, source="kg"))
            if obj:
                enriched = enriched.add_node(TaskGraphNode(obj, "kg_entity", obj, source="kg"))
            if subject and obj and relation:
                enriched = enriched.add_edge(TaskGraphEdge(subject, obj, relation, source="kg"))

        for index, constraint in enumerate(kg_result.constraints, start=1):
            predicate = str(constraint.get("predicate", f"constraint_{index}"))
            enriched = enriched.add_node(
                TaskGraphNode(
                    node_id=f"constraint:{predicate}",
                    node_type="constraint",
                    label=predicate,
                    data=dict(constraint),
                    source="kg",
                )
            )

        for instance in scene_result.instances:
            instance_id = str(instance.get("id", ""))
            if not instance_id:
                continue
            node_id = instance_id
            if any(existing.node_id == instance_id for existing in enriched.nodes):
                node_id = f"scene:{instance_id}"
            enriched = enriched.add_node(
                TaskGraphNode(
                    node_id=node_id,
                    node_type="scene_instance",
                    label=instance_id,
                    data=dict(instance),
                    source="scene",
                )
            )

        for unknown in (*kg_result.unknowns, *scene_result.unknowns):
            enriched = enriched.with_missing_fact(unknown)

        return enriched
