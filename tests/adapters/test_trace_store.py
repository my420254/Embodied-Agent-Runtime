from adapters.tracing import JsonlTraceRecorder


def test_jsonl_trace_recorder_records_and_reads_recent(tmp_path):
    trace_log = tmp_path / "traces.jsonl"
    recorder = JsonlTraceRecorder(trace_log)

    first_id = recorder.record({"trace_id": "trace-1", "task": "切牛肉"})
    second_id = recorder.record({"task": "泡茶"})

    assert first_id == "trace-1"
    assert second_id.startswith("trace-")

    recent = recorder.read_recent(limit=2)

    assert [record["task"] for record in recent] == ["切牛肉", "泡茶"]
    assert recent[0]["recorded_at"]
    assert recent[1]["trace_id"] == second_id
    assert recorder.find_by_trace_id("trace-1")["task"] == "切牛肉"
    assert recorder.find_by_trace_id(second_id)["task"] == "泡茶"
    assert recorder.find_by_trace_id("missing-trace") is None

