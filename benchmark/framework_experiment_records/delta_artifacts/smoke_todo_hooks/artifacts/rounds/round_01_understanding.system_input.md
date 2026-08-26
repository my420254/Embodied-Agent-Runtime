# Round 1 understanding.system Input

## Message 1: system

任务：把 DELTA benchmark case 输入抽取成结构化任务理解。
只返回 JSON；不要解释，不要输出 Markdown。

允许使用的 DELTA 场景实体名：
["banana_peel", "bathroom_1", "bathroom_2", "bed_1", "bed_2", "bedroom_1", "bedroom_2", "book", "bowl_2", "bowl_3", "chair_1", "chair_2", "chair_3", "chair_4", "chair_5", "clock", "cola_can", "corridor_1", "corridor_2", "corridor_3", "couch", "cpu", "desk", "dining_room", "dining_table", "flower", "fork", "fridge_1", "fridge_2", "fridge_3", "glass", "gpu", "kitchen", "knife", "lamp", "living_room", "lobby", "locker", "mainboard", "microwave", "mop", "oven", "paper", "plant_1", "plant_2", "plate", "psu", "ram", "robot_hub", "rotting_apple", "rubbish_bin", "shelf", "sink_1", "sink_2", "spoon", "ssd", "toilet_1", "toilet_2"]

DELTA 任务上下文 JSON：
{
  "dataset": "delta",
  "task_name": "dining:allensville:episode-01",
  "domain": "dining",
  "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
  "task_source": "delta_data_example_py",
  "environment_source": "delta_data_scene_graph_py",
  "scene_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json",
  "delta_add_obj_types": [],
  "delta_env_state_predicates": [
    "item_on(<item_1>, <item_2>): <item_1> is on <item_2>.",
    "item_is_dining_table(<item>): <item> is dining_table."
  ],
  "delta_initial_predicates": [
    "item_is_dining_table dining_table",
    "item_pickable plate",
    "item_accessible plate",
    "item_pickable fork",
    "item_accessible fork",
    "item_pickable knife",
    "item_accessible knife",
    "item_pickable spoon",
    "item_accessible spoon",
    "item_pickable glass",
    "item_accessible glass",
    "item_pickable flower",
    "item_accessible flower"
  ],
  "delta_room_neighbors": {
    "bathroom_1": [
      "corridor_2"
    ],
    "bathroom_2": [
      "corridor_3"
    ],
    "bedroom_1": [
      "corridor_2"
    ],
    "bedroom_2": [
      "corridor_3"
    ],
    "corridor_1": [
      "lobby",
      "corridor_3"
    ],
    "corridor_2": [
      "bathroom_1",
      "bedroom_1",
      "corridor_3"
    ],
    "corridor_3": [
      "corridor_1",
      "corridor_2",
      "bathroom_2",
      "bedroom_2",
      "kitchen",
      "living_room"
    ],
    "dining_room": [
      "kitchen",
      "living_room"
    ],
    "kitchen": [
      "corridor_3",
      "dining_room"
    ],
    "living_room": [
      "corridor_3",
      "dining_room"
    ],
    "lobby": [
      "corridor_1"
    ]
  },
  "delta_accessible_items": [
    "psu",
    "sink_1",
    "mop",
    "gpu",
    "sink_2",
    "mainboard",
    "glass",
    "shelf",
    "book",
    "cpu",
    "rotting_apple",
    "plate",
    "lamp",
    "fridge_1",
    "fridge_2",
    "ssd",
    "cola_can",
    "dining_table",
    "knife",
    "fork",
    "spoon",
    "microwave",
    "oven",
    "rubbish_bin",
    "fridge_3",
    "desk",
    "bowl_2",
    "bowl_3",
    "robot_hub",
    "ram",
    "banana_peel",
    "flower",
    "locker",
    "paper"
  ],
  "loadable_containers": [
    {
      "name": "shelf",
      "room": "bedroom_1",
      "is_loaded": true,
      "contents": [
        "book"
      ],
      "affordances": [
        "drop",
        "load",
        "pick",
        "unload"
      ]
    },
    {
      "name": "locker",
      "room": "lobby",
      "is_loaded": true,
      "contents": [
        "paper"
      ],
      "affordances": [
        "drop",
        "load",
        "pick",
        "unload"
      ]
    }
  ],
  "task_environment_mode": "understanding_pruned",
  "available_entities": [
    "banana_peel",
    "bathroom_1",
    "bathroom_2",
    "bed_1",
    "bed_2",
    "bedroom_1",
    "bedroom_2",
    "book",
    "bowl_2",
    "bowl_3",
    "chair_1",
    "chair_2",
    "chair_3",
    "chair_4",
    "chair_5",
    "clock",
    "cola_can",
    "corridor_1",
    "corridor_2",
    "corridor_3",
    "couch",
    "cpu",
    "desk",
    "dining_room",
    "dining_table",
    "flower",
    "fork",
    "fridge_1",
    "fridge_2",
    "fridge_3",
    "glass",
    "gpu",
    "kitchen",
    "knife",
    "lamp",
    "living_room",
    "lobby",
    "locker",
    "mainboard",
    "microwave",
    "mop",
    "oven",
    "paper",
    "plant_1",
    "plant_2",
    "plate",
    "psu",
    "ram",
    "robot_hub",
    "rotting_apple",
    "rubbish_bin",
    "shelf",
    "sink_1",
    "sink_2",
    "spoon",
    "ssd",
    "toilet_1",
    "toilet_2"
  ]
}
任务上下文中的 domain、scene_name、delta_env_state、delta_add_obj_types、delta_accessible_items、delta_env_state_predicates 是本 benchmark 的 grounding 材料；不要把它们改写成其他 benchmark 的字段。

DELTA 可用 skill 摘要：
[
  {
    "name": "goto",
    "description": "DELTA official executable goto action.",
    "planning_contract": {
      "planner_location_param": "to",
      "planner_action_name": "goto",
      "planner_required_fields": "action,agent,room_1,room_2",
      "planner_fixed_fields": "action=goto;agent=robot",
      "planner_room_fields": "room_1,room_2",
      "planner_context_field": "domain",
      "planner_context_values": "clean,dining,office,pc",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "pick",
    "description": "DELTA official executable pick action.",
    "planning_contract": {
      "planner_item_param": "item",
      "planner_requires_empty_hand": "true",
      "planner_action_name": "pick",
      "planner_required_fields": "action,agent,item,room",
      "planner_fixed_fields": "action=pick;agent=robot",
      "planner_entity_fields": "item",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "clean,dining,office,pc",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "drop",
    "description": "DELTA official executable drop action.",
    "planning_contract": {
      "planner_item_param": "item",
      "planner_destination_param": "room",
      "planner_action_name": "drop",
      "planner_required_fields": "action,agent,item,room",
      "planner_fixed_fields": "action=drop;agent=robot",
      "planner_entity_fields": "item",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "clean,dining,office,pc",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "place_on",
    "description": "DELTA official executable place_on action.",
    "planning_contract": {
      "planner_item_param": "item",
      "planner_destination_param": "surface",
      "planner_action_name": "place_on",
      "planner_required_fields": "action,agent,item_1,item_2,room",
      "planner_fixed_fields": "action=place_on;agent=robot",
      "planner_entity_fields": "item_1,item_2",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "dining",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "dispose",
    "description": "DELTA official executable dispose action.",
    "planning_contract": {
      "planner_item_param": "item",
      "planner_destination_param": "disposal",
      "planner_effect_state_key": "isDisposed",
      "planner_effect_state_value": "true",
      "planner_action_name": "dispose",
      "planner_required_fields": "action,agent,item_1,item_2,room",
      "planner_fixed_fields": "action=dispose;agent=robot",
      "planner_entity_fields": "item_1,item_2",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "clean",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "mop_floor",
    "description": "DELTA official executable mop_floor action.",
    "planning_contract": {
      "planner_location_param": "room",
      "planner_effect_state_key": "floor_clean",
      "planner_effect_state_value": "true",
      "planner_action_name": "mop_floor",
      "planner_required_fields": "action,agent,item,room",
      "planner_fixed_fields": "action=mop_floor;agent=robot",
      "planner_entity_fields": "item",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "clean",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "clean_mop",
    "description": "DELTA official executable clean_mop action.",
    "planning_contract": {
      "planner_item_param": "tool",
      "planner_location_param": "water_source",
      "planner_effect_state_key": "isClean",
      "planner_effect_state_value": "true",
      "planner_action_name": "clean_mop",
      "planner_required_fields": "action,agent,item_1,item_2,room",
      "planner_fixed_fields": "action=clean_mop;agent=robot",
      "planner_entity_fields": "item_1,item_2",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "clean",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "charge",
    "description": "DELTA official executable charge action.",
    "planning_contract": {
      "planner_location_param": "station",
      "planner_requires_empty_hand": "true",
      "planner_effect_state_key": "battery_full",
      "planner_effect_state_value": "true",
      "planner_action_name": "charge",
      "planner_required_fields": "action,agent,item,room",
      "planner_fixed_fields": "action=charge;agent=robot",
      "planner_entity_fields": "item",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "clean",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "assemble",
    "description": "DELTA official executable assemble action.",
    "planning_contract": {
      "planner_target_param": "target_pc",
      "planner_location_param": "room",
      "planner_requires_empty_hand": "true",
      "planner_effect_state_key": "isAssembled",
      "planner_effect_state_value": "true",
      "planner_action_name": "assemble",
      "planner_required_fields": "action,agent,room,item_1,item_2,item_3,item_4,item_5,item_6,pc",
      "planner_fixed_fields": "action=assemble;agent=robot",
      "planner_entity_fields": "item_1,item_2,item_3,item_4,item_5,item_6",
      "planner_room_fields": "room",
      "planner_unchecked_fields": "pc",
      "planner_context_field": "domain",
      "planner_context_values": "pc",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "pick_loadable",
    "description": "DELTA official executable pick_loadable action.",
    "planning_contract": {
      "planner_item_param": "item",
      "planner_requires_empty_hand": "true",
      "planner_action_name": "pick_loadable",
      "planner_required_fields": "action,agent,item,room",
      "planner_fixed_fields": "action=pick_loadable;agent=robot",
      "planner_entity_fields": "item",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "office",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "drop_loadable",
    "description": "DELTA official executable drop_loadable action.",
    "planning_contract": {
      "planner_item_param": "item",
      "planner_destination_param": "room",
      "planner_action_name": "drop_loadable",
      "planner_required_fields": "action,agent,item,room",
      "planner_fixed_fields": "action=drop_loadable;agent=robot",
      "planner_entity_fields": "item",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "office",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "load",
    "description": "DELTA official executable load action.",
    "planning_contract": {
      "planner_item_param": "item",
      "planner_destination_param": "loadable",
      "planner_action_name": "load",
      "planner_required_fields": "action,agent,item_1,item_2,room",
      "planner_fixed_fields": "action=load;agent=robot",
      "planner_entity_fields": "item_1,item_2",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "office",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "unload",
    "description": "DELTA official executable unload action.",
    "planning_contract": {
      "planner_item_param": "item",
      "planner_destination_param": "room",
      "planner_action_name": "unload",
      "planner_required_fields": "action,agent,item_1,item_2,room",
      "planner_fixed_fields": "action=unload;agent=robot",
      "planner_entity_fields": "item_1,item_2",
      "planner_room_fields": "room",
      "planner_context_field": "domain",
      "planner_context_values": "office",
      "planner_allow_extra_fields": "false"
    }
  }
]

理解边界：
1. intent 保留 DELTA 原始任务目标，不生成动作序列。
2. required_item_names 必须使用允许实体名或 DELTA 任务上下文中的完整实体名；房间、物体、工具和充电/清洁设施不能混用类型。
3. required_item_names 的角色必须与 DELTA 任务上下文和可用 skill 参数类型一致；不要把非房间实体放进房间类角色。
4. skill_closure 只能使用 DELTA skills root 中启用的 skill 名，例如 goto、pick、dispose、mop_floor、clean_mop、charge。
5. 如果原始任务要求多个同类实例或多个位置，primary 必须列出不同真实实体，quantity_constraints 记录数量。

输出 JSON 结构：
{"is_complete": true, "is_cancel_all": false, "clarification_question": "", "entity_relevance": {"directly_related": [], "indirectly_related": [], "possibly_related": []}, "skill_closure": [], "structured_task": {"intent": "", "required_item_names": {"targets": {"primary": [], "alternatives": []}, "tools": {"primary": [], "alternatives": []}, "receptacles": {"primary": [], "alternatives": []}}, "quantity_constraints": []}}

## Message 2: human

Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.
