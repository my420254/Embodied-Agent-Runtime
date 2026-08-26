from __future__ import annotations

from domain.action_contracts import (
    AVAILABLE_STATE_ALIASES,
    CLOSED_STATE_ALIASES,
    HIGH_RISK_BOUND_KEYS,
    NON_PICKUP_CLEAN_TARGET_TYPES,
    OPEN_STATE_ALIASES,
    OPENABLE_CONTAINER_TYPES,
    TARGET_CONTAINER,
    TARGET_DEVICE,
    TARGET_ITEM,
    TOGGLE_OFF_STATE_ALIASES,
    TOGGLE_ON_STATE_ALIASES,
    UNAVAILABLE_STATE_ALIASES,
)
from interfaces.contracts import TaskGraph, TodoList, ValidationResult


_HIGH_RISK_CLEARANCE_FLAGS = frozenset(
    {
        "humanNearby",
        "isHumanNearby",
        "nearHuman",
        "personNearby",
        "human_nearby",
        "person_nearby",
        "occupiedByHuman",
        "isOccupiedByHuman",
        "flammableNearby",
        "flammable_nearby",
        "fireHazard",
        "fire_hazard",
        "environmentHazard",
        "environment_hazard",
        "unsafe",
        "blocked",
        "isBlocked",
    }
)


class BasicSafetyPolicyEngine:
    """Structural safety checks for prototype cognitive plans.

    This is not a replacement for sandbox physics validation. It enforces hard
    architecture invariants before any plan reaches execution.
    """

    def validate(self, todo_list: TodoList, graph: TaskGraph | None = None) -> ValidationResult:
        clearance_validation = self._validate_high_risk_clearance(todo_list, graph)
        if not clearance_validation.passed:
            return clearance_validation

        slice_validation = self._validate_slice_safety(todo_list, graph)
        if not slice_validation.passed:
            return slice_validation

        pickup_validation = self._validate_pickup_safety(todo_list, graph)
        if not pickup_validation.passed:
            return pickup_validation

        clean_validation = self._validate_clean_safety(todo_list, graph)
        if not clean_validation.passed:
            return clean_validation

        container_validation = self._validate_container_safety(todo_list, graph)
        if not container_validation.passed:
            return container_validation

        toggle_validation = self._validate_toggle_safety(todo_list, graph)
        if not toggle_validation.passed:
            return toggle_validation

        heat_validation = self._validate_heat_safety(todo_list, graph)
        if not heat_validation.passed:
            return heat_validation

        return ValidationResult(passed=True, layer="safety")

    def _validate_high_risk_clearance(
        self,
        todo_list: TodoList,
        graph: TaskGraph | None = None,
    ) -> ValidationResult:
        scene_nodes = self._scene_nodes_by_id(graph)
        if not scene_nodes:
            return ValidationResult(passed=True, layer="safety")

        for step in todo_list.steps:
            bound_ids = self._high_risk_bound_scene_ids(step.skill, step.parameters)
            for node_id in bound_ids:
                node = scene_nodes.get(node_id, {})
                if not node or not self._node_has_clearance_hazard(node):
                    continue
                return ValidationResult(
                    passed=False,
                    issue="高风险动作缺少人员/环境安全清场",
                    fix=f"{step.skill} 前必须确认目标周围无人员接近、易燃物或其他危险状态",
                    layer="safety",
                    failed_step=step.step,
                )
        return ValidationResult(passed=True, layer="safety")

    def _validate_slice_safety(self, todo_list: TodoList, graph: TaskGraph | None = None) -> ValidationResult:
        steps = todo_list.steps
        slice_indexes = [index for index, step in enumerate(steps) if step.skill == "Slice"]
        if not slice_indexes:
            return ValidationResult(passed=True, layer="safety")
        first_slice = slice_indexes[0]
        slice_step = steps[first_slice]
        if not slice_step.parameters.get("surface"):
            return ValidationResult(
                passed=False,
                issue="切割动作缺少 surface 参数",
                fix="Slice 必须显式绑定切割表面",
                layer="safety",
                failed_step=slice_step.step,
            )
        target = str(slice_step.parameters.get("target_item") or "")
        surface = str(slice_step.parameters.get("surface") or "")
        scene_nodes = self._scene_nodes_by_id(graph)

        target_clean = self._node_is_clean(scene_nodes.get(target, {}))
        surface_clean = self._node_is_clean(scene_nodes.get(surface, {}))
        for step in steps[:first_slice]:
            if step.skill != "Clean":
                continue
            cleaned_target = str(step.parameters.get("target_item") or "")
            if cleaned_target == target:
                target_clean = True
            if cleaned_target == surface:
                surface_clean = True

        has_clean_before_slice = any(step.skill == "Clean" for step in steps[:first_slice])
        if not has_clean_before_slice and not (target_clean and surface_clean):
            return ValidationResult(
                passed=False,
                issue="切割前缺少清洁步骤",
                fix="高风险食材切割前必须先执行 Clean 或证明目标和切割表面已清洁",
                layer="safety",
                failed_step=slice_step.step,
            )
        if not target_clean:
            return ValidationResult(
                passed=False,
                issue="切割前目标物品未清洁",
                fix="Slice 前必须先 Clean 目标物品，或证明目标物品已清洁",
                layer="safety",
                failed_step=slice_step.step,
            )
        if not surface_clean:
            return ValidationResult(
                passed=False,
                issue="切割前缺少清洁切割表面步骤",
                fix="Slice 前必须先 Clean 切割表面，或证明切割表面已清洁",
                layer="safety",
                failed_step=slice_step.step,
            )

        knife_ids = {
            node_id
            for node_id, node in scene_nodes.items()
            if str(node.get("type") or "") == "knife"
        }
        knife_in_hand = any(
            self._node_parent(node) == "robot_hand"
            for node in scene_nodes.values()
            if str(node.get("type") or "") == "knife"
        )
        if knife_ids and not knife_in_hand:
            has_knife_pickup_before = any(
                step.skill == "Pickup" and str(step.parameters.get("target_item") or "") in knife_ids
                for step in steps[:first_slice]
            )
            if not has_knife_pickup_before:
                return ValidationResult(
                    passed=False,
                    issue="切割前缺少刀具拾取步骤",
                    fix="Slice 前必须先 Pickup 可用刀具，或证明刀具已在手中",
                    layer="safety",
                    failed_step=slice_step.step,
                )

        return ValidationResult(passed=True, layer="safety")

    def _node_is_clean(self, node: dict) -> bool:
        states = node.get("states", {}) if isinstance(node.get("states"), dict) else {}
        return self._state_bool(states.get("isClean")) is True or self._state_bool(states.get("clean")) is True

    def _high_risk_bound_scene_ids(self, skill: str, parameters: dict) -> tuple[str, ...]:
        if not isinstance(parameters, dict):
            return ()
        keys = HIGH_RISK_BOUND_KEYS.get(skill, ())
        return tuple(str(parameters.get(key)) for key in keys if parameters.get(key))

    def _node_has_clearance_hazard(self, node: dict) -> bool:
        states = node.get("states", {}) if isinstance(node.get("states"), dict) else {}
        return any(self._state_bool(states.get(flag)) is True for flag in _HIGH_RISK_CLEARANCE_FLAGS)

    def _validate_pickup_safety(self, todo_list: TodoList, graph: TaskGraph | None = None) -> ValidationResult:
        scene_nodes = self._scene_nodes_by_id(graph)
        for index, step in enumerate(todo_list.steps):
            if step.skill != "Pickup":
                continue
            target = str(step.parameters.get("target_item") or "")
            if not target:
                return ValidationResult(
                    passed=False,
                    issue="拾取动作缺少 target_item 参数",
                    fix="Pickup 必须显式绑定待拾取物体",
                    layer="safety",
                    failed_step=step.step,
                )
            target_node = scene_nodes.get(target, {})
            parent_id = self._node_parent(target_node)
            if not parent_id:
                continue
            parent_node = scene_nodes.get(parent_id, {})
            parent_states = parent_node.get("states", {}) if isinstance(parent_node.get("states"), dict) else {}
            if not parent_node or not self._is_openable_container_node(parent_node):
                continue
            if self._open_state(parent_states) is True:
                continue
            has_open_before = any(
                prev.skill == "Open" and prev.parameters.get("target_container") == parent_id
                for prev in todo_list.steps[:index]
            )
            if not has_open_before:
                return ValidationResult(
                    passed=False,
                    issue="从关闭容器拾取物体前缺少打开步骤",
                    fix="Pickup 关闭 openable container 内物体前必须先 Open，或证明容器已打开",
                    layer="safety",
                    failed_step=step.step,
                )
        return ValidationResult(passed=True, layer="safety")

    def _validate_clean_safety(self, todo_list: TodoList, graph: TaskGraph | None = None) -> ValidationResult:
        scene_nodes = self._scene_nodes_by_id(graph)
        for index, step in enumerate(todo_list.steps):
            if step.skill != "Clean":
                continue
            target = str(step.parameters.get("target_item") or "")
            water_source = str(step.parameters.get("water_source") or "")
            if not target or not water_source:
                return ValidationResult(
                    passed=False,
                    issue="清洁动作缺少 target_item 或 water_source 参数",
                    fix="Clean 必须显式绑定待清洁物体和 water_source",
                    layer="safety",
                    failed_step=step.step,
                )

            water_node = scene_nodes.get(water_source, {})
            water_states = water_node.get("states", {}) if isinstance(water_node.get("states"), dict) else {}
            if water_node and not self._is_water_source_node(water_node):
                return ValidationResult(
                    passed=False,
                    issue="清洁动作绑定了非水源目标",
                    fix="Clean 的 water_source 必须是可用水源设备或容器",
                    layer="safety",
                    failed_step=step.step,
                )
            if (
                water_node
                and self._availability_state(water_states) is False
                and self._state_bool(water_states.get("isFilledWithLiquid")) is not True
            ):
                return ValidationResult(
                    passed=False,
                    issue="清洁动作绑定的水源当前不可用",
                    fix="先选择 available 的水源，或证明 water_source 已装有液体",
                    layer="safety",
                    failed_step=step.step,
                )

            target_node = scene_nodes.get(target, {})
            target_parent = self._node_parent(target_node)
            if (
                target_node
                and self._clean_target_requires_pickup(target_node)
                and target_parent not in {"robot_hand", water_source}
            ):
                has_pickup_before = any(
                    prev.skill == "Pickup" and prev.parameters.get("target_item") == target
                    for prev in todo_list.steps[:index]
                )
                if not has_pickup_before:
                    return ValidationResult(
                        passed=False,
                        issue="清洁前缺少拾取待清洁物体步骤",
                        fix="便携物体执行 Clean 前必须先 Pickup，或证明其已在手中/已位于水源处",
                        layer="safety",
                        failed_step=step.step,
                    )
        return ValidationResult(passed=True, layer="safety")

    def _clean_target_requires_pickup(self, node: dict) -> bool:
        if not isinstance(node, dict):
            return False
        states = node.get("states", {}) if isinstance(node.get("states"), dict) else {}
        if (
            self._state_bool(states.get("portable")) is False
            or self._state_bool(states.get("isPortable")) is False
            or self._state_bool(states.get("fixed")) is True
            or self._state_bool(states.get("isFixed")) is True
        ):
            return False
        node_type = str(node.get("type") or "").lower()
        if node_type in NON_PICKUP_CLEAN_TARGET_TYPES:
            return False
        if "surface" in node_type or "counter" in node_type or "fixture" in node_type:
            return False
        return True

    def _validate_container_safety(self, todo_list: TodoList, graph: TaskGraph | None = None) -> ValidationResult:
        scene_nodes = self._scene_nodes_by_id(graph)
        for index, step in enumerate(todo_list.steps):
            if step.skill != "Put":
                continue
            target = step.parameters.get("target_item")
            destination = step.parameters.get("destination")
            if not target or not destination:
                return ValidationResult(
                    passed=False,
                    issue="放置动作缺少 target_item 或 destination 参数",
                    fix="Put 必须显式绑定待放置物体和目标容器/表面",
                    layer="safety",
                    failed_step=step.step,
                )
            destination_node = scene_nodes.get(str(destination), {})
            if not destination_node or not self._is_openable_container_node(destination_node):
                continue
            destination_states = (
                destination_node.get("states", {}) if isinstance(destination_node.get("states"), dict) else {}
            )
            if self._open_state(destination_states) is True:
                continue
            has_open_before = any(
                prev.skill == "Open" and prev.parameters.get("target_container") == destination
                for prev in todo_list.steps[:index]
            )
            if not has_open_before:
                return ValidationResult(
                    passed=False,
                    issue="向关闭容器放置物体前缺少打开步骤",
                    fix="Put 进入 openable container 前必须先 Open，或证明容器已打开",
                    layer="safety",
                    failed_step=step.step,
                )
        return ValidationResult(passed=True, layer="safety")

    def _validate_toggle_safety(self, todo_list: TodoList, graph: TaskGraph | None = None) -> ValidationResult:
        scene_nodes = self._scene_nodes_by_id(graph)
        for index, step in enumerate(todo_list.steps):
            if step.skill != "ToggleOn":
                continue
            target = step.parameters.get("target_device")
            if not target:
                return ValidationResult(
                    passed=False,
                    issue="开关动作缺少 target_device 参数",
                    fix="ToggleOn 必须显式绑定目标设备",
                    layer="safety",
                    failed_step=step.step,
                )
            target_node = scene_nodes.get(str(target), {})
            target_states = target_node.get("states", {}) if isinstance(target_node.get("states"), dict) else {}
            target_type = str(target_node.get("type") or "")
            close_required = graph is None or self._has_open_state(target_states) or target_type in OPENABLE_CONTAINER_TYPES
            if not close_required:
                continue

            observed_open_state = self._open_state(target_states)
            for prev in todo_list.steps[:index]:
                if prev.skill == "Open" and prev.parameters.get("target_container") == target:
                    observed_open_state = True
                elif prev.skill == "Close" and prev.parameters.get("target_container") == target:
                    observed_open_state = False

            if observed_open_state is not False:
                return ValidationResult(
                    passed=False,
                    issue="设备开启前缺少关闭步骤",
                    fix="涉及容器式设备的 ToggleOn 前必须先 Close",
                    layer="safety",
                    failed_step=step.step,
                )
        return ValidationResult(passed=True, layer="safety")

    def _validate_heat_safety(self, todo_list: TodoList, graph: TaskGraph | None = None) -> ValidationResult:
        scene_nodes = self._scene_nodes_by_id(graph)
        initial_states = self._scene_states_by_id(graph)
        for index, step in enumerate(todo_list.steps):
            if step.skill != "Heat":
                continue
            target = step.parameters.get("target_item")
            heating_device = step.parameters.get("heating_device")
            if not target or not heating_device:
                return ValidationResult(
                    passed=False,
                    issue="加热动作缺少 target_item 或 heating_device 参数",
                    fix="Heat 必须显式绑定待加热物品与加热设备",
                    layer="safety",
                    failed_step=step.step,
                )
            target_in_device = self._node_parent(scene_nodes.get(str(target), {})) == str(heating_device)
            device_open_state = self._open_state(initial_states.get(str(heating_device), {}))
            device_on_state = self._toggle_state(initial_states.get(str(heating_device), {}))

            for prev in todo_list.steps[:index]:
                if prev.skill == "Put" and prev.parameters.get("target_item") == target:
                    target_in_device = prev.parameters.get("destination") == heating_device
                elif prev.skill == "Pickup" and prev.parameters.get("target_item") == target:
                    target_in_device = False

                if prev.skill == "Open" and prev.parameters.get("target_container") == heating_device:
                    device_open_state = True
                elif prev.skill == "Close" and prev.parameters.get("target_container") == heating_device:
                    device_open_state = False

                if prev.skill == "ToggleOn" and prev.parameters.get("target_device") == heating_device:
                    device_on_state = True
                elif prev.skill == "ToggleOff" and prev.parameters.get("target_device") == heating_device:
                    device_on_state = False

            if not target_in_device:
                return ValidationResult(
                    passed=False,
                    issue="加热前目标物品未放入加热设备",
                    fix="Heat 前必须先 Put 到 heating_device",
                    layer="safety",
                    failed_step=step.step,
                )
            if device_open_state is not False:
                return ValidationResult(
                    passed=False,
                    issue="加热前缺少关闭加热设备步骤",
                    fix="Heat 前必须先 Close 加热设备",
                    layer="safety",
                    failed_step=step.step,
                )
            if device_on_state is not True:
                return ValidationResult(
                    passed=False,
                    issue="加热前缺少开启加热设备步骤",
                    fix="Heat 前必须先 ToggleOn 加热设备，除非场景状态证明设备已开启",
                    layer="safety",
                    failed_step=step.step,
                )
        return ValidationResult(passed=True, layer="safety")

    def _scene_states_by_id(self, graph: TaskGraph | None) -> dict[str, dict]:
        return {
            instance_id: node.get("states", {})
            for instance_id, node in self._scene_nodes_by_id(graph).items()
            if isinstance(node.get("states"), dict)
        }

    def _scene_nodes_by_id(self, graph: TaskGraph | None) -> dict[str, dict]:
        if graph is None:
            return {}
        nodes: dict[str, dict] = {}
        for node in graph.nodes:
            if node.node_type != "scene_instance" or not isinstance(node.data, dict):
                continue
            instance_id = str(node.data.get("id", ""))
            if instance_id:
                nodes[instance_id] = node.data
        return nodes

    def _node_parent(self, node: dict) -> str:
        if not isinstance(node, dict):
            return ""
        parent = node.get("direct_parent")
        if parent:
            return str(parent)
        location = node.get("location")
        return str(location) if location else ""

    def _state_bool(self, value) -> bool | None:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "yes", "1", "open", "opened", "on", "available", "enabled"}:
                return True
            if normalized in {"false", "no", "0", "closed", "off", "unavailable", "disabled"}:
                return False
        return None

    def _state_from_aliases(
        self,
        states: dict,
        positive_aliases: tuple[str, ...],
        negative_aliases: tuple[str, ...] = (),
    ) -> bool | None:
        if not isinstance(states, dict):
            return None
        for alias in positive_aliases:
            value = self._state_bool(states.get(alias))
            if value is not None:
                return value
        for alias in negative_aliases:
            value = self._state_bool(states.get(alias))
            if value is not None:
                return not value
        return None

    def _open_state(self, states: dict) -> bool | None:
        return self._state_from_aliases(
            states,
            OPEN_STATE_ALIASES,
            CLOSED_STATE_ALIASES,
        )

    def _has_open_state(self, states: dict) -> bool:
        return self._open_state(states) is not None

    def _toggle_state(self, states: dict) -> bool | None:
        return self._state_from_aliases(
            states,
            TOGGLE_ON_STATE_ALIASES,
            TOGGLE_OFF_STATE_ALIASES,
        )

    def _availability_state(self, states: dict) -> bool | None:
        return self._state_from_aliases(
            states,
            AVAILABLE_STATE_ALIASES,
            UNAVAILABLE_STATE_ALIASES,
        )

    def _is_water_source_node(self, node: dict) -> bool:
        if not isinstance(node, dict):
            return False
        node_type = str(node.get("type") or "")
        states = node.get("states", {}) if isinstance(node.get("states"), dict) else {}
        return (
            node_type == "water_source"
            or self._availability_state(states) is True
            or self._state_bool(states.get("isFilledWithLiquid")) is True
        )

    def _is_openable_container_node(self, node: dict) -> bool:
        if not isinstance(node, dict):
            return False
        node_type = str(node.get("type") or "")
        states = node.get("states", {}) if isinstance(node.get("states"), dict) else {}
        return self._has_open_state(states) or node_type in OPENABLE_CONTAINER_TYPES
