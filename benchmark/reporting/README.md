# Benchmark Reporting

更新时间：2026-08-06

## 目标

`benchmark/reporting` 负责把 framework benchmark 的每条 case 记录成可审计 artifacts 和 `trace_report.md`。记录原则：

- `todo_list` 是统一变量名，里面保存当前数据集的原生动作序列。
- reporting 不判断 benchmark/native action 模式，也不把动作强行包成 framework `execution/skill/parameters`。
- 每条 case 都要能追溯输入、understanding、planning、LLM 调用、contract 检查、sandbox 变化、最终态审计和官方评估。

## 标准 artifacts

每条 case 的 `artifacts/` 下应包含：

- `case_input.json` / `case_input_summary.json`
- `prepared_environment.json` / `prepared_environment_summary.json`
- `environment_audit.json`
- `understanding_input.json` / `understanding_output.json`
- `planning_input.json` / `planning_output.json`
- `contract_audit.json`
- `planning_feature_records.json`
- `goal_check.json`
- `official_eval.json`
- `llm_io.json`
- `rounds/round_*_input.md` 和 `rounds/round_*_output.txt`

这些文件由 `trace_artifacts.py` 和各 benchmark 的 persist/report writer 生成。

## todo_list 审计字段

planning 相关报告统一使用：

- `todo_output_parser_path`
- `todo_step_adapter_path`
- `todo_list_validator_path`
- `todo_llm_output`
- `todo_parse_error`
- `todo_list`
- `validated_todo_actions`
- `todo_checkpoint_env`
- `todo_checkpoint_robot`

不再使用旧字段：

- `planning_output_mode`
- `native_llm_output`
- `native_parse_error`
- `validated_native_actions`
- `native_checkpoint_*`

## contract_audit.json

`contract_audit.json` 记录动作 schema 检查：

- 当前数据集启用的 skill contract。
- `todo_list` 顶层字段形状。
- 动作名分布。
- 是否出现 framework execution wrapper。
- 必填字段、固定字段、实体字段、额外字段检查。
- `todo_list_count`、`validated_todo_actions_count`、`validated_steps_count`。

contract 只描述动作格式和参数规则，不写具体 case 的答案序列。

## sandbox 与最终态

sandbox 检查必须使用当前数据集自己的环境：

- DELTA 使用 DELTA room/item/PDDL 环境。
- EAI BEHAVIOR 使用 BEHAVIOR initial env 和 goal clauses。
- EAI VirtualHome 使用 VirtualHome graph/object table。
- ReAcTree WAH 使用 WAH init graph/task_goal。
- ReAcTree ALFRED 使用 ALFRED official scene cache/AI2-THOR state。

`goal_check.json` 保存 benchmark-local final-state compare、state diff 和 official evaluator summary。最终态 compare 由各数据集 settings 的 `final_state_module` 指定。

## LLM 调用记录

`llm_io.json` 记录每次模型调用：

- `process_name`
- `prompt_name`
- `call_stage`
- chat input
- raw output

常见调用：

- `understanding.system`
- `understanding.final_state`
- `planning.main_system`
- `planning.state_diff_audit`

如果发生 repair，`planning.main_system` 会出现多轮，例如 ALFRED smoke 中初次 planning 后因 sandbox 拦截进入 repair。

## 当前审计批次

本轮 2026-08-06 的手工审计和 smoke/full 启动记录在：

```text
/data/zmy/OurAgent-he1/benchmark/framework_experiment_records
```

该目录包含每个数据集的 smoke md、复制后的 artifacts、3.6 full 队列脚本和队列日志。
