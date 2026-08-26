from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from interfaces.contracts import CognitiveSkillContract

try:
    from domain.action_contracts import PRIMITIVE_ACTIONS as _DOMAIN_PRIMITIVE_ACTIONS
except ModuleNotFoundError:
    _DOMAIN_PRIMITIVE_ACTIONS = ()

try:
    from skills.loader import load_enabled_skill_specs
except Exception:
    load_enabled_skill_specs = None  # type: ignore[assignment]


def _fallback_primitive_actions() -> tuple[str, ...]:
    if not callable(load_enabled_skill_specs):
        return ()
    try:
        return tuple(spec.name for spec in load_enabled_skill_specs())
    except Exception:
        return ()


PRIMITIVE_ACTIONS = tuple(_DOMAIN_PRIMITIVE_ACTIONS) or _fallback_primitive_actions()


ATOMIC_LEVEL = "atomic"
ROUTINE_LEVEL = "routine"
CONCRETE_LEVEL = "concrete"
ABSTRACT_LEVEL = "abstract"

SKILL_PYRAMID_LEVELS = (
    ATOMIC_LEVEL,
    ROUTINE_LEVEL,
    CONCRETE_LEVEL,
    ABSTRACT_LEVEL,
)


@dataclass(frozen=True)
class SkillReuseReference:
    """A typed dependency edge inside the static skill pyramid."""

    skill_id: str
    role: str = "uses"
    note: str = ""


@dataclass(frozen=True)
class SkillPyramidNode:
    skill_id: str
    level: str
    layer: int
    description: str
    uses: tuple[SkillReuseReference, ...] = ()
    parents: tuple[str, ...] = ()
    children: tuple[str, ...] = ()


ROUTINE_SKILL_DEFINITIONS: Mapping[str, SkillPyramidNode] = {
    "routine.navigate_to_target": SkillPyramidNode(
        skill_id="routine.navigate_to_target",
        level=ROUTINE_LEVEL,
        layer=1,
        description="Resolve a task target and move the robot near enough to operate on it.",
        uses=(SkillReuseReference("NavigateTo", "atomic"),),
    ),
    "routine.open_container_for_access": SkillPyramidNode(
        skill_id="routine.open_container_for_access",
        level=ROUTINE_LEVEL,
        layer=1,
        description="Approach an openable container and open it before an access-dependent action.",
        uses=(
            SkillReuseReference("NavigateTo", "atomic"),
            SkillReuseReference("Open", "atomic"),
        ),
    ),
    "routine.acquire_object": SkillPyramidNode(
        skill_id="routine.acquire_object",
        level=ROUTINE_LEVEL,
        layer=1,
        description="Navigate to a portable object, recover access if needed, and pick it up.",
        uses=(
            SkillReuseReference("routine.navigate_to_target", "subskill"),
            SkillReuseReference("Pickup", "atomic"),
        ),
    ),
    "routine.place_object": SkillPyramidNode(
        skill_id="routine.place_object",
        level=ROUTINE_LEVEL,
        layer=1,
        description="Navigate to a destination and place the held item there.",
        uses=(
            SkillReuseReference("NavigateTo", "atomic"),
            SkillReuseReference("Put", "atomic"),
        ),
    ),
    "routine.clean_with_water_source": SkillPyramidNode(
        skill_id="routine.clean_with_water_source",
        level=ROUTINE_LEVEL,
        layer=1,
        description="Bring or target a cleanable object at a water source and clean it.",
        uses=(
            SkillReuseReference("routine.acquire_object", "subskill"),
            SkillReuseReference("Clean", "atomic"),
        ),
    ),
    "routine.toggle_device": SkillPyramidNode(
        skill_id="routine.toggle_device",
        level=ROUTINE_LEVEL,
        layer=1,
        description="Navigate to a switchable device and change its toggled state.",
        uses=(
            SkillReuseReference("NavigateTo", "atomic"),
            SkillReuseReference("ToggleOn", "atomic"),
            SkillReuseReference("ToggleOff", "atomic"),
        ),
    ),
    "routine.close_then_activate_device": SkillPyramidNode(
        skill_id="routine.close_then_activate_device",
        level=ROUTINE_LEVEL,
        layer=1,
        description="Close an appliance or container before activating it.",
        uses=(
            SkillReuseReference("Close", "atomic"),
            SkillReuseReference("ToggleOn", "atomic"),
        ),
    ),
    "routine.heat_item_in_device": SkillPyramidNode(
        skill_id="routine.heat_item_in_device",
        level=ROUTINE_LEVEL,
        layer=1,
        description="Place an item in a heating device, close it when needed, activate it, and heat the item.",
        uses=(
            SkillReuseReference("routine.place_object", "subskill"),
            SkillReuseReference("routine.close_then_activate_device", "subskill"),
            SkillReuseReference("Heat", "atomic"),
        ),
    ),
    "routine.direct_interaction": SkillPyramidNode(
        skill_id="routine.direct_interaction",
        level=ROUTINE_LEVEL,
        layer=1,
        description="Navigate to a visible or reachable object and perform a one-step interaction.",
        uses=(SkillReuseReference("routine.navigate_to_target", "subskill"),),
    ),
}


CONCRETE_SKILL_REUSE: Mapping[str, tuple[SkillReuseReference, ...]] = {
    "cooking.cut_ingredient": (
        SkillReuseReference("routine.acquire_object", "prepare_target"),
        SkillReuseReference("routine.clean_with_water_source", "precondition_repair"),
        SkillReuseReference("routine.place_object", "prepare_surface"),
        SkillReuseReference("Slice", "atomic"),
    ),
    "cooking.make_tea": (
        SkillReuseReference("routine.open_container_for_access", "access"),
        SkillReuseReference("routine.acquire_object", "prepare_ingredients"),
        SkillReuseReference("routine.clean_with_water_source", "precondition_repair"),
        SkillReuseReference("routine.heat_item_in_device", "transform"),
    ),
    "laundry.do_laundry": (
        SkillReuseReference("routine.open_container_for_access", "access"),
        SkillReuseReference("routine.acquire_object", "prepare_load"),
        SkillReuseReference("routine.place_object", "load"),
        SkillReuseReference("routine.close_then_activate_device", "run_machine"),
    ),
    "device.turn_on": (SkillReuseReference("routine.toggle_device", "state_change"),),
    "device.turn_off": (SkillReuseReference("routine.toggle_device", "state_change"),),
    "container.open": (SkillReuseReference("routine.open_container_for_access", "access"),),
    "container.close": (
        SkillReuseReference("routine.navigate_to_target", "locate"),
        SkillReuseReference("Close", "atomic"),
    ),
    "object.put_into_container": (
        SkillReuseReference("routine.open_container_for_access", "access"),
        SkillReuseReference("routine.acquire_object", "prepare_item"),
        SkillReuseReference("routine.place_object", "place"),
        SkillReuseReference("Close", "atomic"),
    ),
    "object.clean": (SkillReuseReference("routine.clean_with_water_source", "clean"),),
    "object.pickup": (SkillReuseReference("routine.acquire_object", "acquire"),),
    "object.read": (
        SkillReuseReference("routine.acquire_object", "optional_acquire"),
        SkillReuseReference("Read", "atomic"),
    ),
    "object.observe": (
        SkillReuseReference("routine.direct_interaction", "inspect"),
        SkillReuseReference("Observe", "atomic"),
    ),
    "object.touch": (
        SkillReuseReference("routine.direct_interaction", "interact"),
        SkillReuseReference("Touch", "atomic"),
    ),
    "device.type_on": (
        SkillReuseReference("routine.direct_interaction", "interact"),
        SkillReuseReference("Type", "atomic"),
    ),
    "object.sleep_on": (
        SkillReuseReference("routine.direct_interaction", "interact"),
        SkillReuseReference("Sleep", "atomic"),
    ),
    "object.drink": (
        SkillReuseReference("routine.acquire_object", "optional_acquire"),
        SkillReuseReference("Drink", "atomic"),
    ),
    "object.sit_on": (
        SkillReuseReference("routine.direct_interaction", "interact"),
        SkillReuseReference("Sit", "atomic"),
    ),
}


ABSTRACT_SKILL_DEFINITIONS: Mapping[str, SkillPyramidNode] = {
    "abstract.acquire_transform_place": SkillPyramidNode(
        skill_id="abstract.acquire_transform_place",
        level=ABSTRACT_LEVEL,
        layer=3,
        description="General schema for acquiring objects, repairing preconditions, transforming them, and placing them.",
        children=(
            "cooking.cut_ingredient",
            "cooking.make_tea",
            "laundry.do_laundry",
            "object.put_into_container",
            "object.clean",
        ),
    ),
    "abstract.container_access_workflow": SkillPyramidNode(
        skill_id="abstract.container_access_workflow",
        level=ABSTRACT_LEVEL,
        layer=3,
        description="General schema for open-access-place-close workflows around containers and appliances.",
        children=(
            "container.open",
            "container.close",
            "object.put_into_container",
            "cooking.make_tea",
            "laundry.do_laundry",
        ),
    ),
    "abstract.device_state_workflow": SkillPyramidNode(
        skill_id="abstract.device_state_workflow",
        level=ABSTRACT_LEVEL,
        layer=3,
        description="General schema for changing state on switchable or typeable devices.",
        children=("device.turn_on", "device.turn_off", "device.type_on"),
    ),
    "abstract.perceive_or_interact": SkillPyramidNode(
        skill_id="abstract.perceive_or_interact",
        level=ABSTRACT_LEVEL,
        layer=3,
        description="General schema for direct object perception and simple embodied interaction.",
        children=(
            "object.observe",
            "object.read",
            "object.touch",
            "object.drink",
            "object.sit_on",
            "object.sleep_on",
        ),
    ),
}


def _is_atomic_contract(skill_id: str, contract: CognitiveSkillContract) -> bool:
    return tuple(contract.uses_primitives) == (skill_id,)


def _primitive_nodes(contracts: Mapping[str, CognitiveSkillContract] | None = None) -> dict[str, SkillPyramidNode]:
    nodes = {
        name: SkillPyramidNode(
            skill_id=name,
            level=ATOMIC_LEVEL,
            layer=0,
            description=f"Indivisible atomic action contract for {name}.",
        )
        for name in PRIMITIVE_ACTIONS
    }
    for skill_id, contract in (contracts or {}).items():
        if _is_atomic_contract(skill_id, contract):
            nodes[skill_id] = SkillPyramidNode(
                skill_id=skill_id,
                level=ATOMIC_LEVEL,
                layer=0,
                description=contract.description,
            )
    return nodes


def _concrete_nodes(contracts: Mapping[str, CognitiveSkillContract]) -> dict[str, SkillPyramidNode]:
    abstract_parents = _parents_by_child(ABSTRACT_SKILL_DEFINITIONS)
    return {
        skill_id: SkillPyramidNode(
            skill_id=skill_id,
            level=CONCRETE_LEVEL,
            layer=2,
            description=contract.description,
            uses=CONCRETE_SKILL_REUSE.get(
                skill_id,
                tuple(SkillReuseReference(primitive, "atomic") for primitive in contract.uses_primitives),
            ),
            parents=abstract_parents.get(skill_id, ()),
        )
        for skill_id, contract in contracts.items()
        if not _is_atomic_contract(skill_id, contract)
    }


def _parents_by_child(nodes: Mapping[str, SkillPyramidNode]) -> dict[str, tuple[str, ...]]:
    parents: dict[str, list[str]] = {}
    for parent_id, node in nodes.items():
        for child_id in node.children:
            parents.setdefault(child_id, []).append(parent_id)
    return {child_id: tuple(parent_ids) for child_id, parent_ids in parents.items()}


def _children_by_reuse(nodes: Mapping[str, SkillPyramidNode]) -> dict[str, tuple[str, ...]]:
    children: dict[str, list[str]] = {}
    for skill_id, node in nodes.items():
        for ref in node.uses:
            children.setdefault(ref.skill_id, []).append(skill_id)
    return {dependency_id: tuple(child_ids) for dependency_id, child_ids in children.items()}


def build_static_skill_pyramid(
    contracts: Mapping[str, CognitiveSkillContract] | None = None,
) -> dict[str, SkillPyramidNode]:
    """Build the current static skill pyramid without changing planning behavior."""

    if contracts is None:
        from cognitive.skill_library import SKILL_CONTRACTS

        contracts = SKILL_CONTRACTS

    nodes: dict[str, SkillPyramidNode] = {}
    nodes.update(_primitive_nodes(contracts))
    nodes.update(ROUTINE_SKILL_DEFINITIONS)
    nodes.update(_concrete_nodes(contracts))

    reuse_children = _children_by_reuse(nodes)
    for skill_id, node in tuple(nodes.items()):
        if skill_id in reuse_children:
            nodes[skill_id] = SkillPyramidNode(
                skill_id=node.skill_id,
                level=node.level,
                layer=node.layer,
                description=node.description,
                uses=node.uses,
                parents=node.parents,
                children=reuse_children[skill_id],
            )

    for skill_id, node in ABSTRACT_SKILL_DEFINITIONS.items():
        children = tuple(child_id for child_id in node.children if child_id in nodes)
        if not children:
            continue
        nodes[skill_id] = SkillPyramidNode(
            skill_id=node.skill_id,
            level=node.level,
            layer=node.layer,
            description=node.description,
            uses=node.uses,
            parents=node.parents,
            children=children,
        )
    return nodes


def skill_ids_by_level(
    level: str,
    nodes: Mapping[str, SkillPyramidNode] | None = None,
) -> tuple[str, ...]:
    if nodes is None:
        nodes = build_static_skill_pyramid()
    return tuple(skill_id for skill_id, node in nodes.items() if node.level == level)


def get_skill_pyramid_node(
    skill_id: str,
    nodes: Mapping[str, SkillPyramidNode] | None = None,
) -> SkillPyramidNode | None:
    if nodes is None:
        nodes = build_static_skill_pyramid()
    return nodes.get(skill_id)


def direct_reuse_chain(
    skill_id: str,
    nodes: Mapping[str, SkillPyramidNode] | None = None,
) -> tuple[SkillPyramidNode, ...]:
    if nodes is None:
        nodes = build_static_skill_pyramid()
    node = nodes.get(skill_id)
    if node is None:
        return ()
    return tuple(nodes[ref.skill_id] for ref in node.uses if ref.skill_id in nodes)


def validate_skill_pyramid(
    contracts: Mapping[str, CognitiveSkillContract] | None = None,
    nodes: Mapping[str, SkillPyramidNode] | None = None,
) -> tuple[str, ...]:
    if contracts is None:
        from cognitive.skill_library import SKILL_CONTRACTS

        contracts = SKILL_CONTRACTS
    if nodes is None:
        nodes = build_static_skill_pyramid(contracts)

    issues: list[str] = []
    primitive_ids = set(PRIMITIVE_ACTIONS) | {
        skill_id
        for skill_id, contract in contracts.items()
        if _is_atomic_contract(skill_id, contract)
    }

    for skill_id, contract in contracts.items():
        node = nodes.get(skill_id)
        if node is None:
            issues.append(f"missing skill node: {skill_id}")
            continue
        expected_level = ATOMIC_LEVEL if _is_atomic_contract(skill_id, contract) else CONCRETE_LEVEL
        if node.level != expected_level:
            issues.append(f"skill node {skill_id} must be level={expected_level}")
        for primitive in contract.uses_primitives:
            if primitive not in primitive_ids:
                issues.append(f"skill {skill_id} uses unknown primitive {primitive}")

    for skill_id, node in nodes.items():
        if node.level not in SKILL_PYRAMID_LEVELS:
            issues.append(f"node {skill_id} has unknown level {node.level}")
        for ref in node.uses:
            if ref.skill_id not in nodes:
                issues.append(f"node {skill_id} uses missing skill {ref.skill_id}")
        for parent_id in node.parents:
            if parent_id not in nodes:
                issues.append(f"node {skill_id} has missing parent {parent_id}")
        for child_id in node.children:
            if child_id not in nodes:
                issues.append(f"node {skill_id} has missing child {child_id}")

    return tuple(issues)
