from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.delta.framework.code.launcher import main  # noqa: E402


if __name__ == "__main__":
    os.environ["OURAGENT_FRAMEWORK_ENTRYPOINT"] = "run.py"
    raise SystemExit(main())
