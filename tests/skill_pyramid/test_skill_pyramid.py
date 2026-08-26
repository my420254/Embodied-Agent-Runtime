from skill_pyramid import (
    ABSTRACT_LEVEL,
    ATOMIC_LEVEL,
    CONCRETE_LEVEL,
    ROUTINE_LEVEL,
    build_static_skill_pyramid,
    direct_reuse_chain,
    skill_ids_by_level,
    validate_skill_pyramid,
)


def test_skill_pyramid_builds_all_four_levels():
    nodes = build_static_skill_pyramid()

    assert nodes["NavigateTo"].level == ATOMIC_LEVEL
    assert nodes["routine.acquire_object"].level == ROUTINE_LEVEL
    assert nodes["cooking.make_tea"].level == CONCRETE_LEVEL
    assert nodes["abstract.acquire_transform_place"].level == ABSTRACT_LEVEL
    assert "Slice" in skill_ids_by_level(ATOMIC_LEVEL, nodes)


def test_skill_pyramid_tracks_direct_reuse():
    nodes = build_static_skill_pyramid()

    acquire_chain = direct_reuse_chain("routine.acquire_object", nodes)
    heat_refs = {ref.skill_id for ref in nodes["routine.heat_item_in_device"].uses}

    assert {node.skill_id for node in acquire_chain} == {
        "routine.navigate_to_target",
        "Pickup",
    }
    assert {
        "routine.place_object",
        "routine.close_then_activate_device",
        "Heat",
    } <= heat_refs


def test_skill_pyramid_is_structurally_valid():
    assert validate_skill_pyramid() == ()
