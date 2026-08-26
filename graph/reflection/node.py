import json
from ace.playbook import load_section_rules, write_experience
from config.json_utils import parse_json_from_llm
from config.llms import get_reflection_llm
from config.prompts import render_prompt
from config.settings import get_config
from graph.state import ReflectionState

try:
    from langchain_core.messages import HumanMessage
except Exception:  # pragma: no cover - fallback for lean test environments
    class HumanMessage:  # type: ignore[no-redef]
        def __init__(self, content: str):
            self.content = content

# =====================================================================
# 设计说明
# ─────────────────────────────────────────────────────────────────────
# 反思四层架构：
#
# ┌──────────────────────────────────────────────────────────────────┐
# │ Layer1: 指令理解层反思 (layer1_understanding)                     │
# │   触发：failure_layer == "understanding"                         │
# │   职责：分析理解层的实体召回偏差、意图误解                         │
# │   输出：corrected_understanding、写入 understanding playbook      │
# │   路由：retry_understanding                                       │
# ├──────────────────────────────────────────────────────────────────┤
# │ Layer2: 任务分解层反思 (layer2_planning)                          │
# │   触发：failure_layer == "planning"                              │
# │   职责：分析步骤缺失、顺序错误、约束违反                           │
# │   输出：new_constraints、写入 planning playbook                   │
# │   路由：retry_planning                                            │
# ├──────────────────────────────────────────────────────────────────┤
# │ Layer3: 可行性审计层反思 (layer3_feasibility)                     │
# │   触发：failure_layer == "feasibility"                           │
# │   职责：分析反复被 evaluator 拦截的深层原因                        │
# │   输出：写入 planning playbook（source="reflection_layer3"）      │
# │   路由：retry_planning                                            │
# ├──────────────────────────────────────────────────────────────────┤
# │ Layer4: 执行/任务管理层反思 (layer4_execution)                    │
# │   触发：failure_layer == "execution"                             │
# │   职责：工具替代、执行层容错                                       │
# │   输出：corrected_execution、写入 execution playbook              │
# │   路由：retry_execution                                           │
# └──────────────────────────────────────────────────────────────────┘
#
# ace/playbooks/{section}.json 按层存储经验：
# - understanding.json: reflection_layer1 写入
# - planning.json: reflection_layer2 / reflection_layer3 / evaluator 写入
# - execution.json: reflection_layer4 写入
# =====================================================================


def _flatten_names(names_data) -> list:
    if not names_data:
        return []
    if isinstance(names_data, list):
        return names_data
    if isinstance(names_data, dict):
        names = []
        names.extend(names_data.get("primary", []))
        names.extend(names_data.get("alternatives", []))
        return names
    return []


# ─────────────────────────────────────────────────────────────────────
# 节点 0：失败分诊台（四层路由）
# ─────────────────────────────────────────────────────────────────────
def failure_triage_node(state: ReflectionState) -> ReflectionState:
    """
    根据 failure_layer 和 retry_count 决定路由到哪一层。

    路由逻辑：
    - failure_layer == "understanding" → layer1_understanding
    - failure_layer == "planning"      → layer2_planning
    - failure_layer == "feasibility"   → layer3_feasibility
    - failure_layer == "execution"     → layer4_execution

    如果同一层反复失败（retry_count > 0），升级到上一层：
    - execution 反复失败 → planning
    - planning  反复失败 → understanding
    """
    retry_count   = state.get("reflection_retry_count", 0)
    failure_layer = state.get("failure_layer", "execution")
    max_retries = get_config("reflection", "max_retries", default=3)
    if not isinstance(max_retries, int) or max_retries < 1:
        max_retries = 3

    if retry_count >= max_retries:
        error_msg = state.get("error_feedback", "")
        suffix = f"反思重试已达到上限({max_retries})，终止自动修复。"
        return {
            "determined_reflection_layer": "end",
            "reflection_retry_count": retry_count,
            "execution_status": "failed",
            "error_feedback": f"{error_msg}\n{suffix}" if error_msg else suffix,
            "next_routing": "end",
        }

    # 基础路由映射
    layer_map = {
        "understanding": "layer1_understanding",
        "planning":      "layer2_planning",
        "feasibility":   "layer3_feasibility",
        "execution":     "layer4_execution"
    }

    determined = layer_map.get(failure_layer, "layer4_execution")

    # 升级逻辑：反复失败则升一层
    if retry_count >= 2:
        upgrade_map = {
            "layer4_execution":     "layer2_planning",
            "layer3_feasibility":   "layer2_planning",
            "layer2_planning":      "layer1_understanding",
            "layer1_understanding": "layer1_understanding"  # 已是最高层，不再升级
        }
        upgraded  = upgrade_map.get(determined, determined)
        if upgraded != determined:
            print(f"\n[分诊台] 反复失败({retry_count}次)，从 {determined} 升级到 {upgraded}")
            determined = upgraded

    return {
        "determined_reflection_layer": determined,
        "reflection_retry_count":      retry_count + 1
    }


# ─────────────────────────────────────────────────────────────────────
# 节点 1：指令理解层反思
# ─────────────────────────────────────────────────────────────────────
def layer1_understanding_reflection_node(state: ReflectionState) -> ReflectionState:
    """
    诊断：理解层的实体召回偏差、意图误解、规则触发遗漏。
    输出：修正建议 + 写入 understanding playbook
    路由：retry_understanding
    """
    failed_act    = state.get("failed_action", "无")
    error_msg     = state.get("error_feedback", "无报错")
    original      = state.get("original_instruction", "")
    st_task       = state.get("structured_task", {})
    feature_flags = state.get("feature_flags", {})
    messages_ctx  = str([m.content for m in state.get("messages", [])
                         if hasattr(m, 'content')])[-500:]  # 最近500字符

    history = load_section_rules("understanding")

    sys_prompt = render_prompt(
        "reflection.layer1_understanding",
        original=original,
        failed_action=failed_act,
        error_feedback=error_msg,
        structured_task_json=json.dumps(st_task, ensure_ascii=False),
        messages_context=messages_ctx,
        history=history,
    )

    response = get_reflection_llm().invoke([HumanMessage(content=sys_prompt)])
    result   = parse_json_from_llm(response.content, fallback={
        "corrected_understanding": "",
        "correction_strategy":     "理解层诊断崩溃，请重新输入指令",
        "next_routing":            "retry_understanding"
    })

    # 写入 playbook
    rule = result.get("experience_rule", "")
    if rule:
        write_experience(
            section="understanding",
            source="reflection_layer1",
            rule=rule,
            intent_context=original,
            feature_flags=feature_flags,
        )

    return {
        "failure_level":           "Layer1_指令理解层",
        "corrected_understanding": result.get("corrected_understanding", ""),
        "understanding_fix":       result.get("correction_strategy", ""),
        "correction_strategy":     result.get("correction_strategy", ""),
        "clarification_question":  "",
        "next_routing":            "retry_understanding",
        "extracted_experience":    result.get("diagnosis", "")
    }


# ─────────────────────────────────────────────────────────────────────
# 节点 2：任务分解层反思
# ─────────────────────────────────────────────────────────────────────
def layer2_planning_reflection_node(state: ReflectionState) -> ReflectionState:
    """
    诊断：分解层的步骤缺失、顺序错误、约束违反。
    输出：new_constraints + 写入 planning playbook
    路由：retry_planning
    """
    failed_act       = state.get("failed_action", "无")
    error_msg        = state.get("error_feedback", "无")
    original         = state.get("original_instruction", "")
    feature_flags    = state.get("feature_flags", {})
    resolved_env     = state.get("environment", {})
    task_stack       = state.get("task_stack", [])
    original_todo    = str(task_stack[-1].get("todo_list", []) if task_stack else [])
    evaluator_findings = state.get("evaluator_findings", [])

    history = load_section_rules("planning")

    # 可行性发现汇总（如果有）
    findings_str = ""
    if evaluator_findings:
        findings_str = "\n".join([f"  - {f.get('issue', '')} → {f.get('fix', '')}"
                                   for f in evaluator_findings])

    sys_prompt = render_prompt(
        "reflection.layer2_planning",
        original=original,
        failed_action=failed_act,
        error_feedback=error_msg,
        original_todo=original_todo,
        resolved_env_json=json.dumps(resolved_env, ensure_ascii=False)[:800],
        findings=findings_str if findings_str else "（无额外可行性发现）",
        history=history,
    )

    response = get_reflection_llm().invoke([HumanMessage(content=sys_prompt)])
    result   = parse_json_from_llm(response.content, fallback={
        "new_constraints":     [],
        "correction_strategy": "规划层诊断崩溃",
        "next_routing":        "retry_planning"
    })

    rule = result.get("experience_rule", "")
    if rule:
        write_experience(
            section="planning",
            source="reflection_layer2",
            rule=rule,
            intent_context=original,
            feature_flags=feature_flags,
        )

    return {
        "failure_level":       "Layer2_任务分解层",
        "new_constraints":     result.get("new_constraints", []),
        "corrected_plan_hint": result.get("corrected_plan_hint", ""),
        "correction_strategy": result.get("correction_strategy", ""),
        "next_routing":        "retry_planning",
        "extracted_experience": result.get("diagnosis", "")
    }


# ─────────────────────────────────────────────────────────────────────
# 节点 3：可行性审计层反思
# ─────────────────────────────────────────────────────────────────────
def layer3_feasibility_reflection_node(state: ReflectionState) -> ReflectionState:
    """
    触发场景：可行性审计（evaluator）反复拦截，说明分解层有系统性错误。
    诊断：找出 evaluator 反复拦截的深层原因（而非具体问题）。
    输出：写入 planning playbook（source="reflection_layer3"）
    路由：retry_planning

    注意：evaluator 每次拦截时已经直接写了 planning playbook，
    本层是在反思层被触发后，对「为什么规划层反复犯错」做更深层的归因。
    """
    error_msg        = state.get("error_feedback", "无")
    original         = state.get("original_instruction", "")
    st_task          = state.get("structured_task", {})
    feature_flags    = state.get("feature_flags", {})
    evaluator_findings = state.get("evaluator_findings", [])
    retry_count      = state.get("reflection_retry_count", 0)

    history = load_section_rules("planning")

    findings_str = "\n".join([
        f"  [{i+1}] {f.get('issue', '')} → {f.get('fix', '')}"
        for i, f in enumerate(evaluator_findings)
    ]) if evaluator_findings else "（无具体发现记录）"

    sys_prompt = render_prompt(
        "reflection.layer3_feasibility",
        retry_count=retry_count,
        original=original,
        error_feedback=error_msg,
        structured_task_json=json.dumps(st_task, ensure_ascii=False),
        findings=findings_str,
        history=history,
    )

    response = get_reflection_llm().invoke([HumanMessage(content=sys_prompt)])
    result   = parse_json_from_llm(response.content, fallback={
        "root_cause":         "可行性层诊断崩溃",
        "correction_strategy": "降级到规划层重试",
        "next_routing":       "retry_planning"
    })

    rule = result.get("experience_rule", "")
    if rule:
        write_experience(
            section="planning",
            source="reflection_layer3",
            rule=rule,
            intent_context=original,
            feature_flags=feature_flags,
        )

    return {
        "failure_level":       "Layer3_可行性审计层",
        "feasibility_fix":     result.get("feasibility_fix", ""),
        "planning_lesson":     rule,
        "correction_strategy": result.get("correction_strategy", ""),
        "next_routing":        "retry_planning",
        "extracted_experience": result.get("root_cause", "")
    }


# ─────────────────────────────────────────────────────────────────────
# 节点 4：执行/任务管理层反思
# ─────────────────────────────────────────────────────────────────────
def layer4_execution_reflection_node(state: ReflectionState) -> ReflectionState:
    """
    诊断：执行层的工具替代、硬件容错、任务管理异常。
    输出：corrected_execution + 写入 execution playbook
    路由：retry_execution（工具替代）或 retry_planning（需要重规划）
    """
    failed_act    = state.get("failed_action", "无")
    error_msg     = state.get("error_feedback", "无报错")
    st_task       = state.get("structured_task", {})
    resolved_env  = state.get("environment", {})
    original      = state.get("original_instruction", "")
    feature_flags = state.get("feature_flags", {})

    # 从结构化任务中提取工具和容器池
    names_info        = st_task.get("required_item_names", {})
    tools_pool        = _flatten_names(names_info.get("tools", []))
    receptacles_pool  = _flatten_names(names_info.get("receptacles", []))

    # 构建带状态的备选池
    all_available = tools_pool + receptacles_pool
    available_with_states = {
        item_name: resolved_env.get(item_name, {"states": "未知"})
        for item_name in resolved_env
        if any(kw in item_name for kw in all_available)
    }

    history = load_section_rules("execution")

    sys_prompt = render_prompt(
        "reflection.layer4_execution",
        failed_action=failed_act,
        error_feedback=error_msg,
        available_with_states_json=json.dumps(available_with_states, ensure_ascii=False),
        history=history,
    )

    response = get_reflection_llm().invoke([HumanMessage(content=sys_prompt)])
    result   = parse_json_from_llm(response.content, fallback={
        "failure_type":      "d",
        "corrected_execution": {},
        "correction_strategy": "执行层诊断崩溃，降级到规划层",
        "next_routing":      "retry_planning"
    })

    rule = result.get("experience_rule", "")
    if rule:
        write_experience(
            section="execution",
            source="reflection_layer4",
            rule=rule,
            intent_context=original,
            feature_flags=feature_flags,
        )

    return {
        "failure_level":     "Layer4_执行与任务管理层",
        "corrected_execution": result.get("corrected_execution", {}),
        "alternative_tools": result.get("alternative_tools", []),
        "correction_strategy": result.get("correction_strategy", ""),
        "next_routing":      result.get("next_routing", "retry_planning"),
        "extracted_experience": result.get("diagnosis", "")
    }


# ─────────────────────────────────────────────────────────────────────
# 图结构与路由
# ─────────────────────────────────────────────────────────────────────
def route_after_triage(state: ReflectionState) -> str:
    return state.get("determined_reflection_layer", "layer4_execution")


def build_reflection_graph():
    try:
        from langgraph.graph import END, StateGraph
    except Exception as exc:  # pragma: no cover - fail-soft import boundary
        raise RuntimeError("langgraph is required to build the reflection graph") from exc

    workflow = StateGraph(ReflectionState)

    workflow.add_node("failure_triage",           failure_triage_node)
    workflow.add_node("layer1_understanding",      layer1_understanding_reflection_node)
    workflow.add_node("layer2_planning",           layer2_planning_reflection_node)
    workflow.add_node("layer3_feasibility",        layer3_feasibility_reflection_node)
    workflow.add_node("layer4_execution",          layer4_execution_reflection_node)

    workflow.set_entry_point("failure_triage")

    workflow.add_conditional_edges(
        "failure_triage",
        route_after_triage,
        {
            "layer1_understanding": "layer1_understanding",
            "layer2_planning":      "layer2_planning",
            "layer3_feasibility":   "layer3_feasibility",
            "layer4_execution":     "layer4_execution",
            "end":                  END,
        }
    )

    # 四层都直接结束（经验已在各层节点内写入，不再需要单独的 ace_curator 节点）
    workflow.add_edge("layer1_understanding", END)
    workflow.add_edge("layer2_planning",      END)
    workflow.add_edge("layer3_feasibility",   END)
    workflow.add_edge("layer4_execution",     END)

    return workflow.compile()
