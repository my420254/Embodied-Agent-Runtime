from pathlib import Path

from adapters.sandbox import apply_sandbox_action
from config.settings import get_config, project_path
from skills.loader import load_enabled_skill_names
from skills.registry import get_skill_handlers
from benchmark.reactree.alfred.framework.code.skills.go_to.handler import GoToSkill


def test_each_enabled_skill_has_prompt_metadata_and_handler():
    configured_root = Path(str(get_config("skills", "root", default="skills") or "skills"))
    skills_dir = configured_root if configured_root.is_absolute() else project_path(str(configured_root))
    enabled_skills = set(load_enabled_skill_names())
    loaded_handlers = set(get_skill_handlers())

    assert enabled_skills
    assert enabled_skills == loaded_handlers
    for skill_name in enabled_skills:
        assert (skills_dir / skill_name / "prompt.md").exists()
        assert (skills_dir / skill_name / "skill.yaml").exists()
        assert (skills_dir / skill_name / "handler.py").exists()


def test_apply_sandbox_action_rejects_room_level_navigation():
    sim_env = {
        "厨房": {"direct_parent": "未知环境", "full_path": [], "states": {}},
        "桌子": {"direct_parent": "厨房", "full_path": ["厨房"], "states": {}},
    }
    sim_robot = {"robot_location": "桌子", "robot_holding": "空"}

    ok, issue, fix = apply_sandbox_action(sim_env, sim_robot, "NavigateTo", {"target_location": "厨房"})

    assert not ok
    assert "泛区域" in issue
    assert "具体交互节点" in fix
    assert sim_robot["robot_location"] == "桌子"


def test_go_to_allows_direct_navigation_to_pickupable_instance():
    sim_env = {
        "Dresser (1)": {
            "direct_parent": "Bedroom (1)",
            "type": "receptacle",
            "states": {},
        },
        "CellPhone (1)": {
            "direct_parent": "Dresser (1)",
            "properties": ["pickupable"],
            "states": {},
        },
    }

    assert GoToSkill().validate(
        sim_env,
        {"robot_location": "Bedroom (1)"},
        {"target": "CellPhone (1)"},
    ) == (True, "", "")


def test_apply_sandbox_action_allows_redundant_idempotent_actions():
    sim_env = {
        "橱柜_1": {
            "direct_parent": "厨房",
            "full_path": ["厨房"],
            "states": {"isOpen": True},
        },
        "灯_1": {
            "direct_parent": "厨房",
            "full_path": ["厨房"],
            "states": {"isToggled": True},
        },
    }
    sim_robot = {"robot_location": "橱柜_1", "robot_holding": "空"}

    assert apply_sandbox_action(
        sim_env,
        sim_robot,
        "NavigateTo",
        {"target_location": "橱柜_1"},
    ) == (True, "", "")
    assert apply_sandbox_action(
        sim_env,
        sim_robot,
        "Open",
        {"target_container": "橱柜_1"},
    ) == (True, "", "")

    sim_robot["robot_location"] = "灯_1"
    assert apply_sandbox_action(
        sim_env,
        sim_robot,
        "ToggleOn",
        {"target_device": "灯_1"},
    ) == (True, "", "")


def test_apply_sandbox_action_pickup_moves_item_to_robot_hand():
    sim_env = {
        "桌子": {"direct_parent": "厨房", "full_path": ["厨房"], "states": {}},
        "苹果": {"direct_parent": "桌子", "full_path": ["厨房", "桌子"], "states": {}},
    }
    sim_robot = {"robot_location": "桌子", "robot_holding": "空"}

    ok, issue, fix = apply_sandbox_action(sim_env, sim_robot, "Pickup", {"target_item": "苹果"})

    assert ok
    assert issue == ""
    assert fix == ""
    assert sim_robot["robot_holding"] == "苹果"
    assert sim_env["苹果"]["direct_parent"] == "robot_hand"


def test_apply_sandbox_action_pickup_allows_navigation_to_room_level_object():
    sim_env = {
        "洗衣房": {"direct_parent": "未知环境", "full_path": [], "states": {}},
        "洗衣液_1": {"direct_parent": "洗衣房", "full_path": ["洗衣房"], "states": {}},
    }
    sim_robot = {"robot_location": "洗衣液_1", "robot_holding": "空"}

    ok, issue, fix = apply_sandbox_action(sim_env, sim_robot, "Pickup", {"target_item": "洗衣液_1"})

    assert ok
    assert issue == ""
    assert fix == ""
    assert sim_robot["robot_holding"] == "洗衣液_1"
    assert sim_env["洗衣液_1"]["direct_parent"] == "robot_hand"


def test_apply_sandbox_action_rejects_pickup_from_closed_container():
    sim_env = {
        "抽屉": {
            "direct_parent": "厨房",
            "full_path": ["厨房"],
            "states": {"isOpen": False},
        },
        "刀": {
            "direct_parent": "抽屉",
            "full_path": ["厨房", "抽屉"],
            "states": {"isSharp": True},
        },
    }
    sim_robot = {"robot_location": "抽屉", "robot_holding": "空"}

    ok, issue, fix = apply_sandbox_action(sim_env, sim_robot, "Pickup", {"target_item": "刀"})

    assert not ok
    assert issue == "物理可达性受限"
    assert "Open" in fix


def test_apply_sandbox_action_pickup_allows_open_ancestor_for_internal_component():
    sim_env = {
        "冰箱_1": {
            "direct_parent": "厨房",
            "full_path": ["厨房"],
            "states": {"isOpen": True},
        },
        "冷冻室_1": {
            "direct_parent": "冰箱_1",
            "full_path": ["厨房", "冰箱_1"],
            "states": {},
        },
        "冷冻猪肉_1": {
            "direct_parent": "冷冻室_1",
            "full_path": ["厨房", "冰箱_1", "冷冻室_1"],
            "states": {"isFrozen": True},
        },
    }
    sim_robot = {"robot_location": "冰箱_1", "robot_holding": "空"}

    ok, issue, fix = apply_sandbox_action(sim_env, sim_robot, "Pickup", {"target_item": "冷冻猪肉_1"})

    assert ok
    assert issue == ""
    assert fix == ""
    assert sim_robot["robot_holding"] == "冷冻猪肉_1"
    assert sim_env["冷冻猪肉_1"]["direct_parent"] == "robot_hand"


def test_apply_sandbox_action_rejects_slice_dirty_food():
    sim_env = {
        "厨房操作台_1": {
            "direct_parent": "厨房",
            "full_path": ["厨房"],
            "states": {},
        },
        "土豆_1": {
            "direct_parent": "厨房操作台_1",
            "full_path": ["厨房", "厨房操作台_1"],
            "states": {"isClean": False},
        },
        "厨师刀_1": {
            "direct_parent": "robot_hand",
            "full_path": [],
            "states": {"isSharp": True, "isBroken": False},
        },
    }
    sim_robot = {"robot_location": "厨房操作台_1", "robot_holding": "厨师刀_1"}

    ok, issue, fix = apply_sandbox_action(
        sim_env,
        sim_robot,
        "Slice",
        {"target_item": "土豆_1", "surface": "厨房操作台_1"},
    )

    assert not ok
    assert issue == "卫生前置约束未满足"
    assert "Clean" in fix
