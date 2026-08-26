from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from config.settings import project_path
from interfaces.contracts import CognitiveSkillContract


HIGH_RISK_PRIMITIVES = frozenset({"Slice", "Heat", "ToggleOn", "Clean"})
ALLOWED_SKILL_STATUSES = frozenset({"draft", "candidate", "validated", "deployed", "deprecated"})
DEFAULT_SKILL_EVAL_CASES_FILE = project_path("cognitive", "skill_eval_cases.json")


@dataclass(frozen=True)
class SkillEvalResult:
    skill_id: str
    case_id: str
    suite: str
    passed: bool
    failure_category: str = ""


@dataclass(frozen=True)
class SkillLifecycleGate:
    name: str
    passed: bool
    reason: str = ""


@dataclass(frozen=True)
class SkillLifecycleEvidenceSummary:
    case_count: int
    passed_count: int
    failed_count: int
    suite_counts: dict[str, int]
    suite_pass_counts: dict[str, int]
    suite_failed_counts: dict[str, int]
    suite_pass_rates: dict[str, float]
    failure_category_counts: dict[str, int]
    failed_case_ids: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "case_count": self.case_count,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "suite_counts": dict(self.suite_counts),
            "suite_pass_counts": dict(self.suite_pass_counts),
            "suite_failed_counts": dict(self.suite_failed_counts),
            "suite_pass_rates": dict(self.suite_pass_rates),
            "failure_category_counts": dict(self.failure_category_counts),
            "failed_case_ids": list(self.failed_case_ids),
        }


@dataclass(frozen=True)
class SkillLifecycleReport:
    skill_id: str
    status: str
    deployable: bool
    gates: tuple[SkillLifecycleGate, ...]
    evidence: SkillLifecycleEvidenceSummary

    def as_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "status": self.status,
            "deployable": self.deployable,
            "gates": [
                {"name": gate.name, "passed": gate.passed, "reason": gate.reason}
                for gate in self.gates
            ],
            "evidence": self.evidence.as_dict(),
        }


@dataclass(frozen=True)
class SkillLifecycleSummary:
    skill_count: int
    deployable_count: int
    deployable_rate: float
    status_counts: dict[str, int]
    failed_gate_counts: dict[str, int]
    failed_gate_skill_ids: dict[str, tuple[str, ...]]
    gate_pass_rates: dict[str, float]
    suite_counts: dict[str, int]
    suite_pass_rates: dict[str, float]
    failure_category_counts: dict[str, int]

    def as_dict(self) -> dict:
        return {
            "skill_count": self.skill_count,
            "deployable_count": self.deployable_count,
            "deployable_rate": self.deployable_rate,
            "status_counts": dict(self.status_counts),
            "failed_gate_counts": dict(self.failed_gate_counts),
            "failed_gate_skill_ids": {
                gate_name: list(skill_ids)
                for gate_name, skill_ids in self.failed_gate_skill_ids.items()
            },
            "gate_pass_rates": dict(self.gate_pass_rates),
            "suite_counts": dict(self.suite_counts),
            "suite_pass_rates": dict(self.suite_pass_rates),
            "failure_category_counts": dict(self.failure_category_counts),
        }


def validate_skill_lifecycle(
    contract: CognitiveSkillContract,
    eval_results: Iterable[SkillEvalResult] = (),
) -> SkillLifecycleReport:
    results = tuple(result for result in eval_results if result.skill_id == contract.skill_id)
    gates = (
        _status_gate(contract),
        _metadata_gate(contract),
        _sandbox_gate(contract, results),
        _regression_gate(contract, results),
        _high_risk_gate(contract),
    )
    return SkillLifecycleReport(
        skill_id=contract.skill_id,
        status=contract.status,
        deployable=all(gate.passed for gate in gates),
        gates=gates,
        evidence=_summarize_eval_results(results),
    )


def validate_skill_library_lifecycle(
    contracts: Iterable[CognitiveSkillContract],
    eval_results: Iterable[SkillEvalResult] = (),
) -> dict[str, SkillLifecycleReport]:
    results = tuple(eval_results)
    return {contract.skill_id: validate_skill_lifecycle(contract, results) for contract in contracts}


def summarize_skill_lifecycle(
    reports: Mapping[str, SkillLifecycleReport] | Iterable[SkillLifecycleReport],
) -> SkillLifecycleSummary:
    report_values = tuple(reports.values() if isinstance(reports, Mapping) else reports)
    skill_count = len(report_values)
    deployable_count = sum(1 for report in report_values if report.deployable)
    status_counts: dict[str, int] = {}
    failed_gate_counts: dict[str, int] = {}
    failed_gate_skill_ids: dict[str, list[str]] = {}
    gate_totals: dict[str, int] = {}
    gate_passed: dict[str, int] = {}
    suite_totals: dict[str, int] = {}
    suite_passed: dict[str, int] = {}
    failure_category_counts: dict[str, int] = {}

    for report in report_values:
        status_counts[report.status] = status_counts.get(report.status, 0) + 1
        for gate in report.gates:
            gate_totals[gate.name] = gate_totals.get(gate.name, 0) + 1
            if gate.passed:
                gate_passed[gate.name] = gate_passed.get(gate.name, 0) + 1
            else:
                failed_gate_counts[gate.name] = failed_gate_counts.get(gate.name, 0) + 1
                failed_gate_skill_ids.setdefault(gate.name, []).append(report.skill_id)
        for suite, count in report.evidence.suite_counts.items():
            suite_totals[suite] = suite_totals.get(suite, 0) + count
        for suite, count in report.evidence.suite_pass_counts.items():
            suite_passed[suite] = suite_passed.get(suite, 0) + count
        for category, count in report.evidence.failure_category_counts.items():
            failure_category_counts[category] = failure_category_counts.get(category, 0) + count

    return SkillLifecycleSummary(
        skill_count=skill_count,
        deployable_count=deployable_count,
        deployable_rate=_rate(deployable_count, skill_count),
        status_counts=status_counts,
        failed_gate_counts=failed_gate_counts,
        failed_gate_skill_ids={
            gate_name: tuple(skill_ids)
            for gate_name, skill_ids in failed_gate_skill_ids.items()
        },
        gate_pass_rates={
            gate_name: _rate(gate_passed.get(gate_name, 0), total)
            for gate_name, total in gate_totals.items()
        },
        suite_counts=suite_totals,
        suite_pass_rates={
            suite: _rate(suite_passed.get(suite, 0), total)
            for suite, total in suite_totals.items()
        },
        failure_category_counts=failure_category_counts,
    )


def load_skill_eval_results(path: str | Path | None = None) -> tuple[SkillEvalResult, ...]:
    eval_path = Path(path) if path is not None else DEFAULT_SKILL_EVAL_CASES_FILE
    data = json.loads(eval_path.read_text(encoding="utf-8"))
    raw_cases = data.get("cases", data) if isinstance(data, dict) else data
    if not isinstance(raw_cases, list):
        raise ValueError("skill eval case file must contain a list or {'cases': [...]}")

    results: list[SkillEvalResult] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        if not isinstance(raw_case, dict):
            raise ValueError(f"skill eval case #{index} must be an object")
        results.append(
            SkillEvalResult(
                skill_id=str(raw_case.get("skill_id", "")),
                case_id=str(raw_case.get("case_id", "")),
                suite=str(raw_case.get("suite", "")),
                passed=bool(raw_case.get("passed", False)),
                failure_category=str(raw_case.get("failure_category", "")),
            )
        )
    return tuple(results)


def _metadata_gate(contract: CognitiveSkillContract) -> SkillLifecycleGate:
    missing = []
    if not contract.uses_primitives:
        missing.append("uses_primitives")
    if not contract.kg_queries:
        missing.append("kg_queries")
    if not contract.success_criteria:
        missing.append("success_criteria")
    if missing:
        return SkillLifecycleGate("metadata_contract", False, f"missing {', '.join(missing)}")
    return SkillLifecycleGate("metadata_contract", True)


def _status_gate(contract: CognitiveSkillContract) -> SkillLifecycleGate:
    if contract.status not in ALLOWED_SKILL_STATUSES:
        return SkillLifecycleGate("status_contract", False, f"unknown lifecycle status {contract.status!r}")
    if contract.status == "deprecated":
        return SkillLifecycleGate("status_contract", False, "deprecated skill is not deployable")
    return SkillLifecycleGate("status_contract", True)


def _sandbox_gate(contract: CognitiveSkillContract, results: tuple[SkillEvalResult, ...]) -> SkillLifecycleGate:
    sandbox_results = [result for result in results if result.suite == "sandbox"]
    if not sandbox_results:
        return SkillLifecycleGate("sandbox_eval", False, "missing sandbox eval evidence")
    if not all(result.passed for result in sandbox_results):
        return SkillLifecycleGate("sandbox_eval", False, "one or more sandbox eval cases failed")
    return SkillLifecycleGate("sandbox_eval", True)


def _regression_gate(contract: CognitiveSkillContract, results: tuple[SkillEvalResult, ...]) -> SkillLifecycleGate:
    regression_results = [result for result in results if result.suite == "regression"]
    if contract.status == "deployed" and not regression_results:
        return SkillLifecycleGate("regression_eval", False, "deployed skill requires regression eval evidence")
    if not all(result.passed for result in regression_results):
        return SkillLifecycleGate("regression_eval", False, "one or more regression eval cases failed")
    return SkillLifecycleGate("regression_eval", True)


def _high_risk_gate(contract: CognitiveSkillContract) -> SkillLifecycleGate:
    risky = sorted(set(contract.uses_primitives) & HIGH_RISK_PRIMITIVES)
    if not risky:
        return SkillLifecycleGate("high_risk_policy", True)
    if not contract.failure_policy:
        return SkillLifecycleGate("high_risk_policy", False, f"missing failure_policy for {', '.join(risky)}")
    return SkillLifecycleGate("high_risk_policy", True)


def _summarize_eval_results(results: tuple[SkillEvalResult, ...]) -> SkillLifecycleEvidenceSummary:
    suite_counts: dict[str, int] = {}
    suite_pass_counts: dict[str, int] = {}
    suite_failed_counts: dict[str, int] = {}
    failure_category_counts: dict[str, int] = {}
    failed_case_ids: list[str] = []

    for result in results:
        suite = result.suite or "unknown"
        suite_counts[suite] = suite_counts.get(suite, 0) + 1
        if result.passed:
            suite_pass_counts[suite] = suite_pass_counts.get(suite, 0) + 1
        else:
            suite_failed_counts[suite] = suite_failed_counts.get(suite, 0) + 1
            failed_case_ids.append(result.case_id)
            category = result.failure_category or "uncategorized"
            failure_category_counts[category] = failure_category_counts.get(category, 0) + 1

    passed_count = sum(1 for result in results if result.passed)
    failed_count = len(results) - passed_count
    return SkillLifecycleEvidenceSummary(
        case_count=len(results),
        passed_count=passed_count,
        failed_count=failed_count,
        suite_counts=suite_counts,
        suite_pass_counts=suite_pass_counts,
        suite_failed_counts=suite_failed_counts,
        suite_pass_rates={
            suite: _rate(suite_pass_counts.get(suite, 0), count)
            for suite, count in suite_counts.items()
        },
        failure_category_counts=failure_category_counts,
        failed_case_ids=tuple(failed_case_ids),
    )


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator
