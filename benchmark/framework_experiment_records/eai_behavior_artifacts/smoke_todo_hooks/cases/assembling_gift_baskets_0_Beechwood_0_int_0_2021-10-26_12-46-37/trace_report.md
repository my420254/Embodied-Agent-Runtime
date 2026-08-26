# EAI Case Report: assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37

- dataset: `behavior`
- mode: `framework`
- status: `done`
- case meta: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_smoke_20260806_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/case.json`
- raw output: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_smoke_20260806_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/raw_output.json`
- trace json: ``
- evaluator summary: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_smoke_20260806_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/evaluated/behavior/evaluate_results/action_sequencing/summary/eai_behavior_smoke_20260806_todo_hooks__assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37_outputs.json`
- evaluator detail: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_smoke_20260806_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/evaluated/behavior/evaluate_results/action_sequencing/log/eai_behavior_smoke_20260806_todo_hooks__assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37_outputs.json`

- 完整阶段 artifact：`/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_smoke_20260806_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts`
- 完整输入输出 / 审计文件：`case_input.json`, `case_input_summary.json`, `prepared_environment.json`, `prepared_environment_summary.json`, `environment_audit.json`, `understanding_input.json`, `understanding_input_summary.json`, `understanding_output.json`, `understanding_output_summary.json`, `planning_input.json`, `planning_input_summary.json`, `planning_output.json`, `planning_output_summary.json`, `contract_audit.json`, `planning_feature_records.json`, `llm_io.json`, `goal_check.json`, `official_eval.json`, `process_summary.json`

## Result Summary
- task_success: `True`
- task_success_rate: `1.0`
- official_available: `True`
- execution_success: `True`
- execution_success_rate: `1.0`
- planning execution_status: `completed`
- planning is_feasible: `True`
- planning feedback: `规划合法，验证环节闭环。`
- todo_contract status: `passed`
- todo_contract audit: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_smoke_20260806_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/contract_audit.json`

## Failure Summary
- framework passed: `True`
- framework intercept count: `0`
- framework terminal failure: ``
- official evaluator passed: `True`
- official evaluator failure type: ``
- official evaluator failure reason: ``

## Prompt / Round Files
- interceptions summary: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_smoke_20260806_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/rounds/interceptions.md`
- rounds index: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_smoke_20260806_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/rounds/rounds_index.json`

## Sequence

## Evaluator
- summary file: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_smoke_20260806_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/evaluated/behavior/evaluate_results/action_sequencing/summary/eai_behavior_smoke_20260806_todo_hooks__assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37_outputs.json`
- detail file: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/framework/results/eai_behavior_smoke_20260806_todo_hooks/cases/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37/artifacts/evaluated/behavior/evaluate_results/action_sequencing/log/eai_behavior_smoke_20260806_todo_hooks__assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37_outputs.json`

## Evaluator Detail Digest
```json
{
  "error_type": {
    "parsing": null,
    "hullucination": null,
    "arguments": null,
    "execution_success": true
  },
  "goal_rst": {
    "all_goal_satisfied_ig": true,
    "all_goal_satisfied_graph": true,
    "tot_predicates": 4.0,
    "tot_edge_predicates": 4.0,
    "tot_node_predicates": 0.0,
    "satisfied_predicates": 4.0,
    "satisfied_edge_predicates": 4.0,
    "satisfied_node_predicates": 0.0,
    "pure_edge_predicates": 4,
    "pure_node_predicates": 0,
    "mixed_predicates": 0,
    "satisfied_pure_edge_predicates": 4,
    "satisfied_pure_node_predicates": 0,
    "satisfied_mixed_predicates": 0
  },
  "satisfication_info": {
    "satisfied": [
      0,
      1,
      2,
      3
    ],
    "unsatisfied": []
  },
  "first_execution_error": null
}
```
