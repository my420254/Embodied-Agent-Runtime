"""Decode configured skill calls into the shared execution shape."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from functools import lru_cache

from skills.contracts import SkillContract, load_all_skill_contracts, load_skill_contracts

_ACTION_CALL_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\((.*)\)\s*$")


@lru_cache(maxsize=16)
def _contracts(profile: str = "") -> dict[str, SkillContract]:
    return load_skill_contracts(profile or None)


@lru_cache(maxsize=1)
def _all_contracts() -> dict[str, SkillContract]:
    return load_all_skill_contracts()


@lru_cache(maxsize=16)
def _parameter_orders(profile: str = "") -> dict[str, tuple[str, ...]]:
    return {
        name: tuple(contract.parameters)
        for name, contract in _contracts(profile).items()
    }


def action_domain(skill: str, profile: str | None = None) -> str:
    """Return the execution domain declared by the skill itself."""
    contract = _contracts(profile or "").get(skill) or _all_contracts().get(skill)
    return contract.execution_domain if contract and contract.execution_domain else "通用控制"


def _strip_arg(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _split_action_args(raw_args: str) -> list[str]:
    if not raw_args.strip():
        return []
    args = []
    current = []
    quote = ""
    escape = False
    for char in raw_args:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\" and quote:
            current.append(char)
            escape = True
            continue
        if char in ("'", '"'):
            current.append(char)
            quote = "" if quote == char else (char if not quote else quote)
            continue
        if char == "," and not quote:
            args.append(_strip_arg("".join(current)))
            current = []
            continue
        current.append(char)
    args.append(_strip_arg("".join(current)))
    return args


def _parse_action_call(
    text: str,
    parameter_orders: Mapping[str, Sequence[str]],
) -> tuple[str, dict]:
    match = _ACTION_CALL_RE.match(text or "")
    if not match:
        return "", {}
    skill = match.group(1)
    args = _split_action_args(match.group(2))
    if not args:
        return skill, {}

    if all("=" in arg for arg in args):
        params = {}
        for arg in args:
            key, value = arg.split("=", 1)
            params[key.strip()] = _strip_arg(value)
        return skill, params

    parameter_order = list(parameter_orders.get(skill, ()))
    if len(args) > len(parameter_order):
        return skill, {}
    return skill, {parameter_order[index]: value for index, value in enumerate(args)}


def parse_action_call(text: str, profile: str | None = None) -> tuple[str, dict]:
    """Parse a compact action call using the selected skill profile."""
    return _parse_action_call(text, _parameter_orders(profile or ""))


def format_action_call(act_name: str, params: dict) -> str:
    if not params:
        return f"{act_name}()"
    args = ", ".join(f"{key}={value}" for key, value in params.items())
    return f"{act_name}({args})"


def extract_action(item, profile: str | None = None) -> tuple[str, dict, str]:
    if isinstance(item, str):
        act_name, params = parse_action_call(item, profile)
        action = format_action_call(act_name, params) if act_name else item
        return act_name, params, action
    if isinstance(item, dict):
        execution = item.get("execution")
        if isinstance(execution, dict):
            act_name = execution.get("skill", "")
            params = execution.get("parameters", {}) or {}
            return act_name, params, format_action_call(act_name, params)
        act_name = item.get("skill", "")
        params = item.get("parameters", {}) or {}
        if act_name:
            return act_name, params, format_action_call(act_name, params)
    return "", {}, str(item)


def ensure_execution_shape(step, profile: str | None = None) -> dict:
    if isinstance(step, str):
        act, params, _ = extract_action(step, profile)
        return {"execution": {"skill": act, "parameters": params}} if act else {}
    if not isinstance(step, dict):
        return {}
    act, params, _ = extract_action(step, profile)
    if act and not step.get("execution"):
        step["execution"] = {"skill": act, "parameters": params}
    return step


def summarize_action_targets(params: dict) -> tuple[str, str]:
    target = ""
    location = ""
    for key, value in params.items():
        if not value:
            continue
        if not target and ("target" in key or key == "object"):
            target = value
            continue
        if not location and any(
            token in key
            for token in (
                "location",
                "destination",
                "surface",
                "source",
                "device",
                "receptacle",
            )
        ):
            location = value
    return target, location


__all__ = [
    "action_domain",
    "ensure_execution_shape",
    "extract_action",
    "format_action_call",
    "parse_action_call",
    "summarize_action_targets",
]
