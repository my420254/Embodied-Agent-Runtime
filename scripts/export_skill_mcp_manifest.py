#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from adapters.mcp_skill_adapter import export_mcp_skill_manifest
from config.settings import project_path


def main() -> None:
    parser = argparse.ArgumentParser(description="导出 OurAgent 技能为 MCP 风格工具清单。")
    parser.add_argument(
        "--output",
        default=str(project_path("docs", "mcp_skill_manifest.json")),
        help="输出 JSON 文件路径，默认写入 docs/mcp_skill_manifest.json。",
    )
    parser.add_argument("--profile", default=None, help="技能 profile，默认使用 settings.json。")
    parser.add_argument("--include-all", action="store_true", help="导出 skills/ 下全部技能。")
    args = parser.parse_args()

    output = export_mcp_skill_manifest(
        args.output,
        profile=args.profile,
        include_all=args.include_all,
    )
    print(f"MCP skill manifest exported: {output}")


if __name__ == "__main__":
    main()
