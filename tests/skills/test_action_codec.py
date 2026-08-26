from skills.action_codec import (
    action_domain,
    ensure_execution_shape,
    extract_action,
    parse_action_call,
)


def test_profile_codec_resolves_positional_parameters_from_skill_contracts():
    skill, parameters = parse_action_call("Put(鸡蛋_1, 陶瓷盘_1)")

    assert skill == "Put"
    assert parameters == {
        "target_item": "鸡蛋_1",
        "destination": "陶瓷盘_1",
    }


def test_profile_codec_normalizes_compact_action_string():
    assert ensure_execution_shape("Open(顶层橱柜_1)") == {
        "execution": {
            "skill": "Open",
            "parameters": {"target_container": "顶层橱柜_1"},
        }
    }


def test_action_domain_comes_from_the_selected_skill_contract():
    assert action_domain("NavigateTo") == "底盘控制"
    assert action_domain("Read", profile="eai_virtualhome") == "感知/信息交互"
    assert action_domain("Unknown") == "通用控制"


def test_extract_action_accepts_minimal_execution_shape():
    step = {"skill": "NavigateTo", "parameters": {"target_location": "冰箱_1"}}

    skill, parameters, action_str = extract_action(step)

    assert skill == "NavigateTo"
    assert parameters == {"target_location": "冰箱_1"}
    assert action_str == "NavigateTo(target_location=冰箱_1)"


def test_ensure_execution_shape_wraps_minimal_skill_parameters_shape():
    step = {"skill": "Pickup", "parameters": {"target_item": "鸡蛋_1"}}

    normalized = ensure_execution_shape(step)

    assert normalized["execution"] == {
        "skill": "Pickup",
        "parameters": {"target_item": "鸡蛋_1"},
    }


def test_named_parameters_do_not_depend_on_profile_order():
    skill, parameters = parse_action_call(
        "NavigateTo(target_location=顶层橱柜_1)"
    )

    assert skill == "NavigateTo"
    assert parameters == {"target_location": "顶层橱柜_1"}
