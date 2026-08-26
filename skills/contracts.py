"""Typed contracts derived from configured executable skills."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from skills.loader import (
    SkillSpec,
    get_default_profile,
    load_enabled_skill_specs,
    load_skill_spec,
    load_skills_config,
)
from config.settings import project_path


_PARAM_ROW_RE = re.compile(r"^\|\s*([A-Za-z_][A-Za-z0-9_]*)\s*\|\s*([^|]+?)\s*\|")
_HIGH_RISK_SKILLS = frozenset({"Clean", "Heat", "Slice", "ToggleOn"})


@dataclass(frozen=True)
class SkillContract:
    skill_id: str
    description: str
    parameters: dict[str, str]
    handler: str
    execution_domain: str = ""
    planning_contract: dict[str, str] = field(default_factory=dict)
    failure_policy: dict[str, str] = field(default_factory=dict)
    status: str = "deployed"
    version: str = "skill-profile"


def _parameters_from_prompt(prompt_path: Path) -> dict[str, str]:
    try:
        text = prompt_path.read_text(encoding="utf-8")
    except OSError:
        return {}

    parameters: dict[str, str] = {}
    for raw_line in text.splitlines():
        match = _PARAM_ROW_RE.match(raw_line.strip())
        if not match:
            continue
        name, value_type = match.groups()
        if name.lower() in {"参数", "参数名", "name", "parameter"}:
            continue
        parameters[name] = value_type.strip() or "string"
    return parameters


def _contract_from_spec(spec: SkillSpec) -> SkillContract:
    failure_policy = (
        {"on_validation_failure": "repair_or_replan"}
        if spec.name in _HIGH_RISK_SKILLS
        else {}
    )
    return SkillContract(
        skill_id=spec.name,
        description=spec.description,
        parameters=_parameters_from_prompt(spec.path / spec.prompt),
        handler=spec.handler,
        execution_domain=spec.execution_domain,
        planning_contract=dict(spec.planning_contract),
        failure_policy=failure_policy,
    )


def load_skill_contracts(profile: str | None = None) -> dict[str, SkillContract]:
    return {
        spec.name: _contract_from_spec(spec)
        for spec in load_enabled_skill_specs(profile or get_default_profile())
    }


def load_all_skill_contracts() -> dict[str, SkillContract]:
    config = load_skills_config()
    root_value = str(config.get("root", "skills") or "skills")
    root = Path(root_value)
    if not root.is_absolute():
        root = project_path(root_value)
    enabled = config.get("enabled", []) if isinstance(config, dict) else []
    names = {
        str(name)
        for name in enabled
        if name
    }
    if root.exists():
        names.update(path.name for path in root.iterdir() if (path / "skill.yaml").exists())
    contracts: dict[str, SkillContract] = {}
    for name in sorted(names):
        spec = load_skill_spec(name)
        if spec is not None:
            contracts[spec.name] = _contract_from_spec(spec)
    return contracts


__all__ = ["SkillContract", "load_all_skill_contracts", "load_skill_contracts"]
