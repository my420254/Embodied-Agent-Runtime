from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, runtime_checkable


ApplyAction = Callable[[dict, dict, str, dict], tuple[bool, str, str]]
ValidateAction = Callable[[dict, dict, str, dict], tuple[bool, str, str]]
ApplyEffect = Callable[[dict, dict, str, dict], None]


@dataclass(frozen=True)
class RepairContext:
    todo_list: list[dict[str, Any]]
    validated_steps: list[dict[str, Any]]
    failed_step: dict[str, Any]
    issue_type: str
    fix_advice: str
    failure_env: dict[str, Any]
    failure_robot: dict[str, Any]
    trajectory_records: list[dict[str, Any]]
    sandbox_start_env: dict[str, Any]
    sandbox_start_robot: dict[str, Any]
    structured_task: dict[str, Any]
    relevant_item_names: list[str]
    environment: dict[str, Any]
    skill_profile: str | None
    skill_catalog: Any
    skill_handlers: Mapping[str, Any]
    skill_prompts: str
    apply_action: ApplyAction
    validate_action: ValidateAction | None = None
    skill_closure: list[str] = field(default_factory=list)
    goal_test: Callable[[dict, dict], bool] | None = None
    apply_effect: ApplyEffect | None = None


@dataclass(frozen=True)
class RepairDiagnosis:
    strategy_name: str
    prompt: str
    merge_context: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    disposition: str = "repair"
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RepairAssembly:
    strategy_name: str
    success: bool
    todo_list: list[dict[str, Any]] = field(default_factory=list)
    step_provenance: list[dict[str, Any]] = field(default_factory=list)
    segment_checks: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""


@runtime_checkable
class RepairStrategy(Protocol):
    """Strategy-specific diagnosis and complete-candidate assembly."""

    name: str

    def find_errors(self, context: RepairContext) -> RepairDiagnosis:
        ...

    def reassemble(
        self,
        diagnosis: RepairDiagnosis,
        generated_todo_list: list[dict[str, Any]],
    ) -> RepairAssembly:
        ...


@dataclass(frozen=True)
class RepairSelection:
    strategy: RepairStrategy | None = None
    selected_names: tuple[str, ...] = ()
    error: str = ""


class RepairStrategyRegistry:
    def __init__(
        self,
        strategies: Iterable[RepairStrategy] = (),
        *,
        default_strategy: str | None = None,
    ):
        self._strategies = tuple(strategies)
        self._default_strategy = default_strategy
        names = [strategy.name for strategy in self._strategies]
        if len(names) != len(set(names)):
            raise ValueError("repair strategy names must be unique")

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(strategy.name for strategy in self._strategies)

    def select(self, strategy_name: str | None = None) -> RepairSelection:
        selected = str(strategy_name or self._default_strategy or "").strip().lower()
        if selected in {"none", ""}:
            return RepairSelection()
        if selected.startswith("invalid:"):
            names = tuple(filter(None, selected.removeprefix("invalid:").split(",")))
            return RepairSelection(
                selected_names=names,
                error=(
                    "无效修复策略配置: "
                    f"{', '.join(names) or selected}; "
                    "planning.evaluation.repair_strategy 只允许 "
                    "none/retrac/sda/vcr"
                ),
            )
        strategy = self._strategy_named(selected)
        if strategy is None:
            return RepairSelection(
                selected_names=(selected,),
                error=f"未知修复策略: {selected}",
            )
        return RepairSelection(strategy=strategy, selected_names=(selected,))

    def _strategy_named(self, name: str) -> RepairStrategy | None:
        for strategy in self._strategies:
            if strategy.name == name:
                return strategy
        return None

__all__ = [
    "ApplyAction",
    "ApplyEffect",
    "ValidateAction",
    "RepairAssembly",
    "RepairContext",
    "RepairDiagnosis",
    "RepairSelection",
    "RepairStrategy",
    "RepairStrategyRegistry",
]
