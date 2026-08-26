# Round 4 planning.state_diff_audit Input

## Message 1: human

任务：根据 VirtualHome sandbox 前后状态差异判断任务是否完成。
只输出 JSON；不要解释，不要生成动作。

任务目标：Relax on sofa

完整 native action 计划摘要：
[
  {
    "action": "WALK",
    "args": [
      "couch"
    ]
  },
  {
    "action": "SIT",
    "args": [
      "couch"
    ]
  }
]

本轮实际模拟步骤：
[
  {
    "action": "WALK",
    "args": [
      "couch"
    ]
  },
  {
    "action": "SIT",
    "args": [
      "couch"
    ]
  }
]

轨迹摘要：
Step 1: WALK(['couch'])
Step 2: SIT(['couch'])

VirtualHome 状态差异 JSON：
{
  "entity_count_compared": 8,
  "changed_entity_count": 0,
  "truncated_entity_count": 0,
  "has_changes": true,
  "robot": {
    "changed": true,
    "before": {
      "robot_location": "bedroom_anchor",
      "robot_holding": "空",
      "robot_hands": {
        "left": "空",
        "right": "空"
      },
      "manipulator_mode": "dual_arm"
    },
    "after": {
      "robot_location": "couch",
      "robot_holding": "空",
      "robot_hands": {
        "left": "空",
        "right": "空"
      },
      "manipulator_mode": "dual_arm",
      "posture": "sitting",
      "isSleeping": false,
      "last_seat": "couch"
    }
  },
  "entities": []
}

状态审计上下文 JSON：
{
  "entity_count_available": 8,
  "entity_count_in_context": 4,
  "truncated_entity_count": 0,
  "note": "state_diff only lists changed entities; unchanged entities in this context still prove final goal state when their after state satisfies the task.",
  "robot": {
    "changed": true,
    "before": {
      "robot_location": "bedroom_anchor",
      "robot_holding": "空",
      "robot_hands": {
        "left": "空",
        "right": "空"
      },
      "manipulator_mode": "dual_arm"
    },
    "after": {
      "robot_location": "couch",
      "robot_holding": "空",
      "robot_hands": {
        "left": "空",
        "right": "空"
      },
      "manipulator_mode": "dual_arm",
      "posture": "sitting",
      "isSleeping": false,
      "last_seat": "couch"
    }
  },
  "entities": [
    {
      "name": "couch",
      "changed": false,
      "before": {
        "type": "receptacle",
        "direct_parent": "mat_401",
        "direct_relation": "ontop",
        "is_container": true,
        "full_path": [
          "home_office",
          "home_office_anchor",
          "mat_401"
        ],
        "states": {
          "isClean": true,
          "isDirty": false
        },
        "properties": [
          "SITTABLE",
          "MOVABLE",
          "SURFACES",
          "LIEABLE"
        ]
      },
      "after": {
        "type": "receptacle",
        "direct_parent": "mat_401",
        "direct_relation": "ontop",
        "is_container": true,
        "full_path": [
          "home_office",
          "home_office_anchor",
          "mat_401"
        ],
        "states": {
          "isClean": true,
          "isDirty": false
        },
        "properties": [
          "SITTABLE",
          "MOVABLE",
          "SURFACES",
          "LIEABLE"
        ]
      }
    },
    {
      "name": "mat_401",
      "changed": false,
      "before": {
        "type": "receptacle",
        "direct_parent": "home_office_anchor",
        "direct_relation": "inside",
        "is_container": true,
        "full_path": [
          "home_office",
          "home_office_anchor"
        ],
        "states": {
          "isDirty": true,
          "isClean": false
        },
        "properties": [
          "GRABBABLE",
          "SURFACES",
          "MOVABLE",
          "SITTABLE",
          "LIEABLE"
        ]
      },
      "after": {
        "type": "receptacle",
        "direct_parent": "home_office_anchor",
        "direct_relation": "inside",
        "is_container": true,
        "full_path": [
          "home_office",
          "home_office_anchor"
        ],
        "states": {
          "isDirty": true,
          "isClean": false
        },
        "properties": [
          "GRABBABLE",
          "SURFACES",
          "MOVABLE",
          "SITTABLE",
          "LIEABLE"
        ]
      }
    },
    {
      "name": "home_office_anchor",
      "changed": false,
      "before": {
        "type": "receptacle",
        "direct_parent": "home_office",
        "direct_relation": "inside",
        "is_container": true,
        "full_path": [
          "home_office"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": "receptacle",
        "direct_parent": "home_office",
        "direct_relation": "inside",
        "is_container": true,
        "full_path": [
          "home_office"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "home_office",
      "changed": false,
      "before": {
        "type": "room",
        "direct_parent": "未知环境",
        "direct_relation": null,
        "is_container": false,
        "full_path": [],
        "states": {},
        "properties": []
      },
      "after": {
        "type": "room",
        "direct_parent": "未知环境",
        "direct_relation": null,
        "is_container": false,
        "full_path": [],
        "states": {},
        "properties": []
      }
    }
  ],
  "task_context": {
    "dataset": "virtualhome",
    "instruction": "Relax on sofa",
    "identifier": "3_1",
    "raw_source": "virtualhome_initial_env_cache",
    "initial_environment_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/eai/virtualhome/initial_envs/3_1.json",
    "initial_environment_source": "virtualhome_original_init_graph",
    "environment_source": "virtualhome_original_init_graph",
    "pddl_objects": [
      "character",
      "couch",
      "bedroom",
      "home_office",
      "television"
    ],
    "pddl_goal": [
      [
        "sitting",
        "character"
      ],
      [
        "ontop",
        "character",
        "couch"
      ]
    ],
    "pddl_goal_clauses": [
      "sitting character",
      "ontop character couch"
    ],
    "pddl_goal_hints": [
      "sitting character",
      "ontop character couch"
    ],
    "external_goal_text": "sitting character; ontop character couch",
    "goal_hand_targets": {},
    "pddl_goal_count": 2,
    "available_entities": [
      "bathroom",
      "bathroom_anchor",
      "bathroom_cabinet",
      "bathroom_counter",
      "bathtub",
      "bed",
      "bedroom",
      "bedroom_anchor",
      "bench_227",
      "bench_228",
      "bookshelf_101",
      "bookshelf_233",
      "bookshelf_354",
      "ceiling_16",
      "ceiling_17",
      "ceiling_18",
      "ceiling_19",
      "ceiling_20",
      "ceiling_21",
      "ceiling_216",
      "ceiling_217",
      "ceiling_218",
      "ceiling_219",
      "ceiling_220",
      "ceiling_221",
      "ceiling_337",
      "ceiling_338",
      "ceiling_339",
      "ceiling_340",
      "ceiling_341",
      "ceiling_342",
      "ceiling_343",
      "ceiling_344",
      "ceiling_345",
      "ceiling_87",
      "ceiling_88",
      "ceiling_89",
      "ceiling_90",
      "ceiling_91",
      "ceiling_92",
      "ceiling_93",
      "ceiling_94",
      "ceiling_95",
      "ceilinglamp_223",
      "ceilinglamp_224",
      "ceilinglamp_26",
      "ceilinglamp_349",
      "ceilinglamp_96",
      "chair_103",
      "chair_106",
      "chair_2013",
      "chair_356",
      "check_2007",
      "check_2011",
      "closetdrawer_116",
      "closetdrawer_117",
      "closetdrawer_118",
      "closetdrawer_119",
      "closetdrawer_120",
      "closetdrawer_121",
      "closetdrawer_122",
      "closetdrawer_143",
      "closetdrawer_146",
      "closetdrawer_148",
      "closetdrawer_150",
      "closetdrawer_154",
      "closetdrawer_158",
      "closetdrawer_160",
      "closetdrawer_377",
      "closetdrawer_380",
      "closetdrawer_382",
      "closetdrawer_384",
      "closetdrawer_388",
      "closetdrawer_392",
      "closetdrawer_394",
      "coffe_maker",
      "colander",
      "computer_170",
      "computer_417",
      "couch",
      "cpuscreen_171",
      "cpuscreen_416",
      "cup_2002",
      "cup_2012",
      "cupboard",
      "curtain_181",
      "curtain_23",
      "curtain_24",
      "curtain_25",
      "curtain_39",
      "curtain_407",
      "curtain_408",
      "curtain_409",
      "desk_104",
      "desk_357",
      "dining_room",
      "dining_room_anchor",
      "dirt",
      "door_222",
      "door_44",
      "doorjamb_165",
      "doorjamb_346",
      "doorjamb_347",
      "doorjamb_45",
      "drawing_174",
      "drawing_175",
      "drawing_176",
      "drawing_238",
      "drawing_239",
      "drawing_240",
      "drawing_241",
      "drawing_242",
      "drawing_243",
      "drawing_400",
      "drawing_402",
      "drawing_403",
      "drawing_404",
      "dresser_108",
      "dresser_123",
      "dresser_358",
      "dustpan",
      "envelope",
      "faucet_232",
      "faucet_43",
      "filing_cabinet",
      "floor_2",
      "floor_202",
      "floor_203",
      "floor_204",
      "floor_205",
      "floor_206",
      "floor_207",
      "floor_208",
      "floor_3",
      "floor_320",
      "floor_321",
      "floor_322",
      "floor_323",
      "floor_324",
      "floor_325",
      "floor_326",
      "floor_327",
      "floor_328",
      "floor_4",
      "floor_5",
      "floor_6",
      "floor_68",
      "floor_69",
      "floor_7",
      "floor_70",
      "floor_71",
      "floor_72",
      "floor_73",
      "floor_74",
      "floor_75",
      "floor_76",
      "floor_77",
      "floor_8",
      "food_food",
      "food_pizza",
      "freezer",
      "hanger_109",
      "hanger_110",
      "hanger_111",
      "hanger_112",
      "hanger_113",
      "hanger_114",
      "hanger_115",
      "hanger_124",
      "hanger_126",
      "hanger_128",
      "hanger_130",
      "hanger_132",
      "hanger_134",
      "hanger_136",
      "hanger_138",
      "hanger_140",
      "hanger_141",
      "hanger_142",
      "hanger_359",
      "hanger_361",
      "hanger_363",
      "hanger_365",
      "hanger_367",
      "hanger_369",
      "hanger_372",
      "hanger_374",
      "hanger_375",
      "hanger_376",
      "home_office",
      "home_office_anchor",
      "keyboard_168",
      "keyboard_415",
      "kitchen_counter",
      "laundry_detergent",
      "light_169",
      "light_245",
      "light_411",
      "light_64",
      "mat_173",
      "mat_22",
      "mat_236",
      "mat_237",
      "mat_401",
      "microwave",
      "mop",
      "mouse_166",
      "mouse_413",
      "mousepad_167",
      "mousepad_414",
      "nightstand_100",
      "nightstand_102",
      "orchid_178",
      "orchid_244",
      "oven",
      "phone",
      "photoframe_185",
      "photoframe_285",
      "photoframe_430",
      "pillow_182",
      "pillow_183",
      "pillow_2008",
      "pillow_405",
      "pillow_406",
      "pot",
      "powersocket_246",
      "powersocket_412",
      "rag",
      "shower_36",
      "shower_38",
      "sink_231",
      "sink_42",
      "spoon",
      "stovefan",
      "table_107",
      "table_226",
      "table_355",
      "tablelamp_97",
      "tablelamp_98",
      "television",
      "television_248",
      "toaster",
      "toilet",
      "towel_rack_31",
      "towel_rack_32",
      "towel_rack_33",
      "towel_rack_34",
      "trashcan",
      "tray",
      "tvstand_225",
      "tvstand_353",
      "wall_10",
      "wall_11",
      "wall_12",
      "wall_13",
      "wall_14",
      "wall_15",
      "wall_209",
      "wall_210",
      "wall_211",
      "wall_212",
      "wall_213",
      "wall_214",
      "wall_215",
      "wall_329",
      "wall_330",
      "wall_331",
      "wall_332",
      "wall_333",
      "wall_334",
      "wall_335",
      "wall_336",
      "wall_78",
      "wall_79",
      "wall_80",
      "wall_81",
      "wall_82",
      "wall_83",
      "wall_84",
      "wall_85",
      "wall_9",
      "wall_clock",
      "walllamp_27",
      "walllamp_28",
      "walllamp_29",
      "walllamp_350",
      "walllamp_351",
      "wallshelf_234",
      "wallshelf_235",
      "wallshelf_35",
      "window_348",
      "window_63",
      "window_86"
    ]
  },
  "evaluation_context": {},
  "external_goal": {
    "has_external_goal": true,
    "external_goal_state": {},
    "external_goal_text": "sitting character; ontop character couch",
    "structured_goal_state": {},
    "structured_final_state": {
      "character": {
        "sitting": true,
        "ontop": "couch"
      }
    }
  },
  "benchmark_final_state_compare": {
    "benchmark": "EAI-VirtualHome",
    "status": "prepared_for_framework_llm_judge",
    "environment_format": "VirtualHome initial_env_cache graph 转成 benchmark 本地房间/对象状态图",
    "action_format": "VirtualHome 官方 action sequencing 原生动作 JSON 对象：{action, args}",
    "official_evaluator": "EAI VirtualHome action_sequencing evaluator，执行符号图状态模拟",
    "used_fields": {
      "task_context": [
        "dataset",
        "environment_source",
        "external_goal_text",
        "identifier",
        "initial_environment_cache_path",
        "initial_environment_source",
        "instruction",
        "pddl_goal",
        "pddl_goal_clauses",
        "pddl_goal_count",
        "pddl_goal_hints",
        "pddl_objects",
        "raw_source"
      ],
      "evaluation_context": [],
      "external_goal": [
        "external_goal_text",
        "has_external_goal",
        "structured_final_state"
      ],
      "state_diff": [
        "entities",
        "robot"
      ]
    },
    "benchmark_goal": {
      "task_context": {
        "dataset": "virtualhome",
        "instruction": "Relax on sofa",
        "identifier": "3_1",
        "raw_source": "virtualhome_initial_env_cache",
        "initial_environment_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/eai/virtualhome/initial_envs/3_1.json",
        "initial_environment_source": "virtualhome_original_init_graph",
        "environment_source": "virtualhome_original_init_graph",
        "pddl_objects": [
          "character",
          "couch",
          "bedroom",
          "home_office",
          "television"
        ],
        "pddl_goal": [
          [
            "sitting",
            "character"
          ],
          [
            "ontop",
            "character",
            "couch"
          ]
        ],
        "pddl_goal_clauses": [
          "sitting character",
          "ontop character couch"
        ],
        "pddl_goal_hints": [
          "sitting character",
          "ontop character couch"
        ],
        "external_goal_text": "sitting character; ontop character couch",
        "pddl_goal_count": 2
      },
      "evaluation_context": {},
      "goal_projection": {},
      "external_goal": {
        "has_external_goal": true,
        "external_goal_state": {},
        "external_goal_text": "sitting character; ontop character couch",
        "structured_goal_state": {},
        "structured_final_state": {
          "character": {
            "sitting": true,
            "ontop": "couch"
          }
        }
      }
    },
    "understanding_final_state": {
      "character": {
        "sitting": true,
        "ontop": "couch"
      }
    },
    "state_diff_summary": {
      "entity_count_compared": 8,
      "changed_entity_count": 0,
      "changed_entities": [],
      "changed_entities_truncated": false,
      "robot_changed": true,
      "robot_change": {
        "changed": true,
        "before": {
          "robot_location": "bedroom_anchor",
          "robot_holding": "空",
          "robot_hands": {
            "left": "空",
            "right": "空"
          },
          "manipulator_mode": "dual_arm"
        },
        "after": {
          "robot_location": "couch",
          "robot_holding": "空",
          "robot_hands": {
            "left": "空",
            "right": "空"
          },
          "manipulator_mode": "dual_arm",
          "posture": "sitting",
          "isSleeping": false,
          "last_seat": "couch"
        }
      }
    },
    "initial_environment_summary": {
      "available": true,
      "entity_count": 8,
      "type_counts": {
        "receptacle": 4,
        "room": 4
      },
      "states_sample": {
        "couch": {
          "isClean": true,
          "isDirty": false
        },
        "mat_401": {
          "isDirty": true,
          "isClean": false
        }
      },
      "relations_sample": {
        "couch": {
          "direct_relation": "ontop",
          "direct_parent": "mat_401"
        },
        "home_office": {
          "direct_relation": "",
          "direct_parent": "未知环境"
        },
        "home_office_anchor": {
          "direct_relation": "inside",
          "direct_parent": "home_office"
        },
        "mat_401": {
          "direct_relation": "inside",
          "direct_parent": "home_office_anchor"
        },
        "bedroom_anchor": {
          "direct_relation": "inside",
          "direct_parent": "bedroom"
        },
        "bedroom": {
          "direct_relation": "",
          "direct_parent": "未知环境"
        },
        "bathroom": {
          "direct_relation": "",
          "direct_parent": "未知环境"
        },
        "dining_room": {
          "direct_relation": "",
          "direct_parent": "未知环境"
        }
      }
    },
    "final_environment_summary": {
      "available": true,
      "entity_count": 8,
      "type_counts": {
        "receptacle": 4,
        "room": 4
      },
      "states_sample": {
        "couch": {
          "isClean": true,
          "isDirty": false
        },
        "mat_401": {
          "isDirty": true,
          "isClean": false
        }
      },
      "relations_sample": {
        "couch": {
          "direct_relation": "ontop",
          "direct_parent": "mat_401"
        },
        "home_office": {
          "direct_relation": "",
          "direct_parent": "未知环境"
        },
        "home_office_anchor": {
          "direct_relation": "inside",
          "direct_parent": "home_office"
        },
        "mat_401": {
          "direct_relation": "inside",
          "direct_parent": "home_office_anchor"
        },
        "bedroom_anchor": {
          "direct_relation": "inside",
          "direct_parent": "bedroom"
        },
        "bedroom": {
          "direct_relation": "",
          "direct_parent": "未知环境"
        },
        "bathroom": {
          "direct_relation": "",
          "direct_parent": "未知环境"
        },
        "dining_room": {
          "direct_relation": "",
          "direct_parent": "未知环境"
        }
      }
    },
    "initial_robot": {
      "robot_location": "bedroom_anchor",
      "robot_holding": "空",
      "robot_hands": {
        "left": "空",
        "right": "空"
      },
      "manipulator_mode": "dual_arm"
    },
    "final_robot": {
      "robot_location": "couch",
      "robot_holding": "空",
      "robot_hands": {
        "left": "空",
        "right": "空"
      },
      "manipulator_mode": "dual_arm",
      "posture": "sitting",
      "isSleeping": false,
      "last_seat": "couch"
    },
    "fairness_notes": [
      "pddl_goal 是 EAI case 输入中的公开目标约束；最终态审计按该目标和 sandbox diff 判断，不对比文字答案。"
    ],
    "judge_contract": "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。",
    "enabled": true,
    "comparer_module": "benchmark.eai.virtualhome.framework.code.final_state"
  }
}

判定边界：
1. 优先读取 state_audit_context.benchmark_final_state_compare；其中包含 VirtualHome PDDL 目标投影和本地环境差异摘要。
2. 结合 understanding final_state、pddl_goal/external_goal_text、sandbox final environment/final robot 和 state_diff 判断关键目标是否完成。
3. 不使用人工动作序列答案；保持 VirtualHome 原生动作和图状态语义。
4. 如果关键目标缺失，is_passed=false，并写出缺失的最终状态和后续 planning 应补的动作类型。
5. 如果当前最终态只需追加动作即可修复，repair_mode="continue_from_current"；如果已验证前缀本身错，repair_mode="reset_and_replan"。

输出 JSON：
{"is_passed": true, "issue": "", "fix_advice": "", "repair_mode": "continue_from_current", "accepted_diffs": [], "unexpected_diffs": []}
