from pathlib import Path
from string import Template

from config.project_io import load_project_json
from config.settings import get_config, project_path


DEFAULT_PROMPTS_FILE = "config/prompts.json"


def _same_prompt_file(left: str, right: str) -> bool:
    if not left or not right:
        return False
    try:
        left_path = Path(left)
        right_path = Path(right)
        if not left_path.is_absolute():
            left_path = project_path(str(left_path))
        if not right_path.is_absolute():
            right_path = project_path(str(right_path))
        return left_path.resolve() == right_path.resolve()
    except Exception:
        return str(left) == str(right)


def _merge_prompt_file(prompts: dict, filename: str) -> dict:
    loaded = load_project_json(filename, fallback={})
    if not isinstance(loaded, dict):
        return prompts
    merged = dict(prompts)
    merged.update(loaded)
    return merged


def load_prompts() -> dict:
    configured_file = str(get_config("files", "prompts", default=DEFAULT_PROMPTS_FILE) or "").strip()
    if configured_file and not _same_prompt_file(configured_file, DEFAULT_PROMPTS_FILE):
        benchmark_runtime = get_config("benchmark", "runtime", default={}) or {}
        if isinstance(benchmark_runtime, dict) and benchmark_runtime:
            return _merge_prompt_file({}, configured_file)
        prompts = _merge_prompt_file({}, DEFAULT_PROMPTS_FILE)
        return _merge_prompt_file(prompts, configured_file)
    return _merge_prompt_file({}, DEFAULT_PROMPTS_FILE)


def _template_variables(template: str) -> set[str]:
    variables: set[str] = set()
    for match in Template.pattern.finditer(template):
        name = match.group("named") or match.group("braced")
        if name:
            variables.add(name)
    return variables


def _prompt_template(name: str) -> str:
    prompts = load_prompts()
    template = prompts.get(name, "")
    if isinstance(template, list):
        template = "\n".join(str(item) for item in template)
    if not template:
        raise KeyError(f"missing prompt template: {name}")
    return str(template)


def prompt_variable_report(name: str, values: dict | None = None, *, template: str | None = None) -> dict:
    if template is None:
        template = _prompt_template(name)
    provided = set((values or {}).keys())
    required = _template_variables(template)
    return {
        "prompt_name": name,
        "required_vars": sorted(required),
        "provided_vars": sorted(provided),
        "missing_vars": sorted(required - provided),
        "unused_vars": sorted(provided - required),
    }


def render_prompt(name: str, **values) -> str:
    template = _prompt_template(name)
    report = prompt_variable_report(name, values, template=template)
    missing = report["missing_vars"]
    if missing:
        raise KeyError(f"missing prompt variables for {name}: {', '.join(missing)}")
    return Template(template).safe_substitute(**values)
