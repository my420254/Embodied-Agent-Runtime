from graph.understanding import node as understanding_node
from graph.understanding import pipeline as understanding_pipeline
from graph.understanding.features import entity_repair, goal_state_extract
from graph.understanding.features.normalize import normalize_structured_task


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self, content: str):
        self.content = content

    def invoke(self, messages):
        return FakeResponse(self.content)


def _state(raw_instruction: str, entities: set[str] | list[str], **overrides):
    state = {
        "raw_instruction": raw_instruction,
        "messages": [],
        "task_context": {"available_entities": sorted(str(name) for name in entities)},
    }
    state.update(overrides)
    return state


def test_analyze_instruction_normalizes_required_item_schema(monkeypatch):
    entities = {"苹果_1", "盘子_1", "水果刀_1"}
    monkeypatch.setattr(understanding_node, "load_system_rules", lambda: "")
    monkeypatch.setattr(understanding_node, "load_understanding_playbook", lambda: "")
    monkeypatch.setattr(understanding_node, "render_prompt", lambda *args, **kwargs: "prompt")
    monkeypatch.setattr(understanding_node, "get_understanding_llm", lambda: FakeLLM("{}"))
    monkeypatch.setattr(
        understanding_node,
        "parse_json_from_llm",
        lambda *args, **kwargs: {
            "is_complete": True,
            "is_cancel_all": False,
            "clarification_question": "",
                "structured_task": {
                    "intent": "把苹果放到盘子里",
                "required_item_names": {
                    "targets": ["苹果_1"],
                    "tools": {"primary": ["水果刀_1"], "alternatives": []},
                    "receptacles": {"primary": ["盘子_1"]},
                },
                "goal_state": {
                    "entities": {
                        "苹果_1": {"direct_parent": "盘子_1"},
                    }
                },
            },
        },
    )

    result = understanding_node.analyze_instruction(_state("把苹果放到盘子里", entities))

    structured = result["structured_task"]
    assert structured["intent"] == "把苹果放到盘子里"
    assert "operation_type" not in structured
    assert structured["required_item_names"]["targets"] == {"primary": ["苹果_1"], "alternatives": []}
    assert structured["required_item_names"]["tools"] == {"primary": ["水果刀_1"], "alternatives": []}
    assert structured["required_item_names"]["receptacles"] == {"primary": ["盘子_1"], "alternatives": []}
    assert "rule_triggered" not in structured["required_item_names"]
    assert structured["goal_state"] == {
        "entities": {"苹果_1": {"direct_parent": "盘子_1"}}
    }
    assert "triggered_rules" not in structured
    assert set(result["relevant_item_names"]) == {
        "苹果_1",
        "盘子_1",
        "水果刀_1",
    }
    assert result["needs_clarification"] is False


def test_analyze_instruction_repairs_invalid_entity_names_with_llm(monkeypatch):
    entities = {"苹果_1", "盘子_1"}
    monkeypatch.setattr(understanding_node, "load_system_rules", lambda: "")
    monkeypatch.setattr(understanding_node, "load_understanding_playbook", lambda: "")
    monkeypatch.setattr(understanding_node, "render_prompt", lambda *args, **kwargs: "prompt")
    monkeypatch.setattr(understanding_node, "get_understanding_llm", lambda: FakeLLM("{}"))
    parse_calls = {"count": 0}

    invalid_result = {
        "is_complete": True,
        "is_cancel_all": False,
        "clarification_question": "",
        "structured_task": {
            "intent": "把苹果放到盘子里",
            "required_item_names": {
                "targets": {"primary": ["苹果_2"], "alternatives": []},
                "tools": {"primary": [], "alternatives": []},
                "receptacles": {"primary": ["盘子_1"], "alternatives": []},
            },
            "goal_state": {
                "entities": {
                    "苹果_2": {"direct_parent": "盘子_1"},
                }
            },
        },
    }
    repaired_result = {
        "is_complete": True,
        "is_cancel_all": False,
        "clarification_question": "",
        "structured_task": {
            "intent": "把苹果放到盘子里",
            "required_item_names": {
                "targets": {"primary": ["苹果_1"], "alternatives": []},
                "tools": {"primary": [], "alternatives": []},
                "receptacles": {"primary": ["盘子_1"], "alternatives": []},
            },
        },
    }

    def fake_parse(*args, **kwargs):
        parse_calls["count"] += 1
        return invalid_result if parse_calls["count"] == 1 else repaired_result

    monkeypatch.setattr(
        understanding_node,
        "parse_json_from_llm",
        fake_parse,
    )

    result = understanding_node.analyze_instruction(_state("把苹果放到盘子里", entities))

    assert result["is_complete"] is True
    assert result["needs_clarification"] is False
    assert result["clarification_question"] == ""
    assert parse_calls["count"] == 2
    assert result["structured_task"]["required_item_names"]["targets"]["primary"] == ["苹果_1"]
    assert "invalid_entity_names" not in result
    assert "dropped_invalid_entity_names" not in result
    assert result["entity_repair"]["attempts"] == 1


def test_analyze_instruction_cancel_returns_normalized_empty_schema():
    result = understanding_node.analyze_instruction(
        {
            "raw_instruction": "取消当前任务",
            "messages": [],
        }
    )

    assert result["is_complete"] is True
    assert result["is_cancel_all"] is True
    assert result["needs_clarification"] is False
    assert result["relevant_item_names"] == []
    assert "operation_type" not in result["structured_task"]
    assert result["structured_task"]["required_item_names"] == {
        "targets": {"primary": [], "alternatives": []},
        "tools": {"primary": [], "alternatives": []},
        "receptacles": {"primary": [], "alternatives": []},
    }


def test_analyze_instruction_ignores_model_operation_type(monkeypatch):
    entities = {"floor_lamp"}
    monkeypatch.setattr(understanding_node, "load_system_rules", lambda: "")
    monkeypatch.setattr(understanding_node, "load_understanding_playbook", lambda: "")
    monkeypatch.setattr(understanding_node, "render_prompt", lambda *args, **kwargs: "prompt")
    monkeypatch.setattr(understanding_node, "get_understanding_llm", lambda: FakeLLM("{}"))
    monkeypatch.setattr(
        understanding_node,
        "parse_json_from_llm",
        lambda *args, **kwargs: {
            "is_complete": True,
            "is_cancel_all": False,
            "clarification_question": "",
            "structured_task": {
                "intent": "Turn on the light",
                "operation_type": "open",
                "required_item_names": {
                    "targets": {"primary": ["floor_lamp"], "alternatives": []},
                    "tools": {"primary": [], "alternatives": []},
                    "receptacles": {"primary": [], "alternatives": []},
                },
            },
        },
    )

    result = understanding_node.analyze_instruction(_state("Turn on the light", entities))

    assert "operation_type" not in result["structured_task"]


def test_analyze_instruction_outputs_relevant_scene_items(monkeypatch):
    entities = {"苹果_1", "盘子_1", "水果刀_1"}
    monkeypatch.setattr(understanding_node, "load_system_rules", lambda: "")
    monkeypatch.setattr(understanding_node, "load_understanding_playbook", lambda: "")
    monkeypatch.setattr(understanding_node, "render_prompt", lambda *args, **kwargs: "prompt")
    monkeypatch.setattr(understanding_node, "get_understanding_llm", lambda: FakeLLM("{}"))
    monkeypatch.setattr(
        understanding_node,
        "parse_json_from_llm",
        lambda *args, **kwargs: {
            "is_complete": True,
            "is_cancel_all": False,
            "clarification_question": "",
            "structured_task": {
                "intent": "把苹果放到盘子里",
                "required_item_names": {
                    "targets": {"primary": ["苹果_1"], "alternatives": []},
                    "tools": {"primary": [], "alternatives": []},
                    "receptacles": {"primary": ["盘子_1"], "alternatives": []},
                },
            },
        },
    )

    result = understanding_node.analyze_instruction(_state("把苹果放到盘子里", entities))

    assert result["relevant_item_names"] == ["苹果_1", "盘子_1"]


def test_analyze_instruction_outputs_relevance_ranked_items(monkeypatch):
    entities = {"牛肉_1", "菜刀_1", "砧板_1", "冰箱_1"}
    monkeypatch.setattr(understanding_node, "load_system_rules", lambda: "")
    monkeypatch.setattr(understanding_node, "load_understanding_playbook", lambda: "")
    monkeypatch.setattr(understanding_node, "render_prompt", lambda *args, **kwargs: "prompt")
    monkeypatch.setattr(understanding_node, "get_understanding_llm", lambda: FakeLLM("{}"))
    monkeypatch.setattr(
        understanding_node,
        "parse_json_from_llm",
        lambda *args, **kwargs: {
            "is_complete": True,
            "is_cancel_all": False,
            "clarification_question": "",
            "entity_relevance": {
                "directly_related": [
                    {"name": "菜刀_1", "score": 0.7, "required": True},
                    {"name": "牛肉_1", "score": 1.0, "required": True},
                ],
                "indirectly_related": [
                    {"name": "冰箱_1", "score": 0.4, "required": False},
                    {"name": "砧板_1", "score": 0.9, "required": True},
                ],
                "possibly_related": [],
            },
            "structured_task": {
                "intent": "切牛肉",
                "required_item_names": {
                    "targets": {"primary": ["牛肉_1"], "alternatives": []},
                    "tools": {"primary": ["菜刀_1"], "alternatives": []},
                    "receptacles": {"primary": ["砧板_1"], "alternatives": ["冰箱_1"]},
                },
            },
        },
    )

    result = understanding_node.analyze_instruction(_state("切牛肉", entities))

    assert result["relevant_item_names"] == [
        "牛肉_1",
        "菜刀_1",
        "砧板_1",
        "冰箱_1",
    ]


def test_analyze_instruction_marks_clarification_needed(monkeypatch):
    entities = {"苹果_1", "盘子_1"}
    monkeypatch.setattr(understanding_node, "load_system_rules", lambda: "")
    monkeypatch.setattr(understanding_node, "load_understanding_playbook", lambda: "")
    monkeypatch.setattr(understanding_node, "render_prompt", lambda *args, **kwargs: "prompt")
    monkeypatch.setattr(understanding_node, "get_understanding_llm", lambda: FakeLLM("{}"))
    monkeypatch.setattr(
        understanding_node,
        "parse_json_from_llm",
        lambda *args, **kwargs: {
            "is_complete": False,
            "is_cancel_all": False,
            "clarification_question": "请问您要操作哪个物品？",
            "structured_task": {
                "intent": "",
                "required_item_names": {},
            },
        },
    )

    result = understanding_node.analyze_instruction(_state("处理一下", entities))

    assert result["is_complete"] is False
    assert result["needs_clarification"] is True
    assert result["clarification_question"] == "请问您要操作哪个物品？"


def test_understanding_pipeline_uses_feature_config(monkeypatch):
    monkeypatch.setattr(
        understanding_pipeline,
        "load_feature_config",
        lambda: {
            "enabled_features": ["clarification"],
            "features": {
                "clarification": "graph.understanding.features.clarification:run",
            },
        },
    )

    result = understanding_pipeline.run_understanding_pipeline("", {"苹果_1"}, [])

    assert result["is_complete"] is False
    assert result["needs_clarification"] is True
    assert "希望机器人执行什么任务" in result["clarification_question"]


def test_analyze_instruction_does_not_add_missing_operation_type(monkeypatch):
    entities = {"mainboard", "living_room"}
    monkeypatch.setattr(understanding_node, "load_system_rules", lambda: "")
    monkeypatch.setattr(understanding_node, "load_understanding_playbook", lambda: "")
    monkeypatch.setattr(understanding_node, "render_prompt", lambda *args, **kwargs: "prompt")
    monkeypatch.setattr(understanding_node, "get_understanding_llm", lambda: FakeLLM("{}"))
    monkeypatch.setattr(
        understanding_node,
        "parse_json_from_llm",
        lambda *args, **kwargs: {
            "is_complete": True,
            "is_cancel_all": False,
            "clarification_question": "",
            "structured_task": {
                "intent": "bring mainboard to the living room",
                "required_item_names": {
                    "targets": {"primary": ["mainboard"], "alternatives": []},
                    "tools": {"primary": [], "alternatives": []},
                    "receptacles": {"primary": ["living_room"], "alternatives": []},
                },
            },
        },
    )

    result = understanding_node.analyze_instruction(
        _state("bring mainboard to the living room", entities)
    )

    assert "operation_type" not in result["structured_task"]


def test_final_state_extract_uses_single_settings_switch():
    assert goal_state_extract._enabled({"enabled": True}) is True
    assert goal_state_extract._enabled({"enabled": False}) is False
    assert entity_repair._enabled({"enabled": False}, {"entity_repair": True}) is True
    assert entity_repair._enabled({"enabled": True}, {"entity_repair": False}) is False


def test_final_state_extract_skips_incomplete_understanding(monkeypatch):
    calls = {"render": 0}

    class FakeNode:
        @staticmethod
        def render_prompt(*args, **kwargs):
            calls["render"] += 1
            return "prompt"

        @staticmethod
        def get_understanding_llm():
            raise AssertionError("final state prompt should not run for incomplete understanding")

        @staticmethod
        def parse_json_from_llm(*args, **kwargs):
            return {}

    monkeypatch.setattr(goal_state_extract, "_understanding_node", lambda: FakeNode)

    output = goal_state_extract.run(
        {
            "feature_settings": {"goal_state_extract": {"enabled": True}},
            "runtime_options": {},
            "task": "处理一下",
            "scene_entities": ["苹果_1"],
        },
        {
            "is_complete": False,
            "needs_clarification": True,
            "structured_task": {"intent": ""},
        },
    )

    assert output == {}
    assert calls["render"] == 0


def test_normalize_preserves_distinct_multi_instance_targets():
    structured = normalize_structured_task(
        {
            "intent": "拿 5 个苹果",
            "required_item_names": {
                "targets": {
                    "primary": ["apple_1", "apple_2", "apple_3", "apple_4", "apple_5"],
                    "alternatives": [],
                }
            },
            "quantity_constraints": [
                {
                    "role": "targets",
                    "object_type": "apple",
                    "count": 5,
                    "selected_entities": ["apple_1", "apple_2", "apple_3", "apple_4", "apple_5"],
                }
            ],
        }
    )

    assert structured["required_item_names"]["targets"]["primary"] == [
        "apple_1",
        "apple_2",
        "apple_3",
        "apple_4",
        "apple_5",
    ]
    assert structured["quantity_constraints"][0]["count"] == 5


def test_entity_repair_retries_when_quantity_constraint_is_underfilled(monkeypatch):
    calls = {"parse": 0}

    class FakeNode:
        @staticmethod
        def load_system_rules():
            return ""

        @staticmethod
        def render_prompt(*args, **kwargs):
            return "prompt"

        @staticmethod
        def get_understanding_llm():
            return FakeLLM("{}")

        @staticmethod
        def parse_json_from_llm(*args, **kwargs):
            calls["parse"] += 1
            return {
                "is_complete": True,
                "structured_task": {
                    "intent": "拿 5 个苹果",
                    "required_item_names": {
                        "targets": {
                            "primary": ["apple_1", "apple_2", "apple_3", "apple_4", "apple_5"],
                            "alternatives": [],
                        },
                        "tools": {"primary": [], "alternatives": []},
                        "receptacles": {"primary": [], "alternatives": []},
                    },
                    "quantity_constraints": [
                        {
                            "role": "targets",
                            "object_type": "apple",
                            "count": 5,
                            "selected_entities": ["apple_1", "apple_2", "apple_3", "apple_4", "apple_5"],
                        }
                    ],
                },
            }

    monkeypatch.setattr(entity_repair, "_understanding_node", lambda: FakeNode)

    result = entity_repair.run(
        {
            "task": "拿 5 个苹果",
            "scene_entities": ["apple_1", "apple_2", "apple_3", "apple_4", "apple_5"],
            "feature_settings": {"entity_repair": {"enabled": True, "max_attempts": 2}},
            "runtime_options": {},
        },
        {
            "is_complete": True,
            "structured_task": {
                "intent": "拿 5 个苹果",
                "required_item_names": {
                    "targets": {"primary": ["apple_1"], "alternatives": []},
                    "tools": {"primary": [], "alternatives": []},
                    "receptacles": {"primary": [], "alternatives": []},
                },
                "quantity_constraints": [
                    {
                        "role": "targets",
                        "object_type": "apple",
                        "count": 5,
                        "selected_entities": ["apple_1"],
                    }
                ],
            },
        },
    )

    assert calls["parse"] == 1
    assert result["structured_task"]["required_item_names"]["targets"]["primary"] == [
        "apple_1",
        "apple_2",
        "apple_3",
        "apple_4",
        "apple_5",
    ]
    assert result["entity_repair"]["quantity_constraint_issues"] == []
