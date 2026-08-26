"""Terminal renderer for the OurAgent CLI.

Pure view layer: formats LangGraph state dumps into readable terminal panels.
It never drives the graph; the engine (agent_runtime.engine) calls back into
render_stream() with each streamed output chunk.
"""

# =====================================================================
# 打印工具 (UI 格式化)
# 作用：在终端绘制分割线，使系统输出呈现标准的结构化监控面板风格
# =====================================================================
def print_banner(title):
    """打印带上下粗边框的标题"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def print_divider(char="-"):
    """打印细分割线"""
    print(char * 70)


def _grounding_rows_for_display(grounding: dict, relevant_names: list | None, limit: int = 30) -> tuple[list, int]:
    if not isinstance(grounding, dict) or not grounding:
        return [], 0

    selected = []
    seen = set()
    for name in relevant_names or []:
        if name in grounding and name not in seen:
            selected.append(name)
            seen.add(name)
            parent = grounding.get(name, {}).get("direct_parent")
            if parent in grounding and parent not in seen:
                selected.append(parent)
                seen.add(parent)

    names = selected or list(grounding.keys())
    rows = [(name, grounding[name]) for name in names[:limit] if name in grounding]
    omitted = max(len(names) - len(rows), 0)
    return rows, omitted


# =====================================================================
# 全链路渲染器 (Renderer)
# 架构价值：彻底剥离“控制逻辑”与“视图渲染”。
# 本函数仅负责将状态机流转时输出的 state 数据格式化并打印至终端。
# =====================================================================
def render_stream(stream_generator, config, graph_app):
    """
    逐事件渲染每个节点的输出。
    """
    for output in stream_generator:
        namespace, chunk = output
        
        for node_name, state in chunk.items():

            # ──────────────────────────────────────────────────────
            # 渲染：指令理解分析节点
            if node_name == "analyze":
                st   = state.get("structured_task", {})
                msgs = state.get("messages") or graph_app.get_state(config).values.get("messages", [])
                last = msgs[-1].content if msgs else "（无）"

                print("[模块 1: 指令理解 (Understanding)]")
                print(f"  - 输入指令: '{last}'")
                print(f"  - 意图锁定: 【{st.get('intent', '未知')}】")
                
                concepts = st.get("required_item_names", {})
                if concepts:
                    print("  - [泛化实体提炼]:")
                    print(f"    ├─ 操作目标:   {concepts.get('targets', [])}")
                    print(f"    ├─ 涉及容器:   {concepts.get('receptacles', [])}")
                    print(f"    ├─ 工具及备用: {concepts.get('tools', [])}")

                if state.get("is_complete"):
                    print("  - 结果: [通过] 指令完备 -> 流转至规划模块")
                else:
                    print("  - 结果: [拦截] 指令不完备 -> 触发主动澄清")
                print_divider()

            # ──────────────────────────────────────────────────────
            # 渲染：主动反问节点
            elif node_name == "ask":
                msgs = state.get("messages") or graph_app.get_state(config).values.get("messages", [])
                q    = msgs[-1].content if msgs else "（无澄清内容）"
                print("[模块 1: 主动澄清 (Ask)]")
                print(f"  - 系统发问: {q}")
                print_divider()

            # ──────────────────────────────────────────────────────
            # 渲染：任务规划节点 (适配全新 JSON 结构)
            elif node_name == "decompose":
                full_state = graph_app.get_state(config).values
                st         = full_state.get("structured_task", {})
                todo_list  = state.get("todo_list", [])
                iters      = state.get("iteration_count", 1)
                
                re_trac_memory  = state.get("re_trac_memory", {}).get("failed_lessons", [])
                validated_steps = state.get("validated_steps", [])

                print(f"[模块 2: 任务分解 (Planning) — 第 {iters} 次迭代]")

                if iters == 1:
                    grounding = state.get("environment", {})
                    relevant_names = full_state.get("relevant_item_names", [])
                    rows, omitted = _grounding_rows_for_display(grounding, relevant_names)
                    print("  - [物理沙盘快照]:")
                    if not grounding:
                        print("    (未查询到相关实体上下文)")
                    for item, info in rows:
                        print(f"    ├─ {item}: 位置={info.get('direct_parent')}  状态={info.get('states')}")
                    if omitted:
                        print(f"    └─ ... 已省略 {omitted} 个实体")
                    print()
                else:
                    if re_trac_memory:
                        print("  - [RE-TRAC 历史防错记录]:")
                        for lesson in re_trac_memory:
                            print(f"    × {lesson}")
                    if validated_steps:
                        print(f"  - [Checkpoint 还原]: 已锁定前 {len(validated_steps)} 步合法序列，触发断点续写流程。")
                    print()

                print("  - [推演动作序列]:")
                if not todo_list:
                    print("    (序列为空)")
                else:
                    for step in todo_list:
                        step_num = step.get('step', '?')
                        
                        # 兼容新版 Anthropic 风格 JSON
                        execution = step.get('execution', {})
                        if execution:
                            skill = execution.get('skill', '未知动作')
                            params = execution.get('parameters', {})
                            action_str = f"{skill}({params})"
                        else:
                            # 兼容可能遗留的旧版输出
                            action_str = step.get('action', '未知动作')
                            
                        awareness = step.get('state_awareness', {})
                        pred_loc = awareness.get('current_location', '未知')
                        pred_hold = awareness.get('current_held_item', '未知')
                        
                        checks = step.get('pre_flight_checks', [])
                        reason_str = " | ".join(checks) if checks else step.get('reason_and_check', '无检验记录')
                        
                        print(f"    [{step_num}] {action_str}")
                        print(f"        ├─ 检验核对: {reason_str}")
                        print(f"        └─ 预期终态: 位置=[{pred_loc}] | 手持=[{pred_hold}]")
                print_divider()

            # ──────────────────────────────────────────────────────
            # 渲染：计划审计节点
            elif node_name == "evaluate":
                is_feasible = state.get("is_feasible")
                feedback    = state.get("feedback")
                exec_status = state.get("execution_status")

                print("[模块 2: 计划审计 (Evaluator)]")
                
                if exec_status == "failed":
                    max_iterations = get_config("planning", "max_iterations", default=10)
                    print(f"  - [系统熔断] 物理拦截超限 ({max_iterations}次)，规划引擎终止运行。")
                    print(f"  - 终止理由: {state.get('error_feedback', '无')}")
                    print("  - 路由转向: 强制切入反思接管模式...")
                    print_divider()
                    continue

                if is_feasible:
                    print("  - 结果: [通过] 审计验证完成")
                    print_divider("=")
                    print("[已锁定动作序列 (交付执行层)]:")
                    
                    final_todo = state.get("todo_list", [])
                    if not final_todo:
                        reason = feedback if feedback else "任务流为空，无需后续动作。"
                        print(f"  提示: {reason}")
                    else:
                        print(json.dumps(final_todo, ensure_ascii=False, indent=2))
                    
                    print("\n[状态] 数据流转至物理执行层")
                    print_divider("=")
                else:
                    print(f"  - 结果: [驳回] 计划审计未通过。")
                    print(f"  - 拦截理由: {feedback}")
                    print_divider()

            # ──────────────────────────────────────────────────────
            # 渲染：任务管理中枢
            elif node_name == "task_manager":
                status = state.get("execution_status")
                stack  = state.get("task_stack", [])

                if status == "interrupted":
                    print()
                    print_divider("=")
                    print("[任务管理中枢] 中断触发：原任务队列挂起，系统转向新指令解析阶段。")
                    print_divider("=")

                elif status == "paused":
                    print()
                    print_divider("=")
                    print("[任务管理中枢] 当前任务已暂停，任务栈保留在检查点。")
                    print_divider("=")

                elif status == "cancelled":
                    print()
                    print_divider("=")
                    print("[任务管理中枢] 当前任务已取消，任务栈已清空或回退。")
                    print_divider("=")

                elif status == "success":
                    print()
                    print_divider("=")
                    print("[任务管理中枢] 当前任务栈内物理动作已全部清空。")
                    print_divider("=")

                elif stack:
                    top = stack[-1] 
                    remaining_steps = len(top.get("todo_list", []))
                    if remaining_steps > 0:
                        first_item = top["todo_list"][0]
                        if isinstance(first_item, dict) and "execution" in first_item:
                            next_action = f"{first_item['execution'].get('skill', '未知')}(...)"
                        else:
                            next_action = "未知动作"

                        print(f"\n[任务管理中枢] 当前主干任务: 「{top.get('instruction', '')}」")
                        print(f"  剩余步骤: {remaining_steps}")
                        print(f"  预备执行动作: {next_action}")
                        print(f"  当前压栈深度: {len(stack)}")

            # ──────────────────────────────────────────────────────
            # 渲染：极速分类节点
            elif node_name == "task_classification":
                category = state.get("current_action_category", "未分类")
                full_state = graph_app.get_state(config).values
                stack = state.get("task_stack") or full_state.get("task_stack", [])
                cur_action = "未知动作"
                
                if stack and stack[-1].get("todo_list"):
                    item = stack[-1]["todo_list"][0]
                    if isinstance(item, dict) and "execution" in item:
                        cur_action = item["execution"].get("skill", "未知动作")
                if cur_action == "未知动作":
                    print(f"  [指令分类] 当前动作所属调用域: {category}")
                else:
                    print(f"  [指令分类] {cur_action} -> 所属调用域: {category}")

            # ──────────────────────────────────────────────────────
            # 渲染：底层工具报错
            elif node_name == "simulate_action":
                status = state.get("execution_status")
                if status == "failed":
                    print()
                    print_divider("=")
                    print(f"[底层调用] 硬件或工具链执行抛出异常")
                    print(f"  异常动作: {state.get('failed_action', '未知')}")
                    print(f"  错误详情: {state.get('error_feedback', '未知')}")
                    print(f"  捕获层级: {state.get('failure_layer', '未知')}")
                    print_divider("=")

            # ──────────────────────────────────────────────────────
            # 渲染：反思分诊台
            elif node_name == "failure_triage":
                layer = state.get("determined_reflection_layer", "未知")
                layer_names = {
                    "layer1_understanding": "Layer1 指令理解层",
                    "layer2_planning":      "Layer2 规划逻辑层",
                    "layer3_feasibility":   "Layer3 可行性审计层",
                    "layer4_execution":     "Layer4 执行/任务管理层"
                }
                print(f"\n[异常分析] 激活故障分诊协议 -> 分发至: {layer_names.get(layer, layer)}")
                print_divider()

            # 渲染：各级反思诊断结果
            elif node_name in ("layer1_understanding", "layer2_planning", "layer3_feasibility", "layer4_execution"):
                labels = {
                    "layer1_understanding": "Layer1 指令理解异常反思",
                    "layer2_planning":      "Layer2 任务分解流异常反思",
                    "layer3_feasibility":   "Layer3 可行性审计异常反思",
                    "layer4_execution":     "Layer4 执行与任务管理异常反思"
                }
                print(f"[{labels.get(node_name, node_name)}]")
                
                if node_name == "layer4_execution":
                    alt_tools = state.get('alternative_tools', [])
                    if alt_tools:
                        print(f"  - 系统检测到可用替代工具: {alt_tools}")
                    print(f"  - 动作修正提议: {state.get('corrected_execution', {})}")
                elif node_name == "layer2_planning":
                    constraints = state.get('new_constraints', [])
                    if constraints:
                        print(f"  - 追加临时环境约束: {constraints}")
                elif node_name == "layer1_understanding":
                    cq = state.get('clarification_question', '')
                    if cq:
                        print(f"  - 拟定对等澄清话术: {cq}")
                elif node_name == "layer3_feasibility":
                    fix = state.get('feasibility_fix', '')
                    if fix:
                        print(f"  - 审计修复方向: {fix}")

                print(f"  - 整体修正策略: {state.get('correction_strategy', '无')}")
                print(f"  - 后续重试路由: {state.get('next_routing', '未知')}")
                print_divider()

            # 渲染：经验法则入库
            elif node_name == "ace_curator":
                print(f"[经验沉淀 (Curator)] 知识库检索与更新执行完毕")
                exp = state.get("extracted_experience", "")
                if exp:
                    print(f"  - 新增记录: {exp}")
                print_divider()

            # ──────────────────────────────────────────────────────
            # 渲染：系统过桥节点
            elif node_name == "Handle_Interrupt":
                new_instr = state.get("raw_instruction", "未知指令")
                print(f"\n[任务阻断] 捕获优先级覆盖指令: \"{new_instr}\" -> 转交意图解析单元")
                print_divider()

            elif node_name == "Inject_And_Execute":
                print(f"\n[资源调度] 新任务分配完毕，前置任务栈状态已封存。")
                print_divider()

            elif node_name in ("Retry_Execution", "Retry_Planning", "Retry_Understanding"):
                labels = {
                    "Retry_Execution":     "执行层回滚重试 (应用工具修正)",
                    "Retry_Planning":      "规划层回滚重试 (引入新边界约束)",
                    "Retry_Understanding": "理解层回滚重试 (启动用户交互澄清)"
                }
                print(f"\n[异常恢复] 状态机跳转 -> {labels.get(node_name, node_name)}")
                print_divider()
            
            # ──────────────────────────────────────────────────────
            # 渲染：人类验收环节
            elif node_name == "Ask_Human_Feedback":
                print("\n" + "=" * 70)
                print(state.get("clarification_question", "[系统提示] 流程抵达检查点，等待操作员验收。"))
                print("=" * 70)


# =====================================================================
