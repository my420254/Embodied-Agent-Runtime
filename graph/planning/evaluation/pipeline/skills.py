from __future__ import annotations

import inspect
from types import MappingProxyType
from typing import Any, Callable

from ..dependencies import EvaluationDependencies
from ..models import EvaluationSkillSnapshot


def load_skill_snapshot(
    profile: str | None,
    dependencies: EvaluationDependencies,
) -> EvaluationSkillSnapshot:
    """Load every profile-scoped skill dependency exactly once per request."""

    handlers = dict(dependencies.get_skill_handlers(profile))
    prompts = _load_prompts(dependencies.load_enabled_skill_prompts, profile)
    supports_handlers = _supports_keyword(
        dependencies.apply_sandbox_action,
        "handlers",
    )
    supports_profile = _supports_keyword(
        dependencies.apply_sandbox_action,
        "profile",
    )

    def apply_action(
        env: dict,
        robot: dict,
        skill: str,
        parameters: dict,
        **_call_context: Any,
    ) -> tuple[bool, str, str]:
        kwargs: dict[str, Any] = {}
        if supports_profile:
            kwargs["profile"] = profile
        if supports_handlers:
            kwargs["handlers"] = handlers
        return dependencies.apply_sandbox_action(
            env,
            robot,
            skill,
            parameters,
            **kwargs,
        )

    return EvaluationSkillSnapshot(
        catalog=dependencies.load_skill_catalog(profile),
        handlers=MappingProxyType(handlers),
        prompts=prompts,
        apply_action=apply_action,
    )


def _load_prompts(loader: Callable[..., str], profile: str | None) -> str:
    if _accepts_positional_argument(loader):
        return str(loader(profile) or "")
    return str(loader() or "")


def _accepts_positional_argument(callback: Callable[..., Any]) -> bool:
    try:
        parameters = inspect.signature(callback).parameters.values()
    except (TypeError, ValueError):
        return True
    return any(
        parameter.kind
        in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.VAR_POSITIONAL,
        }
        for parameter in parameters
    )


def _supports_keyword(callback: Callable[..., Any], keyword: str) -> bool:
    try:
        parameters = inspect.signature(callback).parameters.values()
    except (TypeError, ValueError):
        return False
    return any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD
        or parameter.name == keyword
        for parameter in parameters
    )


__all__ = ["load_skill_snapshot"]
