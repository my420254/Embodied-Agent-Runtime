from skills.loader import load_enabled_skill_names
from skills.planning_catalog import load_planning_catalog


def test_evaluation_provided_catalog_supports_planning_contract_queries():
    enabled = set(load_enabled_skill_names("core_household"))
    catalog = load_planning_catalog("core_household")

    assert catalog.location_action("冰箱_1")["skill"] in enabled
    assert catalog.grasp_action("鸡蛋_1")["skill"] in enabled
    assert catalog.place_action("鸡蛋_1", "陶瓷盘_1")["skill"] in enabled
    assert catalog.state_action("isOpen", True, "冰箱_1")["skill"] in enabled
    assert catalog.state_action("isOpen", False, "冰箱_1")["skill"] in enabled
    assert catalog.state_action("isToggled", True, "微波炉_1")["skill"] in enabled
