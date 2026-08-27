import importlib
from dataclasses import dataclass
from pathlib import Path

from config.settings import get_config, project_path
from skills.base import SkillHandler


@dataclass(frozen=True)
class SkillSpec:
    name: str
    description: str
    prompt: str
    handler: str
    execution_domain: str
    path: Path
    planning_contract: dict[str, str]


def _parse_skill_yaml(path: Path) -> dict:
    data = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("\"'")
    return data


def load_skills_config() -> dict:
    config = get_config("skills", default={})
    return config if isinstance(config, dict) else {}


def get_default_profile() -> str:
    return str(get_config("skills", "profile", default="default") or "default")


def _skills_root() -> Path:
    root = str(get_config("skills", "root", default="skills") or "skills")
    path = Path(root)
    return path if path.is_absolute() else project_path(root)


def load_enabled_skill_names(profile: str | None = None) -> list[str]:
    data = load_skills_config()
    del profile
    enabled = data.get("enabled", [])
    if not isinstance(enabled, list):
        return []
    return [str(name) for name in enabled]


def load_skill_spec(name: str) -> SkillSpec | None:
    skill_dir = _skills_root() / name
    skill_yaml = skill_dir / "skill.yaml"
    if not skill_yaml.exists():
        print(f"[系统警报] 技能 {name} 缺少 skill.yaml，已跳过")
        return None
    data = _parse_skill_yaml(skill_yaml)
    return SkillSpec(
        name=data.get("name", name),
        description=data.get("description", ""),
        prompt=data.get("prompt", "prompt.md"),
        handler=data.get("handler", ""),
        execution_domain=data.get("execution_domain", ""),
        path=skill_dir,
        planning_contract={key: value for key, value in data.items() if key.startswith("planner_")},
    )


def load_enabled_skill_specs(profile: str | None = None) -> list[SkillSpec]:
    specs = []
    for name in load_enabled_skill_names(profile):
        spec = load_skill_spec(name)
        if spec is not None:
            specs.append(spec)
    return specs


def instantiate_handler(spec: SkillSpec) -> SkillHandler | None:
    module_name, _, class_name = spec.handler.partition(":")
    if not module_name or not class_name:
        print(f"[系统警报] 技能 {spec.name} 的 handler 配置无效: {spec.handler}")
        return None
    try:
        module = importlib.import_module(module_name)
        handler_class = getattr(module, class_name)
        return handler_class()
    except Exception as e:
        print(f"[系统警报] 技能 {spec.name} handler 加载失败: {e}")
        return None


def load_enabled_handlers(profile: str | None = None) -> dict[str, SkillHandler]:
    handlers = {}
    for spec in load_enabled_skill_specs(profile):
        handler = instantiate_handler(spec)
        if handler is not None:
            handlers[handler.name] = handler
    return handlers


def load_enabled_prompts(profile: str | None = None) -> str:
    prompts = []
    common_path = _skills_root() / "common.md"
    if common_path.exists():
        prompts.append(common_path.read_text(encoding="utf-8"))
    for spec in load_enabled_skill_specs(profile):
        prompt_path = spec.path / spec.prompt
        try:
            prompts.append(prompt_path.read_text(encoding="utf-8"))
        except Exception as e:
            prompts.append(f"【系统警报：读取技能 {spec.name} 说明失败: {e}】")
    if not prompts:
        profile_name = profile or get_default_profile()
        return f"【系统警报：profile {profile_name} 未加载到任何可用技能，请检查 settings.skills.root/enabled】"
    return "\n\n".join(prompts)


def load_prompts_for(names: list[str] | None) -> str:
    """加载 common.md + 仅命中 names 的技能说明（与 enabled 求交集）。

    - names 与 enabled 做大小写不敏感交集，按 enabled 顺序输出；
    - 命中集合非空且至少加载到一份技能说明时，才在最前面拼上 common.md；
    - names 为空、或与 enabled 零命中、或所有命中技能说明都读不出来时，
      返回 ""，让调用方自行回退到全量 enabled（避免过滤后给模型空技能表）。
    """
    requested = [str(name).strip() for name in (names or []) if str(name).strip()]
    if not requested:
        return ""
    enabled = load_enabled_skill_names()
    requested_lower = {name.lower() for name in requested}
    selected = [name for name in enabled if name.lower() in requested_lower]
    if not selected:
        return ""
    skill_prompts: list[str] = []
    for name in selected:
        spec = load_skill_spec(name)
        if spec is None:
            continue
        prompt_path = spec.path / spec.prompt
        try:
            skill_prompts.append(prompt_path.read_text(encoding="utf-8"))
        except Exception as e:
            skill_prompts.append(f"【系统警报：读取技能 {spec.name} 说明失败: {e}】")
    if not skill_prompts:
        return ""
    prompts: list[str] = []
    common_path = _skills_root() / "common.md"
    if common_path.exists():
        prompts.append(common_path.read_text(encoding="utf-8"))
    prompts.extend(skill_prompts)
    return "\n\n".join(prompts)
