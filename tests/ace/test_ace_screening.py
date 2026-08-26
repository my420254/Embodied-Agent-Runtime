from ace import playbook
from ace import storage
from ace.screening import apply_screening_records, classify_comparison


def use_temp_playbooks(tmp_path, monkeypatch):
    playbook_dir = str(tmp_path / "playbooks")
    monkeypatch.setattr(playbook, "PLAYBOOK_DIR", playbook_dir)
    monkeypatch.setattr(storage, "PLAYBOOK_DIR", playbook_dir)


def test_classify_comparison_detects_helpful_and_harmful():
    assert classify_comparison(
        {
            "without_rule": {"success": False, "failed_step": 2},
            "with_rule": {"success": True, "failed_step": 5},
        }
    ) == "helpful"

    assert classify_comparison(
        {
            "without_rule": {"success": True},
            "with_rule": {"success": False, "failed_step": 1},
        }
    ) == "harmful"


def test_screening_promotes_candidate_after_helpful_train_evidence(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)
    assert playbook.write_candidate_experience("planning", "train_screening", "访问容器前先 Open。")
    rule_id = playbook.iter_all_section_rules("planning")[0]["id"]

    records = [
        {
            "rule_id": rule_id,
            "case_id": f"train-{idx}",
            "without_rule": {"success": False, "failed_step": 2},
            "with_rule": {"success": True, "failed_step": 5},
        }
        for idx in range(3)
    ]

    summary = apply_screening_records("planning", records)
    promoted = playbook.iter_section_rules("planning")[0]

    assert summary["processed"] == 3
    assert summary["helpful"] == 3
    assert summary["promoted"] == 1
    assert promoted["id"] == rule_id
    assert promoted["helpful_count"] == 3
    assert promoted["status"] == "promoted"


def test_screening_deprecates_candidate_on_counterexample(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)
    assert playbook.write_candidate_experience("planning", "train_screening", "总是先 Open。")
    rule_id = playbook.iter_all_section_rules("planning")[0]["id"]

    summary = apply_screening_records(
        "planning",
        [
            {
                "rule_id": rule_id,
                "case_id": "train-bad",
                "reason": "多余 Open 导致机械臂冲突。",
                "without_rule": {"success": True},
                "with_rule": {"success": False, "failed_step": 1},
            }
        ],
    )
    rule = playbook.iter_all_section_rules("planning")[0]

    assert summary["harmful"] == 1
    assert summary["deprecated"] == 1
    assert rule["status"] == "deprecated"
    assert rule["harmful_count"] == 1
    assert rule["counterexamples"][0]["case_id"] == "train-bad"
    assert playbook.iter_section_rules("planning") == []
