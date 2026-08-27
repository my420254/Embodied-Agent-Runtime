from adapters.tracing import JsonlTraceRecorder, TraceHarness


def test_trace_harness_records_replays_and_summarizes(tmp_path):
    recorder = JsonlTraceRecorder(tmp_path / "trace.jsonl")
    harness = TraceHarness(recorder, trace_id="trace-demo", task_id="task-demo")

    harness.record_node("understanding", input_summary="把土豆切片", output_summary="intent=Slice")
    harness.record_tool("Pickup", arguments={"target_item": "土豆_1"}, observation="ok", latency_ms=12.5)
    harness.record_failure("execution", "刀具不可达", node="Slice")

    replay = harness.replay()
    summary = TraceHarness.summarize(replay)

    assert [event["event_type"] for event in replay] == ["node", "tool", "failure"]
    assert summary["ok"] is False
    assert summary["step_count"] == 3
    assert summary["failure_layers"] == ["execution"]
    assert summary["total_latency_ms"] == 12.5


def test_trace_harness_compare_reports_delta(tmp_path):
    recorder = JsonlTraceRecorder(tmp_path / "trace.jsonl")
    left = TraceHarness(recorder, trace_id="trace-left")
    right = TraceHarness(recorder, trace_id="trace-right")

    left.record_node("planning", latency_ms=10)
    right.record_node("planning", latency_ms=10)
    right.record_node("reflection", latency_ms=5)

    comparison = TraceHarness.compare(left.replay(), right.replay())

    assert comparison["delta_step_count"] == 1
    assert comparison["delta_latency_ms"] == 5
