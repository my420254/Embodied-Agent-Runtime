from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ace.screening import apply_screening_records


def load_records(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("comparisons", [])
    if not isinstance(data, list):
        raise ValueError("comparison file must contain a list or {'comparisons': [...]}")
    return [item for item in data if isinstance(item, dict)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate ACE candidate rules against train-split A/B comparison records."
    )
    parser.add_argument("--section", default="planning")
    parser.add_argument("--comparisons", required=True, help="JSON list of candidate-rule A/B comparison records.")
    parser.add_argument("--promote_helpful_threshold", type=int, default=3)
    parser.add_argument("--max_harmful_for_promotion", type=int, default=0)
    parser.add_argument("--deprecate_harmful_threshold", type=int, default=1)
    args = parser.parse_args()

    records = load_records(args.comparisons)
    summary = apply_screening_records(
        args.section,
        records,
        promote_helpful_threshold=args.promote_helpful_threshold,
        max_harmful_for_promotion=args.max_harmful_for_promotion,
        deprecate_harmful_threshold=args.deprecate_harmful_threshold,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
