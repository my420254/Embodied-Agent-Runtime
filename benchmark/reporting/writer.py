from __future__ import annotations

from pathlib import Path
from typing import Any

from benchmark.reporting.config import load_report_config
from benchmark.reporting.delta import write_case_report as _write_delta_case_report
from benchmark.reporting.eai import write_case_report as _write_eai_case_report
from benchmark.reporting.reactree import (
    write_case_report as _write_reactree_case_report,
    write_case_report_from_file as _write_reactree_case_report_from_file,
)


def write_case_report(*, config_name: str, **kwargs: Any) -> Path:
    config = load_report_config(config_name)
    style = str(config.get("style", "") or "").strip().lower()
    if style == "eai":
        return _write_eai_case_report(config=config, **kwargs)
    if style == "delta":
        return _write_delta_case_report(config=config, **kwargs)
    if style == "reactree":
        if "row" in kwargs:
            return _write_reactree_case_report(config=config, **kwargs)
        return _write_reactree_case_report_from_file(config=config, **kwargs)
    raise ValueError(f"unsupported report style for {config_name}: {style}")
