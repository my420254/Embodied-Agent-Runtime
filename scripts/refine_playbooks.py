import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ace.refine import refine_playbook
from ace.storage import PLAYBOOK_DIR
from config.settings import project_path


def _available_sections() -> list[str]:
    playbook_dir = project_path(PLAYBOOK_DIR)
    if not playbook_dir.exists():
        return []
    return sorted(path.stem for path in playbook_dir.glob("*.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Refine ACE playbooks by merging duplicates and deprecating harmful rules.")
    parser.add_argument("--section", action="append", help="Section to refine. Defaults to every playbook section.")
    parser.add_argument("--duplicate-similarity", type=float, default=None)
    parser.add_argument("--keep-harmful", action="store_true", help="Do not deprecate rules with consistently harmful feedback.")
    args = parser.parse_args()

    sections = args.section or _available_sections()
    results = [
        refine_playbook(
            section,
            duplicate_similarity=args.duplicate_similarity,
            prune_harmful=not args.keep_harmful,
        )
        for section in sections
    ]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
