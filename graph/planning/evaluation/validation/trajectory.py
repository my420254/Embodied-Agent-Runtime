from __future__ import annotations


def step_number(step: dict | None) -> int | None:
    if not isinstance(step, dict):
        return None
    try:
        return int(step.get("step"))
    except (TypeError, ValueError):
        return None


def todo_action_trajectory(todo_plan: list[dict]) -> str:
    rows = []
    for step in todo_plan or []:
        if "object" in step:
            rows.append(f"Step {step.get('step')}: {step.get('action')}({step.get('object')})")
        else:
            rows.append(f"Step {step.get('step')}: {step.get('action')}({step.get('args', [])})")
    return "\n".join(rows)


def todo_trajectory(todo_list: list[dict]) -> str:
    return "\n".join(
        [
            f"Step {s.get('step')}: {s.get('execution', {}).get('skill')}({list(s.get('execution', {}).get('parameters', {}).values())})"
            for s in todo_list
        ]
    )
