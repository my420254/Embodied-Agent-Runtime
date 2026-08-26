from __future__ import annotations

from skills.registry import apply_skill


def apply_sandbox_action(
    sim_env: dict,
    sim_robot: dict,
    act: str,
    params: dict,
) -> tuple[bool, str, str]:
    """通过技能注册表校验并应用一个沙盒动作，是规划审计层的统一入口。"""
    return apply_skill(sim_env, sim_robot, act, params)
  
