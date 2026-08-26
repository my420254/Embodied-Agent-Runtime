from graph.planning import normalizer


def test_normalize_todo_list_accepts_minimal_skill_parameters_shape(monkeypatch):
    monkeypatch.setattr(
        normalizer,
        "get_full_flat_house",
        lambda *_args, **_kwargs: {
            "厨房操作台_1": {"direct_parent": "厨房", "full_path": ["厨房"], "states": {}},
            "冰箱_1": {"direct_parent": "厨房", "full_path": ["厨房"], "states": {}},
        },
    )

    todo = [
        {"skill": "NavigateTo", "parameters": {"target_location": "冰箱_1"}},
        {"skill": "Pickup", "parameters": {"target_item": "鸡蛋_1"}},
    ]

    normalized = normalizer._normalize_todo_list(
        todo,
        {"robot_location": "厨房操作台_1", "robot_holding": "空"},
    )

    assert [step["step"] for step in normalized] == [1, 2]
    assert normalized[0]["execution"] == {
        "skill": "NavigateTo",
        "parameters": {"target_location": "冰箱_1"},
    }
    assert normalized[1]["execution"] == {
        "skill": "Pickup",
        "parameters": {"target_item": "鸡蛋_1"},
    }


def test_normalize_todo_list_accepts_action_call_strings(monkeypatch):
    monkeypatch.setattr(
        normalizer,
        "get_full_flat_house",
        lambda *_args, **_kwargs: {
            "厨房操作台_1": {"direct_parent": "厨房", "full_path": ["厨房"], "states": {}},
            "顶层橱柜_1": {"direct_parent": "厨房", "full_path": ["厨房"], "states": {}},
        },
    )

    normalized = normalizer._normalize_todo_list(
        ["NavigateTo(顶层橱柜_1)", "Open(顶层橱柜_1)"],
        {"robot_location": "厨房操作台_1", "robot_holding": "空"},
    )

    assert [step["execution"] for step in normalized] == [
        {"skill": "NavigateTo", "parameters": {"target_location": "顶层橱柜_1"}},
        {"skill": "Open", "parameters": {"target_container": "顶层橱柜_1"}},
    ]


def test_normalizer_preserves_invalid_steps_for_evaluator_reporting(monkeypatch):
    monkeypatch.setattr(
        normalizer,
        "get_full_flat_house",
        lambda *_args, **_kwargs: {
            "厨房_1": {"type": "room", "direct_parent": "未知环境", "states": {}},
        },
    )

    normalized = normalizer._normalize_todo_list(
        [
            "NavigateTo(不存在_1)",
            {"execution": {"skill": "InventedSkill", "parameters": {}}},
            {"unexpected": "shape"},
        ],
        {"robot_location": "厨房_1", "robot_holding": "空"},
    )

    assert len(normalized) == 3
    assert [step["step"] for step in normalized] == [1, 2, 3]
    assert normalized[0]["execution"]["parameters"]["target_location"] == "不存在_1"
    assert normalized[1]["execution"]["skill"] == "InventedSkill"
    assert normalized[2]["unexpected"] == "shape"
