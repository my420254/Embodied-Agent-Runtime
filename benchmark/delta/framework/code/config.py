from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config.settings import project_path


@dataclass(frozen=True)
class DeltaBenchmarkConfig:
    dataset_name: str
    repo_root: Path
    extracted_cases_path: Path
    extracted_envs_root: Path
    default_split: str
    default_limit: int
    default_output: str
    splits: tuple[str, ...]
    domains: tuple[str, ...]


def load_config() -> DeltaBenchmarkConfig:
    return DeltaBenchmarkConfig(
        dataset_name="delta",
        repo_root=project_path("benchmark", "datasets", "native", "delta"),
        extracted_cases_path=project_path("benchmark", "datasets", "extracted", "delta", "cases.json"),
        extracted_envs_root=project_path("benchmark", "datasets", "extracted", "delta", "initial_envs"),
        default_split="default",
        default_limit=4,
        default_output="benchmark/delta/framework/results/_standalone/generated/delta/outputs.json",
        splits=("default",),
        domains=("clean", "dining", "pc", "office"),
    )


__all__ = ["DeltaBenchmarkConfig", "load_config"]
