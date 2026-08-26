# Round 1 understanding.system Input

## Message 1: system

任务：把 ALFRED benchmark case 输入抽取成结构化任务理解。
只返回 JSON；不要解释，不要输出 Markdown。

允许使用的 ALFRED 场景实体名：
["Apple (1)", "Apple (2)", "Apple (3)", "Bowl (1)", "Bowl (2)", "Bowl (3)", "Bread (1)", "Bread (2)", "ButterKnife (1)", "ButterKnife (2)", "ButterKnife (3)", "Cabinet (1)", "Cabinet (10)", "Cabinet (11)", "Cabinet (12)", "Cabinet (13)", "Cabinet (14)", "Cabinet (15)", "Cabinet (16)", "Cabinet (17)", "Cabinet (18)", "Cabinet (19)", "Cabinet (2)", "Cabinet (20)", "Cabinet (21)", "Cabinet (22)", "Cabinet (23)", "Cabinet (24)", "Cabinet (25)", "Cabinet (26)", "Cabinet (3)", "Cabinet (4)", "Cabinet (5)", "Cabinet (6)", "Cabinet (7)", "Cabinet (8)", "Cabinet (9)", "CoffeeMachine (1)", "CounterTop (1)", "CounterTop (2)", "CounterTop (3)", "Cup (1)", "Cup (2)", "Curtains (1)", "DishSponge (1)", "DishSponge (2)", "Drawer (1)", "Drawer (10)", "Drawer (11)", "Drawer (12)", "Drawer (2)", "Drawer (3)", "Drawer (4)", "Drawer (5)", "Drawer (6)", "Drawer (7)", "Drawer (8)", "Drawer (9)", "Egg (1)", "Faucet (1)", "Fork (1)", "Fork (2)", "Fork (3)", "Fridge (1)", "GarbageCan (1)", "Knife (1)", "Lettuce (1)", "Lettuce (2)", "Lettuce (3)", "LightSwitch (1)", "Microwave (1)", "Mug (1)", "Pan (1)", "Pan (2)", "PaperTowelRoll (1)", "Pencil (1)", "Pencil (2)", "PepperShaker (1)", "PepperShaker (2)", "Plate (1)", "Plate (2)", "Pot (1)", "Pot (2)", "Potato (1)", "SaltShaker (1)", "Sink (1)", "SinkBasin (1)", "SoapBottle (1)", "Spatula (1)", "Spoon (1)", "Spoon (2)", "Spoon (3)", "StoveBurner (1)", "StoveBurner (2)", "StoveBurner (3)", "StoveBurner (4)", "StoveKnob (1)", "StoveKnob (2)", "StoveKnob (3)", "StoveKnob (4)", "Toaster (1)", "Tomato (1)", "Tomato (2)", "Window (1)", "WineBottle (1)"]

ALFRED 任务上下文 JSON：
{
  "dataset": "reactree_alfred",
  "task": "pick_heat_then_place_in_recep-PotatoSliced-None-SinkBasin-13/trial_T20190909_115736_122556",
  "repeat_idx": 0,
  "instruction": "Place a cooked potato slice in the sink",
  "task_desc": "",
  "task_source": "alfred_pp_annotation_json",
  "environment_source": "alfred_official_scene_prepare_cache",
  "initial_scene_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/alfred/initial_envs/pick_heat_then_place_in_recep-PotatoSliced-None-SinkBasin-13__trial_T20190909_115736_122556__ann_0.json",
  "available_entities": [
    "Apple (1)",
    "Apple (2)",
    "Apple (3)",
    "Bowl (1)",
    "Bowl (2)",
    "Bowl (3)",
    "Bread (1)",
    "Bread (2)",
    "ButterKnife (1)",
    "ButterKnife (2)",
    "ButterKnife (3)",
    "Cabinet (1)",
    "Cabinet (10)",
    "Cabinet (11)",
    "Cabinet (12)",
    "Cabinet (13)",
    "Cabinet (14)",
    "Cabinet (15)",
    "Cabinet (16)",
    "Cabinet (17)",
    "Cabinet (18)",
    "Cabinet (19)",
    "Cabinet (2)",
    "Cabinet (20)",
    "Cabinet (21)",
    "Cabinet (22)",
    "Cabinet (23)",
    "Cabinet (24)",
    "Cabinet (25)",
    "Cabinet (26)",
    "Cabinet (3)",
    "Cabinet (4)",
    "Cabinet (5)",
    "Cabinet (6)",
    "Cabinet (7)",
    "Cabinet (8)",
    "Cabinet (9)",
    "CoffeeMachine (1)",
    "CounterTop (1)",
    "CounterTop (2)",
    "CounterTop (3)",
    "Cup (1)",
    "Cup (2)",
    "Curtains (1)",
    "DishSponge (1)",
    "DishSponge (2)",
    "Drawer (1)",
    "Drawer (10)",
    "Drawer (11)",
    "Drawer (12)",
    "Drawer (2)",
    "Drawer (3)",
    "Drawer (4)",
    "Drawer (5)",
    "Drawer (6)",
    "Drawer (7)",
    "Drawer (8)",
    "Drawer (9)",
    "Egg (1)",
    "Faucet (1)",
    "Fork (1)",
    "Fork (2)",
    "Fork (3)",
    "Fridge (1)",
    "GarbageCan (1)",
    "Knife (1)",
    "Lettuce (1)",
    "Lettuce (2)",
    "Lettuce (3)",
    "LightSwitch (1)",
    "Microwave (1)",
    "Mug (1)",
    "Pan (1)",
    "Pan (2)",
    "PaperTowelRoll (1)",
    "Pencil (1)",
    "Pencil (2)",
    "PepperShaker (1)",
    "PepperShaker (2)",
    "Plate (1)",
    "Plate (2)",
    "Pot (1)",
    "Pot (2)",
    "Potato (1)",
    "SaltShaker (1)",
    "Sink (1)",
    "SinkBasin (1)",
    "SoapBottle (1)",
    "Spatula (1)",
    "Spoon (1)",
    "Spoon (2)",
    "Spoon (3)",
    "StoveBurner (1)",
    "StoveBurner (2)",
    "StoveBurner (3)",
    "StoveBurner (4)",
    "StoveKnob (1)",
    "StoveKnob (2)",
    "StoveKnob (3)",
    "StoveKnob (4)",
    "Toaster (1)",
    "Tomato (1)",
    "Tomato (2)",
    "Window (1)",
    "WineBottle (1)"
  ]
}
任务上下文中的 task、repeat_idx、instruction、task_desc、initial_scene_cache_path 和 AI2THOR 对象名是本 benchmark 的 grounding；必须保持 ALFRED 任务语义和实例命名。

ALFRED 可用 skill 摘要：
[
  {
    "name": "go to",
    "description": "Official ReAcTree ALFRED navigation action.",
    "planning_contract": {
      "planner_location_param": "target",
      "planner_action_name": "go to",
      "planner_required_fields": "action,target",
      "planner_fixed_fields": "action=go to",
      "planner_entity_fields": "target",
      "planner_allow_extra_fields": "false",
      "planner_entity_pattern": "alfred_instance"
    }
  },
  {
    "name": "pick up",
    "description": "Official ReAcTree ALFRED pickup action.",
    "planning_contract": {
      "planner_item_param": "target",
      "planner_requires_empty_hand": "true",
      "planner_action_name": "pick up",
      "planner_required_fields": "action,target",
      "planner_fixed_fields": "action=pick up",
      "planner_entity_fields": "target",
      "planner_allow_extra_fields": "false",
      "planner_entity_pattern": "alfred_instance"
    }
  },
  {
    "name": "put down",
    "description": "Official ReAcTree ALFRED put-down action.",
    "planning_contract": {
      "planner_destination_param": "target",
      "planner_action_name": "put down",
      "planner_required_fields": "action,target",
      "planner_fixed_fields": "action=put down",
      "planner_entity_fields": "target",
      "planner_allow_extra_fields": "false",
      "planner_entity_pattern": "alfred_instance"
    }
  },
  {
    "name": "open",
    "description": "Official ReAcTree ALFRED open action.",
    "planning_contract": {
      "planner_target_param": "target",
      "planner_location_param": "target",
      "planner_state_key": "isOpen",
      "planner_state_value": "true",
      "planner_reversible_state": "true",
      "planner_action_name": "open",
      "planner_required_fields": "action,target",
      "planner_fixed_fields": "action=open",
      "planner_entity_fields": "target",
      "planner_allow_extra_fields": "false",
      "planner_entity_pattern": "alfred_instance"
    }
  },
  {
    "name": "close",
    "description": "Official ReAcTree ALFRED close action.",
    "planning_contract": {
      "planner_target_param": "target",
      "planner_location_param": "target",
      "planner_state_key": "isOpen",
      "planner_state_value": "false",
      "planner_reversible_state": "true",
      "planner_action_name": "close",
      "planner_required_fields": "action,target",
      "planner_fixed_fields": "action=close",
      "planner_entity_fields": "target",
      "planner_allow_extra_fields": "false",
      "planner_entity_pattern": "alfred_instance"
    }
  },
  {
    "name": "turn on",
    "description": "Official ReAcTree ALFRED turn-on action.",
    "planning_contract": {
      "planner_target_param": "target",
      "planner_location_param": "target",
      "planner_state_key": "isToggled",
      "planner_state_value": "true",
      "planner_reversible_state": "true",
      "planner_action_name": "turn on",
      "planner_required_fields": "action,target",
      "planner_fixed_fields": "action=turn on",
      "planner_entity_fields": "target",
      "planner_allow_extra_fields": "false",
      "planner_entity_pattern": "alfred_instance"
    }
  },
  {
    "name": "turn off",
    "description": "Official ReAcTree ALFRED turn-off action.",
    "planning_contract": {
      "planner_target_param": "target",
      "planner_location_param": "target",
      "planner_state_key": "isToggled",
      "planner_state_value": "false",
      "planner_reversible_state": "true",
      "planner_action_name": "turn off",
      "planner_required_fields": "action,target",
      "planner_fixed_fields": "action=turn off",
      "planner_entity_fields": "target",
      "planner_allow_extra_fields": "false",
      "planner_entity_pattern": "alfred_instance"
    }
  },
  {
    "name": "slice",
    "description": "Official ReAcTree ALFRED slice action.",
    "planning_contract": {
      "planner_item_param": "target",
      "planner_effect_state_key": "sliced",
      "planner_effect_state_value": "true",
      "planner_action_name": "slice",
      "planner_required_fields": "action,target",
      "planner_fixed_fields": "action=slice",
      "planner_entity_fields": "target",
      "planner_allow_extra_fields": "false",
      "planner_entity_pattern": "alfred_instance",
      "planner_dynamic_entity_rule": "alfred_slice_aliases"
    }
  }
]

理解边界：
1. intent 保留 ALFRED instruction/task_desc 的任务目标，不输出动作序列。
2. required_item_names 必须使用允许实体名中的 AI2THOR 对象实例名，并保留编号格式。
3. 对 ALFRED 复合任务，要按任务语义把目标物、工具/设备、最终容器分别放入 targets/tools/receptacles。
4. skill_closure 只能使用 ALFRED skills root 中启用的 skill，例如 go_to、pick_up、put_down、open、close、turn_on、turn_off、slice。

输出 JSON 结构：
{"is_complete": true, "is_cancel_all": false, "clarification_question": "", "entity_relevance": {"directly_related": [], "indirectly_related": [], "possibly_related": []}, "skill_closure": [], "structured_task": {"intent": "", "required_item_names": {"targets": {"primary": [], "alternatives": []}, "tools": {"primary": [], "alternatives": []}, "receptacles": {"primary": [], "alternatives": []}}, "quantity_constraints": []}}

## Message 2: human

Place a cooked potato slice in the sink
