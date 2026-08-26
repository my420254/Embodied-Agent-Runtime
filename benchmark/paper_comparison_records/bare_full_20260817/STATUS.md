# Bare Full Rerun Status 2026-08-17

- resumed_from_session: `01a00d4b-4b56-7c30-92f6-d3d1fc60f0c1`
- rollout: `/data/zmy/.codex_runtime/sessions/2026/08/17/rollout-2026-08-17T01-17-13-01a00d4b-4b56-7c30-92f6-d3d1fc60f0c1.jsonl`
- continued_from_session: `01a00df9-0442-7f42-8045-ba0efcf196a4`
- continuation_rollout: `/data/zmy/.codex_runtime/sessions/2026/08/17/rollout-2026-08-17T04-26-58-01a00df9-0442-7f42-8045-ba0efcf196a4.jsonl`
- current_tmux: `bare_full_qwen36_lane_20260817` + `qwen35_wah_20260817` + `qwen35_alfred_seen_20260817`
- launch_script: `/data/zmy/OurAgent-he1/benchmark/paper_comparison_records/run_bare_full_qwen36_lane_20260817.sh` + `run_bare_full_qwen35_lane_20260817.sh`
- log_root: `/data/zmy/OurAgent-he1/benchmark/paper_comparison_records/bare_full_20260817/logs_lanes`

## User Request

Run smoke first, then rerun bare baselines after clearing results:

- DELTA
- ReAcTree WAH
- ReAcTree ALFRED
- EAI BEHAVIOR
- EAI VirtualHome

## Smoke Checks

- DELTA smoke: `codex_delta_bare_smoke_20260817`
  - Path: `/data/zmy/OurAgent-he1/benchmark/delta/bare_baseline/results/codex_delta_bare_smoke_20260817`
  - Result before clearing: `done_cases=1`, `parse_error=""`, official action parsing/evaluator path OK.
- EAI BEHAVIOR smoke: `codex_behavior_bare_smoke_20260817`
  - Path before clearing: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/bare_baseline/results/codex_behavior_bare_smoke_20260817`
  - Result before clearing: `done_cases=1`, official evaluator returned.
- EAI VirtualHome smoke: `codex_virtualhome_bare_smoke_20260817`
  - Path before clearing: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/bare_baseline/results/codex_virtualhome_bare_smoke_20260817`
  - Result before clearing: `done_cases=1`, task success 100 for case `3_1`; safe summary handled upstream zero-denominator issue.
- ReAcTree WAH smoke: `codex_wah_bare_smoke_official_20260817`
  - Path before clearing: `/data/zmy/OurAgent-he1/benchmark/reactree/wah/bare_baseline/results/codex_wah_bare_smoke_official_20260817`
  - Result before clearing: `done_cases=1`, `official_available_count=1`, `evaluation_modes.reactree_official_wah_unity=1`.
- ReAcTree ALFRED smoke used existing interface:
  - Command: `/data/zmy/alfred/bare_baseline/run_bare_18004.sh --split valid_seen --limit 1 --run-name codex_alfred_bare_smoke_20260817 --reset`
  - Path before clearing: `/data/zmy/alfred/bare_baseline/results/codex_alfred_bare_smoke_20260817`
  - Result before clearing: `status=done`, `text_returncode=0`, `simulation_returncode=0`, `official_available=1`.

## Results Cleared

Cleared and recreated:

- `/data/zmy/OurAgent-he1/benchmark/delta/bare_baseline/results`
- `/data/zmy/OurAgent-he1/benchmark/eai/behavior/bare_baseline/results`
- `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/bare_baseline/results`
- `/data/zmy/OurAgent-he1/benchmark/reactree/wah/bare_baseline/results`
- `/data/zmy/OurAgent-he1/benchmark/reactree/alfred/bare_baseline/results`
- `/data/zmy/alfred/bare_baseline/results`

## Dual-Lane 12-Run Matrix

Started at `2026-08-17 07:25:21 UTC` as two parallel lanes:

- `bare_full_qwen36_lane_20260817` uses `18003/Qwen3.6-27B`.
- `bare_full_qwen35_lane_20260817` uses `18004/Qwen3.5-9B`.

Execution order across both lanes:

Qwen3.6 lane: `3 -> 5 -> 7 -> 9 -> 10`.
Qwen3.5 lane: `4 -> 8 -> 6 -> 11 -> 12`.

1. `delta_bare_full_qwen35_20260817`
   - Wrapper: `benchmark/delta/bare_baseline/code/run.py`
   - Run root: `/data/zmy/OurAgent-he1/benchmark/delta/bare_baseline/results/delta_bare_full_qwen35_20260817`
   - LLM: `18004/Qwen3.5-9B`
   - workers: `5`
   - status: completed, kept.
2. `eai_behavior_bare_full_qwen36_20260817`
   - Wrapper: `benchmark/eai/behavior/bare_baseline/code/run.py`
   - Run root: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/bare_baseline/results/eai_behavior_bare_full_qwen36_20260817`
   - LLM: `18003/Qwen3.6-27B`
   - workers: `5`
   - status: completed, kept.
3. `delta_bare_full_qwen36_20260817`
   - Wrapper: `benchmark/delta/bare_baseline/code/run.py`
   - Run root: `/data/zmy/OurAgent-he1/benchmark/delta/bare_baseline/results/delta_bare_full_qwen36_20260817`
   - LLM: `18003/Qwen3.6-27B`
   - workers: `5`
   - status: running.
4. `eai_behavior_bare_full_qwen35_20260817`
   - Wrapper: `benchmark/eai/behavior/bare_baseline/code/run.py`
   - Run root: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/bare_baseline/results/eai_behavior_bare_full_qwen35_20260817`
   - LLM: `18004/Qwen3.5-9B`
   - workers: `5`
5. `eai_virtualhome_bare_full_qwen36_20260817`
   - Wrapper: `benchmark/eai/virtualhome/bare_baseline/code/run.py`
   - Run root: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/bare_baseline/results/eai_virtualhome_bare_full_qwen36_20260817`
   - LLM: `18003/Qwen3.6-27B`
   - workers: `5`
   - full `342` cases, no `--valid-only`.
6. `eai_virtualhome_bare_full_qwen35_20260817`
   - Wrapper: `benchmark/eai/virtualhome/bare_baseline/code/run.py`
   - Run root: `/data/zmy/OurAgent-he1/benchmark/eai/virtualhome/bare_baseline/results/eai_virtualhome_bare_full_qwen35_20260817`
   - LLM: `18004/Qwen3.5-9B`
   - workers: `5`
   - full `342` cases, no `--valid-only`.
7. `reactree_wah_bare_full_qwen36_official_100_20260817`
   - Wrapper: `benchmark/reactree/wah/bare_baseline/code/run.py`
   - Uses existing WAH Unity official evaluator via `evaluate_reactree_goals -> _official_eval_worker.py`
   - Run root: `/data/zmy/OurAgent-he1/benchmark/reactree/wah/bare_baseline/results/reactree_wah_bare_full_qwen36_official_100_20260817`
   - LLM: `18003/Qwen3.6-27B`
   - workers: `5`
   - main denominator: `100` task-level cases (`task_id:0`).
   - official ports: `9910+0..4`
8. `reactree_wah_bare_full_qwen35_official_100_20260817`
   - Wrapper: `benchmark/reactree/wah/bare_baseline/code/run.py`
   - Run root: `/data/zmy/OurAgent-he1/benchmark/reactree/wah/bare_baseline/results/reactree_wah_bare_full_qwen35_official_100_20260817`
   - LLM: `18004/Qwen3.5-9B`
   - workers: `5`
   - main denominator: `100` task-level cases (`task_id:0`).
   - official ports: `9920+0..4`
9. `reactree_alfred_bare_full_qwen36_seen_20260817`
   - Wrapper: `benchmark/reactree/alfred/bare_baseline/code/run.py`
   - Run root: `/data/zmy/OurAgent-he1/benchmark/reactree/alfred/bare_baseline/results/reactree_alfred_bare_full_qwen36_seen_20260817`
   - LLM: `18003/Qwen3.6-27B`
   - workers: `5`, X displays `98..102`, `valid_seen`.
10. `reactree_alfred_bare_full_qwen36_unseen_20260817`
    - Wrapper: `benchmark/reactree/alfred/bare_baseline/code/run.py`
    - Run root: `/data/zmy/OurAgent-he1/benchmark/reactree/alfred/bare_baseline/results/reactree_alfred_bare_full_qwen36_unseen_20260817`
    - LLM: `18003/Qwen3.6-27B`
    - workers: `5`, X displays `108..112`, `valid_unseen`.
11. `reactree_alfred_bare_full_qwen35_seen_20260817`
    - Wrapper: `benchmark/reactree/alfred/bare_baseline/code/run.py`
    - Run root: `/data/zmy/OurAgent-he1/benchmark/reactree/alfred/bare_baseline/results/reactree_alfred_bare_full_qwen35_seen_20260817`
    - LLM: `18004/Qwen3.5-9B`
    - workers: `5`, X displays `118..122`, `valid_seen`.
12. `reactree_alfred_bare_full_qwen35_unseen_20260817`
    - Wrapper: `benchmark/reactree/alfred/bare_baseline/code/run.py`
    - Run root: `/data/zmy/OurAgent-he1/benchmark/reactree/alfred/bare_baseline/results/reactree_alfred_bare_full_qwen35_unseen_20260817`
    - LLM: `18004/Qwen3.5-9B`
    - workers: `5`, X displays `128..132`, `valid_unseen`.

## Check Commands

```bash
tmux ls
tmux capture-pane -pt bare_full_qwen36_lane_20260817 -S -120
tail -n 80 /data/zmy/OurAgent-he1/benchmark/paper_comparison_records/bare_full_20260817/logs_lanes/qwen36/delta_bare_full_qwen36_20260817.log
tmux capture-pane -pt bare_full_qwen35_lane_20260817 -S -120
tail -n 80 /data/zmy/OurAgent-he1/benchmark/paper_comparison_records/bare_full_20260817/logs_lanes/qwen35/eai_behavior_bare_full_qwen35_20260817.log
find /data/zmy/OurAgent-he1/benchmark -path '*/bare_baseline/results/*/summary.json' -print
find /data/zmy/alfred/bare_baseline/results -maxdepth 2 -name summary.json -print
```

## Current State 2026-08-17 07:25 UTC

- Two model lanes run concurrently; each lane uses `--workers 5` inside its current dataset.
- Current tmux: `bare_full_qwen36_lane_20260817` and `bare_full_qwen35_lane_20260817`.
- DELTA Qwen3.5 completed at `2026-08-17 04:51:23 UTC`.
  - Summary: `total_cases=600`, `done_cases=600`, `failed_cases=0`, `success_cases=89`, `case_success_rate=14.833333333333334`, `goal_success_rate=0.6892460317460258`.
  - Summary path: `/data/zmy/OurAgent-he1/benchmark/delta/bare_baseline/results/delta_bare_full_qwen35_20260817/summary.json`.
- EAI BEHAVIOR Qwen3.6 completed and kept:
  - Summary path: `/data/zmy/OurAgent-he1/benchmark/eai/behavior/bare_baseline/results/eai_behavior_bare_full_qwen36_20260817/summary.json`.
- Qwen3.6 lane current step: `delta_bare_full_qwen36_20260817`, resumed from 16 completed cases.
  - Process: `/data/zmy/envs/ouragent/bin/python benchmark/delta/bare_baseline/code/run.py --run-name delta_bare_full_qwen36_20260817 --workers 5 --ports 18003 --api-model Qwen3.6-27B --api-key qwen-local-key --resume`.
- Qwen3.5 lane current step: `eai_behavior_bare_full_qwen35_20260817`.
  - Process: `/data/zmy/envs/ouragent/bin/python benchmark/eai/behavior/bare_baseline/code/run.py --run-name eai_behavior_bare_full_qwen35_20260817 --workers 5 --ports 18004 --api-model Qwen3.5-9B --api-key qwen-local-key --resume`.

## Semantics 2026-08-17 07:25 UTC

Main target is three papers / five datasets, with both model backends for every dataset:

- 5 datasets: DELTA, EAI BEHAVIOR, EAI VirtualHome, ReAcTree WAH, ReAcTree ALFRED.
- 2 models: `18003/Qwen3.6-27B` and `18004/Qwen3.5-9B`.
- Main table: `5 x 2 = 10` full experiments.
- ALFRED seen/unseen are both part of the ALFRED experiment, so execution units are 12 runs: `valid_seen` and `valid_unseen` for each backend.
- EAI VirtualHome uses full `342`, not `--valid-only` `338`.
- WAH main denominator is `100` task-level cases (`task_id:0`); the `195` instruction-level extracted cases are not mixed into the main table.
- EAI BEHAVIOR/VirtualHome evaluation is CPU-only, no simulator port.
- WAH Unity ports: Qwen3.6 lane `9910..9914`; Qwen3.5 lane `9920..9924`.
- ALFRED Xvfb displays: Qwen3.6 lane `98..102` and `108..112`; Qwen3.5 lane `118..122` and `128..132`.

Actual endpoint probe:

- `18003 -> Qwen3.6-27B`
- `18004 -> Qwen3.5-9B`
- `18001/18002` refused connection from this host.

Already completed and kept:

- `delta_bare_full_qwen35_20260817`: DELTA, Qwen3.5, 600/600.
- `eai_behavior_bare_full_qwen36_20260817`: EAI BEHAVIOR, Qwen3.6, 100/100.

Current lanes skip the two completed runs and run the remaining 10 execution units in parallel by model, all with 5 internal workers where supported:

- DELTA Qwen3.6, 600.
- EAI BEHAVIOR Qwen3.5, 100.
- EAI VirtualHome Qwen3.6, 342.
- EAI VirtualHome Qwen3.5, 342.
- ReAcTree WAH Qwen3.6, 100 task-level, Unity official evaluator.
- ReAcTree WAH Qwen3.5, 100 task-level, Unity official evaluator.
- ReAcTree ALFRED valid_seen Qwen3.6, 820, AI2-THOR/Xvfb.
- ReAcTree ALFRED valid_unseen Qwen3.6, 821, AI2-THOR/Xvfb.
- ReAcTree ALFRED valid_seen Qwen3.5, 820, AI2-THOR/Xvfb.
- ReAcTree ALFRED valid_unseen Qwen3.5, 821, AI2-THOR/Xvfb.

## Update 2026-08-17 07:45 UTC

Added a third parallel lane so the Qwen3.5 endpoint (18004) runs two datasets at once:

- `qwen35_virtualhome_parallel_20260817` runs EAI VirtualHome Qwen3.5 (342 cases, 5 workers, `--resume`) in parallel with the main Qwen3.5 lane.
  - Command: `/data/zmy/envs/ouragent/bin/python benchmark/eai/virtualhome/bare_baseline/code/run.py --run-name eai_virtualhome_bare_full_qwen35_20260817 --workers 5 --ports 18004 --api-model Qwen3.5-9B --api-key qwen-local-key --resume`
  - Log: `/data/zmy/OurAgent-he1/benchmark/paper_comparison_records/bare_full_20260817/logs_lanes/qwen35/eai_virtualhome_bare_full_qwen35_20260817_parallel.log`
  - VirtualHome is CPU-only (uses extracted `initial_envs`), no Unity/Xvfb ports, so it does not conflict with WAH or ALFRED.
  - The main Qwen3.5 lane will later reach its own `eai_virtualhome_bare_full_qwen35_20260817` step; `--resume` will make it skip already-done cases.

Progress at 07:45 UTC:

- Qwen3.6 lane (18003): DELTA `delta_bare_full_qwen36_20260817` ~72/600, ~3-4 cases/min with 5 workers.
- Qwen3.5 lane (18004): BEHAVIOR `eai_behavior_bare_full_qwen35_20260817` 100/100 generated; official re-evaluator (`agent_evaluation`) still finishing, then lane moves to WAH.
- Parallel Qwen3.5: VirtualHome 43/342 and climbing, ~20 cases/min.

ETA (rough, observed rates):

- BEHAVIOR final eval: minutes away.
- VirtualHome Qwen3.5: ~15-20 min total.
- WAH (both models, 100 task-level with Unity evaluator): ~1 h each once started.
- DELTA Qwen3.6: ~2.5-3 h from 07:45 (600 @ 3-4/min).
- ALFRED seen/unseen (820/821 per model per split): the long tail, est. several hours per split.

## Update 2026-08-17 07:50 UTC

Added a fourth lane to keep Qwen3.5 busy on the long tail:

- `qwen35_alfred_unseen_parallel_20260817` runs ALFRED `valid_unseen` Qwen3.5 (821 cases, 5 workers, Xvfb `128..132`, `--resume`), same run name as the main lane's final step.
  - Command: `/data/zmy/envs/ouragent/bin/python benchmark/reactree/alfred/bare_baseline/code/run.py --run-name reactree_alfred_bare_full_qwen35_unseen_20260817 --workers 5 --ports 18004 --api-model Qwen3.5-9B --api-key qwen-local-key --eval-set valid_unseen --x-displays 128 129 130 131 132 --resume`
  - Log: `/data/zmy/OurAgent-he1/benchmark/paper_comparison_records/bare_full_20260817/logs_lanes/qwen35/reactree_alfred_bare_full_qwen35_unseen_20260817_parallel.log`
  - Expected: when the main Qwen3.5 lane later reaches its own ALFRED unseen step while this lane still holds X displays `128..132`, that step exits fast with `reactree_alfred_x_display 已被其他当前 framework run 锁定` (non-blocking flock) and the lane finishes; the parallel lane already covers that matrix cell. No data corruption.
- Qwen3.5 now runs two datasets concurrently: VirtualHome (parallel) + WAH/ALFRED-seen (main lane), plus ALFRED unseen long-tail (parallel).

Progress at 07:50 UTC:

- Qwen3.6 lane (18003): DELTA ~84/600.
- Qwen3.5 main lane (18004): BEHAVIOR 100/100, official re-evaluator still running (started ~07:42); WAH will start after it exits.
- Parallel VirtualHome Qwen3.5: ~120/342.
- Parallel ALFRED unseen Qwen3.5: started, 821 cases, Xvfb up.

## Update 2026-08-17 09:48 UTC

The original `bare_full_qwen35_lane_20260817` tmux died silently after its BEHAVIOR step ended at `08:16:47` (status=0). No WAH log was created and no Unity port check message remains, so the WAH step never ran; the session is gone. VirtualHome (342/342) and ALFRED unseen (821/821) had already been covered by the parallel lanes and are complete with summaries.

Restarted the two missing Qwen3.5 steps as standalone tmux sessions at `09:47`:

- `qwen35_wah_20260817`: `reactree_wah_bare_full_qwen35_official_100_20260817`, 100 task-level, Unity ports `9920..9924`, 5 workers, `--resume`. Already ~50/100 at 09:48, all `done`.
- `qwen35_alfred_seen_20260817`: `reactree_alfred_bare_full_qwen35_seen_20260817`, `valid_seen` 820, Xvfb `118..122`, 5 workers, `--resume`. Started.

Matrix status at 09:48 UTC:

- Completed (5/12): DELTA-Q3.5 600, BEHAVIOR-Q3.6 100, BEHAVIOR-Q3.5 100, VirtualHome-Q3.5 342, ALFRED unseen-Q3.5 821.
- Running (3/12): DELTA-Q3.6 ~420/600, WAH-Q3.5 ~50/100, ALFRED seen-Q3.5 ~9/820.
- Pending in Qwen3.6 lane after DELTA: VirtualHome 342, WAH 100, ALFRED seen 820, ALFRED unseen 821.

## Update 2026-08-18 03:23 UTC

User redeployed `18002/18003/18004` to `Qwen3.6-27B`; checked `/v1/models` before launch:

- `18002 -> Qwen3.6-27B`
- `18003 -> Qwen3.6-27B`
- `18004 -> Qwen3.6-27B`

Confirmed remaining work:

- Completed: 8/12 execution units.
- Remaining: 4/12 execution units, all `Qwen3.6-27B`:
  - `eai_virtualhome_bare_full_qwen36_20260817`, full 342.
  - `reactree_wah_bare_full_qwen36_official_100_20260817`, 100 task-level `:0` cases.
  - `reactree_alfred_bare_full_qwen36_seen_20260817`, valid_seen 820.
  - `reactree_alfred_bare_full_qwen36_unseen_20260817`, valid_unseen 821.

Wrote completed-results report:

- `/data/zmy/bare_full_completed_results_20260818.md`

Started the four remaining Qwen3.6 execution units in one tmux orchestrator:

- tmux: `qwen36_remaining_3ports_20260818`
- launch script: `/data/zmy/OurAgent-he1/benchmark/paper_comparison_records/run_qwen36_remaining_three_ports_20260818.sh`
- log root: `/data/zmy/OurAgent-he1/benchmark/paper_comparison_records/bare_full_20260817/logs_lanes/qwen36_three_ports`
- queue log: `/data/zmy/OurAgent-he1/benchmark/paper_comparison_records/bare_full_20260817/logs_lanes/qwen36_three_ports/queue_20260818.log`

Launch allocation:

- VirtualHome: `--workers 9 --ports 18002 18003 18004`, no simulator.
- WAH: `--workers 6 --ports 18002 18003 18004`, Unity ports `9910..9915`.
- ALFRED seen: `--workers 6 --ports 18002 18003 18004`, X displays `98 99 101 102 103 104`.
- ALFRED unseen: `--workers 6 --ports 18002 18003 18004`, X displays `108..113`.

Notes:

- Avoided stale `/tmp/.X100-lock`; no lock cleanup was performed.
- Initial manifests were written under all four remaining run roots; main processes were alive at `2026-08-18 03:23 UTC`.

## Update 2026-08-18 04:21 UTC

Current completion:

- Completed: 10/12 execution units.
- Remaining: 2/12 execution units:
  - `reactree_alfred_bare_full_qwen36_seen_20260817`, 254/820 at `04:21 UTC`, running.
  - `reactree_alfred_bare_full_qwen36_unseen_20260817`, 262/821 at `04:21 UTC`, running.

New completed Qwen3.6 runs:

- `eai_virtualhome_bare_full_qwen36_20260817`: completed 342/342.
  - `task_success_rate=37.7049%`
  - `total_goal=52.1452%`
  - `execution_success_rate=64.3%`
  - three-endpoint distribution: `18002=114`, `18003=114`, `18004=114`.
- `reactree_wah_bare_full_qwen36_official_100_20260817`: completed 100/100.
  - Initial fast pass had Unity port launch conflicts: `official_available_count=54/100`.
  - Re-evaluated existing raw outputs without extra LLM calls using `/data/zmy/OurAgent-he1/benchmark/paper_comparison_records/reevaluate_wah_official_qwen36_20260818.py`.
  - Re-eval ports: `9940..9945`.
  - Final official availability: `100/100`.
  - `official_task_success_rate=2.0%`, `official_goal_success_rate=2.0%`, `official_subgoal_success_rate=12.483333333333334%`.

Updated completed-results report:

- `/data/zmy/bare_full_completed_results_20260818.md`

## Update 2026-08-18 05:46 UTC

Bare full matrix is now complete: 12/12 execution units.

Final Qwen3.6 ALFRED summaries:

- `reactree_alfred_bare_full_qwen36_seen_20260817`: completed 820/820.
  - `official_available_count=819/820`
  - `official_task_success_rate=26.00732600732601%`
  - `execution_success_count=406`
  - endpoint distribution: `18002=274`, `18003=273`, `18004=273`.
- `reactree_alfred_bare_full_qwen36_unseen_20260817`: completed 821/821.
  - `official_available_count=820/821`
  - `official_task_success_rate=22.926829268292682%`
  - `execution_success_count=451`
  - endpoint distribution: `18002=274`, `18003=274`, `18004=273`.

Updated completed-results report:

- `/data/zmy/bare_full_completed_results_20260818.md`
