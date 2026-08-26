from skills.loader import get_default_profile, load_enabled_handlers, load_enabled_prompts


def get_skill_handlers(profile: str | None = None) -> dict:
    return load_enabled_handlers(profile or get_default_profile())


def apply_skill(
    sim_env: dict,
    sim_robot: dict,
    act: str,
    params: dict,
    profile: str | None = None,
    handlers: dict | None = None,
) -> tuple[bool, str, str]:
    active_handlers = handlers if handlers is not None else get_skill_handlers(profile)
    handler = active_handlers.get(act)
    if handler is None:
        current_profile = profile or get_default_profile()
        return False, "调用无效动作", f"技能 {act} 在当前 profile={current_profile} 中未启用或未定义"

    ok, issue, fix = handler.validate(sim_env, sim_robot, params)
    if not ok:
        return ok, issue, fix
    handler.apply(sim_env, sim_robot, params)
    return True, "", ""


def load_enabled_skill_prompts(profile: str | None = None) -> str:
    return load_enabled_prompts(profile or get_default_profile())
