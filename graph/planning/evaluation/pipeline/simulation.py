from __future__ import annotations

import copy

from ..models import (
    EvaluationFailure,
    EvaluationFailureCode,
    EvaluationSession,
    SimulationResult,
)


def run_base_simulation(
    session: EvaluationSession,
) -> SimulationResult:
    """Simulate one candidate against an isolated request-local world snapshot."""

    pending = session._pending_simulation()
    todo_list = copy.deepcopy(pending.todo_list)
    todo_steps = (
        todo_list[len(session.prefix_steps) :]
        if session.modes.reuse_validated_prefix
        else todo_list
    )
    validated_steps = copy.deepcopy(pending.validated_steps)
    sim_env = copy.deepcopy(pending.repair_base_env)
    sim_robot = copy.deepcopy(pending.repair_base_robot)
    trajectory_records: list[dict] = []

    for step in todo_steps:
        execution = step.get("execution", {}) if isinstance(step, dict) else {}
        if not isinstance(execution, dict) or not execution:
            failure = EvaluationFailure(
                step=copy.deepcopy(step) if isinstance(step, dict) else {},
                code=EvaluationFailureCode.FORMAT_ERROR,
                issue_type="输出格式异常",
                fix_advice="必须提供符合规范的 execution 字典",
                checkpoint_env=copy.deepcopy(sim_env),
                checkpoint_robot=copy.deepcopy(sim_robot),
            )
            return _simulation_result(
                pending,
                todo_list=todo_list,
                todo_steps=todo_steps,
                validated_steps=validated_steps,
                sim_env=sim_env,
                sim_robot=sim_robot,
                trajectory_records=trajectory_records,
                failure=failure,
            )

        snap_env = copy.deepcopy(sim_env)
        snap_robot = copy.deepcopy(sim_robot)
        ok, issue_type, fix = session.skills.apply_action(
            sim_env,
            sim_robot,
            execution.get("skill", ""),
            execution.get("parameters", {}),
        )
        if not ok:
            failure = EvaluationFailure(
                step=copy.deepcopy(step),
                code=_handler_failure_code(
                    issue_type,
                    str(execution.get("skill", "")),
                ),
                issue_type=issue_type,
                fix_advice=fix,
                checkpoint_env=snap_env,
                checkpoint_robot=snap_robot,
            )
            return _simulation_result(
                pending,
                todo_list=todo_list,
                todo_steps=todo_steps,
                validated_steps=validated_steps,
                sim_env=sim_env,
                sim_robot=sim_robot,
                trajectory_records=trajectory_records,
                failure=failure,
            )

        validated_steps.append(copy.deepcopy(step))
        trajectory_records.append(
            {
                "step": copy.deepcopy(step),
                "before_env": snap_env,
                "before_robot": snap_robot,
                "after_env": copy.deepcopy(sim_env),
                "after_robot": copy.deepcopy(sim_robot),
            }
        )
    return _simulation_result(
        pending,
        todo_list=todo_list,
        todo_steps=todo_steps,
        validated_steps=validated_steps,
        sim_env=sim_env,
        sim_robot=sim_robot,
        trajectory_records=trajectory_records,
    )


def _simulation_result(
    pending: SimulationResult,
    *,
    todo_list: list[dict],
    todo_steps: list[dict],
    validated_steps: list[dict],
    sim_env: dict,
    sim_robot: dict,
    trajectory_records: list[dict],
    failure: EvaluationFailure | None = None,
) -> SimulationResult:
    return SimulationResult(
        todo_list=copy.deepcopy(todo_list),
        todo_steps=copy.deepcopy(todo_steps),
        validated_steps=copy.deepcopy(validated_steps),
        final_env=copy.deepcopy(sim_env),
        final_robot=copy.deepcopy(sim_robot),
        start_env=copy.deepcopy(pending.start_env),
        start_robot=copy.deepcopy(pending.start_robot),
        repair_base_env=copy.deepcopy(pending.repair_base_env),
        repair_base_robot=copy.deepcopy(pending.repair_base_robot),
        trajectory_records=copy.deepcopy(trajectory_records),
        failure=failure,
        simulated=True,
    )


_HANDLER_FAILURE_CODES = {
    "调用无效动作": EvaluationFailureCode.INVALID_ACTION,
    "目标不存在": EvaluationFailureCode.INVALID_ACTION,
    "设施属性不符": EvaluationFailureCode.INVALID_ACTION,
    "前置状态未满足": EvaluationFailureCode.ACCESSIBILITY,
    "前置位置依赖未满足": EvaluationFailureCode.NAVIGATION_PRECONDITION,
    "物理可达性受限": EvaluationFailureCode.ACCESSIBILITY,
    "距离干涉": EvaluationFailureCode.ACCESSIBILITY,
    "空间干涉": EvaluationFailureCode.ACCESSIBILITY,
    "目标不可坐": EvaluationFailureCode.ACCESSIBILITY,
    "容器依赖未满足": EvaluationFailureCode.CONTAINER_STATE,
    "容器干涉拦截": EvaluationFailureCode.CONTAINER_STATE,
    "单臂约束违规": EvaluationFailureCode.ARM_STATE,
    "机械臂冲突": EvaluationFailureCode.ARM_STATE,
    "手持物品不匹配": EvaluationFailureCode.ARM_STATE,
    "卫生前置约束未满足": EvaluationFailureCode.SAFETY_PRECONDITION,
    "安全约束违规": EvaluationFailureCode.SAFETY_PRECONDITION,
    "工具依赖未满足": EvaluationFailureCode.SAFETY_PRECONDITION,
    "工具状态受限": EvaluationFailureCode.SAFETY_PRECONDITION,
    "电源依赖未满足": EvaluationFailureCode.DEVICE_STATE,
}


def _handler_failure_code(issue_type: str, skill: str) -> EvaluationFailureCode:
    """Adapt the legacy handler tuple once at the evaluation boundary."""

    issue = str(issue_type or "").strip()
    if issue.startswith("无效的导航"):
        return EvaluationFailureCode.INVALID_ACTION
    if issue in {"冗余操作", "冗余操作拦截"}:
        if skill in {"Open", "Close"}:
            return EvaluationFailureCode.CONTAINER_STATE
        if skill in {"ToggleOn", "ToggleOff"}:
            return EvaluationFailureCode.DEVICE_STATE
        if skill == "NavigateTo":
            return EvaluationFailureCode.NAVIGATION_PRECONDITION
        return EvaluationFailureCode.INVALID_ACTION
    return _HANDLER_FAILURE_CODES.get(issue, EvaluationFailureCode.UNKNOWN)


run_sandbox_simulation = run_base_simulation


__all__ = [
    "run_base_simulation",
    "run_sandbox_simulation",
]
