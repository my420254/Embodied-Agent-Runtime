from __future__ import annotations

from pathlib import Path


STANDARD_TRACE_ARTIFACT_FILES = (
    "case_input.json",
    "case_input_summary.json",
    "prepared_environment.json",
    "prepared_environment_summary.json",
    "environment_audit.json",
    "understanding_input.json",
    "understanding_input_summary.json",
    "understanding_output.json",
    "understanding_output_summary.json",
    "planning_input.json",
    "planning_input_summary.json",
    "planning_output.json",
    "planning_output_summary.json",
    "contract_audit.json",
    "planning_feature_records.json",
    "llm_io.json",
    "goal_check.json",
    "official_eval.json",
    "process_summary.json",
)


def append_stage_artifact_overview(lines: list[str], artifacts_dir: Path) -> None:
    lines.append(f"- 完整阶段 artifact：`{artifacts_dir}`")
    lines.append("- 完整输入输出 / 审计文件：" + ", ".join(f"`{name}`" for name in STANDARD_TRACE_ARTIFACT_FILES))
