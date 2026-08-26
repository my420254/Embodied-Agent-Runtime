from __future__ import annotations

import re
from pathlib import Path

from interfaces.contracts import CognitiveSkillContract, TaskGraph
from interfaces.services import BrainTask
from skills.loader import SkillSpec, load_enabled_skill_specs


_PARAM_ROW_RE = re.compile(r"^\|\s*([A-Za-z_][A-Za-z0-9_]*)\s*\|\s*([^|]+?)\s*\|")


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


def _contract_from_skill_spec(spec: SkillSpec) -> CognitiveSkillContract:
    parameters = _parameters_from_prompt(spec.path / spec.prompt)
    failure_policy = {}
    if spec.name in {"Clean", "Heat", "Slice", "ToggleOn"}:
        failure_policy = {"on_validation_failure": "repair_or_replan"}
    return CognitiveSkillContract(
        skill_id=spec.name,
        description=spec.description,
        parameters=parameters,
        uses_primitives=(spec.name,),
        applicable_when=("enabled_by_settings",),
        kg_queries=({"query_type": "enabled_skill", "skill": spec.name},),
        success_criteria=("handler.validate passes before handler.apply",),
        failure_policy=failure_policy,
        status="deployed",
        version="settings-driven",
    )


def load_cognitive_skill_contracts() -> dict[str, CognitiveSkillContract]:
    return {
        contract.skill_id: contract
        for spec in load_enabled_skill_specs()
        for contract in (_contract_from_skill_spec(spec),)
    }


SKILL_CONTRACTS: dict[str, CognitiveSkillContract] = load_cognitive_skill_contracts()


class StaticSkillLibrary:
    """Static library built from the currently enabled skills."""

    def __init__(self, contracts: dict[str, CognitiveSkillContract] | None = None) -> None:
        self.contracts = dict(contracts) if contracts is not None else load_cognitive_skill_contracts()

    def get(self, skill_id: str) -> CognitiveSkillContract | None:
        return self.contracts.get(skill_id)

    def get_candidates(self, task: BrainTask, graph: TaskGraph) -> tuple[CognitiveSkillContract, ...]:
        candidate_ids = [
            node.node_id
            for node in graph.nodes
            if node.node_type == "cognitive_skill"
        ]
        if candidate_ids:
            return tuple(self.contracts[skill_id] for skill_id in candidate_ids if skill_id in self.contracts)
        return tuple(self.contracts.values())
