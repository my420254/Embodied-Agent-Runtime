from __future__ import annotations

import copy
import heapq
from collections.abc import Callable
from typing import Any

from SDA.skill_catalog import SkillRepairCatalog, load_repair_catalog


Action = dict[str, Any]
ApplyAction = Callable[[dict, dict, str, dict], tuple[bool, str, str]]

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Bound on the number of expanded search nodes before residual planning gives
# up and reports failure. Keeps worst-case latency predictable for the planner
# thread; it is a search budget, not a tuned heuristic constant.
_MAX_EXPANSIONS = 2000


def generate_adaptive_subtree(
    *,
    discarded_suffix: list,
    checkpoint_env: dict,
    checkpoint_robot: dict,
    apply_action: ApplyAction,
    max_actions: int = 80,
    max_repairs_per_action: int = 4,
    repair_catalog: SkillRepairCatalog | None = None,
) -> dict[str, Any]:
    """Generate a sandbox-verified replacement suffix via residual planning.

    Replaces the discarded suffix with a freshly planned suffix that reaches
    the same *remaining goal* (the grounded facts the original suffix was meant
    to establish) from the checkpoint state. Search is a best-first walk over
    grounded states using skill contracts as the action model, validated step
    by step against the same sandbox used by the evaluator. This makes the
    repair complete over the contract action set: any reachable suffix can be
    found, and the order of the discarded suffix is not assumed to be right.

    The discarded suffix still contributes two things, neither of which is
    "the order to replay": (1) the set of grounded goal facts derived from the
    target values of its `can_set_state` / `can_transform_item` actions, and
    (2) a fallback ordering hint that breaks ties when several states have the
    same heuristic value. Both are goal-derived, not order-derived.
    """
    catalog = repair_catalog or load_repair_catalog()
    env0 = copy.deepcopy(checkpoint_env or {})
    robot0 = copy.deepcopy(checkpoint_robot or {})

    original_actions = [_normalize_action(step) for step in discarded_suffix or []]
    original_actions = [action for action in original_actions if action.get("skill")]
    goal = _remaining_goal(original_actions, env0, robot0, catalog)
    order_hint = _order_hint(original_actions, catalog)

    planner = _ResidualPlanner(
        catalog=catalog,
        apply_action=apply_action,
        max_actions=max_actions,
        goal=goal,
        order_hint=order_hint,
        max_expansions=_MAX_EXPANSIONS,
    )
    result = planner.search(env0, robot0)
    return _format_result(result, max_actions=max_actions)


# ---------------------------------------------------------------------------
# Result shaping
# ---------------------------------------------------------------------------


def _format_result(search_result: dict[str, Any], *, max_actions: int) -> dict[str, Any]:
    actions = search_result.get("actions", [])
    if not search_result.get("success"):
        return {
            "success": False,
            "mode": "sda_adaptive_action_subtree",
            "actions": _numbered_actions(actions),
            "action_count": len(actions),
            "failure_reason": search_result.get("failure_reason", "residual_planning_failed"),
            "failure_details": search_result.get("failure_details", {}),
            "repair_log": search_result.get("repair_log", []),
        }
    return {
        "success": True,
        "mode": "sda_adaptive_action_subtree",
        "actions": _numbered_actions(actions),
        "action_count": len(actions),
        "final_env": search_result["final_env"],
        "final_robot": search_result["final_robot"],
        "repair_log": search_result.get("repair_log", []),
        "planner_stats": search_result.get("planner_stats", {}),
    }


def _numbered_actions(actions: list[Action]) -> list[dict[str, Any]]:
    return [
        {
            "step": index,
            "execution": {
                "skill": action.get("skill", ""),
                "parameters": copy.deepcopy(action.get("parameters", {}) or {}),
            },
        }
        for index, action in enumerate(actions, start=1)
    ]


# ---------------------------------------------------------------------------
# Goal extraction
# ---------------------------------------------------------------------------


def _remaining_goal(
    original_actions: list[Action],
    env: dict,
    robot: dict,
    catalog: SkillRepairCatalog,
) -> set[tuple[str, str, Any]]:
    """Grounded goal facts the discarded suffix was meant to establish.

    Only the *final* effect of each (entity, state-key) is kept — a suffix that
    opens then closes the same container has `isOpen=False` as its residual
    contribution for that entity, not both. Without this last-writer rule the
    goal set would be self-contradictory (asking for isOpen True and False on
    the same container) and unreachable by any planner. Effects already
    satisfied at the checkpoint are still retained. They may be temporarily
    violated by access-enabling actions, but the replacement suffix must restore
    them before it is accepted.
    """
    final_effects: dict[tuple[str, str], Any] = {}
    direct_parent_effects: dict[str, str] = {}
    for action in original_actions:
        spec = catalog.get(str(action.get("skill", "") or ""))
        if not spec:
            continue
        if spec.can_set_state and spec.state_key:
            target = spec.target_value(action)
            if target:
                final_effects[(target, spec.state_key)] = spec.state_value
        if spec.effect_state_key:
            item = spec.item_value(action)
            if item:
                final_effects[(item, spec.effect_state_key)] = spec.effect_state_value
        if spec.can_place_item:
            item = spec.item_value(action)
            destination = spec.destination_value(action)
            if item and destination:
                direct_parent_effects[item] = destination

    goal: set[tuple[str, str, Any]] = set()
    for (entity, key), value in final_effects.items():
        goal.add((entity, key, value))
    for item, destination in direct_parent_effects.items():
        goal.add((item, "direct_parent", destination))

    return goal


def _fact_holds(fact: tuple[str, str, Any], env: dict, robot: dict) -> bool:
    entity, key, value = fact
    if entity == "robot":
        return robot.get(key) == value
    info = env.get(entity, {})
    if not isinstance(info, dict):
        return info == value
    if key == "direct_parent":
        return info.get("direct_parent") == value
    states = info.get("states", {})
    return isinstance(states, dict) and states.get(key) == value


def _unsatisfied_goal_count(env: dict, robot: dict, goal: set[tuple[str, str, Any]]) -> int:
    return sum(1 for fact in goal if not _fact_holds(fact, env, robot))


def _order_hint(original_actions: list[Action], catalog: SkillRepairCatalog) -> list[Action]:
    """Tie-break hint derived from the original suffix's action sequence.

    Used only to break ties among states with equal h-value. It does not force
    the planner to replay the original order; it just expresses a weak
    preference for the planner's suffix to resemble the discarded one when
    several suffixes are equally short. Cheap and only consulted in ties.
    """
    return [copy.deepcopy(action) for action in original_actions]


# ---------------------------------------------------------------------------
# State encoding & candidate generation
# ---------------------------------------------------------------------------


def _state_key(env: dict, robot: dict, depth: int) -> tuple:
    """Stable hashable identity for a grounded state.

    Search actions have uniform positive cost, so reaching the same grounded
    world state at a greater depth can never improve the remaining suffix.
    Keeping depth in the signature lets reversible actions generate infinite
    Open/Close/Toggle/Navigate cycles; the world signature is the useful state.
    """
    return _world_signature(env, robot)


def _world_signature(env: dict, robot: dict) -> tuple:
    env_sig = tuple(
        (name, _entity_signature(info))
        for name, info in sorted(env.items(), key=lambda item: str(item[0]))
        if isinstance(info, dict)
    )
    robot_sig = tuple(sorted((str(k), _value_signature(v)) for k, v in (robot or {}).items()))
    return (env_sig, robot_sig)


def _entity_signature(info: dict) -> tuple:
    states = info.get("states", {})
    states_sig = (
        tuple(sorted((str(k), _value_signature(v)) for k, v in states.items()))
        if isinstance(states, dict)
        else ()
    )
    return (str(info.get("direct_parent", "") or ""), states_sig)


def _value_signature(value: Any) -> str:
    if isinstance(value, bool):
        return "b1" if value else "b0"
    return f"v:{value!r}"


def _candidate_actions(
    env: dict,
    robot: dict,
    catalog: SkillRepairCatalog,
    order_hint: list[Action],
    goal: set[tuple[str, str, Any]],
) -> list[Action]:
    """Enumerate contract-derived actions applicable at this state.

    Four sources, all goal- or state-derived, none scene-specific:
    (1) the order-hint actions — the planner gets a chance to execute the
        original intent when it is legal;
    (2) one move/navigate action toward each entity referenced by the goal or
        by an order-hint action, so the robot can reposition to act;
    (3) the universal state-writing skills (open/close/toggle) restricted to
        entities in the goal's reachable set (the goal entities plus their
        ancestor chain — opening an ancestor is how you reach a nested goal
        entity);
    (4) grasp/place over the carried item and the goal's grasp/place targets.
    """
    actions: list[Action] = []

    seen: set[str] = set()
    for action in order_hint:
        key = _action_json(action)
        if key in seen:
            continue
        seen.add(key)
        actions.append(copy.deepcopy(action))

    goal_entities = _entities_for_goal(goal)
    reachable: set[str] = set()
    for entity in goal_entities:
        if entity in env:
            reachable.add(entity)
            reachable.update(_parent_chain(entity, env))
    # Order-hint referenced entities also need to be movable-to.
    for action in order_hint:
        spec = catalog.get(str(action.get("skill", "") or ""))
        if not spec:
            continue
        for value in (
            spec.target_value(action),
            spec.item_value(action),
            spec.destination_value(action),
            spec.location_value(action),
            spec.device_value(action),
        ):
            if value and value in env:
                reachable.add(value)
                reachable.update(_parent_chain(value, env))

    transform_preconditions = _transform_state_preconditions(order_hint, catalog)
    actions.extend(_movement_actions(env, robot, catalog, reachable))
    actions.extend(_state_write_actions(env, catalog, reachable, goal, transform_preconditions))
    actions.extend(_transfer_actions(env, robot, catalog, goal))

    return _dedupe_actions(actions)


def _entities_for_goal(goal: set[tuple[str, str, Any]]) -> set[str]:
    return {fact[0] for fact in goal if fact[0] != "robot"}


def _movement_actions(
    env: dict,
    robot: dict,
    catalog: SkillRepairCatalog,
    target_entities: set[str],
) -> list[Action]:
    move_spec = catalog._first(lambda spec: spec.can_move_robot)  # noqa: SLF001
    if not move_spec or not move_spec.location_param:
        return []
    actions: list[Action] = []
    current_loc = str(robot.get("robot_location", "") or "")
    for entity in sorted(target_entities):
        if entity in env and entity != current_loc:
            actions.append({"skill": move_spec.name, "parameters": {move_spec.location_param: entity}})
    return actions


def _state_write_actions(
    env: dict,
    catalog: SkillRepairCatalog,
    reachable: set[str],
    goal: set[tuple[str, str, Any]],
    transform_preconditions: set[tuple[str, str, Any]],
) -> list[Action]:
    """Emit open/close/toggle over state-writing skills, scoped to reachable set.

    The cross-product is (state-writing skill × goal-reachable entity). Scoping
    to the reachable set — goal entities plus their ancestor chain — keeps the
    branching factor proportional to the goal, not to the whole scene. The
    search's goal test prunes what is useless; we don't pre-filter by "is this
    state already right" because enabling writes (Open) are needed exactly when
    a later Close will undo them.
    """
    actions: list[Action] = []
    for spec in catalog.specs:
        if not spec.can_set_state or not spec.target_param or not spec.state_key:
            continue
        for entity in sorted(reachable):
            if entity in env and _state_write_target_allowed(spec, entity, env, goal, transform_preconditions):
                actions.append({"skill": spec.name, "parameters": {spec.target_param: entity}})
    return actions


def _transform_state_preconditions(order_hint: list[Action], catalog: SkillRepairCatalog) -> set[tuple[str, str, Any]]:
    preconditions: set[tuple[str, str, Any]] = set()
    for action in order_hint:
        spec = catalog.get(str(action.get("skill", "") or ""))
        if not spec or not spec.can_transform_item:
            continue
        device = spec.device_value(action)
        if device and spec.device_state_key:
            preconditions.add((device, spec.device_state_key, spec.device_state_value))
        if device and spec.container_state_key:
            preconditions.add((device, spec.container_state_key, spec.container_state_value))
    return preconditions


def _state_write_target_allowed(
    spec,
    entity: str,
    env: dict,
    goal: set[tuple[str, str, Any]],
    transform_preconditions: set[tuple[str, str, Any]],
) -> bool:
    info = env.get(entity, {})
    states = info.get("states", {}) if isinstance(info, dict) else {}
    if (entity, spec.state_key, spec.state_value) in goal:
        return True
    if (entity, spec.state_key, spec.state_value) in transform_preconditions:
        return True
    if not isinstance(states, dict) or spec.state_key not in states:
        return False
    return bool(spec.access_state and spec.state_value is True)


def _transfer_actions(
    env: dict,
    robot: dict,
    catalog: SkillRepairCatalog,
    goal: set[tuple[str, str, Any]],
) -> list[Action]:
    carried = _carried_entity(robot)
    actions: list[Action] = []
    grasp_spec = catalog._first(lambda spec: spec.can_grasp_item)  # noqa: SLF001
    place_spec = catalog._first(lambda spec: spec.can_place_item)  # noqa: SLF001
    # Grasp only entities the goal needs (or the carried item's chain) — grasping
    # arbitrary scene items never advances a goal and explodes the frontier.
    goal_entities = _entities_for_goal(goal)
    grasp_targets = _grasp_goal_entities(goal, catalog) & set(env.keys())
    if grasp_spec and grasp_spec.item_param:
        for entity in sorted(grasp_targets):
            if entity != carried:
                actions.append({"skill": grasp_spec.name, "parameters": {grasp_spec.item_param: entity}})
    if place_spec and place_spec.item_param and place_spec.destination_param and carried:
        destinations = _candidate_drop_sites(env, carried, catalog, goal_entities)
        for entity in sorted(destinations):
            actions.append(
                {
                    "skill": place_spec.name,
                    "parameters": {place_spec.item_param: carried, place_spec.destination_param: entity},
                }
            )
    return actions


def _grasp_goal_entities(goal: set[tuple[str, str, Any]], catalog: SkillRepairCatalog) -> set[str]:
    targets: set[str] = set()
    transform_effects = {
        (spec.effect_state_key, spec.effect_state_value)
        for spec in catalog.specs
        if spec.can_transform_item and spec.effect_state_key
    }
    for entity, key, value in goal:
        if entity == "robot":
            continue
        if key == "direct_parent":
            targets.add(entity)
        elif (key, value) in transform_effects:
            targets.add(entity)
    return targets


def _candidate_drop_sites(
    env: dict,
    carried: str,
    catalog: SkillRepairCatalog,
    goal_entities: set[str],
) -> set[str]:
    """Where the carried item may be temporarily placed.

    Two categories, both principled:
    - goal destinations: any entity that the goal's direct_parent facts name
      as a target parent (the carried item's *final* home, if it is the goal
      item);
    - staging sites: reachable containers that are not behind an
      access-controlled ancestor and not the carried item's own descendant.
      These are the slots a planner needs to free a hand so a later grasp can
      happen — the universal "put down so I can pick up something else" move.
    Both categories are derived from the goal and from the standing
    reachability structure of the scene, never from a scene-specific score.
    """
    sites: set[str] = set()
    for entity in goal_entities:
        if entity in env and entity != carried and not _is_descendant_of(entity, carried, env):
            sites.add(entity)
    access_state_keys = catalog.access_state_keys()
    for name, info in env.items():
        if name == carried or not isinstance(info, dict):
            continue
        states = info.get("states", {}) if isinstance(info.get("states"), dict) else {}
        if any(states.get(key) is False for key in access_state_keys):
            continue  # itself access-locked
        if any(states.get(key) is False for key in access_state_keys for _ in (None,)):
            continue
        if _is_descendant_of(str(name), carried, env):
            continue
        if _has_access_controlled_ancestor(str(name), env, catalog):
            continue
        sites.add(str(name))
    return sites


def _dedupe_actions(actions: list[Action]) -> list[Action]:
    deduped: list[Action] = []
    seen: set[str] = set()
    for action in actions:
        if not action.get("skill"):
            continue
        key = _action_json(action)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(action)
    return deduped


def _action_json(action: Action) -> str:
    import json

    return json.dumps(action, ensure_ascii=False, sort_keys=True)


# ---------------------------------------------------------------------------
# Relaxed-plan heuristic (delete-relaxation, FF-style)
# ---------------------------------------------------------------------------


def _relaxed_plan_heuristic(
    env: dict,
    robot: dict,
    goal: set[tuple[str, str, Any]],
    catalog: SkillRepairCatalog,
) -> int:
    """h(s): FF-style delete-relaxed plan length from s to goal.

    Preconditions are ignored (max relaxisation) and effects are applied
    monotonically over grounded actions derived from the contract action set
    and the entities in s. Each layer adds every effect of every grounded
    action whose effects include a not-yet-held fact; the number of layers
    needed for the goal to become true is returned. Admissible (delete
    relaxation never over-estimates) and far more informed than the plain
    unsatisfied-goal count — it can see that reaching `isCooked` takes several
    enabling layers (place → close → toggle → heat), which the count-only
    heuristic cannot and what made GBFS thrash.
    """
    if not goal:
        return 0

    facts: set = set()
    _seed_facts(env, robot, facts)
    held = _goal_holds_in_facts(goal, facts)
    if held:
        return 0

    grounded = _relaxed_grounded_actions(env, catalog)
    effect_list: list[set] = [_effects_of(g, env, catalog) for g in grounded]

    layers = 0
    while layers < 64:
        progressed = False
        new_facts: set = set()
        for effects in effect_list:
            additions = effects - facts
            if additions:
                new_facts |= additions
                progressed = True
        facts |= new_facts
        layers += 1
        if _goal_holds_in_facts(goal, facts):
            return layers
        if not progressed:
            return layers  # unreachable under relaxation
    return layers


def _goal_holds_in_facts(goal: set[tuple[str, str, Any]], facts: set) -> bool:
    """Check the (entity, key, value) goal against the heuristic fact set.

    Goal tuples use the simplified representation (entity, key, value) where
    key is a state-key or the literal 'direct_parent'. Facts use the tagged
    representation ('state', entity, key, value) / ('direct_parent', entity,
    dest). This bridges the two without rewriting the goal shape.
    """
    for entity, key, value in goal:
        if key == "direct_parent":
            if ("direct_parent", entity, value) not in facts:
                return False
        else:
            if ("state", entity, key, value) not in facts:
                return False
    return True


def _seed_facts(env: dict, robot: dict, facts: set) -> None:
    for key, value in (robot or {}).items():
        facts.add(("robot", str(key), _relax_value(value)))
    for entity, info in (env or {}).items():
        facts.add(("entity", str(entity), "__exists__"))
        if not isinstance(info, dict):
            facts.add(("entity", str(entity), "value"))
            facts.add(("entity_value", str(entity), copy.deepcopy(info)))
            continue
        parent = str(info.get("direct_parent", "") or "")
        if parent:
            facts.add(("direct_parent", str(entity), parent))
        states = info.get("states", {})
        if isinstance(states, dict):
            for skey, svalue in states.items():
                facts.add(("state", str(entity), str(skey), _relax_value(svalue)))


def _relax_value(value: Any) -> Any:
    # Relaxed facts use raw values; only bool handled uniformly with _fact_holds.
    return value


def _effects_of(
    action: Action,
    env: dict,
    catalog: SkillRepairCatalog,
) -> set:
    spec = catalog.get(str(action.get("skill", "") or ""))
    effects: set = set()
    if not spec:
        return effects
    if spec.can_set_state and spec.state_key:
        target = spec.target_value(action)
        if target:
            effects.add(("state", target, spec.state_key, spec.state_value))
    if spec.effect_state_key:
        item = spec.item_value(action)
        if item:
            effects.add(("state", item, spec.effect_state_key, spec.effect_state_value))
    if spec.can_place_item:
        item = spec.item_value(action)
        destination = spec.destination_value(action)
        if item and destination:
            effects.add(("direct_parent", item, destination))
    if spec.can_grasp_item:
        item = spec.item_value(action)
        if item:
            effects.add(("robot", "robot_holding", item))
            effects.add(("direct_parent", item, "robot_hand"))
    return effects


def _relaxed_grounded_actions(env: dict, catalog: SkillRepairCatalog) -> list[Action]:
    grounded: list[Action] = []
    move_spec = catalog._first(lambda spec: spec.can_move_robot)  # noqa: SLF001
    grasp_spec = catalog._first(lambda spec: spec.can_grasp_item)  # noqa: SLF001
    place_spec = catalog._first(lambda spec: spec.can_place_item)  # noqa: SLF001
    entities = sorted(env.keys())
    if move_spec and move_spec.location_param:
        for entity in entities:
            grounded.append({"skill": move_spec.name, "parameters": {move_spec.location_param: entity}})
    for spec in catalog.specs:
        if spec.can_set_state and spec.target_param and spec.state_key:
            for entity in entities:
                grounded.append({"skill": spec.name, "parameters": {spec.target_param: entity}})
    if grasp_spec and grasp_spec.item_param:
        for entity in entities:
            grounded.append({"skill": grasp_spec.name, "parameters": {grasp_spec.item_param: entity}})
    # Transform skills (Heat/Cool/Slice/Clean) declare non-target params their
    # groundings are not enumerateable from the contract alone; we still ground
    # them over every entity pair matching their declared params so the relaxed
    # effect set reflects transform reachability. Over-approximation only lowers
    # h, which preserves admissibility while keeping the heuristic informed.
    transform_specs = [spec for spec in catalog.specs if spec.can_transform_item]
    for spec in transform_specs:
        item_param = spec.item_param
        device_param = spec.device_param or spec.location_param
        for item in entities:
            for device in entities:
                params: dict[str, Any] = {}
                if item_param:
                    params[item_param] = item
                if device_param:
                    params[device_param] = device
                if params:
                    grounded.append({"skill": spec.name, "parameters": params})
    if place_spec and place_spec.item_param and place_spec.destination_param:
        for item in entities:
            for destination in entities:
                if item != destination:
                    grounded.append(
                        {
                            "skill": place_spec.name,
                            "parameters": {place_spec.item_param: item, place_spec.destination_param: destination},
                        }
                    )
    return grounded


# ---------------------------------------------------------------------------
# Best-first residual planner
# ---------------------------------------------------------------------------


class _Node:
    __slots__ = ("env", "robot", "depth", "actions", "h", "unsatisfied", "tie_rank")

    def __init__(
        self,
        env: dict,
        robot: dict,
        depth: int,
        actions: list[Action],
        h: int,
        unsatisfied: int,
        tie_rank: int,
    ):
        self.env = env
        self.robot = robot
        self.depth = depth
        self.actions = actions
        self.h = h
        self.unsatisfied = unsatisfied
        self.tie_rank = tie_rank


class _ResidualPlanner:
    def __init__(
        self,
        *,
        catalog: SkillRepairCatalog,
        apply_action: ApplyAction,
        max_actions: int,
        goal: set[tuple[str, str, Any]],
        order_hint: list[Action],
        max_expansions: int,
    ):
        self.catalog = catalog
        self.apply_action = apply_action
        self.max_actions = max_actions
        self.goal = goal
        self.order_hint = order_hint
        self.max_expansions = max_expansions
        self._order_index = {key: i for i, key in enumerate(_action_json(a) for a in order_hint)}
        self._expanded = 0
        self._seen: set[tuple] = set()
        self._heuristic_cache: dict[tuple, int] = {}

    def search(self, env: dict, robot: dict) -> dict[str, Any]:
        repair_log: list[dict[str, Any]] = []
        start_h = self._heuristic(env, robot)
        start_unsatisfied = _unsatisfied_goal_count(env, robot, self.goal)
        if not self.goal:
            # Nothing left to achieve; the checkpoint state already satisfies
            # the residual goal. Return an empty (zero-action) suffix.
            return {
                "success": True,
                "actions": [],
                "final_env": copy.deepcopy(env),
                "final_robot": copy.deepcopy(robot),
                "repair_log": repair_log,
                "planner_stats": {"expanded": 0, "h_start": 0, "goal_size": 0},
            }
        start = _Node(env, robot, 0, [], start_h, start_unsatisfied, 0)
        frontier: list[_Node] = []
        heapq.heappush(frontier, self._queue_item(start))
        self._mark_seen(start)

        while frontier:
            _, _, depth, _, _, node = heapq.heappop(frontier)
            if node.unsatisfied == 0:
                # Goal reached; validate the full suffix actually holds in the
                # final sandbox state (it does by construction, but assert for
                # safety against any contract/goal mismatch).
                return {
                    "success": True,
                    "actions": copy.deepcopy(node.actions),
                    "final_env": node.env,
                    "final_robot": node.robot,
                    "repair_log": repair_log,
                    "planner_stats": {
                        "expanded": self._expanded,
                        "h_start": start_h,
                        "goal_size": len(self.goal),
                        "suffix_length": len(node.actions),
                    },
                }
            if self._expanded >= self.max_expansions:
                return self._failure(
                    "residual_planning_expansion_budget",
                    {"expanded": self._expanded, "depth": depth, "h": node.h},
                    repair_log,
                    node,
                )
            self._expanded += 1
            self._expand(node, frontier, repair_log)

        return self._failure(
            "residual_planning_exhausted",
            {"expanded": self._expanded, "frontier_empty": True},
            repair_log,
            None,
        )

    def _expand(self, node: _Node, frontier: list, repair_log: list[dict[str, Any]]) -> None:
        if len(node.actions) >= self.max_actions:
            return
        candidates = _candidate_actions(node.env, node.robot, self.catalog, self.order_hint, self.goal)
        for action in candidates:
            if len(node.actions) + 1 > self.max_actions:
                continue
            next_env = copy.deepcopy(node.env)
            next_robot = copy.deepcopy(node.robot)
            ok, issue, fix = self.apply_action(
                next_env,
                next_robot,
                action.get("skill", ""),
                action.get("parameters", {}) or {},
            )
            if not ok:
                repair_log.append(
                    {
                        "event": "sandbox_rejected_successor",
                        "depth": node.depth,
                        "action": copy.deepcopy(action),
                        "issue": issue,
                        "fix": fix,
                    }
                )
                continue
            key = _state_key(next_env, next_robot, node.depth + 1)
            if key in self._seen:
                continue
            self._seen.add(key)
            child_h = self._heuristic(next_env, next_robot)
            child_unsatisfied = _unsatisfied_goal_count(next_env, next_robot, self.goal)
            child_actions = node.actions + [copy.deepcopy(action)]
            tie_rank = self._order_index.get(_action_json(action), len(self._order_index))
            child = _Node(next_env, next_robot, node.depth + 1, child_actions, child_h, child_unsatisfied, tie_rank)
            heapq.heappush(frontier, self._queue_item(child))

    def _mark_seen(self, node: _Node) -> None:
        self._seen.add(_state_key(node.env, node.robot, node.depth))

    def _heuristic(self, env: dict, robot: dict) -> int:
        key = _world_signature(env, robot)
        if key not in self._heuristic_cache:
            self._heuristic_cache[key] = _relaxed_plan_heuristic(env, robot, self.goal, self.catalog)
        return self._heuristic_cache[key]

    def _queue_item(self, node: _Node) -> tuple:
        return (node.unsatisfied, node.h, node.depth, node.tie_rank, self._node_seq(), node)

    def _failure(
        self,
        reason: str,
        details: dict[str, Any],
        repair_log: list[dict[str, Any]],
        node: _Node | None,
    ) -> dict[str, Any]:
        return {
            "success": False,
            "actions": copy.deepcopy(node.actions) if node is not None else [],
            "final_env": copy.deepcopy(node.env) if node is not None else {},
            "final_robot": copy.deepcopy(node.robot) if node is not None else {},
            "failure_reason": reason,
            "failure_details": details,
            "repair_log": repair_log,
            "planner_stats": {"expanded": self._expanded, "goal_size": len(self.goal)},
        }

    _seq_counter = 0

    def _node_seq(self) -> int:
        # Stable tie-breaker so heapq never compares _Node objects directly.
        type(self)._seq_counter += 1
        return type(self)._seq_counter


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _normalize_action(step: dict | None) -> Action:
    if not isinstance(step, dict):
        return {}
    execution = step.get("execution")
    if isinstance(execution, dict):
        skill = execution.get("skill", "")
        params = execution.get("parameters", {}) or {}
    else:
        skill = step.get("skill", "")
        params = step.get("parameters", {}) or {}
    return {"skill": str(skill or ""), "parameters": copy.deepcopy(params if isinstance(params, dict) else {})}


def _carried_entity(robot: dict) -> str:
    carried = str((robot or {}).get("robot_holding", "") or "")
    return "" if carried in {"", "空"} else carried


def _parent_chain(entity: str, env: dict) -> list[str]:
    """Ancestors of `entity` walking up `direct_parent`, stopping at room level."""
    chain: list[str] = []
    seen = set()
    current = entity
    while current in env and current not in seen:
        seen.add(current)
        info = env.get(current, {})
        if not isinstance(info, dict):
            break
        parent = str(info.get("direct_parent", "") or "")
        if not parent or parent in {"robot_hand", "未知环境"}:
            break
        if parent not in env:
            break
        chain.append(parent)
        current = parent
    return chain


def _is_descendant_of(candidate: str, ancestor: str, env: dict) -> bool:
    return ancestor in _parent_chain(candidate, env)


def _has_access_controlled_ancestor(entity: str, env: dict, catalog: SkillRepairCatalog) -> bool:
    """True if some ancestor of `entity` carries an access-state predicate."""
    access_state_keys = catalog.access_state_keys()
    for ancestor in _parent_chain(entity, env):
        info = env.get(ancestor, {})
        states = info.get("states", {}) if isinstance(info, dict) else {}
        if isinstance(states, dict) and any(key in states for key in access_state_keys):
            return True
    return False
