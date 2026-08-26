# Round 1 understanding.system Input

## Message 1: system

任务：把 EAI VirtualHome case 输入抽取成结构化任务理解。
只返回 JSON；不要解释，不要输出 Markdown。

允许使用的 VirtualHome 场景实体名：
["bathroom", "bathroom_anchor", "bathroom_cabinet", "bathroom_counter", "bathtub", "bed", "bedroom", "bedroom_anchor", "bench_227", "bench_228", "bookshelf_101", "bookshelf_233", "bookshelf_354", "ceiling_16", "ceiling_17", "ceiling_18", "ceiling_19", "ceiling_20", "ceiling_21", "ceiling_216", "ceiling_217", "ceiling_218", "ceiling_219", "ceiling_220", "ceiling_221", "ceiling_337", "ceiling_338", "ceiling_339", "ceiling_340", "ceiling_341", "ceiling_342", "ceiling_343", "ceiling_344", "ceiling_345", "ceiling_87", "ceiling_88", "ceiling_89", "ceiling_90", "ceiling_91", "ceiling_92", "ceiling_93", "ceiling_94", "ceiling_95", "ceilinglamp_223", "ceilinglamp_224", "ceilinglamp_26", "ceilinglamp_349", "ceilinglamp_96", "chair_103", "chair_106", "chair_2013", "chair_356", "check_2007", "check_2011", "closetdrawer_116", "closetdrawer_117", "closetdrawer_118", "closetdrawer_119", "closetdrawer_120", "closetdrawer_121", "closetdrawer_122", "closetdrawer_143", "closetdrawer_146", "closetdrawer_148", "closetdrawer_150", "closetdrawer_154", "closetdrawer_158", "closetdrawer_160", "closetdrawer_377", "closetdrawer_380", "closetdrawer_382", "closetdrawer_384", "closetdrawer_388", "closetdrawer_392", "closetdrawer_394", "coffe_maker", "colander", "computer_170", "computer_417", "couch", "cpuscreen_171", "cpuscreen_416", "cup_2002", "cup_2012", "cupboard", "curtain_181", "curtain_23", "curtain_24", "curtain_25", "curtain_39", "curtain_407", "curtain_408", "curtain_409", "desk_104", "desk_357", "dining_room", "dining_room_anchor", "dirt", "door_222", "door_44", "doorjamb_165", "doorjamb_346", "doorjamb_347", "doorjamb_45", "drawing_174", "drawing_175", "drawing_176", "drawing_238", "drawing_239", "drawing_240", "drawing_241", "drawing_242", "drawing_243", "drawing_400", "drawing_402", "drawing_403", "drawing_404", "dresser_108", "dresser_123", "dresser_358", "dustpan", "envelope", "faucet_232", "faucet_43", "filing_cabinet", "floor_2", "floor_202", "floor_203", "floor_204", "floor_205", "floor_206", "floor_207", "floor_208", "floor_3", "floor_320", "floor_321", "floor_322", "floor_323", "floor_324", "floor_325", "floor_326", "floor_327", "floor_328", "floor_4", "floor_5", "floor_6", "floor_68", "floor_69", "floor_7", "floor_70", "floor_71", "floor_72", "floor_73", "floor_74", "floor_75", "floor_76", "floor_77", "floor_8", "food_food", "food_pizza", "freezer", "hanger_109", "hanger_110", "hanger_111", "hanger_112", "hanger_113", "hanger_114", "hanger_115", "hanger_124", "hanger_126", "hanger_128", "hanger_130", "hanger_132", "hanger_134", "hanger_136", "hanger_138", "hanger_140", "hanger_141", "hanger_142", "hanger_359", "hanger_361", "hanger_363", "hanger_365", "hanger_367", "hanger_369", "hanger_372", "hanger_374", "hanger_375", "hanger_376", "home_office", "home_office_anchor", "keyboard_168", "keyboard_415", "kitchen_counter", "laundry_detergent", "light_169", "light_245", "light_411", "light_64", "mat_173", "mat_22", "mat_236", "mat_237", "mat_401", "microwave", "mop", "mouse_166", "mouse_413", "mousepad_167", "mousepad_414", "nightstand_100", "nightstand_102", "orchid_178", "orchid_244", "oven", "phone", "photoframe_185", "photoframe_285", "photoframe_430", "pillow_182", "pillow_183", "pillow_2008", "pillow_405", "pillow_406", "pot", "powersocket_246", "powersocket_412", "rag", "shower_36", "shower_38", "sink_231", "sink_42", "spoon", "stovefan", "table_107", "table_226", "table_355", "tablelamp_97", "tablelamp_98", "television", "television_248", "toaster", "toilet", "towel_rack_31", "towel_rack_32", "towel_rack_33", "towel_rack_34", "trashcan", "tray", "tvstand_225", "tvstand_353", "wall_10", "wall_11", "wall_12", "wall_13", "wall_14", "wall_15", "wall_209", "wall_210", "wall_211", "wall_212", "wall_213", "wall_214", "wall_215", "wall_329", "wall_330", "wall_331", "wall_332", "wall_333", "wall_334", "wall_335", "wall_336", "wall_78", "wall_79", "wall_80", "wall_81", "wall_82", "wall_83", "wall_84", "wall_85", "wall_9", "wall_clock", "walllamp_27", "walllamp_28", "walllamp_29", "walllamp_350", "walllamp_351", "wallshelf_234", "wallshelf_235", "wallshelf_35", "window_348", "window_63", "window_86"]

VirtualHome 任务上下文 JSON：
{
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
}
任务上下文中的 identifier、instruction、pddl_objects、pddl_goal、pddl_goal_hints、external_goal_text、initial_environment_cache_path 是本 benchmark 的 grounding；必须保持 VirtualHome 目标语义和对象命名。

VirtualHome 可用 skill 摘要：
[
  {
    "name": "WALK",
    "description": "Official VirtualHome WALK action.",
    "planning_contract": {
      "planner_action_name": "WALK",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=WALK",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "FIND",
    "description": "Official VirtualHome FIND action.",
    "planning_contract": {
      "planner_action_name": "FIND",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=FIND",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RUN",
    "description": "Official VirtualHome RUN action.",
    "planning_contract": {
      "planner_action_name": "RUN",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=RUN",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "GRAB",
    "description": "Official VirtualHome GRAB action.",
    "planning_contract": {
      "planner_action_name": "GRAB",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=GRAB",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "PUTIN",
    "description": "Official VirtualHome PUTIN action.",
    "planning_contract": {
      "planner_action_name": "PUTIN",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=PUTIN",
      "planner_args_field": "args",
      "planner_args_arity": "2",
      "planner_entity_args": "0,1",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "PUTON",
    "description": "Official VirtualHome PUTON action.",
    "planning_contract": {
      "planner_action_name": "PUTON",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=PUTON",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "PUTBACK",
    "description": "Official VirtualHome PUTBACK action.",
    "planning_contract": {
      "planner_action_name": "PUTBACK",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=PUTBACK",
      "planner_args_field": "args",
      "planner_args_arity": "2",
      "planner_entity_args": "0,1",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "OPEN",
    "description": "Official VirtualHome OPEN action.",
    "planning_contract": {
      "planner_action_name": "OPEN",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=OPEN",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "CLOSE",
    "description": "Official VirtualHome CLOSE action.",
    "planning_contract": {
      "planner_action_name": "CLOSE",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=CLOSE",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "SWITCHON",
    "description": "Official VirtualHome SWITCHON action.",
    "planning_contract": {
      "planner_action_name": "SWITCHON",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=SWITCHON",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "SWITCHOFF",
    "description": "Official VirtualHome SWITCHOFF action.",
    "planning_contract": {
      "planner_action_name": "SWITCHOFF",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=SWITCHOFF",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "PLUGIN",
    "description": "Official VirtualHome PLUGIN action.",
    "planning_contract": {
      "planner_action_name": "PLUGIN",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=PLUGIN",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "WATCH",
    "description": "Official VirtualHome WATCH action.",
    "planning_contract": {
      "planner_action_name": "WATCH",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=WATCH",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LOOKAT",
    "description": "Official VirtualHome LOOKAT action.",
    "planning_contract": {
      "planner_action_name": "LOOKAT",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=LOOKAT",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LOOKAT_SHORT",
    "description": "VirtualHome LOOKAT_SHORT action.",
    "planning_contract": {
      "planner_action_name": "LOOKAT_SHORT",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=LOOKAT_SHORT",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LOOKAT_MEDIUM",
    "description": "VirtualHome LOOKAT_MEDIUM action.",
    "planning_contract": {
      "planner_action_name": "LOOKAT_MEDIUM",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=LOOKAT_MEDIUM",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LOOKAT_LONG",
    "description": "VirtualHome LOOKAT_LONG action.",
    "planning_contract": {
      "planner_action_name": "LOOKAT_LONG",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=LOOKAT_LONG",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "TOUCH",
    "description": "Official VirtualHome TOUCH action.",
    "planning_contract": {
      "planner_action_name": "TOUCH",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=TOUCH",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "POINTAT",
    "description": "Official VirtualHome POINTAT action.",
    "planning_contract": {
      "planner_action_name": "POINTAT",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=POINTAT",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "TURNTO",
    "description": "Official VirtualHome TURNTO action.",
    "planning_contract": {
      "planner_action_name": "TURNTO",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=TURNTO",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "READ",
    "description": "Official VirtualHome READ action.",
    "planning_contract": {
      "planner_action_name": "READ",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=READ",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "TYPE",
    "description": "Official VirtualHome TYPE action.",
    "planning_contract": {
      "planner_action_name": "TYPE",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=TYPE",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "DRINK",
    "description": "Official VirtualHome DRINK action.",
    "planning_contract": {
      "planner_action_name": "DRINK",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=DRINK",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "SIT",
    "description": "Official VirtualHome SIT action.",
    "planning_contract": {
      "planner_action_name": "SIT",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=SIT",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "LIE",
    "description": "Official VirtualHome LIE action.",
    "planning_contract": {
      "planner_action_name": "LIE",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=LIE",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "SLEEP",
    "description": "Official VirtualHome SLEEP action.",
    "planning_contract": {
      "planner_action_name": "SLEEP",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=SLEEP",
      "planner_args_field": "args",
      "planner_args_arity": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "STANDUP",
    "description": "Official VirtualHome STANDUP action.",
    "planning_contract": {
      "planner_action_name": "STANDUP",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=STANDUP",
      "planner_args_field": "args",
      "planner_args_arity": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "WAKEUP",
    "description": "Official VirtualHome WAKEUP action.",
    "planning_contract": {
      "planner_action_name": "WAKEUP",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=WAKEUP",
      "planner_args_field": "args",
      "planner_args_arity": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "DROP",
    "description": "Official VirtualHome DROP action.",
    "planning_contract": {
      "planner_action_name": "DROP",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=DROP",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RELEASE",
    "description": "Official VirtualHome RELEASE action.",
    "planning_contract": {
      "planner_action_name": "RELEASE",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=RELEASE",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "PUTOBJBACK",
    "description": "Official VirtualHome PUTOBJBACK action.",
    "planning_contract": {
      "planner_action_name": "PUTOBJBACK",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=PUTOBJBACK",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "PUTOFF",
    "description": "Official VirtualHome PUTOFF action.",
    "planning_contract": {
      "planner_action_name": "PUTOFF",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=PUTOFF",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "GREET",
    "description": "Official VirtualHome GREET action.",
    "planning_contract": {
      "planner_action_name": "GREET",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=GREET",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "POUR",
    "description": "Official VirtualHome POUR action.",
    "planning_contract": {
      "planner_action_name": "POUR",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=POUR",
      "planner_args_field": "args",
      "planner_args_arity": "2",
      "planner_entity_args": "0,1",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "MOVE",
    "description": "Official VirtualHome MOVE action.",
    "planning_contract": {
      "planner_action_name": "MOVE",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=MOVE",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "PUSH",
    "description": "Official VirtualHome PUSH action.",
    "planning_contract": {
      "planner_action_name": "PUSH",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=PUSH",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "PULL",
    "description": "Official VirtualHome PULL action.",
    "planning_contract": {
      "planner_action_name": "PULL",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=PULL",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "SQUEEZE",
    "description": "Official VirtualHome SQUEEZE action.",
    "planning_contract": {
      "planner_action_name": "SQUEEZE",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=SQUEEZE",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "PLUGOUT",
    "description": "Official VirtualHome PLUGOUT action.",
    "planning_contract": {
      "planner_action_name": "PLUGOUT",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=PLUGOUT",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "EAT",
    "description": "Official VirtualHome EAT action.",
    "planning_contract": {
      "planner_action_name": "EAT",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=EAT",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "WASH",
    "description": "Official VirtualHome WASH action.",
    "planning_contract": {
      "planner_action_name": "WASH",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=WASH",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "WIPE",
    "description": "Official VirtualHome WIPE action.",
    "planning_contract": {
      "planner_action_name": "WIPE",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=WIPE",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "SCRUB",
    "description": "Official VirtualHome SCRUB action.",
    "planning_contract": {
      "planner_action_name": "SCRUB",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=SCRUB",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "RINSE",
    "description": "Official VirtualHome RINSE action.",
    "planning_contract": {
      "planner_action_name": "RINSE",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=RINSE",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "CUT",
    "description": "Official VirtualHome CUT action.",
    "planning_contract": {
      "planner_action_name": "CUT",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=CUT",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false",
      "planner_dynamic_entity_rule": "slice_parts_from_target"
    }
  },
  {
    "name": "COOK",
    "description": "Official VirtualHome COOK action.",
    "planning_contract": {
      "planner_action_name": "COOK",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=COOK",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  },
  {
    "name": "FREEZE",
    "description": "Official VirtualHome FREEZE action.",
    "planning_contract": {
      "planner_action_name": "FREEZE",
      "planner_required_fields": "action,args",
      "planner_fixed_fields": "action=FREEZE",
      "planner_args_field": "args",
      "planner_args_arity": "1",
      "planner_entity_args": "0",
      "planner_allow_extra_fields": "false"
    }
  }
]

理解边界：
1. intent 保留 VirtualHome instruction 或 task name，不输出动作序列。
2. required_item_names 必须使用允许实体名或 pddl_goal 中可映射的实体名；character/robot 目标要写入 intent 和 quantity_constraints，不要伪造成普通物体。
3. pddl_goal/external_goal_text 是目标依据；要保留关系、状态、位置和 character/robot 相关目标语义。
4. skill_closure 只能使用 VirtualHome skills root 中启用的 skill，例如 WALK、GRAB、PUTIN、PUTON、OPEN、CLOSE、SWITCHON、SIT、LIE、CUT、COOK、FREEZE。

输出 JSON 结构：
{"is_complete": true, "is_cancel_all": false, "clarification_question": "", "entity_relevance": {"directly_related": [], "indirectly_related": [], "possibly_related": []}, "skill_closure": [], "structured_task": {"intent": "", "required_item_names": {"targets": {"primary": [], "alternatives": []}, "tools": {"primary": [], "alternatives": []}, "receptacles": {"primary": [], "alternatives": []}}, "quantity_constraints": []}}

## Message 2: human

Relax on sofa
