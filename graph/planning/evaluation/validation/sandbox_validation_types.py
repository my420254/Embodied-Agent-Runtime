from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class SandboxValidationContext:
    intent: str
    memory: dict
    iters: int
    max_iterations: int
    feature_flags: dict | None
    injected_rule_ids: list[str] | None
    debug_events: list[dict[str, Any]]
    retrac_active: bool
    sda_active: bool
    apply_action: Callable[..., tuple[bool, str, str]]


@dataclass
class SandboxValidationResult:
    sim_env: dict[str, dict[str, Any]]
    sim_robot: dict[str, Any]
    sandbox_start_env: dict[str, dict[str, Any]]
    sandbox_start_robot: dict[str, Any]
    todo_list: list[dict[str, Any]]
    validated_steps: list[dict[str, Any]]
    validated_todo_actions: list[dict[str, Any]]
    validated_audit_steps: list[dict[str, Any]]
    trajectory_str: str
    sda_success_state: dict[str, Any] | None = None
    failure_payload: dict[str, Any] | None = None


@dataclass
class TodoValidationResult:
    todo_list: list[dict[str, Any]]
    validated_steps: list[dict[str, Any]]
    sim_env: dict[str, dict[str, Any]]
    sim_robot: dict[str, Any]
    sda_success_state: dict[str, Any] | None = None
    failure_payload: dict[str, Any] | None = None
