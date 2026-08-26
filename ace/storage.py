import json
import os
from contextlib import contextmanager
from pathlib import Path

from config.project_io import load_project_json
from config.settings import get_config, project_path

from ace.schema import (
    coerce_playbook,
    coerce_rule_metadata,
    empty_playbook,
    safe_section,
    strip_section,
    with_section,
)


PLAYBOOK_DIR = get_config("files", "playbook_dir", default="ace/playbooks")


def section_playbook_path(section: str) -> Path:
    return project_path(PLAYBOOK_DIR, f"{safe_section(section)}.json")


@contextmanager
def playbook_lock(section: str):
    path = section_playbook_path(section)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(path.suffix + ".lock")
    with lock_path.open("w", encoding="utf-8") as lock_file:
        try:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass

def load_section_playbook_unlocked(section: str) -> dict:
    section = safe_section(section)
    path = section_playbook_path(section)
    if path.exists():
        data = coerce_playbook(load_project_json(str(path), fallback=empty_playbook()))
    else:
        data = empty_playbook()
    data["rules"] = [coerce_rule_metadata(section, rule) for rule in data.get("rules", []) if rule.get("rule")]
    return data


def save_section_playbook_unlocked(section: str, data: dict) -> None:
    section = safe_section(section)
    path = section_playbook_path(section)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as f:
        clean_data = coerce_playbook(data)
        clean_data["rules"] = [strip_section(rule) for rule in clean_data.get("rules", [])]
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(temp_path, path)


def load_playbook() -> dict:
    rules = []
    playbook_dir = project_path(PLAYBOOK_DIR)
    sections = set()
    if playbook_dir.exists():
        sections.update(path.stem for path in playbook_dir.glob("*.json"))

    for section in sorted(section for section in sections if section):
        section_data = load_section_playbook_unlocked(section)
        rules.extend(with_section(section, rule) for rule in section_data.get("rules", []))
    return {"rules": rules}


def save_playbook(data: dict) -> None:
    grouped: dict[str, list[dict]] = {}
    for rule in coerce_playbook(data).get("rules", []):
        section = rule.get("section")
        if not section:
            continue
        grouped.setdefault(safe_section(section), []).append(strip_section(rule))

    for section, rules in grouped.items():
        with playbook_lock(section):
            save_section_playbook_unlocked(section, {"rules": rules})


def iter_section_rules(section: str) -> list[dict]:
    section = safe_section(section)
    return [
        with_section(section, rule)
        for rule in load_section_playbook_unlocked(section).get("rules", [])
        if isinstance(rule, dict) and not rule.get("deprecated") and rule.get("status", "promoted") == "promoted"
    ]


def iter_all_section_rules(section: str) -> list[dict]:
    section = safe_section(section)
    return [
        with_section(section, rule)
        for rule in load_section_playbook_unlocked(section).get("rules", [])
        if isinstance(rule, dict)
    ]
