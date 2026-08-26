from __future__ import annotations

from cognitive.planning_context import (
    _append_navigation_step,
    _append_pickup_from_scene,
    _apply_bt_recovery_suffix,
    _first_instance,
    _first_instance_excluding,
    _has_prior_open_step,
    _is_clean,
    _is_openable_container,
    _location,
    _parent_openable_container,
    _preferred_instance,
    _preferred_instance_any,
    _put_plan_requires_close,
    _robot_holding,
    _robot_location,
    _states,
    _task_container_name,
    _task_named_value,
    _task_target_name,
    _task_water_source_name,
    _type_plan_requires_turn_off,
)
from cognitive.planning_strategies import PLANNING_STRATEGIES
from interfaces.contracts import CognitiveSkillContract, PlanStep, TaskGraph, TodoList, ValidationResult
from interfaces.services import BrainTask


class TemplateReasoner:
    """Deterministic planning template used until a real LLM planner is wired in."""

    def generate_plan(
        self,
        task: BrainTask,
        graph: TaskGraph,
        skills: tuple[CognitiveSkillContract, ...],
    ) -> TodoList:
        skill_ids = {skill.skill_id for skill in skills}
        if not skill_ids:
            skill_ids = {node.node_id for node in graph.nodes if node.node_type == "cognitive_skill"}
        for strategy in PLANNING_STRATEGIES:
            if strategy.skill_id in skill_ids:
                return _apply_bt_recovery_suffix(task, strategy.generate(self, task, graph))
        return TodoList(steps=(), task_graph_id=graph.task_graph_id)

    def repair_plan(self, task: BrainTask, graph: TaskGraph, validation: ValidationResult) -> TodoList:
        return self.generate_plan(task, graph, ())

    def _cut_ingredient_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _first_instance(graph, "beef")
        tool = _first_instance(graph, "knife")
        surface = _first_instance(graph, "cutting_board")
        water_source = _first_instance(graph, "water_source")
        if not target or not tool or not surface:
            return TodoList(steps=(), source_skill_id="cooking.cut_ingredient", task_graph_id=graph.task_graph_id)

        target_id = str(target.get("id"))
        tool_id = str(tool.get("id"))
        surface_id = str(surface.get("id"))
        water_source_id = str(water_source.get("id")) if water_source else ""
        steps: list[PlanStep] = []
        current_location = _robot_location(task)
        holding = _robot_holding(task) or "空"

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        def navigate(target_location: str) -> None:
            nonlocal current_location
            if not target_location or target_location == "robot_hand" or current_location == target_location:
                return
            append("NavigateTo", {"target_location": target_location})
            current_location = target_location

        surface_location = _location(surface)
        if water_source_id and not _is_clean(surface):
            if surface_location:
                navigate(surface_location)
            append("Pickup", {"target_item": surface_id})
            holding = surface_id
            navigate(water_source_id)
            append(
                "Clean",
                {"target_item": surface_id, "water_source": water_source_id},
                expected_effects=(f"{surface_id}.isClean == true",),
            )
            if surface_location:
                navigate(surface_location)
                append(
                    "Put",
                    {"target_item": surface_id, "destination": surface_location},
                    preconditions=(f"robot_holding == {surface_id}",),
                    expected_effects=(f"{surface_id}.direct_parent == {surface_location}",),
                )
                holding = "空"

        target_location = _location(target)
        target_parent = str(target.get("direct_parent") or "")
        if holding == target_id or target_parent == "robot_hand":
            holding = target_id
        else:
            navigate(target_location)
            append("Pickup", {"target_item": target_id})
            holding = target_id

        if water_source_id and not _is_clean(target):
            navigate(water_source_id)
            append(
                "Clean",
                {"target_item": target_id, "water_source": water_source_id},
                expected_effects=(f"{target_id}.isClean == true",),
            )

        navigate(surface_id)
        append(
            "Put",
            {"target_item": target_id, "destination": surface_id},
            preconditions=(f"robot_holding == {target_id}",),
            expected_effects=(f"{target_id}.direct_parent == {surface_id}",),
        )
        holding = "空"

        tool_location = _location(tool)
        tool_parent = str(tool.get("direct_parent") or "")
        if holding == tool_id or tool_parent == "robot_hand":
            holding = tool_id
        else:
            navigate(tool_location)
            append("Pickup", {"target_item": tool_id})
            holding = tool_id

        navigate(surface_id)
        append(
            "Slice",
            {"target_item": target_id, "surface": surface_id, "cut_style": "sliced"},
            preconditions=(f"{target_id}.direct_parent == {surface_id}", f"robot_holding == {tool_id}"),
            expected_effects=(f"{target_id}.isSliced == true",),
        )

        if water_source_id:
            navigate(water_source_id)
            append(
                "Clean",
                {"target_item": tool_id, "water_source": water_source_id},
                expected_effects=(f"{tool_id}.isClean == true",),
            )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="cooking.cut_ingredient",
            task_graph_id=graph.task_graph_id,
        )

    def _make_tea_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        tea = _preferred_instance(graph, "tea", _task_named_value(task, "ingredient_name"))
        cup = _preferred_instance(graph, "cup", _task_named_value(task, "cup_name"))
        heating_device = _preferred_instance(graph, "heating_device", _task_named_value(task, "heating_device_name"))
        if heating_device is None:
            heating_device = _preferred_instance(graph, "kettle", _task_named_value(task, "heating_device_name"))
        water_source = _preferred_instance(graph, "water_source", _task_water_source_name(task))
        if not tea or not cup or not heating_device:
            return TodoList(steps=(), source_skill_id="cooking.make_tea", task_graph_id=graph.task_graph_id)

        tea_id = str(tea.get("id"))
        cup_id = str(cup.get("id"))
        heating_device_id = str(heating_device.get("id"))
        water_source_id = str(water_source.get("id")) if water_source else ""
        cup_home = str(cup.get("direct_parent") or cup.get("location") or "")
        heating_states = _states(heating_device)
        tea_states = _states(tea)
        tea_parent = str(tea.get("direct_parent") or "")
        current_location = _robot_location(task)
        holding = _robot_holding(task) or "空"
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        def navigate(target_location: str) -> None:
            nonlocal current_location
            if not target_location or current_location == target_location:
                return
            append("NavigateTo", {"target_location": target_location})
            current_location = target_location

        tea_prepared = (
            tea_states.get("isPrepared") is True
            or tea_states.get("isCooked") is True
            or tea_states.get("isHeated") is True
        )
        if tea_prepared and tea_parent == cup_id:
            return TodoList(steps=(), source_skill_id="cooking.make_tea", task_graph_id=graph.task_graph_id)
        if tea_prepared:
            if holding == tea_id or tea_parent == "robot_hand":
                navigate(cup_id)
                append(
                    "Put",
                    {"target_item": tea_id, "destination": cup_id},
                    preconditions=(f"robot_holding == {tea_id}",),
                    expected_effects=(f"{tea_id}.direct_parent == {cup_id}",),
                )
                return TodoList(
                    steps=tuple(steps),
                    source_skill_id="cooking.make_tea",
                    task_graph_id=graph.task_graph_id,
                )
            if tea_parent == heating_device_id:
                if heating_states.get("isOpen") is False:
                    navigate(heating_device_id)
                    append("Open", {"target_container": heating_device_id})
                navigate(heating_device_id)
                append("Pickup", {"target_item": tea_id})
                navigate(cup_id)
                append(
                    "Put",
                    {"target_item": tea_id, "destination": cup_id},
                    preconditions=(f"robot_holding == {tea_id}",),
                    expected_effects=(f"{tea_id}.direct_parent == {cup_id}",),
                )
                return TodoList(
                    steps=tuple(steps),
                    source_skill_id="cooking.make_tea",
                    task_graph_id=graph.task_graph_id,
                )

        cup_states = _states(cup)
        if cup_states.get("isClean") is False and water_source_id:
            cup_location = _location(cup)
            if cup_location:
                navigate(cup_location)
            append("Pickup", {"target_item": cup_id})
            navigate(water_source_id)
            append(
                "Clean",
                {"target_item": cup_id, "water_source": water_source_id},
                expected_effects=(f"{cup_id}.isClean == true",),
            )
            if cup_home and cup_home != cup_id:
                navigate(cup_home)
                append(
                    "Put",
                    {"target_item": cup_id, "destination": cup_home},
                    preconditions=(f"robot_holding == {cup_id}",),
                    expected_effects=(f"{cup_id}.direct_parent == {cup_home}",),
                )

        if tea_parent == heating_device_id:
            if heating_states.get("isOpen") is True:
                navigate(heating_device_id)
                append("Close", {"target_container": heating_device_id})
            if heating_states.get("isToggled") is not True:
                navigate(heating_device_id)
                append(
                    "ToggleOn",
                    {"target_device": heating_device_id},
                    preconditions=(f"{heating_device_id}.isOpen == false", "robot_holding == 空"),
                    expected_effects=(f"{heating_device_id}.isToggled == true",),
                )
            navigate(heating_device_id)
            append(
                "Heat",
                {"target_item": tea_id, "heating_device": heating_device_id},
                preconditions=(
                    f"{tea_id}.direct_parent == {heating_device_id}",
                    f"{heating_device_id}.isOpen == false",
                    f"{heating_device_id}.isToggled == true",
                ),
                expected_effects=(f"{tea_id}.isCooked == true",),
            )
            append("Open", {"target_container": heating_device_id})
            append("Pickup", {"target_item": tea_id})
            navigate(cup_id)
            append(
                "Put",
                {"target_item": tea_id, "destination": cup_id},
                preconditions=(f"robot_holding == {tea_id}",),
                expected_effects=(f"{tea_id}.direct_parent == {cup_id}",),
            )
            return TodoList(
                steps=tuple(steps),
                source_skill_id="cooking.make_tea",
                task_graph_id=graph.task_graph_id,
            )

        if heating_states.get("isOpen") is False:
            navigate(heating_device_id)
            append("Open", {"target_container": heating_device_id})

        tea_location = _location(tea)
        if tea_location:
            navigate(tea_location)
        append("Pickup", {"target_item": tea_id})

        navigate(heating_device_id)
        append(
            "Put",
            {"target_item": tea_id, "destination": heating_device_id},
            preconditions=(f"robot_holding == {tea_id}",),
            expected_effects=(f"{tea_id}.direct_parent == {heating_device_id}",),
        )
        append("Close", {"target_container": heating_device_id})
        if heating_states.get("isToggled") is not True:
            append(
                "ToggleOn",
                {"target_device": heating_device_id},
                preconditions=(f"{heating_device_id}.isOpen == false", "robot_holding == 空"),
                expected_effects=(f"{heating_device_id}.isToggled == true",),
            )
        append(
            "Heat",
            {"target_item": tea_id, "heating_device": heating_device_id},
            preconditions=(
                f"{tea_id}.direct_parent == {heating_device_id}",
                f"{heating_device_id}.isOpen == false",
                f"{heating_device_id}.isToggled == true",
            ),
            expected_effects=(f"{tea_id}.isCooked == true",),
        )
        append("Open", {"target_container": heating_device_id})
        append("Pickup", {"target_item": tea_id})
        navigate(cup_id)
        append(
            "Put",
            {"target_item": tea_id, "destination": cup_id},
            preconditions=(f"robot_holding == {tea_id}",),
            expected_effects=(f"{tea_id}.direct_parent == {cup_id}",),
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="cooking.make_tea",
            task_graph_id=graph.task_graph_id,
        )

    def _do_laundry_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        clothes = _preferred_instance(graph, "dirty_clothes", _task_named_value(task, "load_name"))
        washer = _preferred_instance(graph, "washing_machine", _task_named_value(task, "washer_name"))
        detergent = _preferred_instance(graph, "detergent", _task_named_value(task, "detergent_name"))
        if not clothes or not washer or not detergent:
            return TodoList(steps=(), source_skill_id="laundry.do_laundry", task_graph_id=graph.task_graph_id)

        clothes_id = str(clothes.get("id"))
        washer_id = str(washer.get("id"))
        detergent_id = str(detergent.get("id"))
        washer_states = washer.get("states", {}) if isinstance(washer.get("states"), dict) else {}
        steps: list[PlanStep] = []
        current_location = _robot_location(task)
        holding = _robot_holding(task) or "空"
        washer_open = washer_states.get("isOpen") is True
        clothes_in_washer = str(clothes.get("direct_parent") or "") == washer_id
        detergent_in_washer = str(detergent.get("direct_parent") or "") == washer_id

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        def navigate(target_location: str) -> None:
            nonlocal current_location
            if not target_location or current_location == target_location:
                return
            append("NavigateTo", {"target_location": target_location})
            current_location = target_location

        def ensure_washer_open() -> None:
            nonlocal washer_open
            if washer_open:
                return
            navigate(washer_id)
            append("Open", {"target_container": washer_id})
            washer_open = True

        def ensure_holding(target: dict, target_id: str) -> None:
            nonlocal holding, current_location
            target_parent = str(target.get("direct_parent") or "")
            if holding == target_id or target_parent == "robot_hand":
                holding = target_id
                return

            parent_container = _parent_openable_container(graph, target)
            parent_container_id = str(parent_container.get("id")) if parent_container else ""
            parent_container_states = _states(parent_container)
            if (
                parent_container_id
                and parent_container_states.get("isOpen") is not True
                and not _has_prior_open_step(steps, parent_container_id)
            ):
                navigate(parent_container_id)
                append(
                    "Open",
                    {"target_container": parent_container_id},
                    expected_effects=(f"{parent_container_id}.isOpen == true",),
                )

            target_location = _location(target)
            if target_location and target_location != parent_container_id:
                navigate(target_location)

            pickup_preconditions = ["robot_holding == 空"]
            if parent_container_id:
                pickup_preconditions.append(f"{parent_container_id}.isOpen == true")
            append(
                "Pickup",
                {"target_item": target_id},
                preconditions=tuple(pickup_preconditions),
                expected_effects=(f"robot_holding == {target_id}",),
            )
            holding = target_id

        if not clothes_in_washer:
            ensure_washer_open()
            ensure_holding(clothes, clothes_id)
            navigate(washer_id)
            append(
                "Put",
                {"target_item": clothes_id, "destination": washer_id},
                preconditions=(f"robot_holding == {clothes_id}",),
                expected_effects=(f"{clothes_id}.direct_parent == {washer_id}",),
            )
            holding = "空"
            clothes_in_washer = True

        if not detergent_in_washer:
            ensure_washer_open()
            ensure_holding(detergent, detergent_id)
            navigate(washer_id)
            append(
                "Put",
                {"target_item": detergent_id, "destination": washer_id},
                preconditions=(f"robot_holding == {detergent_id}",),
                expected_effects=(f"{detergent_id}.direct_parent == {washer_id}",),
            )
            holding = "空"
            detergent_in_washer = True

        if washer_open or not (
            clothes_in_washer
            and detergent_in_washer
            and washer_states.get("isOpen") is False
        ):
            navigate(washer_id)
            append("Close", {"target_container": washer_id})
            washer_open = False
        navigate(washer_id)
        append(
            "ToggleOn",
            {"target_device": washer_id},
            preconditions=(f"{washer_id}.isOpen == false", "robot_holding == 空"),
            expected_effects=(f"{washer_id}.isToggled == true",),
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="laundry.do_laundry",
            task_graph_id=graph.task_graph_id,
        )

    def _turn_on_device_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        device = _preferred_instance(graph, "toggleable_device", _task_target_name(task))
        if not device:
            return TodoList(steps=(), source_skill_id="device.turn_on", task_graph_id=graph.task_graph_id)

        device_id = str(device.get("id"))
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        append("NavigateTo", {"target_location": device_id})
        append(
            "ToggleOn",
            {"target_device": device_id},
            expected_effects=(f"{device_id}.isToggled == true",),
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="device.turn_on",
            task_graph_id=graph.task_graph_id,
        )

    def _turn_off_device_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        device = _preferred_instance(graph, "toggleable_device", _task_target_name(task))
        if not device:
            return TodoList(steps=(), source_skill_id="device.turn_off", task_graph_id=graph.task_graph_id)

        device_id = str(device.get("id"))
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        append("NavigateTo", {"target_location": device_id})
        append(
            "ToggleOff",
            {"target_device": device_id},
            expected_effects=(f"{device_id}.isToggled == false",),
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="device.turn_off",
            task_graph_id=graph.task_graph_id,
        )

    def _open_container_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        container = _preferred_instance(graph, "openable_container", _task_target_name(task))
        if not container:
            return TodoList(steps=(), source_skill_id="container.open", task_graph_id=graph.task_graph_id)

        container_id = str(container.get("id"))
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        append("NavigateTo", {"target_location": container_id})
        append(
            "Open",
            {"target_container": container_id},
            expected_effects=(f"{container_id}.isOpen == true",),
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="container.open",
            task_graph_id=graph.task_graph_id,
        )

    def _close_container_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        container = _preferred_instance(graph, "openable_container", _task_target_name(task))
        if not container:
            return TodoList(steps=(), source_skill_id="container.close", task_graph_id=graph.task_graph_id)

        container_id = str(container.get("id"))
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        append("NavigateTo", {"target_location": container_id})
        append(
            "Close",
            {"target_container": container_id},
            expected_effects=(f"{container_id}.isOpen == false",),
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="container.close",
            task_graph_id=graph.task_graph_id,
        )

    def _pickup_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _preferred_instance(graph, "pickupable_object", _task_target_name(task))
        if not target:
            return TodoList(steps=(), source_skill_id="object.pickup", task_graph_id=graph.task_graph_id)

        steps: list[PlanStep] = []
        _append_pickup_from_scene(graph, steps, target)

        return TodoList(
            steps=tuple(steps),
            source_skill_id="object.pickup",
            task_graph_id=graph.task_graph_id,
        )

    def _put_object_into_container_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _preferred_instance(graph, "pickupable_object", _task_target_name(task))
        target_parent = str(target.get("direct_parent") or "") if target else ""
        excluded_ids = {target_parent} if target_parent else set()
        destination_name = _task_container_name(task)
        destination = _preferred_instance_any(
            graph,
            ("openable_container", "receptacle", "placement_surface", "surface"),
            destination_name,
        )
        if destination and str(destination.get("id") or "") in excluded_ids:
            destination = None
        destination = destination or _first_instance_excluding(graph, "openable_container", excluded_ids) or _first_instance(
            graph, "openable_container"
        )
        if not target or not destination:
            return TodoList(steps=(), source_skill_id="object.put_into_container", task_graph_id=graph.task_graph_id)

        target_id = str(target.get("id"))
        destination_id = str(destination.get("id"))
        destination_states = _states(destination)
        destination_openable = _is_openable_container(destination)
        close_after = _put_plan_requires_close(task) and destination_openable
        current_location = _robot_location(task)
        robot_holding = _robot_holding(task)
        already_holding = robot_holding == target_id or str(target.get("direct_parent") or "") == "robot_hand"
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        def navigate(target_location: str) -> None:
            nonlocal current_location
            if not target_location or current_location == target_location:
                return
            append("NavigateTo", {"target_location": target_location})
            current_location = target_location

        if destination_openable and destination_states.get("isOpen") is False:
            navigate(destination_id)
            append(
                "Open",
                {"target_container": destination_id},
                expected_effects=(f"{destination_id}.isOpen == true",),
            )

        if already_holding:
            navigate(destination_id)
        else:
            _append_pickup_from_scene(graph, steps, target, robot_holding=robot_holding)
            _append_navigation_step(steps, destination_id)
        append(
            "Put",
            {"target_item": target_id, "destination": destination_id},
            preconditions=(f"robot_holding == {target_id}",),
            expected_effects=(f"{target_id}.direct_parent == {destination_id}",),
        )
        if close_after:
            append(
                "Close",
                {"target_container": destination_id},
                expected_effects=(f"{destination_id}.isOpen == false",),
            )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="object.put_into_container",
            task_graph_id=graph.task_graph_id,
        )

    def _clean_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _preferred_instance(graph, "cleanable_object", _task_target_name(task))
        water_source = _preferred_instance(graph, "water_source", _task_water_source_name(task))
        if not target or not water_source:
            return TodoList(steps=(), source_skill_id="object.clean", task_graph_id=graph.task_graph_id)

        target_id = str(target.get("id"))
        target_parent = str(target.get("direct_parent") or "")
        water_source_id = str(water_source.get("id"))
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        if target_parent not in {"robot_hand", water_source_id}:
            _append_pickup_from_scene(graph, steps, target)

        _append_navigation_step(steps, water_source_id)
        append(
            "Clean",
            {"target_item": target_id, "water_source": water_source_id},
            expected_effects=(f"{target_id}.isClean == true",),
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="object.clean",
            task_graph_id=graph.task_graph_id,
        )

    def _read_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _preferred_instance(graph, "readable_object", _task_target_name(task))
        if not target:
            return TodoList(steps=(), source_skill_id="object.read", task_graph_id=graph.task_graph_id)

        target_id = str(target.get("id"))
        target_parent = str(target.get("direct_parent") or "")
        robot_holding = _robot_holding(task)
        already_holding = robot_holding == target_id or target_parent == "robot_hand"
        steps: list[PlanStep] = []
        _append_pickup_from_scene(graph, steps, target, robot_holding=robot_holding)
        if not steps and not already_holding:
            _append_navigation_step(steps, _location(target))
        steps.append(
            PlanStep(
                step=len(steps) + 1,
                skill="Read",
                parameters={"target_item": target_id},
                expected_effects=(f"last_read == {target_id}",),
            )
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="object.read",
            task_graph_id=graph.task_graph_id,
        )

    def _observe_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _preferred_instance(graph, "observable_object", _task_target_name(task))
        if not target:
            return TodoList(steps=(), source_skill_id="object.observe", task_graph_id=graph.task_graph_id)

        target_id = str(target.get("id"))
        target_location = _location(target)
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        if target_location:
            append("NavigateTo", {"target_location": target_location})
        append(
            "Observe",
            {"target_object": target_id},
            expected_effects=(f"last_observed == {target_id}",),
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="object.observe",
            task_graph_id=graph.task_graph_id,
        )

    def _drink_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _preferred_instance(graph, "drinkable_object", _task_target_name(task))
        if not target:
            return TodoList(steps=(), source_skill_id="object.drink", task_graph_id=graph.task_graph_id)

        target_id = str(target.get("id"))
        target_parent = str(target.get("direct_parent") or "")
        robot_holding = _robot_holding(task)
        already_holding = robot_holding == target_id or target_parent == "robot_hand"
        steps: list[PlanStep] = []
        _append_pickup_from_scene(graph, steps, target, robot_holding=robot_holding)
        if not steps and not already_holding:
            _append_navigation_step(steps, _location(target))
        steps.append(
            PlanStep(
                step=len(steps) + 1,
                skill="Drink",
                parameters={"target_item": target_id},
                expected_effects=(f"last_drunk == {target_id}",),
            )
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="object.drink",
            task_graph_id=graph.task_graph_id,
        )

    def _touch_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _preferred_instance(graph, "touchable_object", _task_target_name(task))
        if not target:
            return TodoList(steps=(), source_skill_id="object.touch", task_graph_id=graph.task_graph_id)

        target_id = str(target.get("id"))
        target_location = _location(target)
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        if target_location:
            append("NavigateTo", {"target_location": target_location})
        append(
            "Touch",
            {"target_object": target_id},
            expected_effects=(f"last_touched == {target_id}",),
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="object.touch",
            task_graph_id=graph.task_graph_id,
        )

    def _type_on_device_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _preferred_instance(graph, "typeable_device", _task_target_name(task))
        if not target:
            return TodoList(steps=(), source_skill_id="device.type_on", task_graph_id=graph.task_graph_id)

        target_id = str(target.get("id"))
        target_location = _location(target)
        turn_off_after = _type_plan_requires_turn_off(task)
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        if target_location:
            append("NavigateTo", {"target_location": target_location})
        append(
            "Type",
            {"target_device": target_id},
            expected_effects=(f"last_typed_on == {target_id}",),
        )
        if turn_off_after:
            if not any(
                step.skill == "NavigateTo" and step.parameters.get("target_location") == target_id for step in steps
            ):
                append("NavigateTo", {"target_location": target_id})
            append(
                "ToggleOff",
                {"target_device": target_id},
                expected_effects=(f"{target_id}.isToggled == false",),
            )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="device.type_on",
            task_graph_id=graph.task_graph_id,
        )

    def _sleep_on_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _preferred_instance(graph, "sleepable_object", _task_target_name(task))
        if not target:
            return TodoList(steps=(), source_skill_id="object.sleep_on", task_graph_id=graph.task_graph_id)

        target_id = str(target.get("id"))
        target_location = _location(target)
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        if target_location:
            append("NavigateTo", {"target_location": target_location})
        append(
            "Sleep",
            {"target_bed": target_id},
            expected_effects=(f"last_sleep_target == {target_id}",),
        )

        return TodoList(
            steps=tuple(steps),
            source_skill_id="object.sleep_on",
            task_graph_id=graph.task_graph_id,
        )

    def _sit_on_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList:
        target = _preferred_instance(graph, "seat_object", _task_target_name(task))
        if not target:
            return TodoList(steps=(), source_skill_id="object.sit_on", task_graph_id=graph.task_graph_id)

        target_id = str(target.get("id"))
        target_location = _location(target)
        steps: list[PlanStep] = []

        def append(skill: str, parameters: dict, **kwargs) -> None:
            steps.append(PlanStep(step=len(steps) + 1, skill=skill, parameters=parameters, **kwargs))

        if target_location:
            append("NavigateTo", {"target_location": target_location})
        append("Sit", {"target_seat": target_id})

        return TodoList(
            steps=tuple(steps),
            source_skill_id="object.sit_on",
            task_graph_id=graph.task_graph_id,
        )
