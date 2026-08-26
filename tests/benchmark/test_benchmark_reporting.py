import json

from benchmark import reporting


def test_summarize_cognitive_eval_artifacts_aggregates_across_datasets(tmp_path):
    artifact_a = {
        "dataset": "eai",
        "input_dataset": "virtualhome",
        "eval_type": "action_sequencing",
        "scene_id": 1,
        "model_label": "ouragent_eai_anchor",
        "runner_output_path": "/tmp/generated/eai_anchor_outputs.json",
        "variant": "baseline_todo,kg_task_graph",
        "variants": ["baseline_todo", "kg_task_graph"],
        "variant_count": 2,
        "anchor_variant": "baseline_todo",
        "baseline_output_source": "runner_outputs",
        "total_case_count": 2,
        "supported_case_count": 1,
        "unsupported_case_count": 1,
        "variant_supported_case_counts": {"baseline_todo": 1, "kg_task_graph": 1},
        "supported_task_counts": {"Open freezer": 1},
        "unsupported_task_counts": {"Unsupported idle task": 1},
        "summary": {
            "baseline_todo": {
                "variant": "baseline_todo",
                "case_count": 1,
                "planning_legal_rate": 0.0,
                "sandbox_pass_rate": 0.0,
                "task_success_rate": 0.0,
                "avg_latency_ms": 10.0,
                "orchestration_route_counts": {"baseline_todo": 1},
                "orchestration_route_metrics": {
                    "baseline_todo": {
                        "case_count": 1,
                        "planning_legal_rate": 0.0,
                        "sandbox_pass_rate": 0.0,
                        "task_success_rate": 0.0,
                        "avg_kg_query_count": 0.0,
                        "avg_scene_query_count": 0.0,
                        "avg_latency_ms": 10.0,
                    }
                },
                "failure_categories": {"unsupported": 1},
            },
            "kg_task_graph": {
                "variant": "kg_task_graph",
                "case_count": 1,
                "planning_legal_rate": 1.0,
                "sandbox_pass_rate": 1.0,
                "task_success_rate": 1.0,
                "avg_latency_ms": 30.0,
                "orchestration_route_counts": {"lightweight_scene": 1},
                "orchestration_route_metrics": {
                    "lightweight_scene": {
                        "case_count": 1,
                        "planning_legal_rate": 1.0,
                        "sandbox_pass_rate": 1.0,
                        "task_success_rate": 1.0,
                        "avg_kg_query_count": 0.0,
                        "avg_scene_query_count": 1.0,
                        "avg_latency_ms": 30.0,
                    }
                },
                "failure_categories": {},
            },
        },
        "case_comparisons": {
            "kg_task_graph": {
                "metric_order": ["task_success", "sandbox_passed", "planning_legal"],
                "compared_case_count": 1,
                "improved_case_count": 1,
                "regressed_case_count": 0,
                "tied_case_count": 0,
                "missing_anchor_case_count": 0,
                "missing_variant_case_count": 0,
            }
        },
        "variant_comparisons": {
            "kg_task_graph": {
                "planning_legal_rate_delta_vs_anchor": 1.0,
                "sandbox_pass_rate_delta_vs_anchor": 1.0,
                "task_success_rate_delta_vs_anchor": 1.0,
                "avg_latency_ms_delta_vs_anchor": 20.0,
                "route_case_share_deltas_vs_anchor": {
                    "baseline_todo": -1.0,
                    "lightweight_scene": 1.0,
                },
            }
        },
        "variant_unsupported_cases": {
            "baseline_todo": [
                {
                    "case_id": "eai_a_missing",
                    "task_name": "Unsupported idle task",
                    "reason": "unsupported cognitive eval conversion",
                }
            ],
            "kg_task_graph": [],
        },
        "task_comparisons": {
            "kg_task_graph": {
                "Open freezer": {
                    "compared_case_count": 1,
                    "improved_case_count": 1,
                    "regressed_case_count": 0,
                    "tied_case_count": 0,
                    "missing_anchor_case_count": 0,
                    "missing_variant_case_count": 0,
                }
            }
        },
    }
    artifact_b = {
        "dataset": "delta",
        "input_dataset": "virtualhome",
        "eval_type": "action_sequencing",
        "scene_id": 1,
        "model_label": "ouragent_delta_trial",
        "runner_output_path": "/tmp/generated/delta_trial_outputs.json",
        "variant": "baseline_todo,kg_task_graph",
        "variants": ["baseline_todo", "kg_task_graph"],
        "variant_count": 2,
        "anchor_variant": "baseline_todo",
        "baseline_output_source": "/tmp/baseline_delta_outputs.json",
        "total_case_count": 3,
        "supported_case_count": 2,
        "unsupported_case_count": 1,
        "variant_supported_case_counts": {"baseline_todo": 2, "kg_task_graph": 2},
        "supported_task_counts": {"Wash clothes": 2},
        "unsupported_task_counts": {"Unsupported idle task": 1},
        "summary": {
            "baseline_todo": {
                "variant": "baseline_todo",
                "case_count": 2,
                "planning_legal_rate": 0.5,
                "sandbox_pass_rate": 0.5,
                "task_success_rate": 0.5,
                "avg_latency_ms": 20.0,
                "orchestration_route_counts": {"baseline_todo": 2},
                "orchestration_route_metrics": {
                    "baseline_todo": {
                        "case_count": 2,
                        "planning_legal_rate": 0.5,
                        "sandbox_pass_rate": 0.5,
                        "task_success_rate": 0.5,
                        "avg_kg_query_count": 0.0,
                        "avg_scene_query_count": 0.0,
                        "avg_latency_ms": 20.0,
                    }
                },
                "failure_categories": {"device_state": 1},
            },
            "kg_task_graph": {
                "variant": "kg_task_graph",
                "case_count": 2,
                "planning_legal_rate": 1.0,
                "sandbox_pass_rate": 1.0,
                "task_success_rate": 0.5,
                "avg_latency_ms": 50.0,
                "orchestration_route_counts": {"kg_task_graph": 2},
                "orchestration_route_metrics": {
                    "kg_task_graph": {
                        "case_count": 2,
                        "planning_legal_rate": 1.0,
                        "sandbox_pass_rate": 1.0,
                        "task_success_rate": 0.5,
                        "avg_kg_query_count": 1.0,
                        "avg_scene_query_count": 4.0,
                        "avg_latency_ms": 50.0,
                    }
                },
                "failure_categories": {"execution_failure": 1},
            },
        },
        "case_comparisons": {
            "kg_task_graph": {
                "metric_order": ["task_success", "sandbox_passed", "planning_legal"],
                "compared_case_count": 2,
                "improved_case_count": 0,
                "regressed_case_count": 1,
                "tied_case_count": 1,
                "missing_anchor_case_count": 0,
                "missing_variant_case_count": 0,
            }
        },
        "variant_comparisons": {
            "kg_task_graph": {
                "planning_legal_rate_delta_vs_anchor": 0.5,
                "sandbox_pass_rate_delta_vs_anchor": 0.5,
                "task_success_rate_delta_vs_anchor": 0.0,
                "avg_latency_ms_delta_vs_anchor": 30.0,
                "route_case_share_deltas_vs_anchor": {
                    "baseline_todo": -1.0,
                    "kg_task_graph": 1.0,
                },
            }
        },
        "variant_unsupported_cases": {
            "baseline_todo": [
                {
                    "case_id": "delta_b_parse",
                    "task_name": "Turn on light",
                    "reason": "baseline_todo parse failed: unsupported EAI action sequence action: PLUGIN",
                }
            ],
            "kg_task_graph": [],
        },
        "task_comparisons": {
            "kg_task_graph": {
                "Wash clothes": {
                    "compared_case_count": 2,
                    "improved_case_count": 0,
                    "regressed_case_count": 1,
                    "tied_case_count": 1,
                    "missing_anchor_case_count": 0,
                    "missing_variant_case_count": 0,
                }
            }
        },
    }

    path_a = tmp_path / "artifact_a.json"
    path_b = tmp_path / "artifact_b.json"
    path_a.write_text(json.dumps(artifact_a), encoding="utf-8")
    path_b.write_text(json.dumps(artifact_b), encoding="utf-8")

    payload = reporting.summarize_cognitive_eval_artifact_paths([path_a, path_b])

    assert payload["artifact_count"] == 2
    assert payload["total_case_count"] == 5
    assert payload["supported_case_count"] == 3
    assert payload["unsupported_case_count"] == 2
    assert payload["support_coverage_rate"] == 0.6
    assert payload["variant_supported_case_counts"] == {"baseline_todo": 3, "kg_task_graph": 3}
    assert payload["variant_support_coverage_rates"] == {"baseline_todo": 0.6, "kg_task_graph": 0.6}
    assert payload["supported_task_counts"] == {"Open freezer": 1, "Wash clothes": 2}
    assert payload["unsupported_task_counts"] == {"Unsupported idle task": 2}
    assert payload["context_counts"] == {
        "anchor_variant": {"baseline_todo": 2},
        "baseline_output_source": {
            "/tmp/baseline_delta_outputs.json": 1,
            "runner_outputs": 1,
        },
        "eval_type": {"action_sequencing": 2},
        "input_dataset": {"virtualhome": 2},
        "model_label": {"ouragent_delta_trial": 1, "ouragent_eai_anchor": 1},
        "scene_id": {"1": 2},
    }
    assert sorted(payload["context_groups"]) == ["anchor_variant", "baseline_output_source", "model_label"]
    assert payload["context_groups"]["baseline_output_source"]["runner_outputs"]["artifact_count"] == 1
    assert payload["context_groups"]["baseline_output_source"]["runner_outputs"]["datasets"] == ["eai"]
    assert (
        payload["context_groups"]["baseline_output_source"]["runner_outputs"]["variant_comparison_summary"][
            "kg_task_graph"
        ]["metric_deltas"]["task_success_rate_delta_vs_anchor"]
        == 1.0
    )
    assert payload["context_groups"]["baseline_output_source"]["/tmp/baseline_delta_outputs.json"][
        "supported_case_count"
    ] == 2
    assert (
        payload["context_groups"]["baseline_output_source"]["/tmp/baseline_delta_outputs.json"][
            "variant_comparison_summary"
        ]["kg_task_graph"]["metric_deltas"]["task_success_rate_delta_vs_anchor"]
        == 0.0
    )
    assert payload["context_groups"]["anchor_variant"]["baseline_todo"]["artifact_count"] == 2
    assert payload["context_groups"]["anchor_variant"]["baseline_todo"]["total_case_count"] == 5
    assert payload["context_groups"]["anchor_variant"]["baseline_todo"]["variant_comparison_summary"][
        "kg_task_graph"
    ]["metric_deltas"]["task_success_rate_delta_vs_anchor"] == 1 / 3
    assert payload["context_groups"]["model_label"]["ouragent_eai_anchor"]["artifact_count"] == 1
    assert payload["context_groups"]["model_label"]["ouragent_eai_anchor"]["datasets"] == ["eai"]
    assert payload["context_groups"]["model_label"]["ouragent_delta_trial"]["artifact_count"] == 1
    assert payload["context_groups"]["model_label"]["ouragent_delta_trial"]["datasets"] == ["delta"]
    assert payload["artifact_index"] == [
        {
            "source_path": str(path_b),
            "dataset": "delta",
            "input_dataset": "virtualhome",
            "eval_type": "action_sequencing",
            "scene_id": 1,
            "model_label": "ouragent_delta_trial",
            "runner_output_path": "/tmp/generated/delta_trial_outputs.json",
            "variant": "baseline_todo,kg_task_graph",
            "variants": ["baseline_todo", "kg_task_graph"],
            "variant_count": 2,
            "anchor_variant": "baseline_todo",
            "baseline_output_source": "/tmp/baseline_delta_outputs.json",
            "total_case_count": 3,
            "supported_case_count": 2,
            "unsupported_case_count": 1,
            "support_coverage_rate": 2 / 3,
        },
        {
            "source_path": str(path_a),
            "dataset": "eai",
            "input_dataset": "virtualhome",
            "eval_type": "action_sequencing",
            "scene_id": 1,
            "model_label": "ouragent_eai_anchor",
            "runner_output_path": "/tmp/generated/eai_anchor_outputs.json",
            "variant": "baseline_todo,kg_task_graph",
            "variants": ["baseline_todo", "kg_task_graph"],
            "variant_count": 2,
            "anchor_variant": "baseline_todo",
            "baseline_output_source": "runner_outputs",
            "total_case_count": 2,
            "supported_case_count": 1,
            "unsupported_case_count": 1,
            "support_coverage_rate": 0.5,
        },
    ]
    assert payload["unsupported_reason_counts"] == {
        "baseline_todo": {
            "baseline_todo parse failed: unsupported EAI action sequence action: PLUGIN": 1,
            "unsupported cognitive eval conversion": 1,
        },
        "kg_task_graph": {},
    }
    assert payload["summary"]["baseline_todo"]["case_count"] == 3
    assert payload["summary"]["baseline_todo"]["task_success_rate"] == 1 / 3
    assert payload["summary"]["baseline_todo"]["avg_latency_ms"] == 50 / 3
    assert payload["summary"]["baseline_todo"]["failure_categories"] == {"device_state": 1, "unsupported": 1}
    assert payload["summary"]["baseline_todo"]["orchestration_route_counts"] == {"baseline_todo": 3}
    assert payload["summary"]["baseline_todo"]["orchestration_route_metrics"]["baseline_todo"] == {
        "case_count": 3,
        "avg_kg_query_count": 0.0,
        "avg_latency_ms": 50 / 3,
        "avg_scene_query_count": 0.0,
        "planning_legal_rate": 1 / 3,
        "sandbox_pass_rate": 1 / 3,
        "task_success_rate": 1 / 3,
    }
    assert payload["summary"]["kg_task_graph"]["case_count"] == 3
    assert payload["summary"]["kg_task_graph"]["task_success_rate"] == 2 / 3
    assert payload["summary"]["kg_task_graph"]["avg_latency_ms"] == 130 / 3
    assert payload["summary"]["kg_task_graph"]["orchestration_route_counts"] == {
        "kg_task_graph": 2,
        "lightweight_scene": 1,
    }
    assert payload["summary"]["kg_task_graph"]["orchestration_route_metrics"] == {
        "kg_task_graph": {
            "case_count": 2,
            "avg_kg_query_count": 1.0,
            "avg_latency_ms": 50.0,
            "avg_scene_query_count": 4.0,
            "planning_legal_rate": 1.0,
            "sandbox_pass_rate": 1.0,
            "task_success_rate": 0.5,
        },
        "lightweight_scene": {
            "case_count": 1,
            "avg_kg_query_count": 0.0,
            "avg_latency_ms": 30.0,
            "avg_scene_query_count": 1.0,
            "planning_legal_rate": 1.0,
            "sandbox_pass_rate": 1.0,
            "task_success_rate": 1.0,
        },
    }
    assert payload["route_hotspots"]["baseline_todo"] == {
        "top_routes_by_case_count": [
            {
                "route": "baseline_todo",
                "case_count": 3,
                "task_success_rate": 1 / 3,
                "avg_latency_ms": 50 / 3,
                "avg_kg_query_count": 0.0,
                "avg_scene_query_count": 0.0,
            }
        ],
        "lowest_success_routes": [
            {
                "route": "baseline_todo",
                "case_count": 3,
                "task_success_rate": 1 / 3,
                "avg_latency_ms": 50 / 3,
                "avg_kg_query_count": 0.0,
                "avg_scene_query_count": 0.0,
            }
        ],
        "highest_latency_routes": [
            {
                "route": "baseline_todo",
                "case_count": 3,
                "task_success_rate": 1 / 3,
                "avg_latency_ms": 50 / 3,
                "avg_kg_query_count": 0.0,
                "avg_scene_query_count": 0.0,
            }
        ],
    }
    assert payload["route_hotspots"]["kg_task_graph"] == {
        "top_routes_by_case_count": [
            {
                "route": "kg_task_graph",
                "case_count": 2,
                "task_success_rate": 0.5,
                "avg_latency_ms": 50.0,
                "avg_kg_query_count": 1.0,
                "avg_scene_query_count": 4.0,
            },
            {
                "route": "lightweight_scene",
                "case_count": 1,
                "task_success_rate": 1.0,
                "avg_latency_ms": 30.0,
                "avg_kg_query_count": 0.0,
                "avg_scene_query_count": 1.0,
            },
        ],
        "lowest_success_routes": [
            {
                "route": "kg_task_graph",
                "case_count": 2,
                "task_success_rate": 0.5,
                "avg_latency_ms": 50.0,
                "avg_kg_query_count": 1.0,
                "avg_scene_query_count": 4.0,
            },
            {
                "route": "lightweight_scene",
                "case_count": 1,
                "task_success_rate": 1.0,
                "avg_latency_ms": 30.0,
                "avg_kg_query_count": 0.0,
                "avg_scene_query_count": 1.0,
            },
        ],
        "highest_latency_routes": [
            {
                "route": "kg_task_graph",
                "case_count": 2,
                "task_success_rate": 0.5,
                "avg_latency_ms": 50.0,
                "avg_kg_query_count": 1.0,
                "avg_scene_query_count": 4.0,
            },
            {
                "route": "lightweight_scene",
                "case_count": 1,
                "task_success_rate": 1.0,
                "avg_latency_ms": 30.0,
                "avg_kg_query_count": 0.0,
                "avg_scene_query_count": 1.0,
            },
        ],
    }
    assert payload["variant_comparison_summary"]["kg_task_graph"] == {
        "artifact_count": 2,
        "compared_case_count": 3,
        "anchor_variant_counts": {"baseline_todo": 2},
        "metric_fields": [
            "avg_latency_ms_delta_vs_anchor",
            "planning_legal_rate_delta_vs_anchor",
            "sandbox_pass_rate_delta_vs_anchor",
            "task_success_rate_delta_vs_anchor",
        ],
        "metric_deltas": {
            "avg_latency_ms_delta_vs_anchor": 80 / 3,
            "planning_legal_rate_delta_vs_anchor": 2 / 3,
            "sandbox_pass_rate_delta_vs_anchor": 2 / 3,
            "task_success_rate_delta_vs_anchor": 1 / 3,
        },
        "route_names": ["baseline_todo", "kg_task_graph", "lightweight_scene"],
        "route_case_share_deltas": {
            "baseline_todo": -1.0,
            "kg_task_graph": 2 / 3,
            "lightweight_scene": 1 / 3,
        },
        "per_anchor_variant": {
            "baseline_todo": {
                "artifact_count": 2,
                "compared_case_count": 3,
                "metric_fields": [
                    "avg_latency_ms_delta_vs_anchor",
                    "planning_legal_rate_delta_vs_anchor",
                    "sandbox_pass_rate_delta_vs_anchor",
                    "task_success_rate_delta_vs_anchor",
                ],
                "metric_deltas": {
                    "avg_latency_ms_delta_vs_anchor": 80 / 3,
                    "planning_legal_rate_delta_vs_anchor": 2 / 3,
                    "sandbox_pass_rate_delta_vs_anchor": 2 / 3,
                    "task_success_rate_delta_vs_anchor": 1 / 3,
                },
                "route_names": ["baseline_todo", "kg_task_graph", "lightweight_scene"],
                "route_case_share_deltas": {
                    "baseline_todo": -1.0,
                    "kg_task_graph": 2 / 3,
                    "lightweight_scene": 1 / 3,
                },
            }
        },
    }
    assert payload["case_comparison_counts"]["kg_task_graph"] == {
        "metric_order": ["task_success", "sandbox_passed", "planning_legal"],
        "compared_case_count": 3,
        "improved_case_count": 1,
        "regressed_case_count": 1,
        "tied_case_count": 1,
        "missing_anchor_case_count": 0,
        "missing_variant_case_count": 0,
    }
    assert payload["task_comparisons"]["kg_task_graph"] == {
        "Open freezer": {
            "compared_case_count": 1,
            "improved_case_count": 1,
            "regressed_case_count": 0,
            "tied_case_count": 0,
            "missing_anchor_case_count": 0,
            "missing_variant_case_count": 0,
        },
        "Wash clothes": {
            "compared_case_count": 2,
            "improved_case_count": 0,
            "regressed_case_count": 1,
            "tied_case_count": 1,
            "missing_anchor_case_count": 0,
            "missing_variant_case_count": 0,
        },
    }
    assert payload["comparison_hotspots"]["kg_task_graph"] == {
        "top_improved_tasks": [
            {"task_name": "Open freezer", "improved_case_count": 1, "compared_case_count": 1}
        ],
        "top_regressed_tasks": [
            {"task_name": "Wash clothes", "regressed_case_count": 1, "compared_case_count": 2}
        ],
        "top_missing_variant_tasks": [],
    }
    assert payload["datasets"]["delta"]["artifact_count"] == 1
    assert payload["datasets"]["delta"]["context_counts"] == {
        "anchor_variant": {"baseline_todo": 1},
        "baseline_output_source": {"/tmp/baseline_delta_outputs.json": 1},
        "eval_type": {"action_sequencing": 1},
        "input_dataset": {"virtualhome": 1},
        "model_label": {"ouragent_delta_trial": 1},
        "scene_id": {"1": 1},
    }
    assert payload["datasets"]["delta"]["artifact_index"] == [
        {
            "source_path": str(path_b),
            "dataset": "delta",
            "input_dataset": "virtualhome",
            "eval_type": "action_sequencing",
            "scene_id": 1,
            "model_label": "ouragent_delta_trial",
            "runner_output_path": "/tmp/generated/delta_trial_outputs.json",
            "variant": "baseline_todo,kg_task_graph",
            "variants": ["baseline_todo", "kg_task_graph"],
            "variant_count": 2,
            "anchor_variant": "baseline_todo",
            "baseline_output_source": "/tmp/baseline_delta_outputs.json",
            "total_case_count": 3,
            "supported_case_count": 2,
            "unsupported_case_count": 1,
            "support_coverage_rate": 2 / 3,
        }
    ]
    assert payload["datasets"]["delta"]["unsupported_reason_counts"]["baseline_todo"] == {
        "baseline_todo parse failed: unsupported EAI action sequence action: PLUGIN": 1
    }
    assert payload["datasets"]["delta"]["variant_comparison_summary"]["kg_task_graph"]["metric_deltas"] == {
        "avg_latency_ms_delta_vs_anchor": 30.0,
        "planning_legal_rate_delta_vs_anchor": 0.5,
        "sandbox_pass_rate_delta_vs_anchor": 0.5,
        "task_success_rate_delta_vs_anchor": 0.0,
    }
    assert payload["datasets"]["delta"]["variant_comparison_summary"]["kg_task_graph"]["route_case_share_deltas"] == {
        "baseline_todo": -1.0,
        "kg_task_graph": 1.0,
    }
    assert payload["datasets"]["delta"]["route_hotspots"]["kg_task_graph"] == {
        "top_routes_by_case_count": [
            {
                "route": "kg_task_graph",
                "case_count": 2,
                "task_success_rate": 0.5,
                "avg_latency_ms": 50.0,
                "avg_kg_query_count": 1.0,
                "avg_scene_query_count": 4.0,
            }
        ],
        "lowest_success_routes": [
            {
                "route": "kg_task_graph",
                "case_count": 2,
                "task_success_rate": 0.5,
                "avg_latency_ms": 50.0,
                "avg_kg_query_count": 1.0,
                "avg_scene_query_count": 4.0,
            }
        ],
        "highest_latency_routes": [
            {
                "route": "kg_task_graph",
                "case_count": 2,
                "task_success_rate": 0.5,
                "avg_latency_ms": 50.0,
                "avg_kg_query_count": 1.0,
                "avg_scene_query_count": 4.0,
            }
        ],
    }
    assert payload["datasets"]["delta"]["comparison_hotspots"]["kg_task_graph"]["top_regressed_tasks"] == [
        {"task_name": "Wash clothes", "regressed_case_count": 1, "compared_case_count": 2}
    ]
    assert payload["datasets"]["delta"]["supported_case_count"] == 2
    assert payload["datasets"]["eai"]["artifact_count"] == 1
    assert payload["datasets"]["eai"]["context_counts"] == {
        "anchor_variant": {"baseline_todo": 1},
        "baseline_output_source": {"runner_outputs": 1},
        "eval_type": {"action_sequencing": 1},
        "input_dataset": {"virtualhome": 1},
        "model_label": {"ouragent_eai_anchor": 1},
        "scene_id": {"1": 1},
    }
    assert payload["datasets"]["eai"]["artifact_index"] == [
        {
            "source_path": str(path_a),
            "dataset": "eai",
            "input_dataset": "virtualhome",
            "eval_type": "action_sequencing",
            "scene_id": 1,
            "model_label": "ouragent_eai_anchor",
            "runner_output_path": "/tmp/generated/eai_anchor_outputs.json",
            "variant": "baseline_todo,kg_task_graph",
            "variants": ["baseline_todo", "kg_task_graph"],
            "variant_count": 2,
            "anchor_variant": "baseline_todo",
            "baseline_output_source": "runner_outputs",
            "total_case_count": 2,
            "supported_case_count": 1,
            "unsupported_case_count": 1,
            "support_coverage_rate": 0.5,
        }
    ]
    assert payload["datasets"]["eai"]["unsupported_reason_counts"]["baseline_todo"] == {
        "unsupported cognitive eval conversion": 1
    }
    assert payload["datasets"]["eai"]["variant_comparison_summary"]["kg_task_graph"]["metric_deltas"] == {
        "avg_latency_ms_delta_vs_anchor": 20.0,
        "planning_legal_rate_delta_vs_anchor": 1.0,
        "sandbox_pass_rate_delta_vs_anchor": 1.0,
        "task_success_rate_delta_vs_anchor": 1.0,
    }
    assert payload["datasets"]["eai"]["variant_comparison_summary"]["kg_task_graph"]["route_case_share_deltas"] == {
        "baseline_todo": -1.0,
        "lightweight_scene": 1.0,
    }
    assert payload["datasets"]["eai"]["route_hotspots"]["kg_task_graph"] == {
        "top_routes_by_case_count": [
            {
                "route": "lightweight_scene",
                "case_count": 1,
                "task_success_rate": 1.0,
                "avg_latency_ms": 30.0,
                "avg_kg_query_count": 0.0,
                "avg_scene_query_count": 1.0,
            }
        ],
        "lowest_success_routes": [
            {
                "route": "lightweight_scene",
                "case_count": 1,
                "task_success_rate": 1.0,
                "avg_latency_ms": 30.0,
                "avg_kg_query_count": 0.0,
                "avg_scene_query_count": 1.0,
            }
        ],
        "highest_latency_routes": [
            {
                "route": "lightweight_scene",
                "case_count": 1,
                "task_success_rate": 1.0,
                "avg_latency_ms": 30.0,
                "avg_kg_query_count": 0.0,
                "avg_scene_query_count": 1.0,
            }
        ],
    }
    assert payload["datasets"]["eai"]["comparison_hotspots"]["kg_task_graph"]["top_improved_tasks"] == [
        {"task_name": "Open freezer", "improved_case_count": 1, "compared_case_count": 1}
    ]
    assert payload["datasets"]["eai"]["unsupported_case_count"] == 1
