# EAI Case Report: 3_1

- dataset: `virtualhome`
- mode: `framework`
- status: `done`
- case meta: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_smoke_20260806_todo_hooks/cases/3_1/case.json`
- raw output: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_smoke_20260806_todo_hooks/cases/3_1/raw_output.json`
- trace json: ``
- evaluator summary: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_smoke_20260806_todo_hooks/cases/3_1/artifacts/evaluated/virtualhome/evaluate_results/action_sequencing/eai_virtualhome_smoke_20260806_todo_hooks__3_1/summary.json`
- evaluator detail: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_smoke_20260806_todo_hooks/cases/3_1/artifacts/evaluated/virtualhome/evaluate_results/action_sequencing/eai_virtualhome_smoke_20260806_todo_hooks__3_1/error_info.json`

- 完整阶段 artifact：`/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_smoke_20260806_todo_hooks/cases/3_1/artifacts`
- 完整输入输出 / 审计文件：`case_input.json`, `case_input_summary.json`, `prepared_environment.json`, `prepared_environment_summary.json`, `environment_audit.json`, `understanding_input.json`, `understanding_input_summary.json`, `understanding_output.json`, `understanding_output_summary.json`, `planning_input.json`, `planning_input_summary.json`, `planning_output.json`, `planning_output_summary.json`, `contract_audit.json`, `planning_feature_records.json`, `llm_io.json`, `goal_check.json`, `official_eval.json`, `process_summary.json`

## Result Summary
- task_success: `True`
- task_success_rate: `1.0`
- official_available: `True`
- execution_success: `True`
- execution_success_rate: `100.0`
- planning execution_status: `completed`
- planning is_feasible: `True`
- planning feedback: `规划合法，验证环节闭环。`
- todo_contract status: `passed`
- todo_contract audit: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_smoke_20260806_todo_hooks/cases/3_1/artifacts/contract_audit.json`

## Failure Summary
- framework passed: `True`
- framework intercept count: `0`
- framework terminal failure: ``
- official evaluator passed: `True`
- official evaluator failure type: ``
- official evaluator failure reason: ``

## Prompt / Round Files
- interceptions summary: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_smoke_20260806_todo_hooks/cases/3_1/artifacts/rounds/interceptions.md`
- rounds index: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_smoke_20260806_todo_hooks/cases/3_1/artifacts/rounds/rounds_index.json`

## Sequence

## Evaluator
- summary file: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_smoke_20260806_todo_hooks/cases/3_1/artifacts/evaluated/virtualhome/evaluate_results/action_sequencing/eai_virtualhome_smoke_20260806_todo_hooks__3_1/summary.json`
- detail file: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/framework/results/eai_virtualhome_smoke_20260806_todo_hooks/cases/3_1/artifacts/evaluated/virtualhome/evaluate_results/action_sequencing/eai_virtualhome_smoke_20260806_todo_hooks__3_1/error_info.json`

## Evaluator Detail Digest
```json
{
  "executable": true,
  "actions": [
    "[WALK] <couch> (352)",
    "[SIT] <couch> (352)"
  ],
  "error_type": null,
  "error_action": null
}
```
