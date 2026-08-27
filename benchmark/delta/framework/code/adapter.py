from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any


PAPER_MAIN_DOMAINS = ("clean", "dining", "pc", "office")
PAPER_MAIN_SCENES = ("allensville", "shelbiana", "parole")


# DELTA 适配层只从 /data/zmy/DELTA 读取公开任务定义和环境定义。
#
# 字段公平性边界：
# - goal、scene_graph：任务输入。默认会进入 OurAgent。
# - add_obj、add_act、env_state：DELTA 论文定义的领域对象/动作/谓词说明。
#   `add_act` 用于构建和审计本 benchmark 的 skill 契约，不会作为第二套动作格式
#   原样注入模型提示词；模型只读取被选中 skills 的统一 DELTA/PDDL 契约。
# - subgoal_pddl：评测答案，只由 evaluator 按 case_id 从 DELTA native 数据读取，
#   不进入 case input / worker payload / understanding / planning。
# - gt_cost：论文里的最优/参考 plan cost，只保留在 native 数据中，不进入 worker payload。

@dataclass(frozen=True)
class DeltaTaskSpec:
    domain: str
    scene: str
    goal: str
    gt_cost: int
    add_obj: list[str] | None
    add_act: list[str]
    subgoal_pddl: list[str]
    scene_graph: dict[str, Any]
    env_state: list[str]

def _load_module(module_name: str, path: Path) -> ModuleType:
    """加载 DELTA 原仓库的数据模块。

    DELTA 的任务和场景以 Python 常量形式发布，所以这里用 importlib 读取
    data/example.py 与 data/scene_graph.py，而不是复制一份派生数据。
    """
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load module {module_name} from {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module

def load_delta_task_specs(
    repo_root: str | Path,
    *,
    domains: tuple[str, ...] | list[str] | None = None,
) -> list[DeltaTaskSpec]:
    """从 DELTA 原仓库读取论文主实验 query domain 的任务规格。

    DELTA 论文中 Laundry 是 one-shot example domain；主表 query domain
    是 PC/CLEAN/DINING/OFFICE。原仓库 PDDL 目录还包含 home/human/laundry
    示例 problem，但它们不是 run_delta.sh 主实验循环的一部分。
    """
    repo_root = Path(repo_root)
    example_path = repo_root / "example.py"
    scene_path = repo_root / "scene_graph.py"
    if not example_path.exists():
        example_path = repo_root / "data" / "example.py"
    if not scene_path.exists():
        scene_path = repo_root / "data" / "scene_graph.py"
    example_module = _load_module("delta_example", example_path)
    scene_module = _load_module("delta_scene_graph", scene_path)

    selected_domains = tuple(domains or PAPER_MAIN_DOMAINS)
    domain_map = {
        "pc": example_module.PC,
        "clean": example_module.CLEAN,
        "dining": example_module.DINING,
        "office": example_module.OFFICE,
    }
    scene_map = {
        "allensville": scene_module.ALLENSVILLE,
        "kemblesville": scene_module.KEMBLESVILLE,
        "parole": scene_module.PAROLE,
        "shelbiana": scene_module.SHELBIANA,
    }

    specs = []
    for domain in selected_domains:
        if domain not in domain_map:
            raise ValueError(
                f"DELTA domain {domain!r} is not part of the paper-main query set: "
                f"{', '.join(PAPER_MAIN_DOMAINS)}"
            )
        task = domain_map[domain]
        for scene in PAPER_MAIN_SCENES:
            if scene not in task["scene"]:
                continue
            specs.append(
                DeltaTaskSpec(
                    domain=domain,
                    scene=scene,
                    goal=str(task["goal"]),
                    gt_cost=int(task["gt_cost"].get(scene, 0)),
                    add_obj=list(task.get("add_obj", [])) if task.get("add_obj") else None,
                    add_act=list(task.get("add_act", [])),
                    subgoal_pddl=list(task.get("subgoal_pddl", [])),
                    scene_graph=scene_map[scene],
                    env_state=list(task.get("env_state", [])),
                )
            )
    return specs

def to_case_payload(spec: DeltaTaskSpec) -> dict[str, Any]:
    """转换成 framework case dict。

    注意 subgoal_pddl 是评测答案，不传给 understanding/planning；它只用于
    symbolic debug/fallback evaluator。
    """
    case_id = f"{spec.domain}:{spec.scene}"
    return {
        "case_id": case_id,
        "dataset": "delta",
        "input": {
            "dataset": "delta",
            "benchmark_module": "benchmark.delta",
            "task_id": case_id,
            "instruction": spec.goal,
            "domain": spec.domain,
            "scene_name": spec.scene,
            "scene_graph": spec.scene_graph,
            "task_source": "delta_data_example_py",
            "environment_source": "delta_data_scene_graph_py",
            "delta_env_state": spec.env_state,
            "add_obj": spec.add_obj,
            "add_act": spec.add_act,
        },
        "metadata": {
            "domain": spec.domain,
            "scene": spec.scene,
        },
        "source_path": case_id,
    }


def to_trial_case_payload(spec: DeltaTaskSpec, episode: int) -> dict[str, Any]:
    """转换成带 episode 维度的 DELTA 论文 trial case。

    原 DELTA 脚本对每个 domain-scene 组合重复 50 次。episode 不是新的任务，
    而是同一任务的独立 trial，用独立 case_id 保存，便于 resume 和结果统计。
    """
    base_case = to_case_payload(spec)
    base_input = base_case["input"]
    base_metadata = base_case["metadata"]
    case_id = f"{base_case['case_id']}:episode-{episode:02d}"
    case_input = {
        **base_input,
        "dataset": "delta",
        "benchmark_module": "benchmark.delta",
        "task_id": case_id,
        "base_task_id": base_case["case_id"],
        "episode": episode,
    }
    return {
        "case_id": case_id,
        "dataset": base_case["dataset"],
        "input": case_input,
        "metadata": {
            **base_metadata,
            "base_case_id": base_case["case_id"],
            "episode": episode,
            "trial_kind": "paper_main_episode",
        },
        "source_path": base_case["source_path"],
    }

class DeltaBenchmarkAdapter:
    """DELTA benchmark case 迭代器。

    这里只负责枚举 case 和按 case/domain 过滤，不做规划、不做评测、
    不改变 fairness mode。
    """
    dataset_name = "delta"

    def __init__(
        self,
        repo_root: str | Path,
        *,
        case_id: str | None = None,
        domain: str | None = None,
        episodes: int | None = None,
    ):
        self.repo_root = Path(repo_root)
        self.case_id = case_id
        self.domain = domain
        self.episodes = episodes

    def iter_cases(self) -> list[dict[str, Any]]:
        cases = []
        domains = (self.domain,) if self.domain else PAPER_MAIN_DOMAINS
        for spec in load_delta_task_specs(self.repo_root, domains=domains):
            generated_cases = (
                [to_trial_case_payload(spec, episode) for episode in range(1, self.episodes + 1)]
                if self.episodes is not None
                else [to_case_payload(spec)]
            )
            for case in generated_cases:
                base_case_id = case["metadata"].get("base_case_id") or case["case_id"]
                if self.case_id and self.case_id not in {case["case_id"], base_case_id}:
                    continue
                cases.append(case)
        return cases
