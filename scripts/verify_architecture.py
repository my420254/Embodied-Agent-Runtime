import ast
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOMAIN_FORBIDDEN_IMPORTS = ("langgraph", "langchain", "understanding", "planning", "execution", "reflection", "graph", "nodes", "routes", "main", "test")
CONFIG_FORBIDDEN_IMPORTS = ("ace", "langgraph", "understanding", "planning", "execution", "reflection", "graph", "nodes", "routes", "main", "test")
ACE_FORBIDDEN_IMPORTS = ("benchmark", "langgraph", "understanding", "planning", "execution", "reflection", "graph", "nodes", "routes", "main", "test")
ADAPTERS_FORBIDDEN_IMPORTS = ("ace", "langgraph", "langchain", "understanding", "planning", "execution", "reflection", "graph", "nodes", "routes", "main", "test")
SKILLS_FORBIDDEN_IMPORTS = ("ace", "langgraph", "langchain", "understanding", "planning", "execution", "reflection", "graph", "nodes", "routes", "main", "test")
EXECUTION_FORBIDDEN_IMPORTS = ("ace", "langgraph", "langchain", "understanding", "planning", "reflection", "graph", "nodes", "routes", "main", "test")
RE_TRAC_FORBIDDEN_IMPORTS = ("ace", "config", "langgraph", "langchain", "understanding", "planning", "execution", "reflection", "graph", "nodes", "routes", "main", "test")
MODULE_FORBIDDEN_IMPORTS = ("nodes", "routes", "planning", "reflection", "task_management", "understanding", "state", "main", "test")
GRAPH_FORBIDDEN_IMPORTS = ("benchmark",)
MAIN_ENTRY_FORBIDDEN_IMPORTS = ("langchain", "subgraphs", "domain", "config")
BARE_GRAPH_IMPORTS = ("state", "nodes", "routes", "planning", "reflection", "task_management", "understanding")
PREFIX_FORBIDDEN_IMPORTS = ("langchain",)


def iter_python_files(root: Path):
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def module_name(path: Path) -> str:
    return ".".join(path.relative_to(PROJECT_ROOT).with_suffix("").parts)


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def is_forbidden_root(root: str, forbidden: tuple[str, ...]) -> bool:
    for item in forbidden:
        if root == item:
            return True
        if item in PREFIX_FORBIDDEN_IMPORTS and root.startswith(f"{item}_"):
            return True
    return False


def check_forbidden_imports(package: str, forbidden: tuple[str, ...]) -> list[str]:
    errors = []
    package_root = PROJECT_ROOT / package
    if not package_root.exists():
        return [f"missing package directory: {package}"]
    for path in iter_python_files(package_root):
        roots = imported_roots(path)
        bad = sorted(root for root in roots if is_forbidden_root(root, forbidden))
        if bad:
            errors.append(f"{module_name(path)} imports forbidden roots: {', '.join(bad)}")
    return errors


def check_required_files() -> list[str]:
    required = [
        "config/settings.json",
        "docs/ARCHITECTURE.md",
        "config/prompts.json",
        "config/prompts.py",
        "config/rules.json",
        "adapters/__init__.py",
        "adapters/ros_bridge.py",
        "agent_runtime/engine.py",
        "agent_runtime/service.py",
        "ace/playbook.py",
        "ace/playbooks/planning.json",
        "domain/runtime.py",
        "domain/sandbox.py",
        "execution/__init__.py",
        "execution/common.py",
        "execution/executor.py",
        "execution/result.py",
        "execution/ros/__init__.py",
        "execution/ros/backend.py",
        "execution/simulation/__init__.py",
        "execution/simulation/backend.py",
        "re_trac/__init__.py",
        "re_trac/state.py",
        "skills/base.py",
        "skills/loader.py",
        "skills/registry.py",
        "graph/graph.py",
        "graph/nodes.py",
        "graph/routes.py",
        "graph/state.py",
        "graph/understanding/node.py",
        "graph/planning/node.py",
        "graph/planning/prompts.py",
        "graph/planning/normalizer.py",
        "graph/planning/evaluation/evaluator.py",
        "graph/task_management/node.py",
        "graph/reflection/node.py",
        "scripts/__init__.py",
        "scripts/run_agent.py",
    ]
    return [f"missing required file: {path}" for path in required if not (PROJECT_ROOT / path).exists()]


def check_single_file_forbidden_imports(relative_path: str, forbidden: tuple[str, ...]) -> list[str]:
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        return [f"missing required file: {relative_path}"]
    roots = imported_roots(path)
    bad = sorted(root for root in roots if is_forbidden_root(root, forbidden))
    if bad:
        return [f"{module_name(path)} imports forbidden roots: {', '.join(bad)}"]
    return []


def check_no_bare_graph_imports() -> list[str]:
    errors = []
    roots_to_scan = ["graph", "tests", "scripts", "benchmark", "main.py"]
    for root in roots_to_scan:
        path = PROJECT_ROOT / root
        paths = [path] if path.is_file() else list(iter_python_files(path))
        for file_path in paths:
            roots = imported_roots(file_path)
            bad = sorted(root for root in roots if root in BARE_GRAPH_IMPORTS)
            if bad:
                errors.append(f"{module_name(file_path)} uses bare graph imports: {', '.join(bad)}")
    return errors


def main() -> int:
    errors = []
    errors.extend(check_required_files())
    errors.extend(check_forbidden_imports("domain", DOMAIN_FORBIDDEN_IMPORTS))
    errors.extend(check_forbidden_imports("config", CONFIG_FORBIDDEN_IMPORTS))
    errors.extend(check_forbidden_imports("ace", ACE_FORBIDDEN_IMPORTS))
    errors.extend(check_forbidden_imports("adapters", ADAPTERS_FORBIDDEN_IMPORTS))
    errors.extend(check_forbidden_imports("skills", SKILLS_FORBIDDEN_IMPORTS))
    errors.extend(check_forbidden_imports("execution", EXECUTION_FORBIDDEN_IMPORTS))
    errors.extend(check_forbidden_imports("re_trac", RE_TRAC_FORBIDDEN_IMPORTS))
    errors.extend(check_forbidden_imports("graph", GRAPH_FORBIDDEN_IMPORTS))
    errors.extend(check_no_bare_graph_imports())
    for package in ("graph/understanding", "graph/planning", "graph/task_management", "graph/reflection"):
        errors.extend(check_forbidden_imports(package, MODULE_FORBIDDEN_IMPORTS))
    errors.extend(check_single_file_forbidden_imports("main.py", MAIN_ENTRY_FORBIDDEN_IMPORTS))

    if errors:
        print("Architecture verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
