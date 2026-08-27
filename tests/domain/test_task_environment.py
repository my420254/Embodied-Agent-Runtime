from domain.task_environment import build_task_environment_closure


def test_task_environment_closure_keeps_exact_target_parent_and_container_children():
    scene = {
        "environment": {
            "kitchen": {
                "contains": {
                    "fridge_1": {
                        "type": "receptacle",
                        "states": {"isOpen": False},
                        "contains": {
                            "apple_1": {"type": "object", "states": {}},
                            "milk_1": {"type": "object", "states": {}},
                        },
                    },
                    "lamp_1": {"type": "object", "states": {"isOn": False}},
                }
            }
        }
    }
    structured_task = {
        "required_item_names": {
            "targets": {"primary": ["fridge_1"], "alternatives": []},
            "tools": {"primary": [], "alternatives": []},
            "receptacles": {"primary": [], "alternatives": []},
        }
    }

    closure = build_task_environment_closure(scene, structured_task)

    assert set(closure) == {"kitchen", "fridge_1", "apple_1", "milk_1"}
    assert "lamp_1" not in closure
