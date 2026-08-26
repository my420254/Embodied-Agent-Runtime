import pytest

from adapters.command_bus import InMemoryInterruptBus, configure_default_interrupt_bus
from graph import routes
from graph.task_management.node import route_after_manager, task_manager_node


@pytest.fixture(autouse=True)
def reset_interrupt_bus():
    configure_default_interrupt_bus(InMemoryInterruptBus())
    yield
    configure_default_interrupt_bus(InMemoryInterruptBus())


def _step(skill: str = "NavigateTo") -> dict:
    return {
        "step": 1,
        "execution": {
            "skill": skill,
            "parameters": {"target_location": "厨房"},
        },
    }


def _task(instruction: str, skill: str = "NavigateTo") -> dict:
    return {
        "instruction": instruction,
        "todo_list": [_step(skill)],
    }


def test_external_text_command_interrupts_and_preserves_task_stack():
    bus = InMemoryInterruptBus()
    configure_default_interrupt_bus(bus)
    bus.publish("先去拿杯子")
    task_stack = [_task("去切土豆")]

    result = task_manager_node(
        {
            "task_stack": task_stack,
            "env_state": {"robot_location": "厨房"},
            "execution_status": "running",
        }
    )

    assert result["execution_status"] == "interrupted"
    assert result["task_stack"] == task_stack
    assert result["interrupt_signal"]["kind"] == "new_task"
    assert result["interrupt_signal"]["text"] == "先去拿杯子"
    assert result["messages"][0].content == "先去拿杯子"


def test_injected_interrupt_todo_is_pushed_above_original_task():
    original = _task("去切土豆")
    new_step = _step("Pickup")

    result = task_manager_node(
        {
            "task_stack": [original],
            "env_state": {},
            "interrupt_signal": {
                "kind": "new_task",
                "text": "先拿杯子",
                "new_todo_list": [new_step],
            },
        }
    )

    assert result["execution_status"] == "running"
    assert [task["instruction"] for task in result["task_stack"]] == ["去切土豆", "先拿杯子"]
    assert result["task_stack"][-1]["todo_list"] == [new_step]
    assert result["interrupt_signal"] is None


def test_nested_interrupt_tasks_push_and_resume_multiple_levels():
    stack = [
        _task("任务1"),
        _task("任务2", "Pickup"),
        _task("任务3", "Open"),
    ]
    task4_step = _step("Put")

    pushed = task_manager_node(
        {
            "task_stack": stack,
            "env_state": {},
            "interrupt_signal": {
                "kind": "new_task",
                "text": "任务4",
                "new_todo_list": [task4_step],
            },
        }
    )

    assert pushed["execution_status"] == "running"
    assert [task["instruction"] for task in pushed["task_stack"]] == ["任务1", "任务2", "任务3", "任务4"]
    assert pushed["task_stack"][-1]["todo_list"] == [task4_step]

    task4_done_stack = [dict(task) for task in pushed["task_stack"]]
    task4_done_stack[-1] = {**task4_done_stack[-1], "todo_list": []}
    resumed_task3 = task_manager_node({"task_stack": task4_done_stack, "env_state": {}})

    assert resumed_task3["execution_status"] == "running"
    assert [task["instruction"] for task in resumed_task3["task_stack"]] == ["任务1", "任务2", "任务3"]

    task3_done_stack = [dict(task) for task in resumed_task3["task_stack"]]
    task3_done_stack[-1] = {**task3_done_stack[-1], "todo_list": []}
    resumed_task2 = task_manager_node({"task_stack": task3_done_stack, "env_state": {}})

    assert resumed_task2["execution_status"] == "running"
    assert [task["instruction"] for task in resumed_task2["task_stack"]] == ["任务1", "任务2"]


def test_cancel_current_pops_top_task_and_resumes_original():
    result = task_manager_node(
        {
            "task_stack": [_task("去切土豆"), _task("先拿杯子", "Pickup")],
            "env_state": {},
            "interrupt_signal": {"kind": "cancel_current", "text": "取消当前任务"},
        }
    )

    assert result["execution_status"] == "running"
    assert [task["instruction"] for task in result["task_stack"]] == ["去切土豆"]
    assert result["interrupt_signal"] is None


def test_cancel_all_clears_stack_without_success_feedback_route():
    result = task_manager_node(
        {
            "task_stack": [_task("去切土豆")],
            "env_state": {},
            "interrupt_signal": {"kind": "cancel_all", "text": "不要做了"},
        }
    )

    assert result["execution_status"] == "cancelled"
    assert result["task_stack"] == []
    assert route_after_manager(result) == routes.END
    assert routes.global_task_management_router(result) == routes.END


def test_pause_keeps_task_stack_and_stops_task_management_subgraph():
    result = task_manager_node(
        {
            "task_stack": [_task("去切土豆")],
            "env_state": {},
            "interrupt_signal": {"kind": "pause", "text": "暂停一下"},
        }
    )

    assert result["execution_status"] == "paused"
    assert [task["instruction"] for task in result["task_stack"]] == ["去切土豆"]
    assert route_after_manager(result) == routes.END


def test_global_entry_router_returns_to_task_management_for_suspended_interrupts():
    assert routes.global_entry_router(
        {
            "task_stack": [_task("去切土豆")],
            "interrupt_signal": {"kind": "resume", "text": "继续"},
        }
    ) == "Task_Management_Module"
