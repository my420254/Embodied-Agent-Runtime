from skills.Clean.handler import CleanSkill
from skills.Close.handler import CloseSkill
from skills.Heat.handler import HeatSkill
from skills.Open.handler import OpenSkill
from skills.Put.handler import PutSkill
from skills.Slice.handler import SliceSkill
from skills.ToggleOn.handler import ToggleOnSkill


EMPTY_ROBOT = {"robot_location": "", "robot_holding": "空"}


def test_open_rejects_repeated_state_and_non_openable_target():
    robot = {**EMPTY_ROBOT, "robot_location": "fridge"}
    assert not OpenSkill().validate(
        {"fridge": {"states": {"isOpen": True}}}, robot, {"target_container": "fridge"}
    )[0]
    robot["robot_location"] = "table"
    assert not OpenSkill().validate(
        {"table": {"states": {}}}, robot, {"target_container": "table"}
    )[0]


def test_close_rejects_repeated_state():
    assert not CloseSkill().validate(
        {"fridge": {"states": {"isOpen": False}}},
        {**EMPTY_ROBOT, "robot_location": "fridge"},
        {"target_container": "fridge"},
    )[0]


def test_toggle_rejects_non_switchable_target():
    assert not ToggleOnSkill().validate(
        {"table": {"states": {}}},
        {**EMPTY_ROBOT, "robot_location": "table"},
        {"target_device": "table"},
    )[0]


def test_slice_requires_explicit_usable_tool_and_unsliced_target():
    env = {
        "board": {"states": {}},
        "food": {"direct_parent": "board", "states": {"isClean": True, "isSliced": False}},
        "apple": {"states": {}},
    }
    robot = {"robot_location": "board", "robot_holding": "apple"}
    assert not SliceSkill().validate(env, robot, {"target_item": "food", "surface": "board"})[0]
    env["apple"]["states"] = {"isSharp": True, "isBroken": False}
    env["food"]["states"]["isSliced"] = True
    assert not SliceSkill().validate(env, robot, {"target_item": "food", "surface": "board"})[0]


def test_clean_and_heat_reject_repeated_target_state():
    clean_env = {
        "sink": {"states": {"isFilledWithLiquid": True}},
        "plate": {"direct_parent": "robot_hand", "states": {"isClean": True, "isDirty": False}},
    }
    assert not CleanSkill().validate(
        clean_env,
        {"robot_location": "sink", "robot_holding": "plate"},
        {"target_item": "plate", "water_source": "sink"},
    )[0]
    heat_env = {
        "oven": {"states": {"isOpen": False, "isToggled": True}},
        "food": {"direct_parent": "oven", "states": {"isCooked": True}},
    }
    assert not HeatSkill().validate(
        heat_env,
        {"robot_location": "oven", "robot_holding": "空"},
        {"target_item": "food", "heating_device": "oven"},
    )[0]


def test_put_updates_parent_path_and_relation():
    env = {
        "room": {"full_path": [], "states": {}},
        "fridge": {"full_path": ["room"], "states": {"isOpen": True}, "is_container": True},
        "food": {"direct_parent": "robot_hand", "full_path": [], "states": {}},
    }
    robot = {"robot_location": "fridge", "robot_holding": "food"}
    params = {"target_item": "food", "destination": "fridge"}
    handler = PutSkill()
    assert handler.validate(env, robot, params)[0]
    handler.apply(env, robot, params)
    assert robot["robot_holding"] == "空"
    assert env["food"]["direct_parent"] == "fridge"
    assert env["food"]["direct_relation"] == "inside"
    assert env["food"]["full_path"] == ["room", "fridge"]
