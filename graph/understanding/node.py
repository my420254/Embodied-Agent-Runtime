from ace.playbook import load_section_rules
from config.json_utils import parse_json_from_llm
from config.llms import get_understanding_llm
from config.prompts import render_prompt
from config.project_io import load_project_json
from config.settings import get_config
from domain.scene import get_all_entity_names_from_scene_data
from graph.state import UnderstandingState
from graph.understanding.pipeline import run_understanding_pipeline

# Compatibility injection surface used by pluggable understanding features.
__all__ = ["parse_json_from_llm", "get_understanding_llm", "render_prompt"]

try:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
except Exception:  # pragma: no cover
    class _Message:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

    class AIMessage(_Message):
        pass

    class HumanMessage(_Message):
        pass

    class SystemMessage(_Message):
        pass


def load_system_rules() -> str:
    try:
        data = load_project_json(get_config("files", "rules", default="config/rules.json"), fallback={})
        rules = data.get("static_constraints", [])
        if not rules:
            return "无出厂静态约束规则"
        rule_texts = [
            f"[{i+1}] 触发条件: [{r.get('trigger_condition', '')}] -> 必须执行:[{r.get('enforcement_rule', '')}]"
            for i, r in enumerate(rules)
        ]
        return "\n".join(rule_texts)
    except Exception as e:
        print(f"[系统警报] system_rules.json 加载失败: {e}")
        return "静态规则加载失败"


def load_understanding_playbook() -> str:
    return load_understanding_playbook_for_flags(None)


def load_understanding_playbook_for_flags(feature_flags: dict | None = None) -> str:
    if isinstance(feature_flags, dict) and not bool(feature_flags.get("playbook_retrieval", True)):
        return ""
    return load_section_rules("understanding", empty_message="暂无理解层历史经验.")


def _understanding_feature_flags(state: UnderstandingState) -> dict:
    flags = {}
    state_flags = state.get("feature_flags", {})
    if isinstance(state_flags, dict):
        flags.update(state_flags)
    return flags


def _names_from_sequence(value: object) -> set[str]:
    names: set[str] = set()
    if not isinstance(value, list):
        return names
    for item in value:
        if isinstance(item, str) and item:
            names.add(item)
        elif isinstance(item, dict):
            for key in ("name", "id", "entity", "entity_name"):
                name = item.get(key)
                if name:
                    names.add(str(name))
                    break
    return names


def _looks_like_flat_environment(value: dict) -> bool:
    for info in value.values():
        if isinstance(info, dict) and any(
            key in info for key in ("direct_parent", "full_path", "states")
        ):
            return True
    return False


def _entity_names_from_environment(environment: object) -> set[str]:
    if not isinstance(environment, dict) or not environment:
        return set()
    if _looks_like_flat_environment(environment):
        return {str(name) for name in environment.keys() if name}
    return get_all_entity_names_from_scene_data(environment)


def _entity_names_from_state(state: UnderstandingState, task_context: dict) -> set[str]:
    names = set()
    names.update(_names_from_sequence(task_context.get("available_entities")))
    names.update(_names_from_sequence(task_context.get("entity_catalog")))
    names.update(_names_from_sequence(state.get("entity_catalog")))  # type: ignore[arg-type]
    names.update(_entity_names_from_environment(state.get("environment")))  # type: ignore[arg-type]
    names.update(_entity_names_from_environment(state.get("scene")))  # type: ignore[arg-type]
    return names


def analyze_instruction(state: UnderstandingState) -> UnderstandingState:
    raw_text = state.get("raw_instruction", "")
    valid_messages = [msg for msg in state.get("messages", []) if hasattr(msg, "content")]
    if not raw_text:
        raw_text = valid_messages[-1].content if valid_messages else ""
    task_context = state.get("task_context", {})
    if not isinstance(task_context, dict):
        task_context = {}

    try:
        valid_names = _entity_names_from_state(state, task_context)
    except Exception as e:
        print(f"[理解层] 请求实体加载失败: {e}")
        valid_names = set()

    feature_flags = _understanding_feature_flags(state)
    allow_clarification = bool(feature_flags.get("allow_clarification", True))

    return run_understanding_pipeline(
        raw_text,
        valid_names,
        valid_messages,
        runtime_options={
            "allow_clarification": bool(allow_clarification),
            "feature_flags": feature_flags if isinstance(feature_flags, dict) else {},
            "raise_feature_exceptions": bool(feature_flags.get("raise_feature_exceptions", False)),
            "original_instruction": state.get("original_instruction", raw_text),
            "task_context": task_context,
            "environment": state.get("environment") or state.get("scene"),
        },
    )


def ask_user(state: UnderstandingState) -> UnderstandingState:
    question = state.get("clarification_question", "指令参数缺失：请重新指定操作对象")
    return {"messages": [AIMessage(content=question)]}


def build_understanding_graph():
    from langgraph.graph import END, StateGraph

    workflow = StateGraph(UnderstandingState)
    workflow.add_node("analyze", analyze_instruction)
    workflow.add_node("ask", ask_user)
    workflow.set_entry_point("analyze")
    workflow.add_conditional_edges(
        "analyze",
        lambda state: "ask" if state.get("needs_clarification") else "end",
        {"end": END, "ask": "ask"},
    )
    workflow.add_edge("ask", END)
    return workflow.compile()
