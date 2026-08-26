from __future__ import annotations

from dataclasses import replace

from interfaces.contracts import KGQuery, KGQueryResult, PlanTrace, SceneQuery, SceneQueryResult, TaskGraph
from interfaces.services import BrainPlanResult, BrainTask

from cognitive.kg_service import StaticKGService
from cognitive.reasoner import TemplateReasoner
from cognitive.safety import BasicSafetyPolicyEngine
from cognitive.scene_graph_service import RuntimeSceneGraphService
from cognitive.skill_library import StaticSkillLibrary
from cognitive.task_graph_builder import PolicyTaskGraphBuilder
from cognitive.task_graph_visualization import visualize_task_graph


class PrototypeBrainOrchestrator:
    """Minimal orchestrator for the architecture improvement plan.

    It proves the intended control boundary: orchestration is deterministic;
    KG and scene graph are queried through typed APIs; the planner component
    emits a TodoList; safety validation runs before any executor integration.
    """

    def __init__(
        self,
        *,
        kg: StaticKGService,
        scene: RuntimeSceneGraphService,
        builder: PolicyTaskGraphBuilder | None = None,
        skill_library: StaticSkillLibrary | None = None,
        reasoner: TemplateReasoner | None = None,
        safety: BasicSafetyPolicyEngine | None = None,
    ) -> None:
        self.kg = kg
        self.scene = scene
        self.builder = builder or PolicyTaskGraphBuilder()
        self.skill_library = skill_library or StaticSkillLibrary()
        self.reasoner = reasoner or TemplateReasoner()
        self.safety = safety or BasicSafetyPolicyEngine()

    def plan(self, task: BrainTask) -> BrainPlanResult:
        route = self._select_planning_route(task)
        if route["path"] == "lightweight_scene":
            return self._plan_lightweight(task, route)

        contract_task = task.context.get("task", {})
        kg_query = KGQuery(
            query_type="task_operation_contract",
            payload={"task": contract_task},
            view=self.builder.phase_view,
            relation_allowlist=self.builder.relation_allowlist,
            max_hops=self.builder.max_hops,
            node_budget=self.builder.node_budget,
            edge_budget=self.builder.edge_budget,
        )
        kg_result = self.kg.query(kg_query)
        scene_result = self._query_scene_for_contract(kg_result.scene_queries_needed)
        graph = self.builder.enrich(self.builder.build(task), kg_result, scene_result)
        skills = self.skill_library.get_candidates(task, graph)
        todo = self.reasoner.generate_plan(task, graph, skills)
        validation = self.safety.validate(self._validation_todo(task, graph, skills, todo), graph)
        selected_skill_versions = {skill.skill_id: skill.version for skill in skills}
        task_graph_visualization = visualize_task_graph(graph, include_data=False).as_dict()
        plan_summary = {
            "source_skill_id": todo.source_skill_id,
            "step_count": len(todo.steps),
            "skills": [step.skill for step in todo.steps],
        }
        bt_recovery = task.context.get("bt_recovery", {})
        if isinstance(bt_recovery, dict) and bt_recovery:
            plan_summary["bt_recovery"] = dict(bt_recovery)
        trace = PlanTrace(
            task=task.raw_instruction,
            orchestration=route,
            selected_skill_ids=tuple(skill.skill_id for skill in skills),
            selected_skill_versions=selected_skill_versions,
            kg_query={
                "query_type": kg_query.query_type,
                "view": kg_query.view,
                "payload": kg_query.payload,
                "max_hops": kg_query.max_hops,
                "node_budget": kg_query.node_budget,
                "edge_budget": kg_query.edge_budget,
                "relation_allowlist": list(kg_query.relation_allowlist),
            },
            kg_facts_used=kg_result.facts,
            kg_constraints_used=kg_result.constraints,
            kg_unknowns=kg_result.unknowns,
            scene_queries=kg_result.scene_queries_needed,
            scene_instances_bound=scene_result.instances,
            scene_unknowns=scene_result.unknowns,
            missing_facts=graph.missing_facts,
            task_graph_stats={
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
                "missing_facts": len(graph.missing_facts),
                "max_hops": graph.max_hops,
                "node_budget": graph.node_budget,
                "edge_budget": graph.edge_budget,
            },
            task_graph_visualization=task_graph_visualization,
            plan_summary=plan_summary,
            safety={
                "passed": validation.passed,
                "layer": validation.layer,
                "issue": validation.issue,
                "fix": validation.fix,
                "failed_step": validation.failed_step,
            },
        )
        return BrainPlanResult(
            todo_list=todo,
            validation=validation,
            task_graph=graph,
            selected_skill_ids=tuple(skill.skill_id for skill in skills),
            trace=trace.as_dict(),
        )

    def _plan_lightweight(self, task: BrainTask, route: dict[str, object]) -> BrainPlanResult:
        graph = self.builder.build(task)
        scene_result = self._query_scene_for_lightweight(task)
        graph = self.builder.enrich(graph, KGQueryResult(query_type="lightweight_scene"), scene_result)
        skills = self.skill_library.get_candidates(task, graph)
        todo = self.reasoner.generate_plan(task, graph, skills)
        validation = self.safety.validate(self._validation_todo(task, graph, skills, todo), graph)
        selected_skill_versions = {skill.skill_id: skill.version for skill in skills}
        task_graph_visualization = visualize_task_graph(graph, include_data=False).as_dict()
        plan_summary = {
            "source_skill_id": todo.source_skill_id,
            "step_count": len(todo.steps),
            "skills": [step.skill for step in todo.steps],
        }
        trace = PlanTrace(
            task=task.raw_instruction,
            orchestration=route,
            selected_skill_ids=tuple(skill.skill_id for skill in skills),
            selected_skill_versions=selected_skill_versions,
            kg_query={},
            kg_facts_used=(),
            kg_constraints_used=(),
            kg_unknowns=(),
            scene_queries=scene_result.states.get("_scene_queries", ()),
            scene_instances_bound=scene_result.instances,
            scene_unknowns=scene_result.unknowns,
            missing_facts=graph.missing_facts,
            task_graph_stats={
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
                "missing_facts": len(graph.missing_facts),
                "max_hops": graph.max_hops,
                "node_budget": graph.node_budget,
                "edge_budget": graph.edge_budget,
            },
            task_graph_visualization=task_graph_visualization,
            plan_summary=plan_summary,
            safety={
                "passed": validation.passed,
                "layer": validation.layer,
                "issue": validation.issue,
                "fix": validation.fix,
                "failed_step": validation.failed_step,
            },
        )
        return BrainPlanResult(
            todo_list=todo,
            validation=validation,
            task_graph=graph,
            selected_skill_ids=tuple(skill.skill_id for skill in skills),
            trace=trace.as_dict(),
        )

    def _validation_todo(self, task: BrainTask, graph, skills, todo):
        validated_prefix = self._validated_prefix_todo(task)
        if validated_prefix is not None:
            return self._merge_todo_lists(validated_prefix, todo)

        bt_recovery = task.context.get("bt_recovery", {})
        if not isinstance(bt_recovery, dict):
            return todo
        try:
            failed_step = int(bt_recovery.get("failed_step"))
        except (TypeError, ValueError):
            return todo
        if failed_step <= 1:
            return todo

        base_context = dict(task.context)
        base_context.pop("bt_recovery", None)
        base_task = BrainTask(
            raw_instruction=task.raw_instruction,
            feature_flags=dict(task.feature_flags),
            context=base_context,
        )
        return self.reasoner.generate_plan(base_task, graph, skills)

    def _query_scene_for_contract(self, scene_queries: tuple[dict, ...]) -> SceneQueryResult:
        instances: list[dict] = []
        unknowns: list[str] = []
        seen_ids: set[str] = set()

        def append_instance(instance: dict) -> None:
            instance_id = str(instance.get("id", ""))
            if instance_id and instance_id not in seen_ids:
                seen_ids.add(instance_id)
                instances.append(instance)

        for query in scene_queries:
            query_type = query.get("query")
            if query_type not in {"resolve_instance", "find_instance"}:
                continue
            result = self.scene.query(
                SceneQuery(
                    query_type=str(query_type),
                    payload={
                        "type": query.get("type"),
                        "name_hint": query.get("name_hint", ""),
                    },
                )
            )
            unknowns.extend(result.unknowns)
            for instance in result.instances:
                append_instance(instance)

        queue = list(instances)
        while queue:
            instance = queue.pop(0)
            parent_id = str(instance.get("direct_parent") or "")
            if not parent_id or parent_id in seen_ids:
                continue
            parent_result = self.scene.query(
                SceneQuery(
                    query_type="resolve_instance",
                    payload={
                        "type": "",
                        "name_hint": parent_id,
                    },
                )
            )
            for parent in parent_result.instances:
                parent_id_value = str(parent.get("id", ""))
                if not parent_id_value or parent_id_value in seen_ids:
                    continue
                append_instance(parent)
                queue.append(parent)

        return SceneQueryResult(query_type="contract_scene_queries", instances=tuple(instances), unknowns=tuple(unknowns))

    def _query_scene_for_lightweight(self, task: BrainTask) -> SceneQueryResult:
        contract_task = self._contract_task(task)
        target_type = self._lightweight_target_type(contract_task)
        if not target_type:
            return SceneQueryResult(query_type="lightweight_scene_queries", unknowns=("missing lightweight target type",))
        name_hint = self._lightweight_name_hint(contract_task)
        queries = (
            {
                "query": "resolve_instance",
                "type": target_type,
                "role": self._lightweight_role(contract_task),
                "name_hint": name_hint,
            },
        )
        result = self.scene.query(
            SceneQuery(
                query_type="resolve_instance",
                payload={"type": target_type, "name_hint": name_hint},
            )
        )
        return SceneQueryResult(
            query_type="lightweight_scene_queries",
            instances=result.instances,
            states={"_scene_queries": queries},
            unknowns=result.unknowns,
        )

    def _select_planning_route(self, task: BrainTask) -> dict[str, object]:
        contract_task = self._contract_task(task)
        operation = str(contract_task.get("operation") or "").strip().lower()
        target_type = str(contract_task.get("target_type_hint") or contract_task.get("target_type") or "").strip().lower()
        feature_flag = bool(task.feature_flags.get("cognitive_lightweight_path"))

        if not feature_flag:
            return {"path": "kg_task_graph", "reason": "feature_disabled", "eligible": False}
        if not operation or not target_type:
            return {"path": "kg_task_graph", "reason": "missing_operation_or_target", "eligible": False}
        if task.context.get("bt_recovery") or task.context.get("validated_steps"):
            return {"path": "kg_task_graph", "reason": "repair_context_present", "eligible": False}
        if self._has_named_followup(contract_task):
            return {"path": "kg_task_graph", "reason": "post_actions_present", "eligible": False}
        if self._requires_full_context_operation(operation):
            return {"path": "kg_task_graph", "reason": "requires_full_context_operation", "eligible": False}
        if (operation, target_type) not in self._lightweight_operation_targets():
            return {"path": "kg_task_graph", "reason": "unsupported_lightweight_operation", "eligible": False}

        scene_result = self._query_scene_for_lightweight(task)
        if scene_result.unknowns:
            return {"path": "kg_task_graph", "reason": "scene_binding_failed", "eligible": False}
        if len(scene_result.instances) != 1:
            return {"path": "kg_task_graph", "reason": "scene_binding_ambiguous", "eligible": False}
        return {
            "path": "lightweight_scene",
            "reason": "single_target_low_risk_operation",
            "eligible": True,
            "operation": operation,
            "target_type": target_type,
        }

    def _contract_task(self, task: BrainTask) -> dict:
        contract_task = task.context.get("task", {})
        return contract_task if isinstance(contract_task, dict) else {}

    def _has_named_followup(self, contract_task: dict) -> bool:
        post_actions = contract_task.get("post_actions", ())
        return isinstance(post_actions, (list, tuple, set)) and bool(post_actions)

    def _requires_full_context_operation(self, operation: str) -> bool:
        return operation in {"cut", "make", "do", "clean", "put", "drink", "pickup", "read"}

    def _lightweight_operation_targets(self) -> set[tuple[str, str]]:
        return {
            ("turn_on", "toggleable_device"),
            ("turn_off", "toggleable_device"),
            ("open", "openable_container"),
            ("close", "openable_container"),
            ("observe", "observable_object"),
            ("touch", "touchable_object"),
            ("type", "typeable_device"),
            ("sleep", "sleepable_object"),
            ("sit", "seat_object"),
        }

    def _lightweight_target_type(self, contract_task: dict) -> str:
        return str(contract_task.get("target_type_hint") or contract_task.get("target_type") or "").strip()

    def _lightweight_name_hint(self, contract_task: dict) -> str:
        return str(contract_task.get("target_name") or "").strip()

    def _lightweight_role(self, contract_task: dict) -> str:
        operation = str(contract_task.get("operation") or "").strip().lower()
        return {
            "turn_on": "target_device",
            "turn_off": "target_device",
            "open": "target_container",
            "close": "target_container",
            "observe": "target_object",
            "touch": "target_object",
            "type": "target_device",
            "sleep": "target_bed",
            "sit": "target_seat",
        }.get(operation, "target")

    def _validated_prefix_todo(self, task: BrainTask):
        raw_steps = task.context.get("validated_steps", [])
        if not isinstance(raw_steps, list) or not raw_steps:
            return None

        from interfaces.contracts import PlanStep, TodoList

        steps: list[PlanStep] = []
        for index, raw_step in enumerate(raw_steps, start=1):
            if not isinstance(raw_step, dict):
                continue
            execution = raw_step.get("execution", {})
            if not isinstance(execution, dict) or not execution.get("skill"):
                continue
            parameters = execution.get("parameters", {})
            if parameters is None:
                parameters = {}
            if not isinstance(parameters, dict):
                continue
            steps.append(
                PlanStep(
                    step=int(raw_step.get("step") or index),
                    skill=str(execution.get("skill")),
                    parameters=dict(parameters),
                    preconditions=self._string_tuple(raw_step.get("preconditions")),
                    expected_effects=self._string_tuple(raw_step.get("expected_effects")),
                    success_check=self._string_tuple(raw_step.get("success_check")),
                    failure_policy=self._dict_field(raw_step.get("failure_policy")),
                    retry_policy=self._dict_field(raw_step.get("retry_policy")),
                )
            )
        if not steps:
            return None
        return TodoList(steps=tuple(steps))

    def _merge_todo_lists(self, prefix, suffix):
        from interfaces.contracts import TodoList

        merged_steps = list(prefix.steps)
        merged_steps.extend(
            replace(step, step=len(merged_steps) + index)
            for index, step in enumerate(suffix.steps, start=1)
        )
        return TodoList(
            steps=tuple(merged_steps),
            source_skill_id=suffix.source_skill_id or prefix.source_skill_id,
            task_graph_id=suffix.task_graph_id or prefix.task_graph_id,
        )

    def _string_tuple(self, value) -> tuple[str, ...]:
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, (list, tuple)):
            return tuple(str(item) for item in value)
        return (str(value),)

    def _dict_field(self, value) -> dict:
        if value is None:
            return {}
        if isinstance(value, dict):
            return dict(value)
        return {}
