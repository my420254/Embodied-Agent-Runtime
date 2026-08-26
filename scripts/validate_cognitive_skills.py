from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cognitive.skill_lifecycle import (
    load_skill_eval_results,
    summarize_skill_lifecycle,
    validate_skill_library_lifecycle,
)
from cognitive.skill_library import StaticSkillLibrary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate CognitiveSkill lifecycle gates.")
    parser.add_argument(
        "--eval-cases",
        default=None,
        help="JSON skill eval case file. Defaults to cognitive/skill_eval_cases.json.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional metrics JSON output path for CI/dashboard artifacts.",
    )
    args = parser.parse_args(argv)

    eval_results = load_skill_eval_results(args.eval_cases)
    reports = validate_skill_library_lifecycle(StaticSkillLibrary().contracts.values(), eval_results)
    summary = summarize_skill_lifecycle(reports)
    payload = {
        "passed": all(report.deployable for report in reports.values()),
        "summary": summary.as_dict(),
        "reports": {skill_id: report.as_dict() for skill_id, report in reports.items()},
    }
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
