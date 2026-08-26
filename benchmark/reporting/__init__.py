from benchmark.reporting.writer import write_case_report
from benchmark.reporting.persist import persist_case_bundle
from benchmark.reporting.cognitive_eval import summarize_cognitive_eval_artifact_paths


def summarize_framework_runs(*args, **kwargs):
    from benchmark.reporting.framework_accuracy import summarize_framework_runs as _summarize_framework_runs

    return _summarize_framework_runs(*args, **kwargs)


def summarize_framework_run(*args, **kwargs):
    from benchmark.reporting.framework_accuracy import summarize_framework_run as _summarize_framework_run

    return _summarize_framework_run(*args, **kwargs)

__all__ = [
    "write_case_report",
    "persist_case_bundle",
    "summarize_cognitive_eval_artifact_paths",
    "summarize_framework_runs",
    "summarize_framework_run",
]
