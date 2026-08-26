from __future__ import annotations

from typing import Any

from skills.registry import apply_skill


def apply_sandbox_action(
    sim_env: dict,
    sim_robot: dict,
    act: str,
    params: dict,
    *,
    profile: str | None = None,
    handlers: dict[str, Any] | None = None,
) -> tuple[bool, str, str]:
    """Planning evaluation boundary for skill validation and effects."""

    return apply_skill(
        sim_env,
        sim_robot,
        act,
        params,
        profile=profile,
        handlers=handlers,
    )


__all__ = ["apply_sandbox_action"]
