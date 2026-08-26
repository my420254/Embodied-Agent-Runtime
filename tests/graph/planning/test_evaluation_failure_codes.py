import inspect

from graph.planning.evaluation.models import EvaluationFailureCode
from graph.planning.evaluation.outcomes.reporter import EvaluationReporter
from graph.planning.evaluation.pipeline.simulation import _handler_failure_code


def test_evaluation_failure_codes_are_stable_metric_values():
    assert EvaluationFailureCode.EMPTY_PLAN.value == "empty_plan"
    assert EvaluationFailureCode.FORMAT_ERROR.value == "format_error"
    assert EvaluationFailureCode.SEMANTIC_AUDIT.value == "semantic_audit"
    assert EvaluationFailureCode.STATE_DIFF_AUDIT.value == "state_diff_audit"
    assert EvaluationFailureCode.SCENE_LOAD.value == "scene_load"
    assert EvaluationFailureCode.MODEL_INVOCATION.value == "model_invocation"
    assert EvaluationFailureCode.MODEL_OUTPUT.value == "model_output"


def test_legacy_skill_handler_failures_are_adapted_at_sandbox_boundary():
    assert (
        _handler_failure_code("前置位置依赖未满足", "Pickup")
        is EvaluationFailureCode.NAVIGATION_PRECONDITION
    )
    assert (
        _handler_failure_code("单臂约束违规", "Open")
        is EvaluationFailureCode.ARM_STATE
    )
    assert (
        _handler_failure_code("冗余操作", "Close")
        is EvaluationFailureCode.CONTAINER_STATE
    )
    assert (
        _handler_failure_code("冗余操作", "ToggleOn")
        is EvaluationFailureCode.DEVICE_STATE
    )


def test_unknown_handler_feedback_does_not_infer_a_metric_from_free_text():
    assert (
        _handler_failure_code("新的自由文本原因", "CustomSkill")
        is EvaluationFailureCode.UNKNOWN
    )


def test_reporter_accepts_one_failure_event_instead_of_parallel_fields():
    parameters = inspect.signature(EvaluationReporter.failure).parameters

    assert tuple(parameters) == ("self", "event")
