# Round 1 understanding.system Input

## Message 1: system

任务：把 EAI BEHAVIOR case 输入抽取成结构化任务理解。
只返回 JSON；不要解释，不要输出 Markdown。

允许使用的 BEHAVIOR 场景实体名：
["basket_0", "basket_1", "basket_2", "basket_3", "behavior_room", "behavior_room_anchor", "bow_0", "bow_1", "bow_2", "bow_3", "breakfast_table_13", "candle_0", "candle_1", "candle_2", "candle_3", "cheese_0", "cheese_1", "cheese_2", "cheese_3", "coffee_table_12", "cookie_0", "cookie_1", "cookie_2", "cookie_3", "room_floor_living_room_0"]

BEHAVIOR 任务上下文 JSON：
{
  "dataset": "behavior",
  "instruction": "assembling gift baskets",
  "identifier": "assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37",
  "raw_source": "behavior_initial_env_cache",
  "initial_environment_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/eai/behavior/initial_envs/assembling_gift_baskets_0_Beechwood_0_int_0_2021-10-26_12-46-37.json",
  "initial_environment_source": "igibson_behavior_native_loader",
  "environment_source": "igibson_behavior_native_loader",
  "raw_goal_condition": [
    [
      "forpairs",
      "basket.n.01",
      "-",
      "basket.n.01",
      "candle.n.01",
      "-",
      "candle.n.01",
      "inside",
      "candle.n.01",
      "basket.n.01"
    ],
    [
      "forpairs",
      "basket.n.01",
      "-",
      "basket.n.01",
      "cheese.n.01",
      "-",
      "cheese.n.01",
      "inside",
      "cheese.n.01",
      "basket.n.01"
    ],
    [
      "forpairs",
      "basket.n.01",
      "-",
      "basket.n.01",
      "cookie.n.01",
      "-",
      "cookie.n.01",
      "inside",
      "cookie.n.01",
      "basket.n.01"
    ],
    [
      "forpairs",
      "basket.n.01",
      "-",
      "basket.n.01",
      "bow.n.08",
      "-",
      "bow.n.08",
      "inside",
      "bow.n.08",
      "basket.n.01"
    ]
  ],
  "raw_goal_clauses": [
    "forpairs basket.n.01 - basket.n.01 candle.n.01 - candle.n.01 inside candle.n.01 basket.n.01",
    "forpairs basket.n.01 - basket.n.01 cheese.n.01 - cheese.n.01 inside cheese.n.01 basket.n.01",
    "forpairs basket.n.01 - basket.n.01 cookie.n.01 - cookie.n.01 inside cookie.n.01 basket.n.01",
    "forpairs basket.n.01 - basket.n.01 bow.n.08 - bow.n.08 inside bow.n.08 basket.n.01"
  ],
  "raw_goal_condition_count": 4,
  "name_category": {
    "basket_0": "basket.n.01",
    "basket_1": "basket.n.01",
    "basket_2": "basket.n.01",
    "basket_3": "basket.n.01",
    "room_floor_living_room_0": "floor.n.01",
    "candle_0": "candle.n.01",
    "candle_1": "candle.n.01",
    "candle_2": "candle.n.01",
    "candle_3": "candle.n.01",
    "cookie_0": "cookie.n.01",
    "cookie_1": "cookie.n.01",
    "cookie_2": "cookie.n.01",
    "cookie_3": "cookie.n.01",
    "cheese_0": "cheese.n.01",
    "cheese_1": "cheese.n.01",
    "cheese_2": "cheese.n.01",
    "cheese_3": "cheese.n.01",
    "bow_0": "bow.n.08",
    "bow_1": "bow.n.08",
    "bow_2": "bow.n.08",
    "bow_3": "bow.n.08",
    "breakfast_table_13": "table.n.02",
    "coffee_table_12": "table.n.02",
    "agent.n.01_1": "agent.n.01"
  },
  "available_entities": [
    "basket_0",
    "basket_1",
    "basket_2",
    "basket_3",
    "behavior_room",
    "behavior_room_anchor",
    "bow_0",
    "bow_1",
    "bow_2",
    "bow_3",
    "breakfast_table_13",
    "candle_0",
    "candle_1",
    "candle_2",
    "candle_3",
    "cheese_0",
    "cheese_1",
    "cheese_2",
    "cheese_3",
    "coffee_table_12",
    "cookie_0",
    "cookie_1",
    "cookie_2",
    "cookie_3",
    "room_floor_living_room_0"
  ]
}
任务上下文中的 identifier、instruction、raw_goal_condition、raw_goal_clauses、name_category、initial_environment_cache_path 是本 benchmark 的 grounding；必须保持 BEHAVIOR 目标语义和对象命名。

BEHAVIOR 可用 skill 摘要：
[
  {
    "name": "LEFT_GRASP",
    "description": "Official BEHAVIOR LEFT_GRASP action.",
    "planning_contract": {
      "planner_action_name": "LEFT_GRASP",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=LEFT_GRASP",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RIGHT_GRASP",
    "description": "Official BEHAVIOR RIGHT_GRASP action.",
    "planning_contract": {
      "planner_action_name": "RIGHT_GRASP",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=RIGHT_GRASP",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LEFT_PLACE_ONTOP",
    "description": "Official BEHAVIOR LEFT_PLACE_ONTOP action.",
    "planning_contract": {
      "planner_action_name": "LEFT_PLACE_ONTOP",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=LEFT_PLACE_ONTOP",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RIGHT_PLACE_ONTOP",
    "description": "Official BEHAVIOR RIGHT_PLACE_ONTOP action.",
    "planning_contract": {
      "planner_action_name": "RIGHT_PLACE_ONTOP",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=RIGHT_PLACE_ONTOP",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LEFT_PLACE_INSIDE",
    "description": "Official BEHAVIOR LEFT_PLACE_INSIDE action.",
    "planning_contract": {
      "planner_action_name": "LEFT_PLACE_INSIDE",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=LEFT_PLACE_INSIDE",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RIGHT_PLACE_INSIDE",
    "description": "Official BEHAVIOR RIGHT_PLACE_INSIDE action.",
    "planning_contract": {
      "planner_action_name": "RIGHT_PLACE_INSIDE",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=RIGHT_PLACE_INSIDE",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RIGHT_RELEASE",
    "description": "Official BEHAVIOR RIGHT_RELEASE action.",
    "planning_contract": {
      "planner_action_name": "RIGHT_RELEASE",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=RIGHT_RELEASE",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LEFT_RELEASE",
    "description": "Official BEHAVIOR LEFT_RELEASE action.",
    "planning_contract": {
      "planner_action_name": "LEFT_RELEASE",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=LEFT_RELEASE",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "OPEN",
    "description": "Official BEHAVIOR OPEN action.",
    "planning_contract": {
      "planner_action_name": "OPEN",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=OPEN",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "CLOSE",
    "description": "Official BEHAVIOR CLOSE action.",
    "planning_contract": {
      "planner_action_name": "CLOSE",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=CLOSE",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "COOK",
    "description": "Official BEHAVIOR COOK action.",
    "planning_contract": {
      "planner_action_name": "COOK",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=COOK",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "CLEAN",
    "description": "Official BEHAVIOR CLEAN action.",
    "planning_contract": {
      "planner_action_name": "CLEAN",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=CLEAN",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "FREEZE",
    "description": "Official BEHAVIOR FREEZE action.",
    "planning_contract": {
      "planner_action_name": "FREEZE",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=FREEZE",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "UNFREEZE",
    "description": "Official BEHAVIOR UNFREEZE action.",
    "planning_contract": {
      "planner_action_name": "UNFREEZE",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=UNFREEZE",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "SLICE",
    "description": "Official BEHAVIOR SLICE action.",
    "planning_contract": {
      "planner_action_name": "SLICE",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=SLICE",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false",
      "planner_dynamic_entity_rule": "slice_parts_from_target"
    }
  },
  {
    "name": "SOAK",
    "description": "Official BEHAVIOR SOAK action.",
    "planning_contract": {
      "planner_action_name": "SOAK",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=SOAK",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "DRY",
    "description": "Official BEHAVIOR DRY action.",
    "planning_contract": {
      "planner_action_name": "DRY",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=DRY",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "TOGGLE_ON",
    "description": "Official BEHAVIOR TOGGLE_ON action.",
    "planning_contract": {
      "planner_action_name": "TOGGLE_ON",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=TOGGLE_ON",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "TOGGLE_OFF",
    "description": "Official BEHAVIOR TOGGLE_OFF action.",
    "planning_contract": {
      "planner_action_name": "TOGGLE_OFF",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=TOGGLE_OFF",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LEFT_PLACE_NEXTTO",
    "description": "Official BEHAVIOR LEFT_PLACE_NEXTTO action.",
    "planning_contract": {
      "planner_action_name": "LEFT_PLACE_NEXTTO",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=LEFT_PLACE_NEXTTO",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RIGHT_PLACE_NEXTTO",
    "description": "Official BEHAVIOR RIGHT_PLACE_NEXTTO action.",
    "planning_contract": {
      "planner_action_name": "RIGHT_PLACE_NEXTTO",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=RIGHT_PLACE_NEXTTO",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LEFT_TRANSFER_CONTENTS_INSIDE",
    "description": "Official BEHAVIOR LEFT_TRANSFER_CONTENTS_INSIDE action.",
    "planning_contract": {
      "planner_action_name": "LEFT_TRANSFER_CONTENTS_INSIDE",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=LEFT_TRANSFER_CONTENTS_INSIDE",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RIGHT_TRANSFER_CONTENTS_INSIDE",
    "description": "Official BEHAVIOR RIGHT_TRANSFER_CONTENTS_INSIDE action.",
    "planning_contract": {
      "planner_action_name": "RIGHT_TRANSFER_CONTENTS_INSIDE",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=RIGHT_TRANSFER_CONTENTS_INSIDE",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LEFT_TRANSFER_CONTENTS_ONTOP",
    "description": "Official BEHAVIOR LEFT_TRANSFER_CONTENTS_ONTOP action.",
    "planning_contract": {
      "planner_action_name": "LEFT_TRANSFER_CONTENTS_ONTOP",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=LEFT_TRANSFER_CONTENTS_ONTOP",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RIGHT_TRANSFER_CONTENTS_ONTOP",
    "description": "Official BEHAVIOR RIGHT_TRANSFER_CONTENTS_ONTOP action.",
    "planning_contract": {
      "planner_action_name": "RIGHT_TRANSFER_CONTENTS_ONTOP",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=RIGHT_TRANSFER_CONTENTS_ONTOP",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LEFT_PLACE_NEXTTO_ONTOP",
    "description": "Official BEHAVIOR LEFT_PLACE_NEXTTO_ONTOP action.",
    "planning_contract": {
      "planner_action_name": "LEFT_PLACE_NEXTTO_ONTOP",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=LEFT_PLACE_NEXTTO_ONTOP",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RIGHT_PLACE_NEXTTO_ONTOP",
    "description": "Official BEHAVIOR RIGHT_PLACE_NEXTTO_ONTOP action.",
    "planning_contract": {
      "planner_action_name": "RIGHT_PLACE_NEXTTO_ONTOP",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=RIGHT_PLACE_NEXTTO_ONTOP",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LEFT_PLACE_UNDER",
    "description": "Official BEHAVIOR LEFT_PLACE_UNDER action.",
    "planning_contract": {
      "planner_action_name": "LEFT_PLACE_UNDER",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=LEFT_PLACE_UNDER",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RIGHT_PLACE_UNDER",
    "description": "Official BEHAVIOR RIGHT_PLACE_UNDER action.",
    "planning_contract": {
      "planner_action_name": "RIGHT_PLACE_UNDER",
      "planner_required_fields": "action,object",
      "planner_fixed_fields": "action=RIGHT_PLACE_UNDER",
      "planner_entity_fields": "object",
      "planner_allow_comma_separated_entities": "true",
      "planner_allow_extra_fields": "false"
    }
  }
]

理解边界：
1. intent 保留 BEHAVIOR instruction 和 raw_goal_condition 表达的目标，不输出动作序列。
2. required_item_names 必须使用允许实体名或 name_category 中映射出的真实对象名；synset/category 只能作为类型线索，不能当实体名。
3. raw_goal_condition 是目标依据；关系目标 inside/ontop/under/nextto 和状态目标 cooked/clean/frozen/open 等要保留在 intent/quantity_constraints 中。
4. skill_closure 只能使用 BEHAVIOR skills root 中启用的 skill，例如 LEFT_GRASP、RIGHT_GRASP、LEFT_PLACE_ONTOP、RIGHT_PLACE_INSIDE、OPEN、CLOSE、COOK、CLEAN、FREEZE、SLICE、SOAK、DRY、TOGGLE_ON、TOGGLE_OFF。

输出 JSON 结构：
{"is_complete": true, "is_cancel_all": false, "clarification_question": "", "entity_relevance": {"directly_related": [], "indirectly_related": [], "possibly_related": []}, "skill_closure": [], "structured_task": {"intent": "", "required_item_names": {"targets": {"primary": [], "alternatives": []}, "tools": {"primary": [], "alternatives": []}, "receptacles": {"primary": [], "alternatives": []}}, "quantity_constraints": []}}

## Message 2: human

assembling gift baskets
