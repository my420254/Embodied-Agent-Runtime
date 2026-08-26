from execution import executor


def test_execution_backend_defaults_to_simulation(monkeypatch):
    monkeypatch.setattr(executor, "get_config", lambda *args, default=None: default)

    assert executor.execution_backend() == "simulation"


def test_execute_action_rejects_unknown_backend(monkeypatch):
    monkeypatch.setattr(executor, "execution_backend", lambda: "unknown")

    result = executor.execute_action({}, {"robot_location": "桌子"}, "", 0, 0)

    assert result.ok is False
    assert "未知执行后端" in result.error_feedback
