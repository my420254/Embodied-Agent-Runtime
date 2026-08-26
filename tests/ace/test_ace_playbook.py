from ace import playbook
from ace import storage


def use_temp_playbooks(tmp_path, monkeypatch):
    playbook_dir = str(tmp_path / "playbooks")
    monkeypatch.setattr(playbook, "PLAYBOOK_DIR", playbook_dir)
    monkeypatch.setattr(storage, "PLAYBOOK_DIR", playbook_dir)


def test_write_experience_deduplicates_similar_rules(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)

    first = playbook.write_experience(
        section="planning",
        source="test",
        rule="Pickup 前必须 NavigateTo 到目标物品 direct_parent。",
    )
    second = playbook.write_experience(
        section="planning",
        source="test",
        rule="Pickup 前必须 NavigateTo 到目标物品 direct_parent。 ",
    )

    data = playbook.load_playbook()
    assert first is True
    assert second is False
    assert len(data["rules"]) == 1
    assert data["rules"][0]["id"].startswith("planning-")
    assert data["rules"][0]["helpful_count"] == 0
    assert data["rules"][0]["harmful_count"] == 0
    assert "navigation" in data["rules"][0]["tags"]
    assert (tmp_path / "playbooks" / "planning.json").exists()


def test_write_experience_deduplicates_within_section_only(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)

    assert playbook.write_experience("planning", "test", "同一条经验。") is True
    assert playbook.write_experience("execution", "test", "同一条经验。") is True

    data = playbook.load_playbook()
    assert {rule["section"] for rule in data["rules"]} == {"planning", "execution"}


def test_write_experience_respects_feature_flags(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)

    assert playbook.write_experience(
        "planning",
        "test",
        "这条规则不应写入。",
        feature_flags={"playbook_write": False},
    ) is False
    assert playbook.load_playbook()["rules"] == []


def test_save_playbook_writes_readable_json(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)

    playbook.save_playbook({"rules": [{"section": "planning", "rule": "规则"}]})

    rule = playbook.load_playbook()["rules"][0]
    assert rule["rule"] == "规则"
    assert rule["id"].startswith("planning-")


def test_curate_evaluator_finding_uses_plain_prompt_callback(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)

    def invoke_curator(prompt: str) -> dict:
        assert "物理拦截" in prompt
        return {"is_duplicate": False, "generalized_rule": "规划前必须检查动作前置条件。"}

    written = playbook.curate_evaluator_finding(
        raw_issue="第 1 步物理拦截",
        raw_fix="先导航至目标位置",
        intent="测试任务",
        step_detail="{}",
        invoke_curator=invoke_curator,
    )

    rules = playbook.load_playbook()["rules"]
    assert written is True
    assert rules[0]["section"] == "planning"
    assert rules[0]["rule"] == "规划前必须检查动作前置条件。"

def test_load_relevant_rules_prefers_tags_and_feedback(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)
    playbook.save_playbook(
        {
            "rules": [
                {
                    "section": "planning",
                    "id": "planning-nav",
                    "source": "test",
                    "tags": ["navigation"],
                    "helpful_count": 2,
                    "harmful_count": 0,
                    "rule": "交互前必须先 NavigateTo 到目标对象所在位置。",
                },
                {
                    "section": "planning",
                    "id": "planning-clean",
                    "source": "test",
                    "tags": ["food_cleaning"],
                    "helpful_count": 0,
                    "harmful_count": 0,
                    "rule": "切割食材前必须先 Clean。",
                },
            ]
        }
    )

    rules = playbook.load_relevant_rules(
        "planning",
        intent="拿起桌上的苹果",
        tags=["navigation"],
        limit=1,
    )

    assert [rule["id"] for rule in rules] == ["planning-nav"]


def test_record_rule_feedback_updates_counts(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)
    playbook.save_playbook(
        {
            "rules": [
                {
                    "section": "planning",
                    "id": "planning-nav",
                    "source": "test",
                    "rule": "交互前必须先导航。",
                }
            ]
        }
    )

    assert playbook.record_rule_feedback("planning", ["planning-nav"], outcome="helpful") == 1
    assert playbook.record_rule_feedback("planning", ["planning-nav"], outcome="harmful") == 1

    rule = playbook.iter_section_rules("planning")[0]
    assert rule["helpful_count"] == 1
    assert rule["harmful_count"] == 1


def test_candidate_rules_are_hidden_until_promoted(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)

    assert playbook.write_candidate_experience(
        "planning",
        "train_screening",
        "候选规则：访问容器前先 Open。",
        source_split="train",
        source_case_id="train-case-1",
    ) is True

    assert playbook.iter_section_rules("planning") == []

    candidate = playbook.iter_all_section_rules("planning")[0]
    assert candidate["status"] == "candidate"
    assert candidate["source_split"] == "train"
    assert candidate["source_case_id"] == "train-case-1"

    assert playbook.promote_rule("planning", candidate["id"]) is True
    promoted = playbook.iter_section_rules("planning")[0]
    assert promoted["id"] == candidate["id"]
    assert promoted["status"] == "promoted"


def test_counterexample_records_harmful_evidence_and_can_deprecate(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)
    assert playbook.write_candidate_experience("planning", "train_screening", "总是先 Open。") is True
    candidate = playbook.iter_all_section_rules("planning")[0]

    assert playbook.record_rule_counterexample(
        "planning",
        candidate["id"],
        {
            "case_id": "train-case-2",
            "failure_type": "mechanical_conflict",
            "reason": "机器人手持物体时 Open 会失败。",
        },
        deprecate=True,
    ) is True

    updated = playbook.iter_all_section_rules("planning")[0]
    assert updated["harmful_count"] == 1
    assert updated["status"] == "deprecated"
    assert updated["deprecated"] is True
    assert updated["counterexamples"][0]["case_id"] == "train-case-2"
    assert playbook.iter_section_rules("planning") == []


def test_apply_delta_updates_merges_and_deprecates_rules(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)

    assert playbook.apply_delta("planning", {"op": "add", "id": "r1", "rule": "交互前先导航。"})
    assert playbook.apply_delta("planning", {"op": "add", "id": "r2", "rule": "物理交互前必须先导航到目标。"})
    assert playbook.apply_delta("planning", {"op": "update", "target_id": "r1", "rule": "交互前必须先导航到目标位置。"})
    assert playbook.apply_delta(
        "planning",
        {
            "op": "merge",
            "id": "r3",
            "target_ids": ["r1", "r2"],
            "rule": "所有物理交互前必须导航到目标位置。",
        },
    )
    assert playbook.apply_delta("planning", {"op": "deprecate", "target_id": "r3", "reason": "test"})

    all_rules = {rule["id"]: rule for rule in playbook.iter_all_section_rules("planning")}
    assert all_rules["r1"]["deprecated"] is True
    assert all_rules["r2"]["deprecated"] is True
    assert all_rules["r3"]["deprecated"] is True
    assert all_rules["r3"]["deprecated_reason"] == "test"
    assert playbook.iter_section_rules("planning") == []


def test_refine_playbook_merges_duplicates_and_deprecates_harmful(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)
    playbook.save_playbook(
        {
            "rules": [
                {
                    "section": "planning",
                    "id": "r1",
                    "source": "test",
                    "helpful_count": 2,
                    "harmful_count": 0,
                    "rule": "交互前必须先导航到目标位置。",
                },
                {
                    "section": "planning",
                    "id": "r2",
                    "source": "test",
                    "helpful_count": 1,
                    "harmful_count": 0,
                    "rule": "交互前必须先导航到目标位置。 ",
                },
                {
                    "section": "planning",
                    "id": "r3",
                    "source": "test",
                    "helpful_count": 0,
                    "harmful_count": 3,
                    "rule": "总是忽略导航。",
                },
            ]
        }
    )

    result = playbook.refine_playbook("planning")
    all_rules = {rule["id"]: rule for rule in playbook.iter_all_section_rules("planning")}

    assert result["changed"] is True
    assert result["merged"] == 1
    assert result["deprecated"] == 1
    assert all_rules["r1"]["helpful_count"] == 3
    assert all_rules["r2"]["deprecated"] is True
    assert all_rules["r3"]["deprecated"] is True


def test_learn_from_success_adds_generalized_success_rule(tmp_path, monkeypatch):
    use_temp_playbooks(tmp_path, monkeypatch)
    todo_list = [
        {"execution": {"skill": "NavigateTo", "parameters": {"target_location": "桌子"}}},
        {"execution": {"skill": "Pickup", "parameters": {"target_item": "苹果"}}},
        {"execution": {"skill": "NavigateTo", "parameters": {"target_location": "盘子"}}},
        {"execution": {"skill": "Put", "parameters": {"target_item": "苹果", "destination": "盘子"}}},
    ]

    assert playbook.learn_from_success("planning", "把苹果放到盘子", todo_list) is True
    assert playbook.learn_from_success("planning", "把苹果放到盘子", todo_list) is False

    rules = playbook.iter_section_rules("planning")
    assert len(rules) == 1
    assert "搬运类任务" in rules[0]["rule"]
    assert rules[0]["source"] == "成功轨迹总结"
