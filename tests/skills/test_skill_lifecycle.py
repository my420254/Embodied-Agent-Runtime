import json

from skills.contracts import SkillContract, load_all_skill_contracts, load_skill_contracts
from skills.governance.lifecycle import (
    SkillEvalResult,
    load_skill_eval_results,
    summarize_skill_lifecycle,
    validate_skill_lifecycle,
    validate_skill_library_lifecycle,
)


def test_skill_contracts_follow_the_configured_profile():
    contracts = load_skill_contracts("core_household")

    assert "NavigateTo" in contracts
    assert "Slice" in contracts
    assert "Read" not in contracts
    assert contracts["Slice"].handler == "skills.Slice.handler:SliceSkill"


def test_validate_skill_lifecycle_accepts_deployed_skill_with_evidence():
    contract = load_all_skill_contracts()["ToggleOff"]
    evidence = (
        SkillEvalResult(contract.skill_id, "toggle_off_sandbox", "sandbox", True),
        SkillEvalResult(contract.skill_id, "toggle_off_regression", "regression", True),
    )

    report = validate_skill_lifecycle(contract, evidence)

    assert report.deployable is True
    assert all(gate.passed for gate in report.gates)


def test_validate_skill_lifecycle_requires_regression_evidence():
    contract = load_all_skill_contracts()["ToggleOff"]

    report = validate_skill_lifecycle(
        contract,
        (SkillEvalResult(contract.skill_id, "toggle_off_sandbox", "sandbox", True),),
    )

    regression = next(gate for gate in report.gates if gate.name == "regression_eval")
    assert report.deployable is False
    assert regression.reason == "deployed skill requires regression eval evidence"


def test_validate_skill_lifecycle_rejects_high_risk_skill_without_policy():
    contract = SkillContract(
        skill_id="Heat",
        description="Heat an item.",
        parameters={"target_item": "string"},
        handler="skills.Heat.handler:HeatHandler",
        execution_domain="机械臂控制",
    )
    evidence = (
        SkillEvalResult("Heat", "heat_sandbox", "sandbox", True),
        SkillEvalResult("Heat", "heat_regression", "regression", True),
    )

    report = validate_skill_lifecycle(contract, evidence)

    high_risk = next(gate for gate in report.gates if gate.name == "high_risk_policy")
    assert report.deployable is False
    assert high_risk.reason == "missing failure_policy for Heat"


def test_summarize_skill_lifecycle_reports_failed_gates():
    safe = load_all_skill_contracts()["ToggleOff"]
    unsafe = SkillContract(
        skill_id="Heat",
        description="Heat an item.",
        parameters={"target_item": "string"},
        handler="skills.Heat.handler:HeatHandler",
        execution_domain="机械臂控制",
    )
    evidence = (
        SkillEvalResult("ToggleOff", "off_sandbox", "sandbox", True),
        SkillEvalResult("ToggleOff", "off_regression", "regression", True),
        SkillEvalResult("Heat", "heat_sandbox", "sandbox", True),
    )

    reports = validate_skill_library_lifecycle((safe, unsafe), evidence)
    summary = summarize_skill_lifecycle(reports)

    assert summary.skill_count == 2
    assert summary.deployable_count == 1
    assert summary.failed_gate_counts == {"regression_eval": 1, "high_risk_policy": 1}
    assert summary.failed_gate_skill_ids == {
        "regression_eval": ("Heat",),
        "high_risk_policy": ("Heat",),
    }


def test_load_skill_eval_results_reads_json_case_file(tmp_path):
    case_file = tmp_path / "skill_eval_cases.json"
    case_file.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "skill_id": "NavigateTo",
                        "case_id": "navigate_sandbox",
                        "suite": "sandbox",
                        "passed": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    assert load_skill_eval_results(case_file) == (
        SkillEvalResult("NavigateTo", "navigate_sandbox", "sandbox", True),
    )


def test_all_configured_skills_have_default_lifecycle_evidence():
    contracts = load_all_skill_contracts()
    reports = validate_skill_library_lifecycle(
        contracts.values(),
        load_skill_eval_results(),
    )

    assert set(reports) == set(contracts)
    assert all(report.deployable for report in reports.values())
