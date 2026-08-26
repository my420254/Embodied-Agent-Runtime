import json
import threading
import time
from pathlib import Path

from benchmark import experiment_utils


def test_launch_case_workers_serializes_each_unit_and_parallelizes_units(tmp_path, monkeypatch):
    lock = threading.Lock()
    active_by_unit = {0: 0, 1: 0}
    max_active_by_unit = {0: 0, 1: 0}
    total_active = 0
    max_total_active = 0
    observed_bases: dict[int, set[str]] = {0: set(), 1: set()}

    def fake_run_subprocess(command, *, env, log_path, append, timeout_s):
        nonlocal total_active, max_total_active
        worker_input = Path(command[-1])
        payload = json.loads(worker_input.read_text(encoding="utf-8"))
        unit_index = int(payload["unit_index"])
        case_id = str(payload["case"]["case_id"])
        with lock:
            active_by_unit[unit_index] += 1
            total_active += 1
            max_active_by_unit[unit_index] = max(max_active_by_unit[unit_index], active_by_unit[unit_index])
            max_total_active = max(max_total_active, total_active)
            observed_bases[unit_index].add(env["LANGGRAPH_JSZN_PLANNING_API_BASE"])
        time.sleep(0.02)
        experiment_utils.write_json(
            experiment_utils.case_root(tmp_path, case_id) / "worker_result.json",
            {"case_id": case_id, "status": "done", "row": {"case_id": case_id, "prediction": {}}},
        )
        with lock:
            active_by_unit[unit_index] -= 1
            total_active -= 1
        return 0

    monkeypatch.setattr(experiment_utils, "run_subprocess", fake_run_subprocess)
    cases = [
        {"case_id": f"case-{index}", "dataset": "test", "input": {}, "metadata": {}, "source_path": ""}
        for index in range(6)
    ]
    slots = [
        {"index": 0, "port": 18002, "api_base": "http://host:18002/v1", "api_key": "key", "api_model": "model"},
        {"index": 1, "port": 18003, "api_base": "http://host:18003/v1", "api_key": "key", "api_model": "model"},
    ]

    results = experiment_utils.launch_case_workers(
        benchmark_name="test",
        run_root=tmp_path,
        worker_module="fake.worker",
        cases=cases,
        endpoint_slots=slots,
        unit_count=2,
        group_key=None,
        worker_options={},
        trace=True,
        trace_llm_io=True,
        dry_run=False,
    )

    assert len(results) == 6
    assert max_active_by_unit == {0: 1, 1: 1}
    assert max_total_active == 2
    assert observed_bases == {
        0: {"http://host:18002/v1"},
        1: {"http://host:18003/v1"},
    }
