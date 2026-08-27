from domain.scene import flatten_scene, flat_scene_to_tree_from_base, is_item_accessible


def test_flat_scene_roundtrip_preserves_action_capability_metadata():
    scene = {
        "environment": {
            "kitchen": {
                "type": "room",
                "contains": {
                    "counter_1": {
                        "type": "receptacle",
                        "category": "surface",
                        "abilities": ["PUTBACK"],
                        "nearby": ["fridge_1"],
                        "states": {"isClean": True},
                        "contains": {
                            "cup_1": {
                                "type": "object",
                                "category": "drinkware",
                                "direct_relation": "on",
                                "abilities": ["GRAB"],
                                "nearby": ["counter_1"],
                                "states": {"isClean": True},
                            }
                        },
                    }
                },
            }
        },
        "robot_location": "kitchen",
    }

    flat = flatten_scene(scene)
    rebuilt = flat_scene_to_tree_from_base(flat, {"robot_location": "kitchen"}, scene)
    rebuilt_flat = flatten_scene(rebuilt)

    for name in ("counter_1", "cup_1"):
        assert rebuilt_flat[name]["category"] == flat[name]["category"]
        assert rebuilt_flat[name]["abilities"] == flat[name]["abilities"]
        assert rebuilt_flat[name]["nearby"] == flat[name]["nearby"]


def test_accessibility_infers_inside_relation_for_closed_container_state():
    flat_scene = {
        "drawer_1": {"states": {"isOpen": False}, "direct_parent": "kitchen"},
        "knife_1": {"states": {}, "direct_parent": "drawer_1"},
    }

    assert is_item_accessible("knife_1", flat_scene) is False
