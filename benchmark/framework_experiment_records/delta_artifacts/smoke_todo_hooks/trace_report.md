# DELTA Case Report: dining:allensville:episode-01

## 1. 文件位置

- 结果文件：`/data/zmy/OurAgent-he1/benchmark/delta/framework/results/delta_audit_smoke_20260806_todo_hooks/cases/dining__allensville__episode-01/raw_output.json`
- 完整阶段 artifact：`/data/zmy/OurAgent-he1/benchmark/delta/framework/results/delta_audit_smoke_20260806_todo_hooks/cases/dining__allensville__episode-01/artifacts`
- 完整输入输出 / 审计文件：`case_input.json`, `case_input_summary.json`, `prepared_environment.json`, `prepared_environment_summary.json`, `environment_audit.json`, `understanding_input.json`, `understanding_input_summary.json`, `understanding_output.json`, `understanding_output_summary.json`, `planning_input.json`, `planning_input_summary.json`, `planning_output.json`, `planning_output_summary.json`, `contract_audit.json`, `planning_feature_records.json`, `llm_io.json`, `goal_check.json`, `official_eval.json`, `process_summary.json`

## 2. 当前结果摘要

```json
{
  "case_id": "dining:allensville:episode-01",
  "dataset": "delta",
  "task_success": true,
  "task_success_rate": 1.0,
  "evaluation_route": "val",
  "val_success": true,
  "val_available": true,
  "execution_success": true,
  "execution_status": "completed",
  "is_feasible": true,
  "feedback": "规划合法，验证环节闭环。",
  "official_actions_len": 25,
  "evaluator_execution_calls_len": 25,
  "official_failure_reason": "",
  "todo_contract_status": "not_recorded",
  "todo_contract_event_count": 0,
  "sandbox_failure_reason": "",
  "symbolic_official_alignment": {
    "status": "aligned_success",
    "symbolic_goal_success_rate": 1.0,
    "task_success": true,
    "official_available": true
  }
}
```

## 3. 官方失败 / 本地 Sandbox / Symbolic-Official 对齐

```json
{
  "task_success": true,
  "task_success_rate": 1.0,
  "official_available": true,
  "official_failure_reason": "",
  "sandbox_failed_count": 0,
  "sandbox_failure_reason": "",
  "sandbox_repair_hint": "",
  "sandbox_failed_reasons": [],
  "symbolic_official_alignment": {
    "status": "aligned_success",
    "symbolic_goal_success_rate": 1.0,
    "task_success": true,
    "official_available": true
  },
  "goal_success_rate": 1.0,
  "satisfied_goals": [
    "(item_on plate dining_table)",
    "(item_on fork dining_table)",
    "(item_on knife dining_table)",
    "(item_on spoon dining_table)",
    "(item_on glass dining_table)",
    "(item_on flower dining_table)"
  ],
  "unsatisfied_goals": []
}
```

## 4. 要看的关键字段

- `prediction.benchmark_trace.case_input`：这条数据原始输入
- `prediction.benchmark_trace.prepared_environment`：场景准备结果
- `prediction.benchmark_trace.understanding_input / understanding_output`：understanding 前后
- `prediction.benchmark_trace.planning_input / planning_output`：planning 前后
- `artifacts/contract_audit.json`：本次 todo_list 原生动作契约检查、动作格式、命中 skill schema
- `prediction.benchmark_trace.llm_io`：每次模型输入输出
- `prediction.benchmark_trace.planning_output.planning_debug_events`：每次 contract / sandbox / audit 事件
- `prediction.benchmark_trace.planning_output.re_trac_memory`：re_trac 的 failed lessons
- `prediction.benchmark_trace.planning_output.evaluator_findings`：结构化失败摘要

## 5. Benchmark 原始输入

```json
{
  "schema_version": "framework_trace_v3",
  "process_name": "case_input",
  "payload_role": "output",
  "keys": [
    "add_act",
    "add_obj",
    "base_task_id",
    "benchmark_module",
    "benchmark_settings_file",
    "dataset",
    "delta_env_state",
    "domain",
    "environment_source",
    "episode",
    "instruction",
    "scene_graph_cache_path",
    "scene_name",
    "task_id",
    "task_source"
  ],
  "dataset": "delta",
  "task_id": "dining:allensville:episode-01",
  "identifier": null,
  "benchmark_settings_file": "/data/zmy/OurAgent-he1/benchmark/delta/framework/code/config/settings.json",
  "environment_source": "delta_data_scene_graph_py",
  "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table."
}
```

## 6. Framework 各阶段输入输出

### Prepared Environment
```json
{
  "schema_version": "framework_trace_v3",
  "process_name": "environment_preparation",
  "payload_role": "output",
  "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
  "env_state": {
    "robot_location": "living_room",
    "robot_holding": "空",
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
    "domain": "dining",
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
    ]
  },
  "entity_catalog": {
    "count": 58,
    "sample": [
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
      "rotting_apple"
    ],
    "truncated": true
  },
  "scene": {
    "available": true,
    "entity_count": 58,
    "type_counts": {
      "room": 11,
      "unknown": 35,
      "receptacle": 12
    },
    "rooms": {
      "count": 11,
      "sample": [
        "bathroom_1",
        "bathroom_2",
        "bedroom_1",
        "bedroom_2",
        "corridor_1",
        "corridor_2",
        "corridor_3",
        "dining_room",
        "kitchen",
        "living_room",
        "lobby"
      ],
      "truncated": false
    },
    "receptacles": {
      "count": 12,
      "sample": [
        "banana_peel",
        "cola_can",
        "dining_table",
        "fridge_1",
        "fridge_2",
        "fridge_3",
        "locker",
        "microwave",
        "robot_hub",
        "rotting_apple",
        "rubbish_bin",
        "shelf"
      ],
      "truncated": false
    },
    "entities": {
      "count": 58,
      "sample": [
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
        "microwave"
      ],
      "truncated": true
    },
    "states_sample": {
      "mop": {
        "isClean": true,
        "isDirty": false
      },
      "shelf": {
        "isLoaded": true
      },
      "fridge_1": {
        "isOpen": false,
        "isToggled": false
      },
      "fridge_2": {
        "isOpen": false,
        "isToggled": false
      },
      "microwave": {
        "isOpen": false,
        "isToggled": false
      },
      "oven": {
        "isOpen": false,
        "isToggled": false
      },
      "locker": {
        "isLoaded": true
      }
    },
    "nesting": {
      "available": true,
      "contains_node_count": 11,
      "max_depth": 2
    },
    "flat_schema": {
      "available": true,
      "entity_count": 58,
      "standard_field_counts": {
        "direct_parent": 58,
        "direct_relation": 58,
        "type": 58,
        "states": 58,
        "properties": 58,
        "is_container": 58,
        "full_path": 58
      },
      "relation_entity_count": 47,
      "state_entity_count": 7,
      "property_entity_count": 47,
      "container_count": 12,
      "full_path_entity_count": 47,
      "parent_missing_count": 0,
      "parent_missing_sample": [],
      "parent_reference_missing_count": 0,
      "parent_reference_missing_sample": []
    }
  },
  "context": {
    "selected_graph": {
      "name": "allensville",
      "rooms": {
        "bathroom_1": {
          "items": {
            "psu": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop"
              ],
              "state": "free"
            },
            "sink_1": {
              "accessible": true,
              "affordance": [
                "clean_mop"
              ],
              "state": "free"
            },
            "toilet_1": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            },
            "plant_1": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            },
            "mop": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "clean_mop",
                "mop_floor"
              ],
              "state": "clean"
            }
          },
          "neighbor": [
            "corridor_2"
          ]
        },
        "bathroom_2": {
          "items": {
            "gpu": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop"
              ],
              "state": "free"
            },
            "sink_2": {
              "accessible": true,
              "affordance": [
                "clean_mop"
              ],
              "state": "free"
            },
            "toilet_2": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            },
            "plant_2": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            }
          },
          "neighbor": [
            "corridor_3"
          ]
        },
        "bedroom_1": {
          "items": {
            "mainboard": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop"
              ],
              "state": "free"
            },
            "glass": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "place_on"
              ],
              "state": "free"
            },
            "bed_1": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            },
            "shelf": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "load",
                "unload"
              ],
              "state": "loaded",
              "content": {
                "book": {
                  "accessible": true,
                  "affordance": [
                    "pick",
                    "drop"
                  ],
                  "state": "free"
                }
              }
            }
          },
          "neighbor": [
            "corridor_2"
          ]
        },
        "bedroom_2": {
          "items": {
            "cpu": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop"
              ],
              "state": "free"
            },
            "rotting_apple": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "dispose"
              ],
              "state": "free"
            },
            "plate": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "place_on"
              ],
              "state": "free"
            },
            "bed_2": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            },
            "lamp": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop"
              ],
              "state": "free"
            }
          },
          "neighbor": [
            "corridor_3"
          ]
        },
        "corridor_1": {
          "items": {},
          "neighbor": [
            "lobby",
            "corridor_3"
          ]
        },
        "corridor_2": {
          "items": {
            "fridge_1": {
              "accessible": true,
              "affordance": [
                "open",
                "close"
              ],
              "state": "closed, off"
            },
            "fridge_2": {
              "accessible": true,
              "affordance": [
                "open",
                "close"
              ],
              "state": "closed, off"
            }
          },
          "neighbor": [
            "bathroom_1",
            "bedroom_1",
            "corridor_3"
          ]
        },
        "corridor_3": {
          "items": {},
          "neighbor": [
            "corridor_1",
            "corridor_2",
            "bathroom_2",
            "bedroom_2",
            "kitchen",
            "living_room"
          ]
        },
        "dining_room": {
          "items": {
            "ssd": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop"
              ],
              "state": "free"
            },
            "clock": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            },
            "cola_can": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "dispose"
              ],
              "state": "free"
            },
            "chair_1": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            },
            "chair_2": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            },
            "dining_table": {
              "accessible": true,
              "affordance": [],
              "state": "free"
            }
          },
          "neighbor": [
            "kitchen",
            "living_room"
          ]
        },
        "kitchen": {
          "items": {
            "knife": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "place_on"
              ],
              "state": "free"
            },
            "fork": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "place_on"
              ],
              "state": "free"
            },
            "spoon": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "place_on"
              ],
              "state": "free"
            },
            "microwave": {
              "accessible": true,
              "affordance": [
                "open",
                "close",
                "turnon",
                "turnoff"
              ],
              "state": "closed, off"
            },
            "oven": {
              "accessible": true,
              "affordance": [
                "turnon",
                "turnoff"
              ],
              "state": "closed, off"
            },
            "rubbish_bin": {
              "accessible": true,
              "affordance": [
                "dispose"
              ],
              "state": "free"
            },
            "fridge_3": {
              "accessible": true,
              "affordance": [
                "open",
                "close"
              ],
              "state": "free"
            },
            "chair_3": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            }
          },
          "neighbor": [
            "corridor_3",
            "dining_room"
          ]
        },
        "living_room": {
          "items": {
            "desk": {
              "accessible": true,
              "affordance": [],
              "state": "free"
            },
            "bowl_2": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop"
              ],
              "state": "free"
            },
            "bowl_3": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop"
              ],
              "state": "free"
            },
            "robot_hub": {
              "accessible": true,
              "affordance": [
                "charge"
              ],
              "state": "free"
            },
            "chair_4": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            },
            "chair_5": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            },
            "couch": {
              "accessible": false,
              "affordance": [],
              "state": "free"
            }
          },
          "neighbor": [
            "corridor_3",
            "dining_room"
          ]
        },
        "lobby": {
          "items": {
            "ram": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop"
              ],
              "state": "free"
            },
            "banana_peel": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "dispose"
              ],
              "state": "free"
            },
            "flower": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "place_on"
              ],
              "state": "free"
            },
            "locker": {
              "accessible": true,
              "affordance": [
                "pick",
                "drop",
                "load",
                "unload"
              ],
              "state": "loaded",
              "content": {
                "paper": {
                  "accessible": true,
                  "affordance": [
                    "pick",
                    "drop"
                  ],
                  "state": "free"
                }
              }
            }
          },
          "neighbor": [
            "corridor_1"
          ]
        }
      },
      "agent": {
        "position": "living_room",
        "state": "hand-free"
      }
    },
    "task_context": {
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
      "task_environment_mode": "understanding_pruned"
    }
  }
}
```

### Understanding Input
```json
{
  "schema_version": "framework_trace_v3",
  "process_name": "understanding",
  "payload_role": "input",
  "raw_instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
  "original_instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
  "messages": [
    "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table."
  ],
  "task_context": {
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
  },
  "feature_flags": {
    "sandbox_evaluator": true,
    "state_diff_audit": true,
    "semantic_audit": false,
    "entity_repair_alternatives": false,
    "drop_benchmark_alternatives": true,
    "playbook_retrieval": false,
    "playbook_write": false,
    "reflection": false,
    "candidate_rules": false,
    "train_only_rules": false,
    "allow_clarification": false,
    "raise_feature_exceptions": true
  }
}
```

### Understanding Output
```json
{
  "schema_version": "framework_trace_v3",
  "process_name": "understanding",
  "payload_role": "output",
  "is_complete": true,
  "is_cancel_all": false,
  "clarification_question": "",
  "clarification_suppressed": false,
  "relevant_item_names": {
    "count": 7,
    "sample": [
      "dining_table",
      "plate",
      "fork",
      "knife",
      "spoon",
      "glass",
      "flower"
    ],
    "truncated": false
  },
  "structured_task": {
    "intent": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
    "required_item_names": {
      "targets": {
        "primary": [
          "dining_table"
        ],
        "alternatives": []
      },
      "tools": {
        "primary": [
          "plate",
          "fork",
          "knife",
          "spoon",
          "glass"
        ],
        "alternatives": []
      },
      "receptacles": {
        "primary": [
          "flower"
        ],
        "alternatives": []
      }
    },
    "final_state": {
      "predicates": [
        "item_on(plate, dining_table)",
        "item_on(fork, dining_table)",
        "item_on(knife, dining_table)",
        "item_on(spoon, dining_table)",
        "item_on(glass, dining_table)",
        "item_on(flower, dining_table)"
      ],
      "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
    }
  },
  "understanding_final_state": {
    "predicates": [
      "item_on(plate, dining_table)",
      "item_on(fork, dining_table)",
      "item_on(knife, dining_table)",
      "item_on(spoon, dining_table)",
      "item_on(glass, dining_table)",
      "item_on(flower, dining_table)"
    ],
    "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
  },
  "entity_repair": {
    "needed": false,
    "invalid_names": [],
    "valid_names": [
      "dining_table",
      "plate",
      "fork",
      "knife",
      "spoon",
      "glass",
      "flower"
    ]
  },
  "goal_state_extract": {
    "enabled": true,
    "source": "llm",
    "attempts": 1,
    "raw": {
      "final_state": {
        "predicates": [
          "item_on(plate, dining_table)",
          "item_on(fork, dining_table)",
          "item_on(knife, dining_table)",
          "item_on(spoon, dining_table)",
          "item_on(glass, dining_table)",
          "item_on(flower, dining_table)"
        ],
        "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
      }
    }
  }
}
```

### Planning Input
```json
{
  "schema_version": "framework_trace_v3",
  "process_name": "planning",
  "payload_role": "input",
  "config": {
    "skill_profile": null,
    "repair_strategy": "retrac",
    "todo_output_parser_path": "benchmark.delta.framework.code.native_actions.parse_delta_native_actions",
    "todo_step_adapter_path": "benchmark.delta.framework.code.native_actions.delta_native_step_to_skill_call",
    "todo_list_validator_path": "",
    "feature_flags": {
      "sandbox_evaluator": true,
      "state_diff_audit": true,
      "semantic_audit": false,
      "playbook_retrieval": false,
      "playbook_write": false,
      "reflection": false,
      "candidate_rules": false
    },
    "planning_contract": {
      "available": true,
      "profile": "",
      "config_file": "/data/zmy/OurAgent-he1/benchmark/delta/framework/code/config/settings.json",
      "skills_root": "benchmark/delta/framework/code/skills",
      "enabled_contract_skill_count": 13,
      "raw_contract_count": 13,
      "framework_contract_skills": [
        "goto",
        "pick",
        "drop",
        "place_on",
        "dispose",
        "mop_floor",
        "clean_mop",
        "charge",
        "assemble",
        "pick_loadable",
        "drop_loadable",
        "load",
        "unload"
      ],
      "raw_action_names": [
        "goto",
        "pick",
        "drop",
        "place_on",
        "dispose",
        "mop_floor",
        "clean_mop",
        "charge",
        "assemble",
        "pick_loadable",
        "drop_loadable",
        "load",
        "unload"
      ],
      "raw_actions": [
        {
          "skill": "goto",
          "action_name": "goto",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "room_1",
            "room_2"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "goto"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [],
          "room_fields": [
            "room_1",
            "room_2"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "clean",
            "dining",
            "office",
            "pc"
          ]
        },
        {
          "skill": "pick",
          "action_name": "pick",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "pick"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "clean",
            "dining",
            "office",
            "pc"
          ]
        },
        {
          "skill": "drop",
          "action_name": "drop",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "drop"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "clean",
            "dining",
            "office",
            "pc"
          ]
        },
        {
          "skill": "place_on",
          "action_name": "place_on",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item_1",
            "item_2",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "place_on"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item_1",
            "item_2"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "dining"
          ]
        },
        {
          "skill": "dispose",
          "action_name": "dispose",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item_1",
            "item_2",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "dispose"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item_1",
            "item_2"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "clean"
          ]
        },
        {
          "skill": "mop_floor",
          "action_name": "mop_floor",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "mop_floor"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "clean"
          ]
        },
        {
          "skill": "clean_mop",
          "action_name": "clean_mop",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item_1",
            "item_2",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "clean_mop"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item_1",
            "item_2"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "clean"
          ]
        },
        {
          "skill": "charge",
          "action_name": "charge",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "charge"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "clean"
          ]
        },
        {
          "skill": "assemble",
          "action_name": "assemble",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "room",
            "item_1",
            "item_2",
            "item_3",
            "item_4",
            "item_5",
            "item_6",
            "pc"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "assemble"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item_1",
            "item_2",
            "item_3",
            "item_4",
            "item_5",
            "item_6"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [
            "pc"
          ],
          "context_field": "domain",
          "context_values": [
            "pc"
          ]
        },
        {
          "skill": "pick_loadable",
          "action_name": "pick_loadable",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "pick_loadable"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "office"
          ]
        },
        {
          "skill": "drop_loadable",
          "action_name": "drop_loadable",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "drop_loadable"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "office"
          ]
        },
        {
          "skill": "load",
          "action_name": "load",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item_1",
            "item_2",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "load"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item_1",
            "item_2"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "office"
          ]
        },
        {
          "skill": "unload",
          "action_name": "unload",
          "action_field": "action",
          "required_fields": [
            "action",
            "agent",
            "item_1",
            "item_2",
            "room"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "unload"
            },
            {
              "field": "agent",
              "value": "robot"
            }
          ],
          "entity_fields": [
            "item_1",
            "item_2"
          ],
          "room_fields": [
            "room"
          ],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "domain",
          "context_values": [
            "office"
          ]
        }
      ]
    }
  },
  "input": {
    "understanding_stage_executed": true,
    "structured_task": {
      "intent": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
      "required_item_names": {
        "targets": {
          "primary": [
            "dining_table"
          ],
          "alternatives": []
        },
        "tools": {
          "primary": [
            "plate",
            "fork",
            "knife",
            "spoon",
            "glass"
          ],
          "alternatives": []
        },
        "receptacles": {
          "primary": [
            "flower"
          ],
          "alternatives": []
        }
      },
      "final_state": {
        "predicates": [
          "item_on(plate, dining_table)",
          "item_on(fork, dining_table)",
          "item_on(knife, dining_table)",
          "item_on(spoon, dining_table)",
          "item_on(glass, dining_table)",
          "item_on(flower, dining_table)"
        ],
        "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
      }
    },
    "env_state": {
      "robot_location": "living_room",
      "robot_holding": "空",
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
      "domain": "dining",
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
      ]
    },
    "task_context": {
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
    },
    "feedback": "",
    "environment": {
      "available": true,
      "entity_count": 18,
      "type_counts": {
        "receptacle": 1,
        "room": 11,
        "unknown": 6
      },
      "entities": {
        "count": 18,
        "sample": [
          "bathroom_1",
          "bathroom_2",
          "bedroom_1",
          "bedroom_2",
          "corridor_1",
          "corridor_2",
          "corridor_3",
          "dining_room",
          "dining_table",
          "flower",
          "fork",
          "glass",
          "kitchen",
          "knife",
          "living_room",
          "lobby",
          "plate",
          "spoon"
        ],
        "truncated": false
      },
      "states_sample": {},
      "schema": {
        "available": true,
        "entity_count": 18,
        "standard_field_counts": {
          "direct_parent": 18,
          "direct_relation": 18,
          "type": 18,
          "states": 18,
          "properties": 18,
          "is_container": 18,
          "full_path": 18
        },
        "relation_entity_count": 7,
        "state_entity_count": 0,
        "property_entity_count": 7,
        "container_count": 1,
        "full_path_entity_count": 7,
        "parent_missing_count": 0,
        "parent_missing_sample": [],
        "parent_reference_missing_count": 0,
        "parent_reference_missing_sample": []
      }
    },
    "environment_facts": {
      "available": true,
      "entity_count": 18,
      "facts": [
        {
          "name": "bathroom_1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "bathroom_2",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "bedroom_1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "bedroom_2",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "corridor_1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "corridor_2",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "corridor_3",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "dining_room",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "dining_table",
          "direct_parent": "dining_room",
          "direct_relation": "inside",
          "full_path": [
            "dining_room"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_predicate:item_is_dining_table"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "flower",
          "direct_parent": "lobby",
          "direct_relation": "inside",
          "full_path": [
            "lobby"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "fork",
          "direct_parent": "kitchen",
          "direct_relation": "inside",
          "full_path": [
            "kitchen"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "glass",
          "direct_parent": "bedroom_1",
          "direct_relation": "inside",
          "full_path": [
            "bedroom_1"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "kitchen",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "knife",
          "direct_parent": "kitchen",
          "direct_relation": "inside",
          "full_path": [
            "kitchen"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "living_room",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "lobby",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "plate",
          "direct_parent": "bedroom_2",
          "direct_relation": "inside",
          "full_path": [
            "bedroom_2"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "spoon",
          "direct_parent": "kitchen",
          "direct_relation": "inside",
          "full_path": [
            "kitchen"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        }
      ],
      "truncated": false
    },
    "environment_source": {
      "builder": "build_sandbox_environment",
      "benchmark": "benchmark.delta"
    }
  },
  "resume_state": {
    "validated_todo_actions": {
      "count": 0,
      "sample": [],
      "truncated": false
    },
    "validated_steps": {
      "count": 0,
      "sample": [],
      "truncated": false
    },
    "todo_list_before_planning": {
      "count": 0,
      "sample": [],
      "truncated": false
    },
    "checkpoint_env": {
      "available": true,
      "entity_count": 0,
      "type_counts": {},
      "entities": {
        "count": 0,
        "sample": [],
        "truncated": false
      },
      "states_sample": {},
      "schema": {
        "available": true,
        "entity_count": 0,
        "standard_field_counts": {
          "direct_parent": 0,
          "direct_relation": 0,
          "type": 0,
          "states": 0,
          "properties": 0,
          "is_container": 0,
          "full_path": 0
        },
        "relation_entity_count": 0,
        "state_entity_count": 0,
        "property_entity_count": 0,
        "container_count": 0,
        "full_path_entity_count": 0,
        "parent_missing_count": 0,
        "parent_missing_sample": [],
        "parent_reference_missing_count": 0,
        "parent_reference_missing_sample": []
      }
    },
    "todo_checkpoint_env": {
      "available": true,
      "entity_count": 0,
      "type_counts": {},
      "entities": {
        "count": 0,
        "sample": [],
        "truncated": false
      },
      "states_sample": {},
      "schema": {
        "available": true,
        "entity_count": 0,
        "standard_field_counts": {
          "direct_parent": 0,
          "direct_relation": 0,
          "type": 0,
          "states": 0,
          "properties": 0,
          "is_container": 0,
          "full_path": 0
        },
        "relation_entity_count": 0,
        "state_entity_count": 0,
        "property_entity_count": 0,
        "container_count": 0,
        "full_path_entity_count": 0,
        "parent_missing_count": 0,
        "parent_missing_sample": [],
        "parent_reference_missing_count": 0,
        "parent_reference_missing_sample": []
      }
    }
  }
}
```

### Planning Output
```json
{
  "schema_version": "framework_trace_v3",
  "process_name": "planning",
  "payload_role": "output",
  "status": {
    "is_feasible": true,
    "execution_status": "completed",
    "planner_status": "planned",
    "iteration_count": 1,
    "failure_layer": "",
    "failure_category": "",
    "failed_action": {},
    "feedback": "规划合法，验证环节闭环。",
    "error_feedback": ""
  },
  "output": {
    "todo_list": {
      "count": 25,
      "sample": [
        {
          "step": 1,
          "action": "goto",
          "agent": "robot",
          "room_1": "living_room",
          "room_2": "dining_room"
        },
        {
          "step": 2,
          "action": "goto",
          "agent": "robot",
          "room_1": "dining_room",
          "room_2": "kitchen"
        },
        {
          "step": 3,
          "action": "pick",
          "agent": "robot",
          "item": "fork",
          "room": "kitchen"
        },
        {
          "step": 4,
          "action": "goto",
          "agent": "robot",
          "room_1": "kitchen",
          "room_2": "dining_room"
        },
        {
          "step": 5,
          "action": "place_on",
          "agent": "robot",
          "item_1": "fork",
          "item_2": "dining_table",
          "room": "dining_room"
        },
        {
          "step": 6,
          "action": "goto",
          "agent": "robot",
          "room_1": "dining_room",
          "room_2": "kitchen"
        },
        {
          "step": 7,
          "action": "pick",
          "agent": "robot",
          "item": "knife",
          "room": "kitchen"
        },
        {
          "step": 8,
          "action": "goto",
          "agent": "robot",
          "room_1": "kitchen",
          "room_2": "dining_room"
        }
      ],
      "truncated": true
    },
    "validated_steps": {
      "count": 0,
      "sample": [],
      "truncated": false
    },
    "validated_todo_actions": {
      "count": 25,
      "sample": [
        {
          "step": 1,
          "action": "goto",
          "agent": "robot",
          "room_1": "living_room",
          "room_2": "dining_room"
        },
        {
          "step": 2,
          "action": "goto",
          "agent": "robot",
          "room_1": "dining_room",
          "room_2": "kitchen"
        },
        {
          "step": 3,
          "action": "pick",
          "agent": "robot",
          "item": "fork",
          "room": "kitchen"
        },
        {
          "step": 4,
          "action": "goto",
          "agent": "robot",
          "room_1": "kitchen",
          "room_2": "dining_room"
        },
        {
          "step": 5,
          "action": "place_on",
          "agent": "robot",
          "item_1": "fork",
          "item_2": "dining_table",
          "room": "dining_room"
        },
        {
          "step": 6,
          "action": "goto",
          "agent": "robot",
          "room_1": "dining_room",
          "room_2": "kitchen"
        },
        {
          "step": 7,
          "action": "pick",
          "agent": "robot",
          "item": "knife",
          "room": "kitchen"
        },
        {
          "step": 8,
          "action": "goto",
          "agent": "robot",
          "room_1": "kitchen",
          "room_2": "dining_room"
        }
      ],
      "truncated": true
    },
    "todo_llm_output": "[\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"living_room\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"fork\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"fork\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"knife\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"knife\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"spoon\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"spoon\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"bedroom_1\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"glass\",\n    \"room\": \"bedroom_1\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"bedroom_1\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"glass\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"bedroom_2\"\n  },\n... <truncated 782 chars>",
    "todo_parse_error": "",
    "evaluator_findings": {
      "count": 0,
      "sample": [],
      "truncated": false
    }
  },
  "state": {
    "env_state": {
      "robot_location": "dining_room",
      "robot_holding": "空",
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
      "domain": "dining",
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
      ]
    },
    "environment": {
      "available": true,
      "entity_count": 18,
      "type_counts": {
        "receptacle": 1,
        "room": 11,
        "unknown": 6
      },
      "entities": {
        "count": 18,
        "sample": [
          "bathroom_1",
          "bathroom_2",
          "bedroom_1",
          "bedroom_2",
          "corridor_1",
          "corridor_2",
          "corridor_3",
          "dining_room",
          "dining_table",
          "flower",
          "fork",
          "glass",
          "kitchen",
          "knife",
          "living_room",
          "lobby",
          "plate",
          "spoon"
        ],
        "truncated": false
      },
      "states_sample": {},
      "schema": {
        "available": true,
        "entity_count": 18,
        "standard_field_counts": {
          "direct_parent": 18,
          "direct_relation": 18,
          "type": 18,
          "states": 18,
          "properties": 18,
          "is_container": 18,
          "full_path": 18
        },
        "relation_entity_count": 7,
        "state_entity_count": 0,
        "property_entity_count": 7,
        "container_count": 1,
        "full_path_entity_count": 7,
        "parent_missing_count": 0,
        "parent_missing_sample": [],
        "parent_reference_missing_count": 0,
        "parent_reference_missing_sample": []
      }
    },
    "environment_facts": {
      "available": true,
      "entity_count": 18,
      "facts": [
        {
          "name": "bathroom_1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "bathroom_2",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "bedroom_1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "bedroom_2",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "corridor_1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "corridor_2",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "corridor_3",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "dining_room",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "dining_table",
          "direct_parent": "dining_room",
          "direct_relation": "inside",
          "full_path": [
            "dining_room"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_predicate:item_is_dining_table"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "flower",
          "direct_parent": "dining_table",
          "direct_relation": "inside",
          "full_path": [
            "dining_room",
            "dining_table"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "fork",
          "direct_parent": "dining_table",
          "direct_relation": "inside",
          "full_path": [
            "dining_room",
            "dining_table"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "glass",
          "direct_parent": "dining_table",
          "direct_relation": "inside",
          "full_path": [
            "dining_room",
            "dining_table"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "kitchen",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "knife",
          "direct_parent": "dining_table",
          "direct_relation": "inside",
          "full_path": [
            "dining_room",
            "dining_table"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "living_room",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "lobby",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "plate",
          "direct_parent": "dining_table",
          "direct_relation": "inside",
          "full_path": [
            "dining_room",
            "dining_table"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "spoon",
          "direct_parent": "dining_table",
          "direct_relation": "inside",
          "full_path": [
            "dining_room",
            "dining_table"
          ],
          "states": {},
          "properties": [
            "delta_accessible:true",
            "delta_affordance:drop",
            "delta_affordance:pick",
            "delta_affordance:place_on",
            "delta_predicate:item_pickable",
            "delta_predicate:item_accessible"
          ],
          "type": null,
          "is_container": false
        }
      ],
      "truncated": false
    },
    "environment_source": {
      "builder": "build_sandbox_environment",
      "benchmark": "benchmark.delta"
    },
    "checkpoint_env": {
      "available": true,
      "entity_count": 18,
      "type_counts": {
        "receptacle": 1,
        "room": 11,
        "unknown": 6
      },
      "entities": {
        "count": 18,
        "sample": [
          "bathroom_1",
          "bathroom_2",
          "bedroom_1",
          "bedroom_2",
          "corridor_1",
          "corridor_2",
          "corridor_3",
          "dining_room",
          "dining_table",
          "flower",
          "fork",
          "glass",
          "kitchen",
          "knife",
          "living_room",
          "lobby",
          "plate",
          "spoon"
        ],
        "truncated": false
      },
      "states_sample": {},
      "schema": {
        "available": true,
        "entity_count": 18,
        "standard_field_counts": {
          "direct_parent": 18,
          "direct_relation": 18,
          "type": 18,
          "states": 18,
          "properties": 18,
          "is_container": 18,
          "full_path": 18
        },
        "relation_entity_count": 7,
        "state_entity_count": 0,
        "property_entity_count": 7,
        "container_count": 1,
        "full_path_entity_count": 7,
        "parent_missing_count": 0,
        "parent_missing_sample": [],
        "parent_reference_missing_count": 0,
        "parent_reference_missing_sample": []
      }
    },
    "checkpoint_robot": {
      "robot_location": "dining_room",
      "robot_holding": "空",
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
      "domain": "dining",
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
      ]
    },
    "todo_checkpoint_env": {
      "available": true,
      "entity_count": 18,
      "type_counts": {
        "receptacle": 1,
        "room": 11,
        "unknown": 6
      },
      "entities": {
        "count": 18,
        "sample": [
          "bathroom_1",
          "bathroom_2",
          "bedroom_1",
          "bedroom_2",
          "corridor_1",
          "corridor_2",
          "corridor_3",
          "dining_room",
          "dining_table",
          "flower",
          "fork",
          "glass",
          "kitchen",
          "knife",
          "living_room",
          "lobby",
          "plate",
          "spoon"
        ],
        "truncated": false
      },
      "states_sample": {},
      "schema": {
        "available": true,
        "entity_count": 18,
        "standard_field_counts": {
          "direct_parent": 18,
          "direct_relation": 18,
          "type": 18,
          "states": 18,
          "properties": 18,
          "is_container": 18,
          "full_path": 18
        },
        "relation_entity_count": 7,
        "state_entity_count": 0,
        "property_entity_count": 7,
        "container_count": 1,
        "full_path_entity_count": 7,
        "parent_missing_count": 0,
        "parent_missing_sample": [],
        "parent_reference_missing_count": 0,
        "parent_reference_missing_sample": []
      }
    },
    "todo_checkpoint_robot": {
      "robot_location": "dining_room",
      "robot_holding": "空",
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
      "domain": "dining",
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
      ]
    },
    "re_trac_state": {},
    "sda_state": {}
  },
  "audit": {
    "repair_strategy": "retrac",
    "state_diff_audit": {
      "passed": true,
      "result": {
        "is_passed": true,
        "issue": "",
        "fix_advice": "",
        "repair_mode": "continue_from_current",
        "accepted_diffs": [
          "plate",
          "fork",
          "knife",
          "spoon",
          "glass",
          "flower"
        ],
        "unexpected_diffs": [],
        "audit_method": "framework_llm_state_diff",
        "state_audit_context": {
          "entity_count_available": 18,
          "entity_count_in_context": 8,
          "truncated_entity_count": 0,
          "note": "state_diff only lists changed entities; unchanged entities in this context still prove final goal state when their after state satisfies the task.",
          "robot": {
            "changed": true,
            "before": {
              "robot_location": "living_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            },
            "after": {
              "robot_location": "dining_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            }
          },
          "entities": [
            {
              "name": "dining_table",
              "changed": false,
              "before": {
                "type": "receptacle",
                "direct_parent": "dining_room",
                "direct_relation": "inside",
                "is_container": true,
                "full_path": [
                  "dining_room"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_predicate:item_is_dining_table"
                ]
              },
              "after": {
                "type": "receptacle",
                "direct_parent": "dining_room",
                "direct_relation": "inside",
                "is_container": true,
                "full_path": [
                  "dining_room"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_predicate:item_is_dining_table"
                ]
              }
            },
            {
              "name": "plate",
              "changed": true,
              "before": {
                "type": null,
                "direct_parent": "bedroom_2",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "bedroom_2"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "fork",
              "changed": true,
              "before": {
                "type": null,
                "direct_parent": "kitchen",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "kitchen"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "knife",
              "changed": true,
              "before": {
                "type": null,
                "direct_parent": "kitchen",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "kitchen"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "spoon",
              "changed": true,
              "before": {
                "type": null,
                "direct_parent": "kitchen",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "kitchen"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "glass",
              "changed": true,
              "before": {
                "type": null,
                "direct_parent": "bedroom_1",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "bedroom_1"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "flower",
              "changed": true,
              "before": {
                "type": null,
                "direct_parent": "lobby",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "lobby"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "dining_room",
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
          },
          "evaluation_context": {},
          "external_goal": {
            "has_external_goal": true,
            "external_goal_state": {},
            "external_goal_text": "",
            "structured_goal_state": {},
            "structured_final_state": {
              "predicates": [
                "item_on(plate, dining_table)",
                "item_on(fork, dining_table)",
                "item_on(knife, dining_table)",
                "item_on(spoon, dining_table)",
                "item_on(glass, dining_table)",
                "item_on(flower, dining_table)"
              ],
              "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
            }
          },
          "benchmark_final_state_compare": {
            "benchmark": "DELTA",
            "status": "prepared_for_framework_llm_judge",
            "environment_format": "DELTA scene_graph 转成 benchmark 本地扁平环境，保留 delta_predicate/delta_affordance 属性",
            "action_format": "DELTA 官方原生动作 JSON 对象",
            "official_evaluator": "planning 结束后调用 DELTA PDDL/VAL；评测答案字段不进入 understanding/planning/final_state audit",
            "used_fields": {
              "task_context": [
                "dataset",
                "delta_accessible_items",
                "delta_env_state_predicates",
                "domain",
                "instruction",
                "loadable_containers",
                "scene_graph_cache_path",
                "task_environment_mode",
                "task_name"
              ],
              "evaluation_context": [],
              "external_goal": [
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
                "dataset": "delta",
                "task_name": "dining:allensville:episode-01",
                "domain": "dining",
                "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
                "scene_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json",
                "delta_env_state_predicates": [
                  "item_on(<item_1>, <item_2>): <item_1> is on <item_2>.",
                  "item_is_dining_table(<item>): <item> is dining_table."
                ],
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
                "task_environment_mode": "understanding_pruned"
              },
              "evaluation_context": {},
              "goal_projection": {
                "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
                "domain": "dining",
                "visible_delta_predicates": [
                  "item_on(<item_1>, <item_2>): <item_1> is on <item_2>.",
                  "item_is_dining_table(<item>): <item> is dining_table."
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
                ]
              },
              "external_goal": {
                "has_external_goal": true,
                "external_goal_state": {},
                "external_goal_text": "",
                "structured_goal_state": {},
                "structured_final_state": {
                  "predicates": [
                    "item_on(plate, dining_table)",
                    "item_on(fork, dining_table)",
                    "item_on(knife, dining_table)",
                    "item_on(spoon, dining_table)",
                    "item_on(glass, dining_table)",
                    "item_on(flower, dining_table)"
                  ],
                  "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
                }
              }
            },
            "understanding_final_state": {
              "predicates": [
                "item_on(plate, dining_table)",
                "item_on(fork, dining_table)",
                "item_on(knife, dining_table)",
                "item_on(spoon, dining_table)",
                "item_on(glass, dining_table)",
                "item_on(flower, dining_table)"
              ],
              "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
            },
            "state_diff_summary": {
              "entity_count_compared": 18,
              "changed_entity_count": 6,
              "changed_entities": [
                "flower",
                "fork",
                "glass",
                "knife",
                "plate",
                "spoon"
              ],
              "changed_entities_truncated": false,
              "robot_changed": true,
              "robot_change": {
                "changed": true,
                "before": {
                  "robot_location": "living_room",
                  "robot_holding": "空",
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
                  "domain": "dining",
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
                  ]
                },
                "after": {
                  "robot_location": "dining_room",
                  "robot_holding": "空",
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
                  "domain": "dining",
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
                  ]
                }
              }
            },
            "initial_environment_summary": {
              "available": true,
              "entity_count": 18,
              "type_counts": {
                "receptacle": 1,
                "room": 11,
                "unknown": 6
              },
              "states_sample": {},
              "relations_sample": {
                "dining_table": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_room"
                },
                "dining_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "plate": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom_2"
                },
                "bedroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "fork": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen"
                },
                "kitchen": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "knife": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen"
                },
                "spoon": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen"
                },
                "glass": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom_1"
                },
                "bedroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "flower": {
                  "direct_relation": "inside",
                  "direct_parent": "lobby"
                },
                "lobby": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "living_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_3": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                }
              }
            },
            "final_environment_summary": {
              "available": true,
              "entity_count": 18,
              "type_counts": {
                "receptacle": 1,
                "room": 11,
                "unknown": 6
              },
              "states_sample": {},
              "relations_sample": {
                "dining_table": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_room"
                },
                "dining_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "plate": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "bedroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "fork": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "kitchen": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "knife": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "spoon": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "glass": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "bedroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "flower": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "lobby": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "living_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_3": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                }
              }
            },
            "initial_robot": {
              "robot_location": "living_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            },
            "final_robot": {
              "robot_location": "dining_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            },
            "fairness_notes": [
              "本 comparer 不读取评测答案字段、官方目标字段或参考代价字段。",
              "DELTA 官方目标只在 planning 结束后的官方评测中使用。"
            ],
            "judge_contract": "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。",
            "enabled": true,
            "comparer_module": "benchmark.delta.framework.code.final_state"
          }
        },
        "llm_result": {
          "is_passed": true,
          "issue": "",
          "fix_advice": "",
          "repair_mode": "continue_from_current",
          "accepted_diffs": [
            "plate",
            "fork",
            "knife",
            "spoon",
            "glass",
            "flower"
          ],
          "unexpected_diffs": []
        },
        "benchmark_final_state_compare": {
          "benchmark": "DELTA",
          "status": "prepared_for_framework_llm_judge",
          "environment_format": "DELTA scene_graph 转成 benchmark 本地扁平环境，保留 delta_predicate/delta_affordance 属性",
          "action_format": "DELTA 官方原生动作 JSON 对象",
          "official_evaluator": "planning 结束后调用 DELTA PDDL/VAL；评测答案字段不进入 understanding/planning/final_state audit",
          "used_fields": {
            "task_context": [
              "dataset",
              "delta_accessible_items",
              "delta_env_state_predicates",
              "domain",
              "instruction",
              "loadable_containers",
              "scene_graph_cache_path",
              "task_environment_mode",
              "task_name"
            ],
            "evaluation_context": [],
            "external_goal": [
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
              "dataset": "delta",
              "task_name": "dining:allensville:episode-01",
              "domain": "dining",
              "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
              "scene_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json",
              "delta_env_state_predicates": [
                "item_on(<item_1>, <item_2>): <item_1> is on <item_2>.",
                "item_is_dining_table(<item>): <item> is dining_table."
              ],
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
              "task_environment_mode": "understanding_pruned"
            },
            "evaluation_context": {},
            "goal_projection": {
              "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
              "domain": "dining",
              "visible_delta_predicates": [
                "item_on(<item_1>, <item_2>): <item_1> is on <item_2>.",
                "item_is_dining_table(<item>): <item> is dining_table."
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
              ]
            },
            "external_goal": {
              "has_external_goal": true,
              "external_goal_state": {},
              "external_goal_text": "",
              "structured_goal_state": {},
              "structured_final_state": {
                "predicates": [
                  "item_on(plate, dining_table)",
                  "item_on(fork, dining_table)",
                  "item_on(knife, dining_table)",
                  "item_on(spoon, dining_table)",
                  "item_on(glass, dining_table)",
                  "item_on(flower, dining_table)"
                ],
                "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
              }
            }
          },
          "understanding_final_state": {
            "predicates": [
              "item_on(plate, dining_table)",
              "item_on(fork, dining_table)",
              "item_on(knife, dining_table)",
              "item_on(spoon, dining_table)",
              "item_on(glass, dining_table)",
              "item_on(flower, dining_table)"
            ],
            "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
          },
          "state_diff_summary": {
            "entity_count_compared": 18,
            "changed_entity_count": 6,
            "changed_entities": [
              "flower",
              "fork",
              "glass",
              "knife",
              "plate",
              "spoon"
            ],
            "changed_entities_truncated": false,
            "robot_changed": true,
            "robot_change": {
              "changed": true,
              "before": {
                "robot_location": "living_room",
                "robot_holding": "空",
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
                "domain": "dining",
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
                ]
              },
              "after": {
                "robot_location": "dining_room",
                "robot_holding": "空",
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
                "domain": "dining",
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
                ]
              }
            }
          },
          "initial_environment_summary": {
            "available": true,
            "entity_count": 18,
            "type_counts": {
              "receptacle": 1,
              "room": 11,
              "unknown": 6
            },
            "states_sample": {},
            "relations_sample": {
              "dining_table": {
                "direct_relation": "inside",
                "direct_parent": "dining_room"
              },
              "dining_room": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "plate": {
                "direct_relation": "inside",
                "direct_parent": "bedroom_2"
              },
              "bedroom_2": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "fork": {
                "direct_relation": "inside",
                "direct_parent": "kitchen"
              },
              "kitchen": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "knife": {
                "direct_relation": "inside",
                "direct_parent": "kitchen"
              },
              "spoon": {
                "direct_relation": "inside",
                "direct_parent": "kitchen"
              },
              "glass": {
                "direct_relation": "inside",
                "direct_parent": "bedroom_1"
              },
              "bedroom_1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "flower": {
                "direct_relation": "inside",
                "direct_parent": "lobby"
              },
              "lobby": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "living_room": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "bathroom_1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "bathroom_2": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "corridor_1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "corridor_2": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "corridor_3": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              }
            }
          },
          "final_environment_summary": {
            "available": true,
            "entity_count": 18,
            "type_counts": {
              "receptacle": 1,
              "room": 11,
              "unknown": 6
            },
            "states_sample": {},
            "relations_sample": {
              "dining_table": {
                "direct_relation": "inside",
                "direct_parent": "dining_room"
              },
              "dining_room": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "plate": {
                "direct_relation": "inside",
                "direct_parent": "dining_table"
              },
              "bedroom_2": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "fork": {
                "direct_relation": "inside",
                "direct_parent": "dining_table"
              },
              "kitchen": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "knife": {
                "direct_relation": "inside",
                "direct_parent": "dining_table"
              },
              "spoon": {
                "direct_relation": "inside",
                "direct_parent": "dining_table"
              },
              "glass": {
                "direct_relation": "inside",
                "direct_parent": "dining_table"
              },
              "bedroom_1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "flower": {
                "direct_relation": "inside",
                "direct_parent": "dining_table"
              },
              "lobby": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "living_room": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "bathroom_1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "bathroom_2": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "corridor_1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "corridor_2": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "corridor_3": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              }
            }
          },
          "initial_robot": {
            "robot_location": "living_room",
            "robot_holding": "空",
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
            "domain": "dining",
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
            ]
          },
          "final_robot": {
            "robot_location": "dining_room",
            "robot_holding": "空",
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
            "domain": "dining",
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
            ]
          },
          "fairness_notes": [
            "本 comparer 不读取评测答案字段、官方目标字段或参考代价字段。",
            "DELTA 官方目标只在 planning 结束后的官方评测中使用。"
          ],
          "judge_contract": "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。",
          "enabled": true,
          "comparer_module": "benchmark.delta.framework.code.final_state"
        },
        "has_external_goal": true,
        "final_state_packet": {
          "task_source_text": "",
          "task_context": {
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
          },
          "evaluation_context": {},
          "external_goal": {
            "has_external_goal": true,
            "external_goal_state": {},
            "external_goal_text": "",
            "structured_goal_state": {},
            "structured_final_state": {
              "predicates": [
                "item_on(plate, dining_table)",
                "item_on(fork, dining_table)",
                "item_on(knife, dining_table)",
                "item_on(spoon, dining_table)",
                "item_on(glass, dining_table)",
                "item_on(flower, dining_table)"
              ],
              "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
            }
          },
          "initial": {
            "environment": {
              "dining_table": {
                "direct_parent": "dining_room",
                "direct_relation": "inside",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_predicate:item_is_dining_table"
                ],
                "is_container": true,
                "full_path": [
                  "dining_room"
                ]
              },
              "dining_room": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "plate": {
                "direct_parent": "bedroom_2",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "bedroom_2"
                ]
              },
              "bedroom_2": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "fork": {
                "direct_parent": "kitchen",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen"
                ]
              },
              "kitchen": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "knife": {
                "direct_parent": "kitchen",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen"
                ]
              },
              "spoon": {
                "direct_parent": "kitchen",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen"
                ]
              },
              "glass": {
                "direct_parent": "bedroom_1",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "bedroom_1"
                ]
              },
              "bedroom_1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "flower": {
                "direct_parent": "lobby",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "lobby"
                ]
              },
              "lobby": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "living_room": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "bathroom_1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "bathroom_2": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "corridor_1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "corridor_2": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "corridor_3": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              }
            },
            "robot": {
              "robot_location": "living_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            }
          },
          "final": {
            "environment": {
              "dining_table": {
                "direct_parent": "dining_room",
                "direct_relation": "inside",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_predicate:item_is_dining_table"
                ],
                "is_container": true,
                "full_path": [
                  "dining_room"
                ]
              },
              "dining_room": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "plate": {
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ]
              },
              "bedroom_2": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "fork": {
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ]
              },
              "kitchen": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "knife": {
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ]
              },
              "spoon": {
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ]
              },
              "glass": {
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ]
              },
              "bedroom_1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "flower": {
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ],
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ]
              },
              "lobby": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "living_room": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "bathroom_1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "bathroom_2": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "corridor_1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "corridor_2": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "corridor_3": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              }
            },
            "robot": {
              "robot_location": "dining_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            }
          },
          "state_diff": {
            "entity_count_compared": 18,
            "changed_entity_count": 6,
            "truncated_entity_count": 0,
            "has_changes": true,
            "robot": {
              "changed": true,
              "before": {
                "robot_location": "living_room",
                "robot_holding": "空",
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
                "domain": "dining",
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
                ]
              },
              "after": {
                "robot_location": "dining_room",
                "robot_holding": "空",
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
                "domain": "dining",
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
                ]
              }
            },
            "entities": [
              {
                "name": "flower",
                "change_type": "updated",
                "before": {
                  "type": null,
                  "direct_parent": "lobby",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "lobby"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                },
                "after": {
                  "type": null,
                  "direct_parent": "dining_table",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "dining_room",
                    "dining_table"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                }
              },
              {
                "name": "fork",
                "change_type": "updated",
                "before": {
                  "type": null,
                  "direct_parent": "kitchen",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "kitchen"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                },
                "after": {
                  "type": null,
                  "direct_parent": "dining_table",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "dining_room",
                    "dining_table"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                }
              },
              {
                "name": "glass",
                "change_type": "updated",
                "before": {
                  "type": null,
                  "direct_parent": "bedroom_1",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "bedroom_1"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                },
                "after": {
                  "type": null,
                  "direct_parent": "dining_table",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "dining_room",
                    "dining_table"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                }
              },
              {
                "name": "knife",
                "change_type": "updated",
                "before": {
                  "type": null,
                  "direct_parent": "kitchen",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "kitchen"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                },
                "after": {
                  "type": null,
                  "direct_parent": "dining_table",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "dining_room",
                    "dining_table"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                }
              },
              {
                "name": "plate",
                "change_type": "updated",
                "before": {
                  "type": null,
                  "direct_parent": "bedroom_2",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "bedroom_2"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                },
                "after": {
                  "type": null,
                  "direct_parent": "dining_table",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "dining_room",
                    "dining_table"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                }
              },
              {
                "name": "spoon",
                "change_type": "updated",
                "before": {
                  "type": null,
                  "direct_parent": "kitchen",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "kitchen"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                },
                "after": {
                  "type": null,
                  "direct_parent": "dining_table",
                  "direct_relation": "inside",
                  "is_container": false,
                  "full_path": [
                    "dining_room",
                    "dining_table"
                  ],
                  "states": {},
                  "properties": [
                    "delta_accessible:true",
                    "delta_affordance:drop",
                    "delta_affordance:pick",
                    "delta_affordance:place_on",
                    "delta_predicate:item_pickable",
                    "delta_predicate:item_accessible"
                  ]
                }
              }
            ]
          },
          "trajectory": "Step 1: goto([])\nStep 2: goto([])\nStep 3: pick([])\nStep 4: goto([])\nStep 5: place_on([])\nStep 6: goto([])\nStep 7: pick([])\nStep 8: goto([])\nStep 9: place_on([])\nStep 10: goto([])\nStep 11: pick([])\nStep 12: goto([])\nStep 13: place_on([])\nStep 14: goto([])\nStep 15: pick([])\nStep 16: goto([])\nStep 17: place_on([])\nStep 18: goto([])\nStep 19: pick([])\nStep 20: goto([])\nStep 21: place_on([])\nStep 22: goto([])\nStep 23: pick([])\nStep 24: goto([])\nStep 25: place_on([])",
          "benchmark_final_state_compare": {
            "benchmark": "DELTA",
            "status": "prepared_for_framework_llm_judge",
            "environment_format": "DELTA scene_graph 转成 benchmark 本地扁平环境，保留 delta_predicate/delta_affordance 属性",
            "action_format": "DELTA 官方原生动作 JSON 对象",
            "official_evaluator": "planning 结束后调用 DELTA PDDL/VAL；评测答案字段不进入 understanding/planning/final_state audit",
            "used_fields": {
              "task_context": [
                "dataset",
                "delta_accessible_items",
                "delta_env_state_predicates",
                "domain",
                "instruction",
                "loadable_containers",
                "scene_graph_cache_path",
                "task_environment_mode",
                "task_name"
              ],
              "evaluation_context": [],
              "external_goal": [
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
                "dataset": "delta",
                "task_name": "dining:allensville:episode-01",
                "domain": "dining",
                "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
                "scene_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json",
                "delta_env_state_predicates": [
                  "item_on(<item_1>, <item_2>): <item_1> is on <item_2>.",
                  "item_is_dining_table(<item>): <item> is dining_table."
                ],
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
                "task_environment_mode": "understanding_pruned"
              },
              "evaluation_context": {},
              "goal_projection": {
                "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
                "domain": "dining",
                "visible_delta_predicates": [
                  "item_on(<item_1>, <item_2>): <item_1> is on <item_2>.",
                  "item_is_dining_table(<item>): <item> is dining_table."
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
                ]
              },
              "external_goal": {
                "has_external_goal": true,
                "external_goal_state": {},
                "external_goal_text": "",
                "structured_goal_state": {},
                "structured_final_state": {
                  "predicates": [
                    "item_on(plate, dining_table)",
                    "item_on(fork, dining_table)",
                    "item_on(knife, dining_table)",
                    "item_on(spoon, dining_table)",
                    "item_on(glass, dining_table)",
                    "item_on(flower, dining_table)"
                  ],
                  "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
                }
              }
            },
            "understanding_final_state": {
              "predicates": [
                "item_on(plate, dining_table)",
                "item_on(fork, dining_table)",
                "item_on(knife, dining_table)",
                "item_on(spoon, dining_table)",
                "item_on(glass, dining_table)",
                "item_on(flower, dining_table)"
              ],
              "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
            },
            "state_diff_summary": {
              "entity_count_compared": 18,
              "changed_entity_count": 6,
              "changed_entities": [
                "flower",
                "fork",
                "glass",
                "knife",
                "plate",
                "spoon"
              ],
              "changed_entities_truncated": false,
              "robot_changed": true,
              "robot_change": {
                "changed": true,
                "before": {
                  "robot_location": "living_room",
                  "robot_holding": "空",
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
                  "domain": "dining",
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
                  ]
                },
                "after": {
                  "robot_location": "dining_room",
                  "robot_holding": "空",
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
                  "domain": "dining",
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
                  ]
                }
              }
            },
            "initial_environment_summary": {
              "available": true,
              "entity_count": 18,
              "type_counts": {
                "receptacle": 1,
                "room": 11,
                "unknown": 6
              },
              "states_sample": {},
              "relations_sample": {
                "dining_table": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_room"
                },
                "dining_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "plate": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom_2"
                },
                "bedroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "fork": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen"
                },
                "kitchen": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "knife": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen"
                },
                "spoon": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen"
                },
                "glass": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom_1"
                },
                "bedroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "flower": {
                  "direct_relation": "inside",
                  "direct_parent": "lobby"
                },
                "lobby": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "living_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_3": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                }
              }
            },
            "final_environment_summary": {
              "available": true,
              "entity_count": 18,
              "type_counts": {
                "receptacle": 1,
                "room": 11,
                "unknown": 6
              },
              "states_sample": {},
              "relations_sample": {
                "dining_table": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_room"
                },
                "dining_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "plate": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "bedroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "fork": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "kitchen": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "knife": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "spoon": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "glass": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "bedroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "flower": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "lobby": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "living_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_3": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                }
              }
            },
            "initial_robot": {
              "robot_location": "living_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            },
            "final_robot": {
              "robot_location": "dining_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            },
            "fairness_notes": [
              "本 comparer 不读取评测答案字段、官方目标字段或参考代价字段。",
              "DELTA 官方目标只在 planning 结束后的官方评测中使用。"
            ],
            "judge_contract": "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。",
            "enabled": true,
            "comparer_module": "benchmark.delta.framework.code.final_state"
          }
        },
        "state_diff": {
          "entity_count_compared": 18,
          "changed_entity_count": 6,
          "truncated_entity_count": 0,
          "has_changes": true,
          "robot": {
            "changed": true,
            "before": {
              "robot_location": "living_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            },
            "after": {
              "robot_location": "dining_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            }
          },
          "entities": [
            {
              "name": "flower",
              "change_type": "updated",
              "before": {
                "type": null,
                "direct_parent": "lobby",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "lobby"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "fork",
              "change_type": "updated",
              "before": {
                "type": null,
                "direct_parent": "kitchen",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "kitchen"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "glass",
              "change_type": "updated",
              "before": {
                "type": null,
                "direct_parent": "bedroom_1",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "bedroom_1"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "knife",
              "change_type": "updated",
              "before": {
                "type": null,
                "direct_parent": "kitchen",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "kitchen"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "plate",
              "change_type": "updated",
              "before": {
                "type": null,
                "direct_parent": "bedroom_2",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "bedroom_2"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            },
            {
              "name": "spoon",
              "change_type": "updated",
              "before": {
                "type": null,
                "direct_parent": "kitchen",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "kitchen"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "dining_table",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "dining_room",
                  "dining_table"
                ],
                "states": {},
                "properties": [
                  "delta_accessible:true",
                  "delta_affordance:drop",
                  "delta_affordance:pick",
                  "delta_affordance:place_on",
                  "delta_predicate:item_pickable",
                  "delta_predicate:item_accessible"
                ]
              }
            }
          ]
        }
      },
      "state_diff": {
        "entity_count_compared": 18,
        "changed_entity_count": 6,
        "truncated_entity_count": 0,
        "has_changes": true,
        "robot": {
          "changed": true,
          "before": {
            "robot_location": "living_room",
            "robot_holding": "空",
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
            "domain": "dining",
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
            ]
          },
          "after": {
            "robot_location": "dining_room",
            "robot_holding": "空",
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
            "domain": "dining",
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
            ]
          }
        },
        "entities": [
          {
            "name": "flower",
            "change_type": "updated",
            "before": {
              "type": null,
              "direct_parent": "lobby",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "lobby"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            },
            "after": {
              "type": null,
              "direct_parent": "dining_table",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "dining_room",
                "dining_table"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            }
          },
          {
            "name": "fork",
            "change_type": "updated",
            "before": {
              "type": null,
              "direct_parent": "kitchen",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "kitchen"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            },
            "after": {
              "type": null,
              "direct_parent": "dining_table",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "dining_room",
                "dining_table"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            }
          },
          {
            "name": "glass",
            "change_type": "updated",
            "before": {
              "type": null,
              "direct_parent": "bedroom_1",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "bedroom_1"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            },
            "after": {
              "type": null,
              "direct_parent": "dining_table",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "dining_room",
                "dining_table"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            }
          },
          {
            "name": "knife",
            "change_type": "updated",
            "before": {
              "type": null,
              "direct_parent": "kitchen",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "kitchen"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            },
            "after": {
              "type": null,
              "direct_parent": "dining_table",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "dining_room",
                "dining_table"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            }
          },
          {
            "name": "plate",
            "change_type": "updated",
            "before": {
              "type": null,
              "direct_parent": "bedroom_2",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "bedroom_2"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            },
            "after": {
              "type": null,
              "direct_parent": "dining_table",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "dining_room",
                "dining_table"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            }
          },
          {
            "name": "spoon",
            "change_type": "updated",
            "before": {
              "type": null,
              "direct_parent": "kitchen",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "kitchen"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            },
            "after": {
              "type": null,
              "direct_parent": "dining_table",
              "direct_relation": "inside",
              "is_container": false,
              "full_path": [
                "dining_room",
                "dining_table"
              ],
              "states": {},
              "properties": [
                "delta_accessible:true",
                "delta_affordance:drop",
                "delta_affordance:pick",
                "delta_affordance:place_on",
                "delta_predicate:item_pickable",
                "delta_predicate:item_accessible"
              ]
            }
          }
        ]
      }
    },
    "planning_feature_records": [
      {
        "process_name": "sandbox_validation",
        "enabled": true,
        "status": "passed",
        "config": {
          "todo_step_adapter_path": "benchmark.delta.framework.code.native_actions.delta_native_step_to_skill_call",
          "validator": "todo_schema"
        },
        "inputs": {
          "todo_list": {
            "count": 25,
            "sample": [
              {
                "step": 1,
                "action": "goto",
                "agent": "robot",
                "room_1": "living_room",
                "room_2": "dining_room"
              },
              {
                "step": 2,
                "action": "goto",
                "agent": "robot",
                "room_1": "dining_room",
                "room_2": "kitchen"
              },
              {
                "step": 3,
                "action": "pick",
                "agent": "robot",
                "item": "fork",
                "room": "kitchen"
              },
              {
                "step": 4,
                "action": "goto",
                "agent": "robot",
                "room_1": "kitchen",
                "room_2": "dining_room"
              },
              {
                "step": 5,
                "action": "place_on",
                "agent": "robot",
                "item_1": "fork",
                "item_2": "dining_table",
                "room": "dining_room"
              },
              {
                "step": 6,
                "action": "goto",
                "agent": "robot",
                "room_1": "dining_room",
                "room_2": "kitchen"
              },
              {
                "step": 7,
                "action": "pick",
                "agent": "robot",
                "item": "knife",
                "room": "kitchen"
              },
              {
                "step": 8,
                "action": "goto",
                "agent": "robot",
                "room_1": "kitchen",
                "room_2": "dining_room"
              }
            ],
            "truncated": true
          },
          "initial_environment": {
            "available": true,
            "entity_count": 18,
            "type_counts": {
              "receptacle": 1,
              "room": 11,
              "unknown": 6
            },
            "entities_sample": [
              "bathroom_1",
              "bathroom_2",
              "bedroom_1",
              "bedroom_2",
              "corridor_1",
              "corridor_2",
              "corridor_3",
              "dining_room",
              "dining_table",
              "flower",
              "fork",
              "glass",
              "kitchen",
              "knife",
              "living_room",
              "lobby",
              "plate",
              "spoon"
            ],
            "entities_truncated": false,
            "states_sample": {}
          },
          "initial_robot": {
            "robot_location": "living_room",
            "robot_holding": "空",
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
            "domain": "dining",
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
            ]
          }
        },
        "outputs": {
          "validated_steps": {
            "count": 0,
            "sample": [],
            "truncated": false
          },
          "validated_todo_actions": {
            "count": 25,
            "sample": [
              {
                "step": 1,
                "action": "goto",
                "agent": "robot",
                "room_1": "living_room",
                "room_2": "dining_room"
              },
              {
                "step": 2,
                "action": "goto",
                "agent": "robot",
                "room_1": "dining_room",
                "room_2": "kitchen"
              },
              {
                "step": 3,
                "action": "pick",
                "agent": "robot",
                "item": "fork",
                "room": "kitchen"
              },
              {
                "step": 4,
                "action": "goto",
                "agent": "robot",
                "room_1": "kitchen",
                "room_2": "dining_room"
              },
              {
                "step": 5,
                "action": "place_on",
                "agent": "robot",
                "item_1": "fork",
                "item_2": "dining_table",
                "room": "dining_room"
              },
              {
                "step": 6,
                "action": "goto",
                "agent": "robot",
                "room_1": "dining_room",
                "room_2": "kitchen"
              },
              {
                "step": 7,
                "action": "pick",
                "agent": "robot",
                "item": "knife",
                "room": "kitchen"
              },
              {
                "step": 8,
                "action": "goto",
                "agent": "robot",
                "room_1": "kitchen",
                "room_2": "dining_room"
              }
            ],
            "truncated": true
          },
          "validated_audit_steps": {
            "count": 25,
            "sample": [
              {
                "step": 1,
                "action": "goto",
                "agent": "robot",
                "room_1": "living_room",
                "room_2": "dining_room",
                "execution": {
                  "skill": "goto",
                  "parameters": {
                    "from": "living_room",
                    "to": "dining_room"
                  }
                }
              },
              {
                "step": 2,
                "action": "goto",
                "agent": "robot",
                "room_1": "dining_room",
                "room_2": "kitchen",
                "execution": {
                  "skill": "goto",
                  "parameters": {
                    "from": "dining_room",
                    "to": "kitchen"
                  }
                }
              },
              {
                "step": 3,
                "action": "pick",
                "agent": "robot",
                "item": "fork",
                "room": "kitchen",
                "execution": {
                  "skill": "pick",
                  "parameters": {
                    "item": "fork",
                    "room": "kitchen"
                  }
                }
              },
              {
                "step": 4,
                "action": "goto",
                "agent": "robot",
                "room_1": "kitchen",
                "room_2": "dining_room",
                "execution": {
                  "skill": "goto",
                  "parameters": {
                    "from": "kitchen",
                    "to": "dining_room"
                  }
                }
              },
              {
                "step": 5,
                "action": "place_on",
                "agent": "robot",
                "item_1": "fork",
                "item_2": "dining_table",
                "room": "dining_room",
                "execution": {
                  "skill": "place_on",
                  "parameters": {
                    "item": "fork",
                    "surface": "dining_table",
                    "room": "dining_room"
                  }
                }
              },
              {
                "step": 6,
                "action": "goto",
                "agent": "robot",
                "room_1": "dining_room",
                "room_2": "kitchen",
                "execution": {
                  "skill": "goto",
                  "parameters": {
                    "from": "dining_room",
                    "to": "kitchen"
                  }
                }
              },
              {
                "step": 7,
                "action": "pick",
                "agent": "robot",
                "item": "knife",
                "room": "kitchen",
                "execution": {
                  "skill": "pick",
                  "parameters": {
                    "item": "knife",
                    "room": "kitchen"
                  }
                }
              },
              {
                "step": 8,
                "action": "goto",
                "agent": "robot",
                "room_1": "kitchen",
                "room_2": "dining_room",
                "execution": {
                  "skill": "goto",
                  "parameters": {
                    "from": "kitchen",
                    "to": "dining_room"
                  }
                }
              }
            ],
            "truncated": true
          },
          "final_environment": {
            "available": true,
            "entity_count": 18,
            "type_counts": {
              "receptacle": 1,
              "room": 11,
              "unknown": 6
            },
            "entities_sample": [
              "bathroom_1",
              "bathroom_2",
              "bedroom_1",
              "bedroom_2",
              "corridor_1",
              "corridor_2",
              "corridor_3",
              "dining_room",
              "dining_table",
              "flower",
              "fork",
              "glass",
              "kitchen",
              "knife",
              "living_room",
              "lobby",
              "plate",
              "spoon"
            ],
            "entities_truncated": false,
            "states_sample": {}
          },
          "final_robot": {
            "robot_location": "dining_room",
            "robot_holding": "空",
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
            "domain": "dining",
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
            ]
          },
          "debug_event_counts": {
            "step_check": 25
          },
          "sandbox_rejections": [],
          "planning_evaluator_failures": [],
          "failed_action": {},
          "failure_layer": "",
          "failure_category": "",
          "error_feedback": ""
        }
      },
      {
        "process_name": "dependency_repair",
        "enabled": false,
        "status": "disabled",
        "config": {
          "repair_strategy": "retrac",
          "max_backtrack_depth": 3,
          "max_subtree_actions": 80
        },
        "inputs": {
          "sandbox_failure_present": false,
          "debug_event_counts": {}
        },
        "outputs": {
          "sda_state": {},
          "validated_steps": {
            "count": 0,
            "sample": [],
            "truncated": false
          },
          "validated_todo_actions": {
            "count": 25,
            "sample": [
              {
                "step": 1,
                "action": "goto",
                "agent": "robot",
                "room_1": "living_room",
                "room_2": "dining_room"
              },
              {
                "step": 2,
                "action": "goto",
                "agent": "robot",
                "room_1": "dining_room",
                "room_2": "kitchen"
              },
              {
                "step": 3,
                "action": "pick",
                "agent": "robot",
                "item": "fork",
                "room": "kitchen"
              },
              {
                "step": 4,
                "action": "goto",
                "agent": "robot",
                "room_1": "kitchen",
                "room_2": "dining_room"
              },
              {
                "step": 5,
                "action": "place_on",
                "agent": "robot",
                "item_1": "fork",
                "item_2": "dining_table",
                "room": "dining_room"
              },
              {
                "step": 6,
                "action": "goto",
                "agent": "robot",
                "room_1": "dining_room",
                "room_2": "kitchen"
              },
              {
                "step": 7,
                "action": "pick",
                "agent": "robot",
                "item": "knife",
                "room": "kitchen"
              },
              {
                "step": 8,
                "action": "goto",
                "agent": "robot",
                "room_1": "kitchen",
                "room_2": "dining_room"
              }
            ],
            "truncated": true
          }
        }
      },
      {
        "process_name": "final_state_audit",
        "enabled": true,
        "status": "passed",
        "config": {
          "state_diff_audit": true,
          "auditor": "framework.planning.state_diff_audit_llm",
          "benchmark_comparer": "benchmark.delta.framework.code.final_state"
        },
        "inputs": {
          "understanding_goal": {
            "intent": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
            "required_item_names": {
              "targets": {
                "primary": [
                  "dining_table"
                ],
                "alternatives": []
              },
              "tools": {
                "primary": [
                  "plate",
                  "fork",
                  "knife",
                  "spoon",
                  "glass"
                ],
                "alternatives": []
              },
              "receptacles": {
                "primary": [
                  "flower"
                ],
                "alternatives": []
              }
            },
            "quantity_constraints": [],
            "goal_state": {},
            "desired_state": {},
            "target_state": {},
            "final_state": {
              "predicates": [
                "item_on(plate, dining_table)",
                "item_on(fork, dining_table)",
                "item_on(knife, dining_table)",
                "item_on(spoon, dining_table)",
                "item_on(glass, dining_table)",
                "item_on(flower, dining_table)"
              ],
              "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
            }
          },
          "has_external_goal": false,
          "external_goal_state": {},
          "simulated_steps": {
            "count": 25,
            "sample": [
              {
                "step": 1,
                "action": "goto",
                "agent": "robot",
                "room_1": "living_room",
                "room_2": "dining_room"
              },
              {
                "step": 2,
                "action": "goto",
                "agent": "robot",
                "room_1": "dining_room",
                "room_2": "kitchen"
              },
              {
                "step": 3,
                "action": "pick",
                "agent": "robot",
                "item": "fork",
                "room": "kitchen"
              },
              {
                "step": 4,
                "action": "goto",
                "agent": "robot",
                "room_1": "kitchen",
                "room_2": "dining_room"
              },
              {
                "step": 5,
                "action": "place_on",
                "agent": "robot",
                "item_1": "fork",
                "item_2": "dining_table",
                "room": "dining_room"
              },
              {
                "step": 6,
                "action": "goto",
                "agent": "robot",
                "room_1": "dining_room",
                "room_2": "kitchen"
              },
              {
                "step": 7,
                "action": "pick",
                "agent": "robot",
                "item": "knife",
                "room": "kitchen"
              },
              {
                "step": 8,
                "action": "goto",
                "agent": "robot",
                "room_1": "kitchen",
                "room_2": "dining_room"
              }
            ],
            "truncated": true
          },
          "initial_environment": {
            "available": true,
            "entity_count": 18,
            "type_counts": {
              "receptacle": 1,
              "room": 11,
              "unknown": 6
            },
            "entities_sample": [
              "bathroom_1",
              "bathroom_2",
              "bedroom_1",
              "bedroom_2",
              "corridor_1",
              "corridor_2",
              "corridor_3",
              "dining_room",
              "dining_table",
              "flower",
              "fork",
              "glass",
              "kitchen",
              "knife",
              "living_room",
              "lobby",
              "plate",
              "spoon"
            ],
            "entities_truncated": false,
            "states_sample": {}
          },
          "initial_robot": {
            "robot_location": "living_room",
            "robot_holding": "空",
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
            "domain": "dining",
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
            ]
          },
          "final_environment": {
            "available": true,
            "entity_count": 18,
            "type_counts": {
              "receptacle": 1,
              "room": 11,
              "unknown": 6
            },
            "entities_sample": [
              "bathroom_1",
              "bathroom_2",
              "bedroom_1",
              "bedroom_2",
              "corridor_1",
              "corridor_2",
              "corridor_3",
              "dining_room",
              "dining_table",
              "flower",
              "fork",
              "glass",
              "kitchen",
              "knife",
              "living_room",
              "lobby",
              "plate",
              "spoon"
            ],
            "entities_truncated": false,
            "states_sample": {}
          },
          "final_robot": {
            "robot_location": "dining_room",
            "robot_holding": "空",
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
            "domain": "dining",
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
            ]
          }
        },
        "outputs": {
          "state_diff": {
            "available": true,
            "entity_count_compared": 18,
            "changed_entity_count": 6,
            "changed_entities_sample": [
              "flower",
              "fork",
              "glass",
              "knife",
              "plate",
              "spoon"
            ],
            "changed_entities_truncated": false,
            "robot_changed": true
          },
          "audit_passed": true,
          "issue": "",
          "repair_mode": "continue_from_current",
          "benchmark_compare": {
            "benchmark": "DELTA",
            "status": "prepared_for_framework_llm_judge",
            "environment_format": "DELTA scene_graph 转成 benchmark 本地扁平环境，保留 delta_predicate/delta_affordance 属性",
            "action_format": "DELTA 官方原生动作 JSON 对象",
            "official_evaluator": "planning 结束后调用 DELTA PDDL/VAL；评测答案字段不进入 understanding/planning/final_state audit",
            "used_fields": {
              "task_context": [
                "dataset",
                "delta_accessible_items",
                "delta_env_state_predicates",
                "domain",
                "instruction",
                "loadable_containers",
                "scene_graph_cache_path",
                "task_environment_mode",
                "task_name"
              ],
              "evaluation_context": [],
              "external_goal": [
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
                "dataset": "delta",
                "task_name": "dining:allensville:episode-01",
                "domain": "dining",
                "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
                "scene_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json",
                "delta_env_state_predicates": [
                  "item_on(<item_1>, <item_2>): <item_1> is on <item_2>.",
                  "item_is_dining_table(<item>): <item> is dining_table."
                ],
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
                  {
                    "_truncated": 14
                  }
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
                "task_environment_mode": "understanding_pruned"
              },
              "evaluation_context": {},
              "goal_projection": {
                "instruction": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
                "domain": "dining",
                "visible_delta_predicates": [
                  "item_on(<item_1>, <item_2>): <item_1> is on <item_2>.",
                  "item_is_dining_table(<item>): <item> is dining_table."
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
                ]
              },
              "external_goal": {
                "has_external_goal": true,
                "external_goal_state": {},
                "external_goal_text": "",
                "structured_goal_state": {},
                "structured_final_state": {
                  "predicates": [
                    "item_on(plate, dining_table)",
                    "item_on(fork, dining_table)",
                    "item_on(knife, dining_table)",
                    "item_on(spoon, dining_table)",
                    "item_on(glass, dining_table)",
                    "item_on(flower, dining_table)"
                  ],
                  "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
                }
              }
            },
            "understanding_final_state": {
              "predicates": [
                "item_on(plate, dining_table)",
                "item_on(fork, dining_table)",
                "item_on(knife, dining_table)",
                "item_on(spoon, dining_table)",
                "item_on(glass, dining_table)",
                "item_on(flower, dining_table)"
              ],
              "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
            },
            "state_diff_summary": {
              "entity_count_compared": 18,
              "changed_entity_count": 6,
              "changed_entities": [
                "flower",
                "fork",
                "glass",
                "knife",
                "plate",
                "spoon"
              ],
              "changed_entities_truncated": false,
              "robot_changed": true,
              "robot_change": {
                "changed": true,
                "before": {
                  "robot_location": "living_room",
                  "robot_holding": "空",
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
                  "domain": "dining",
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
                  ]
                },
                "after": {
                  "robot_location": "dining_room",
                  "robot_holding": "空",
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
                  "domain": "dining",
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
                  ]
                }
              }
            },
            "initial_environment_summary": {
              "available": true,
              "entity_count": 18,
              "type_counts": {
                "receptacle": 1,
                "room": 11,
                "unknown": 6
              },
              "states_sample": {},
              "relations_sample": {
                "dining_table": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_room"
                },
                "dining_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "plate": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom_2"
                },
                "bedroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "fork": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen"
                },
                "kitchen": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "knife": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen"
                },
                "spoon": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen"
                },
                "glass": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom_1"
                },
                "bedroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "flower": {
                  "direct_relation": "inside",
                  "direct_parent": "lobby"
                },
                "lobby": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "living_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_3": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                }
              }
            },
            "final_environment_summary": {
              "available": true,
              "entity_count": 18,
              "type_counts": {
                "receptacle": 1,
                "room": 11,
                "unknown": 6
              },
              "states_sample": {},
              "relations_sample": {
                "dining_table": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_room"
                },
                "dining_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "plate": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "bedroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "fork": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "kitchen": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "knife": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "spoon": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "glass": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "bedroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "flower": {
                  "direct_relation": "inside",
                  "direct_parent": "dining_table"
                },
                "lobby": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "living_room": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "bathroom_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_2": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "corridor_3": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                }
              }
            },
            "initial_robot": {
              "robot_location": "living_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            },
            "final_robot": {
              "robot_location": "dining_room",
              "robot_holding": "空",
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
              "domain": "dining",
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
              ]
            },
            "fairness_notes": [
              "本 comparer 不读取评测答案字段、官方目标字段或参考代价字段。",
              "DELTA 官方目标只在 planning 结束后的官方评测中使用。"
            ],
            "judge_contract": "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。",
            "enabled": true,
            "comparer_module": "benchmark.delta.framework.code.final_state"
          }
        }
      }
    ],
    "planning_debug_events": {
      "count": 29,
      "sample": [
        {
          "layer": "repair_strategy",
          "type": "selected",
          "strategy": "retrac",
          "source": "planning.evaluation.repair_strategy"
        },
        {
          "layer": "todo_contract",
          "type": "passed",
          "todo_count": 25
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "goto",
          "parameters": {
            "from": "living_room",
            "to": "dining_room"
          },
          "todo_step": {
            "step": 1,
            "action": "goto",
            "agent": "robot",
            "room_1": "living_room",
            "room_2": "dining_room"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "goto",
          "parameters": {
            "from": "dining_room",
            "to": "kitchen"
          },
          "todo_step": {
            "step": 2,
            "action": "goto",
            "agent": "robot",
            "room_1": "dining_room",
            "room_2": "kitchen"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "pick",
          "parameters": {
            "item": "fork",
            "room": "kitchen"
          },
          "todo_step": {
            "step": 3,
            "action": "pick",
            "agent": "robot",
            "item": "fork",
            "room": "kitchen"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "goto",
          "parameters": {
            "from": "kitchen",
            "to": "dining_room"
          },
          "todo_step": {
            "step": 4,
            "action": "goto",
            "agent": "robot",
            "room_1": "kitchen",
            "room_2": "dining_room"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "place_on",
          "parameters": {
            "item": "fork",
            "surface": "dining_table",
            "room": "dining_room"
          },
          "todo_step": {
            "step": 5,
            "action": "place_on",
            "agent": "robot",
            "item_1": "fork",
            "item_2": "dining_table",
            "room": "dining_room"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "goto",
          "parameters": {
            "from": "dining_room",
            "to": "kitchen"
          },
          "todo_step": {
            "step": 6,
            "action": "goto",
            "agent": "robot",
            "room_1": "dining_room",
            "room_2": "kitchen"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        }
      ],
      "truncated": true
    }
  }
}
```

## 7. Sandbox / ReTrac 统计

```json
{
  "sandbox_check_count": 0,
  "sandbox_failed_count": 0,
  "todo_contract_status": "not_recorded",
  "todo_contract_events": [],
  "re_trac_failed_lessons": {},
  "evaluator_findings": [],
  "validated_steps_count": null
}
```

## 8. Contract / Sandbox / Audit 逐事件记录

```json
[]
```

## 9. LLM 全量输入输出

### Turn 1: understanding

#### Input
```json
[
  {
    "type": "system",
    "content": "任务：把 DELTA benchmark case 输入抽取成结构化任务理解。\n只返回 JSON；不要解释，不要输出 Markdown。\n\n允许使用的 DELTA 场景实体名：\n[\"banana_peel\", \"bathroom_1\", \"bathroom_2\", \"bed_1\", \"bed_2\", \"bedroom_1\", \"bedroom_2\", \"book\", \"bowl_2\", \"bowl_3\", \"chair_1\", \"chair_2\", \"chair_3\", \"chair_4\", \"chair_5\", \"clock\", \"cola_can\", \"corridor_1\", \"corridor_2\", \"corridor_3\", \"couch\", \"cpu\", \"desk\", \"dining_room\", \"dining_table\", \"flower\", \"fork\", \"fridge_1\", \"fridge_2\", \"fridge_3\", \"glass\", \"gpu\", \"kitchen\", \"knife\", \"lamp\", \"living_room\", \"lobby\", \"locker\", \"mainboard\", \"microwave\", \"mop\", \"oven\", \"paper\", \"plant_1\", \"plant_2\", \"plate\", \"psu\", \"ram\", \"robot_hub\", \"rotting_apple\", \"rubbish_bin\", \"shelf\", \"sink_1\", \"sink_2\", \"spoon\", \"ssd\", \"toilet_1\", \"toilet_2\"]\n\nDELTA 任务上下文 JSON：\n{\n  \"dataset\": \"delta\",\n  \"task_name\": \"dining:allensville:episode-01\",\n  \"domain\": \"dining\",\n  \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n  \"task_source\": \"delta_data_example_py\",\n  \"environment_source\": \"delta_data_scene_graph_py\",\n  \"scene_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json\",\n  \"delta_add_obj_types\": [],\n  \"delta_env_state_predicates\": [\n    \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n    \"item_is_dining_table(<item>): <item> is dining_table.\"\n  ],\n  \"delta_initial_predicates\": [\n    \"item_is_dining_table dining_table\",\n    \"item_pickable plate\",\n    \"item_accessible plate\",\n    \"item_pickable fork\",\n    \"item_accessible fork\",\n    \"item_pickable knife\",\n    \"item_accessible knife\",\n    \"item_pickable spoon\",\n    \"item_accessible spoon\",\n    \"item_pickable glass\",\n    \"item_accessible glass\",\n    \"item_pickable flower\",\n    \"item_accessible flower\"\n  ],\n  \"delta_room_neighbors\": {\n    \"bathroom_1\": [\n      \"corridor_2\"\n    ],\n    \"bathroom_2\": [\n      \"corridor_3\"\n    ],\n    \"bedroom_1\": [\n      \"corridor_2\"\n    ],\n    \"bedroom_2\": [\n      \"corridor_3\"\n    ],\n    \"corridor_1\": [\n      \"lobby\",\n      \"corridor_3\"\n    ],\n    \"corridor_2\": [\n      \"bathroom_1\",\n      \"bedroom_1\",\n      \"corridor_3\"\n    ],\n    \"corridor_3\": [\n      \"corridor_1\",\n      \"corridor_2\",\n      \"bathroom_2\",\n      \"bedroom_2\",\n      \"kitchen\",\n      \"living_room\"\n    ],\n    \"dining_room\": [\n      \"kitchen\",\n      \"living_room\"\n    ],\n    \"kitchen\": [\n      \"corridor_3\",\n      \"dining_room\"\n    ],\n    \"living_room\": [\n      \"corridor_3\",\n      \"dining_room\"\n    ],\n    \"lobby\": [\n      \"corridor_1\"\n    ]\n  },\n  \"delta_accessible_items\": [\n    \"psu\",\n    \"sink_1\",\n    \"mop\",\n    \"gpu\",\n    \"sink_2\",\n    \"mainboard\",\n    \"glass\",\n    \"shelf\",\n    \"book\",\n    \"cpu\",\n    \"rotting_apple\",\n    \"plate\",\n    \"lamp\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"ssd\",\n    \"cola_can\",\n    \"dining_table\",\n    \"knife\",\n    \"fork\",\n    \"spoon\",\n    \"microwave\",\n    \"oven\",\n    \"rubbish_bin\",\n    \"fridge_3\",\n    \"desk\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"robot_hub\",\n    \"ram\",\n    \"banana_peel\",\n    \"flower\",\n    \"locker\",\n    \"paper\"\n  ],\n  \"loadable_containers\": [\n    {\n      \"name\": \"shelf\",\n      \"room\": \"bedroom_1\",\n      \"is_loaded\": true,\n      \"contents\": [\n        \"book\"\n      ],\n      \"affordances\": [\n        \"drop\",\n        \"load\",\n        \"pick\",\n        \"unload\"\n      ]\n    },\n    {\n      \"name\": \"locker\",\n      \"room\": \"lobby\",\n      \"is_loaded\": true,\n      \"contents\": [\n        \"paper\"\n      ],\n      \"affordances\": [\n        \"drop\",\n        \"load\",\n        \"pick\",\n        \"unload\"\n      ]\n    }\n  ],\n  \"task_environment_mode\": \"understanding_pruned\",\n  \"available_entities\": [\n    \"banana_peel\",\n    \"bathroom_1\",\n    \"bathroom_2\",\n    \"bed_1\",\n    \"bed_2\",\n    \"bedroom_1\",\n    \"bedroom_2\",\n    \"book\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"chair_1\",\n    \"chair_2\",\n    \"chair_3\",\n    \"chair_4\",\n    \"chair_5\",\n    \"clock\",\n    \"cola_can\",\n    \"corridor_1\",\n    \"corridor_2\",\n    \"corridor_3\",\n    \"couch\",\n    \"cpu\",\n    \"desk\",\n    \"dining_room\",\n    \"dining_table\",\n    \"flower\",\n    \"fork\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"fridge_3\",\n    \"glass\",\n    \"gpu\",\n    \"kitchen\",\n    \"knife\",\n    \"lamp\",\n    \"living_room\",\n    \"lobby\",\n    \"locker\",\n    \"mainboard\",\n    \"microwave\",\n    \"mop\",\n    \"oven\",\n    \"paper\",\n    \"plant_1\",\n    \"plant_2\",\n    \"plate\",\n    \"psu\",\n    \"ram\",\n    \"robot_hub\",\n    \"rotting_apple\",\n    \"rubbish_bin\",\n    \"shelf\",\n    \"sink_1\",\n    \"sink_2\",\n    \"spoon\",\n    \"ssd\",\n    \"toilet_1\",\n    \"toilet_2\"\n  ]\n}\n任务上下文中的 domain、scene_name、delta_env_state、delta_add_obj_types、delta_accessible_items、delta_env_state_predicates 是本 benchmark 的 grounding 材料；不要把它们改写成其他 benchmark 的字段。\n\nDELTA 可用 skill 摘要：\n[\n  {\n    \"name\": \"goto\",\n    \"description\": \"DELTA official executable goto action.\",\n    \"planning_contract\": {\n      \"planner_location_param\": \"to\",\n      \"planner_action_name\": \"goto\",\n      \"planner_required_fields\": \"action,agent,room_1,room_2\",\n      \"planner_fixed_fields\": \"action=goto;agent=robot\",\n      \"planner_room_fields\": \"room_1,room_2\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean,dining,office,pc\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"pick\",\n    \"description\": \"DELTA official executable pick action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_requires_empty_hand\": \"true\",\n      \"planner_action_name\": \"pick\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=pick;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean,dining,office,pc\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"drop\",\n    \"description\": \"DELTA official executable drop action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"room\",\n      \"planner_action_name\": \"drop\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=drop;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean,dining,office,pc\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"place_on\",\n    \"description\": \"DELTA official executable place_on action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"surface\",\n      \"planner_action_name\": \"place_on\",\n      \"planner_required_fields\": \"action,agent,item_1,item_2,room\",\n      \"planner_fixed_fields\": \"action=place_on;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"dining\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"dispose\",\n    \"description\": \"DELTA official executable dispose action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"disposal\",\n      \"planner_effect_state_key\": \"isDisposed\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"dispose\",\n      \"planner_required_fields\": \"action,agent,item_1,item_2,room\",\n      \"planner_fixed_fields\": \"action=dispose;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"mop_floor\",\n    \"description\": \"DELTA official executable mop_floor action.\",\n    \"planning_contract\": {\n      \"planner_location_param\": \"room\",\n      \"planner_effect_state_key\": \"floor_clean\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"mop_floor\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=mop_floor;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"clean_mop\",\n    \"description\": \"DELTA official executable clean_mop action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"tool\",\n      \"planner_location_param\": \"water_source\",\n      \"planner_effect_state_key\": \"isClean\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"clean_mop\",\n      \"planner_required_fields\": \"action,agent,item_1,item_2,room\",\n      \"planner_fixed_fields\": \"action=clean_mop;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"charge\",\n    \"description\": \"DELTA official executable charge action.\",\n    \"planning_contract\": {\n      \"planner_location_param\": \"station\",\n      \"planner_requires_empty_hand\": \"true\",\n      \"planner_effect_state_key\": \"battery_full\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"charge\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=charge;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"assemble\",\n    \"description\": \"DELTA official executable assemble action.\",\n    \"planning_contract\": {\n      \"planner_target_param\": \"target_pc\",\n      \"planner_location_param\": \"room\",\n      \"planner_requires_empty_hand\": \"true\",\n      \"planner_effect_state_key\": \"isAssembled\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"assemble\",\n      \"planner_required_fields\": \"action,agent,room,item_1,item_2,item_3,item_4,item_5,item_6,pc\",\n      \"planner_fixed_fields\": \"action=assemble;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2,item_3,item_4,item_5,item_6\",\n      \"planner_room_fields\": \"room\",\n      \"planner_unchecked_fields\": \"pc\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"pc\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"pick_loadable\",\n    \"description\": \"DELTA official executable pick_loadable action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_requires_empty_hand\": \"true\",\n      \"planner_action_name\": \"pick_loadable\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=pick_loadable;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"office\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"drop_loadable\",\n    \"description\": \"DELTA official executable drop_loadable action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"room\",\n      \"planner_action_name\": \"drop_loadable\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=drop_loadable;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"office\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"load\",\n    \"description\": \"DELTA official executable load action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"loadable\",\n      \"planner_action_name\": \"load\",\n      \"planner_required_fields\": \"action,agent,item_1,item_2,room\",\n      \"planner_fixed_fields\": \"action=load;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"office\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"unload\",\n    \"description\": \"DELTA official executable unload action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"room\",\n      \"planner_action_name\": \"unload\",\n      \"planner_required_fields\": \"action,agent,item_1,item_2,room\",\n      \"planner_fixed_fields\": \"action=unload;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"office\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  }\n]\n\n理解边界：\n1. intent 保留 DELTA 原始任务目标，不生成动作序列。\n2. required_item_names 必须使用允许实体名或 DELTA 任务上下文中的完整实体名；房间、物体、工具和充电/清洁设施不能混用类型。\n3. required_item_names 的角色必须与 DELTA 任务上下文和可用 skill 参数类型一致；不要把非房间实体放进房间类角色。\n4. skill_closure 只能使用 DELTA skills root 中启用的 skill 名，例如 goto、pick、dispose、mop_floor、clean_mop、charge。\n5. 如果原始任务要求多个同类实例或多个位置，primary 必须列出不同真实实体，quantity_constraints 记录数量。\n\n输出 JSON 结构：\n{\"is_complete\": true, \"is_cancel_all\": false, \"clarification_question\": \"\", \"entity_relevance\": {\"directly_related\": [], \"indirectly_related\": [], \"possibly_related\": []}, \"skill_closure\": [], \"structured_task\": {\"intent\": \"\", \"required_item_names\": {\"targets\": {\"primary\": [], \"alternatives\": []}, \"tools\": {\"primary\": [], \"alternatives\": []}, \"receptacles\": {\"primary\": [], \"alternatives\": []}}, \"quantity_constraints\": []}}"
  },
  {
    "type": "human",
    "content": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table."
  }
]
```

#### Output
```text
{
  "is_complete": true,
  "is_cancel_all": false,
  "clarification_question": "",
  "entity_relevance": {
    "directly_related": [
      "dining_table",
      "plate",
      "fork",
      "knife",
      "spoon",
      "glass",
      "flower"
    ],
    "indirectly_related": [],
    "possibly_related": []
  },
  "skill_closure": [
    "goto",
    "pick",
    "place_on"
  ],
  "structured_task": {
    "intent": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.",
    "required_item_names": {
      "targets": {
        "primary": [
          "dining_table"
        ],
        "alternatives": []
      },
      "tools": {
        "primary": [
          "plate",
          "fork",
          "knife",
          "spoon",
          "glass"
        ],
        "alternatives": []
      },
      "receptacles": {
        "primary": [
          "flower"
        ],
        "alternatives": []
      }
    },
    "quantity_constraints": []
  }
}
```

### Turn 2: understanding

#### Input
```json
[
  {
    "type": "system",
    "content": "任务：为 DELTA benchmark case 抽取任务完成后的关键 final_state。\n只返回 JSON；不要解释，不要输出 Markdown。\n\n允许参考的 DELTA 场景实体：\n[\n  \"banana_peel\",\n  \"bathroom_1\",\n  \"bathroom_2\",\n  \"bed_1\",\n  \"bed_2\",\n  \"bedroom_1\",\n  \"bedroom_2\",\n  \"book\",\n  \"bowl_2\",\n  \"bowl_3\",\n  \"chair_1\",\n  \"chair_2\",\n  \"chair_3\",\n  \"chair_4\",\n  \"chair_5\",\n  \"clock\",\n  \"cola_can\",\n  \"corridor_1\",\n  \"corridor_2\",\n  \"corridor_3\",\n  \"couch\",\n  \"cpu\",\n  \"desk\",\n  \"dining_room\",\n  \"dining_table\",\n  \"flower\",\n  \"fork\",\n  \"fridge_1\",\n  \"fridge_2\",\n  \"fridge_3\",\n  \"glass\",\n  \"gpu\",\n  \"kitchen\",\n  \"knife\",\n  \"lamp\",\n  \"living_room\",\n  \"lobby\",\n  \"locker\",\n  \"mainboard\",\n  \"microwave\",\n  \"mop\",\n  \"oven\",\n  \"paper\",\n  \"plant_1\",\n  \"plant_2\",\n  \"plate\",\n  \"psu\",\n  \"ram\",\n  \"robot_hub\",\n  \"rotting_apple\",\n  \"rubbish_bin\",\n  \"shelf\",\n  \"sink_1\",\n  \"sink_2\",\n  \"spoon\",\n  \"ssd\",\n  \"toilet_1\",\n  \"toilet_2\"\n]\n\n当前理解结果：\n{\n  \"intent\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n  \"required_item_names\": {\n    \"targets\": {\n      \"primary\": [\n        \"dining_table\"\n      ],\n      \"alternatives\": []\n    },\n    \"tools\": {\n      \"primary\": [\n        \"plate\",\n        \"fork\",\n        \"knife\",\n        \"spoon\",\n        \"glass\"\n      ],\n      \"alternatives\": []\n    },\n    \"receptacles\": {\n      \"primary\": [\n        \"flower\"\n      ],\n      \"alternatives\": []\n    }\n  }\n}\n\n当前选择摘要：\n{\n  \"structured_task\": {\n    \"intent\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n    \"required_item_names\": {\n      \"targets\": {\n        \"primary\": [\n          \"dining_table\"\n        ],\n        \"alternatives\": []\n      },\n      \"tools\": {\n        \"primary\": [\n          \"plate\",\n          \"fork\",\n          \"knife\",\n          \"spoon\",\n          \"glass\"\n        ],\n        \"alternatives\": []\n      },\n      \"receptacles\": {\n        \"primary\": [\n          \"flower\"\n        ],\n        \"alternatives\": []\n      }\n    }\n  },\n  \"current_final_state\": {},\n  \"scene_entities\": [\n    \"banana_peel\",\n    \"bathroom_1\",\n    \"bathroom_2\",\n    \"bed_1\",\n    \"bed_2\",\n    \"bedroom_1\",\n    \"bedroom_2\",\n    \"book\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"chair_1\",\n    \"chair_2\",\n    \"chair_3\",\n    \"chair_4\",\n    \"chair_5\",\n    \"clock\",\n    \"cola_can\",\n    \"corridor_1\",\n    \"corridor_2\",\n    \"corridor_3\",\n    \"couch\",\n    \"cpu\",\n    \"desk\",\n    \"dining_room\",\n    \"dining_table\",\n    \"flower\",\n    \"fork\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"fridge_3\",\n    \"glass\",\n    \"gpu\",\n    \"kitchen\",\n    \"knife\",\n    \"lamp\",\n    \"living_room\",\n    \"lobby\",\n    \"locker\",\n    \"mainboard\",\n    \"microwave\",\n    \"mop\",\n    \"oven\",\n    \"paper\",\n    \"plant_1\",\n    \"plant_2\",\n    \"plate\",\n    \"psu\",\n    \"ram\",\n    \"robot_hub\",\n    \"rotting_apple\",\n    \"rubbish_bin\",\n    \"shelf\",\n    \"sink_1\",\n    \"sink_2\",\n    \"spoon\",\n    \"ssd\",\n    \"toilet_1\",\n    \"toilet_2\"\n  ]\n}\n\nDELTA 任务上下文：\n{\n  \"dataset\": \"delta\",\n  \"task_name\": \"dining:allensville:episode-01\",\n  \"domain\": \"dining\",\n  \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n  \"task_source\": \"delta_data_example_py\",\n  \"environment_source\": \"delta_data_scene_graph_py\",\n  \"scene_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json\",\n  \"delta_add_obj_types\": [],\n  \"delta_env_state_predicates\": [\n    \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n    \"item_is_dining_table(<item>): <item> is dining_table.\"\n  ],\n  \"delta_initial_predicates\": [\n    \"item_is_dining_table dining_table\",\n    \"item_pickable plate\",\n    \"item_accessible plate\",\n    \"item_pickable fork\",\n    \"item_accessible fork\",\n    \"item_pickable knife\",\n    \"item_accessible knife\",\n    \"item_pickable spoon\",\n    \"item_accessible spoon\",\n    \"item_pickable glass\",\n    \"item_accessible glass\",\n    \"item_pickable flower\",\n    \"item_accessible flower\"\n  ],\n  \"delta_room_neighbors\": {\n    \"bathroom_1\": [\n      \"corridor_2\"\n    ],\n    \"bathroom_2\": [\n      \"corridor_3\"\n    ],\n    \"bedroom_1\": [\n      \"corridor_2\"\n    ],\n    \"bedroom_2\": [\n      \"corridor_3\"\n    ],\n    \"corridor_1\": [\n      \"lobby\",\n      \"corridor_3\"\n    ],\n    \"corridor_2\": [\n      \"bathroom_1\",\n      \"bedroom_1\",\n      \"corridor_3\"\n    ],\n    \"corridor_3\": [\n      \"corridor_1\",\n      \"corridor_2\",\n      \"bathroom_2\",\n      \"bedroom_2\",\n      \"kitchen\",\n      \"living_room\"\n    ],\n    \"dining_room\": [\n      \"kitchen\",\n      \"living_room\"\n    ],\n    \"kitchen\": [\n      \"corridor_3\",\n      \"dining_room\"\n    ],\n    \"living_room\": [\n      \"corridor_3\",\n      \"dining_room\"\n    ],\n    \"lobby\": [\n      \"corridor_1\"\n    ]\n  },\n  \"delta_accessible_items\": [\n    \"psu\",\n    \"sink_1\",\n    \"mop\",\n    \"gpu\",\n    \"sink_2\",\n    \"mainboard\",\n    \"glass\",\n    \"shelf\",\n    \"book\",\n    \"cpu\",\n    \"rotting_apple\",\n    \"plate\",\n    \"lamp\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"ssd\",\n    \"cola_can\",\n    \"dining_table\",\n    \"knife\",\n    \"fork\",\n    \"spoon\",\n    \"microwave\",\n    \"oven\",\n    \"rubbish_bin\",\n    \"fridge_3\",\n    \"desk\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"robot_hub\",\n    \"ram\",\n    \"banana_peel\",\n    \"flower\",\n    \"locker\",\n    \"paper\"\n  ],\n  \"loadable_containers\": [\n    {\n      \"name\": \"shelf\",\n      \"room\": \"bedroom_1\",\n      \"is_loaded\": true,\n      \"contents\": [\n        \"book\"\n      ],\n      \"affordances\": [\n        \"drop\",\n        \"load\",\n        \"pick\",\n        \"unload\"\n      ]\n    },\n    {\n      \"name\": \"locker\",\n      \"room\": \"lobby\",\n      \"is_loaded\": true,\n      \"contents\": [\n        \"paper\"\n      ],\n      \"affordances\": [\n        \"drop\",\n        \"load\",\n        \"pick\",\n        \"unload\"\n      ]\n    }\n  ],\n  \"task_environment_mode\": \"understanding_pruned\",\n  \"available_entities\": [\n    \"banana_peel\",\n    \"bathroom_1\",\n    \"bathroom_2\",\n    \"bed_1\",\n    \"bed_2\",\n    \"bedroom_1\",\n    \"bedroom_2\",\n    \"book\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"chair_1\",\n    \"chair_2\",\n    \"chair_3\",\n    \"chair_4\",\n    \"chair_5\",\n    \"clock\",\n    \"cola_can\",\n    \"corridor_1\",\n    \"corridor_2\",\n    \"corridor_3\",\n    \"couch\",\n    \"cpu\",\n    \"desk\",\n    \"dining_room\",\n    \"dining_table\",\n    \"flower\",\n    \"fork\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"fridge_3\",\n    \"glass\",\n    \"gpu\",\n    \"kitchen\",\n    \"knife\",\n    \"lamp\",\n    \"living_room\",\n    \"lobby\",\n    \"locker\",\n    \"mainboard\",\n    \"microwave\",\n    \"mop\",\n    \"oven\",\n    \"paper\",\n    \"plant_1\",\n    \"plant_2\",\n    \"plate\",\n    \"psu\",\n    \"ram\",\n    \"robot_hub\",\n    \"rotting_apple\",\n    \"rubbish_bin\",\n    \"shelf\",\n    \"sink_1\",\n    \"sink_2\",\n    \"spoon\",\n    \"ssd\",\n    \"toilet_1\",\n    \"toilet_2\"\n  ]\n}\n\n抽取边界：\n1. 只能使用 instruction、domain、delta_env_state_predicates、场景实体和当前理解结果。\n2. 不要读取、猜测或生成评测答案字段、官方目标字段或参考代价字段。\n3. final_state 保持 DELTA 语义，可包含 robot、entities、predicates、notes；不要转成其他 benchmark 的动作或环境格式。\n4. 只表达任务完成后应成立的关键状态，不输出动作序列。\n\n输出 JSON：\n{\"final_state\": {}}"
  },
  {
    "type": "human",
    "content": "请抽取任务完成后的关键 final_state，并只返回 JSON。"
  }
]
```

#### Output
```text
{
  "final_state": {
    "predicates": [
      "item_on(plate, dining_table)",
      "item_on(fork, dining_table)",
      "item_on(knife, dining_table)",
      "item_on(spoon, dining_table)",
      "item_on(glass, dining_table)",
      "item_on(flower, dining_table)"
    ],
    "notes": "Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower)."
  }
}
```

### Turn 3: planning

#### Input
```json
[
  {
    "type": "system",
    "content": "任务：生成 DELTA 官方原生动作计划。\n只输出 JSON；不要解释，不要输出 Markdown。\n\n原始任务：\n\n\n规划目标：\nSet up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\n\n机器人状态：\n- 位置：living_room\n- 手持：空\n- 完整状态：{\"robot_location\":\"living_room\",\"robot_holding\":\"空\",\"delta_room_neighbors\":{\"bathroom_1\":[\"corridor_2\"],\"bathroom_2\":[\"corridor_3\"],\"bedroom_1\":[\"corridor_2\"],\"bedroom_2\":[\"corridor_3\"],\"corridor_1\":[\"lobby\",\"corridor_3\"],\"corridor_2\":[\"bathroom_1\",\"bedroom_1\",\"corridor_3\"],\"corridor_3\":[\"corridor_1\",\"corridor_2\",\"bathroom_2\",\"bedroom_2\",\"kitchen\",\"living_room\"],\"dining_room\":[\"kitchen\",\"living_room\"],\"kitchen\":[\"corridor_3\",\"dining_room\"],\"living_room\":[\"corridor_3\",\"dining_room\"],\"lobby\":[\"corridor_1\"]},\"domain\":\"dining\",\"delta_initial_predicates\":[\"item_is_dining_table dining_table\",\"item_pickable plate\",\"item_accessible plate\",\"item_pickable fork\",\"item_accessible fork\",\"item_pickable knife\",\"item_accessible knife\",\"item_pickable spoon\",\"item_accessible spoon\",\"item_pickable glass\",\"item_accessible glass\",\"item_pickable flower\",\"item_accessible flower\"]}\n\n当前环境 JSON：\n{\"dining_table\":{\"direct_parent\":\"dining_room\",\"direct_relation\":\"inside\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_predicate:item_is_dining_table\"],\"is_container\":true,\"full_path\":[\"dining_room\"]},\"dining_room\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"plate\":{\"direct_parent\":\"bedroom_2\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"bedroom_2\"]},\"bedroom_2\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"fork\":{\"direct_parent\":\"kitchen\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"kitchen\"]},\"kitchen\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"knife\":{\"direct_parent\":\"kitchen\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"kitchen\"]},\"spoon\":{\"direct_parent\":\"kitchen\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"kitchen\"]},\"glass\":{\"direct_parent\":\"bedroom_1\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"bedroom_1\"]},\"bedroom_1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"flower\":{\"direct_parent\":\"lobby\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"lobby\"]},\"lobby\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"living_room\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"bathroom_1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"bathroom_2\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"corridor_1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"corridor_2\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"corridor_3\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]}}\n\n目标物品当前位置（来自官方场景图；pick 的 room 必须与此表一致，只能从物体当前所在房间拾取）：\n- dining_table: dining_room\n- flower: lobby\n- fork: kitchen\n- glass: bedroom_1\n- knife: kitchen\n- plate: bedroom_2\n- spoon: kitchen\n\n任务相关环境事实：\n[{\"name\":\"bathroom_1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"bathroom_2\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"bedroom_1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"bedroom_2\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"corridor_1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"corridor_2\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"corridor_3\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"dining_room\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"dining_table\",\"direct_parent\":\"dining_room\",\"full_path\":[\"dining_room\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"flower\",\"direct_parent\":\"lobby\",\"full_path\":[\"lobby\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"fork\",\"direct_parent\":\"kitchen\",\"full_path\":[\"kitchen\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"glass\",\"direct_parent\":\"bedroom_1\",\"full_path\":[\"bedroom_1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"kitchen\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"knife\",\"direct_parent\":\"kitchen\",\"full_path\":[\"kitchen\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"living_room\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"lobby\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"plate\",\"direct_parent\":\"bedroom_2\",\"full_path\":[\"bedroom_2\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"spoon\",\"direct_parent\":\"kitchen\",\"full_path\":[\"kitchen\"],\"states\":{},\"type\":null,\"is_container\":false}]\n\n任务上下文：\n{\n  \"dataset\": \"delta\",\n  \"task_name\": \"dining:allensville:episode-01\",\n  \"domain\": \"dining\",\n  \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n  \"task_source\": \"delta_data_example_py\",\n  \"environment_source\": \"delta_data_scene_graph_py\",\n  \"scene_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json\",\n  \"delta_add_obj_types\": [],\n  \"delta_env_state_predicates\": [\n    \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n    \"item_is_dining_table(<item>): <item> is dining_table.\"\n  ],\n  \"delta_initial_predicates\": [\n    \"item_is_dining_table dining_table\",\n    \"item_pickable plate\",\n    \"item_accessible plate\",\n    \"item_pickable fork\",\n    \"item_accessible fork\",\n    \"item_pickable knife\",\n    \"item_accessible knife\",\n    \"item_pickable spoon\",\n    \"item_accessible spoon\",\n    \"item_pickable glass\",\n    \"item_accessible glass\",\n    \"item_pickable flower\",\n    \"item_accessible flower\"\n  ],\n  \"delta_room_neighbors\": {\n    \"bathroom_1\": [\n      \"corridor_2\"\n    ],\n    \"bathroom_2\": [\n      \"corridor_3\"\n    ],\n    \"bedroom_1\": [\n      \"corridor_2\"\n    ],\n    \"bedroom_2\": [\n      \"corridor_3\"\n    ],\n    \"corridor_1\": [\n      \"lobby\",\n      \"corridor_3\"\n    ],\n    \"corridor_2\": [\n      \"bathroom_1\",\n      \"bedroom_1\",\n      \"corridor_3\"\n    ],\n    \"corridor_3\": [\n      \"corridor_1\",\n      \"corridor_2\",\n      \"bathroom_2\",\n      \"bedroom_2\",\n      \"kitchen\",\n      \"living_room\"\n    ],\n    \"dining_room\": [\n      \"kitchen\",\n      \"living_room\"\n    ],\n    \"kitchen\": [\n      \"corridor_3\",\n      \"dining_room\"\n    ],\n    \"living_room\": [\n      \"corridor_3\",\n      \"dining_room\"\n    ],\n    \"lobby\": [\n      \"corridor_1\"\n    ]\n  },\n  \"delta_accessible_items\": [\n    \"psu\",\n    \"sink_1\",\n    \"mop\",\n    \"gpu\",\n    \"sink_2\",\n    \"mainboard\",\n    \"glass\",\n    \"shelf\",\n    \"book\",\n    \"cpu\",\n    \"rotting_apple\",\n    \"plate\",\n    \"lamp\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"ssd\",\n    \"cola_can\",\n    \"dining_table\",\n    \"knife\",\n    \"fork\",\n    \"spoon\",\n    \"microwave\",\n    \"oven\",\n    \"rubbish_bin\",\n    \"fridge_3\",\n    \"desk\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"robot_hub\",\n    \"ram\",\n    \"banana_peel\",\n    \"flower\",\n    \"locker\",\n    \"paper\"\n  ],\n  \"loadable_containers\": [\n    {\n      \"name\": \"shelf\",\n      \"room\": \"bedroom_1\",\n      \"is_loaded\": true,\n      \"contents\": [\n        \"book\"\n      ],\n      \"affordances\": [\n        \"drop\",\n        \"load\",\n        \"pick\",\n        \"unload\"\n      ]\n    },\n    {\n      \"name\": \"locker\",\n      \"room\": \"lobby\",\n      \"is_loaded\": true,\n      \"contents\": [\n        \"paper\"\n      ],\n      \"affordances\": [\n        \"drop\",\n        \"load\",\n        \"pick\",\n        \"unload\"\n      ]\n    }\n  ],\n  \"task_environment_mode\": \"understanding_pruned\",\n  \"available_entities\": [\n    \"banana_peel\",\n    \"bathroom_1\",\n    \"bathroom_2\",\n    \"bed_1\",\n    \"bed_2\",\n    \"bedroom_1\",\n    \"bedroom_2\",\n    \"book\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"chair_1\",\n    \"chair_2\",\n    \"chair_3\",\n    \"chair_4\",\n    \"chair_5\",\n    \"clock\",\n    \"cola_can\",\n    \"corridor_1\",\n    \"corridor_2\",\n    \"corridor_3\",\n    \"couch\",\n    \"cpu\",\n    \"desk\",\n    \"dining_room\",\n    \"dining_table\",\n    \"flower\",\n    \"fork\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"fridge_3\",\n    \"glass\",\n    \"gpu\",\n    \"kitchen\",\n    \"knife\",\n    \"lamp\",\n    \"living_room\",\n    \"lobby\",\n    \"locker\",\n    \"mainboard\",\n    \"microwave\",\n    \"mop\",\n    \"oven\",\n    \"paper\",\n    \"plant_1\",\n    \"plant_2\",\n    \"plate\",\n    \"psu\",\n    \"ram\",\n    \"robot_hub\",\n    \"rotting_apple\",\n    \"rubbish_bin\",\n    \"shelf\",\n    \"sink_1\",\n    \"sink_2\",\n    \"spoon\",\n    \"ssd\",\n    \"toilet_1\",\n    \"toilet_2\"\n  ]\n}\n\n新增对象类型（若有）：\n（无）\n\n\n房间邻接表（goto 的 from/to 之间必须在此表中存在可达路径；框架会自动展开为走廊逐跳）：\n- bathroom_1: corridor_2\n- bathroom_2: corridor_3\n- bedroom_1: corridor_2\n- bedroom_2: corridor_3\n- corridor_1: corridor_3, lobby\n- corridor_2: bathroom_1, bedroom_1, corridor_3\n- corridor_3: bathroom_2, bedroom_2, corridor_1, corridor_2, kitchen, living_room\n- dining_room: kitchen, living_room\n- kitchen: corridor_3, dining_room\n- living_room: corridor_3, dining_room\n- lobby: corridor_1\n\n\n理解层实体选择：\n{\n  \"targets\": {\n    \"primary\": [\n      \"dining_table\"\n    ],\n    \"alternatives\": []\n  },\n  \"tools\": {\n    \"primary\": [\n      \"plate\",\n      \"fork\",\n      \"knife\",\n      \"spoon\",\n      \"glass\"\n    ],\n    \"alternatives\": []\n  },\n  \"receptacles\": {\n    \"primary\": [\n      \"flower\"\n    ],\n    \"alternatives\": []\n  }\n}\n\n可用动作与 skill 契约：\n<available_skills>\n---\nname: goto\ndescription: DELTA official executable goto action.\n---\n\n## 参数\n| 参数名 | 类型 | 含义 |\n| --- | --- | --- |\n| agent | string | DELTA PDDL agent，固定为 `robot`。 |\n| room_1 | string | 机器人当前所在的 DELTA 房间名。 |\n| room_2 | string | 机器人要移动到的 DELTA 房间名。 |\n\n## 前提条件\n- 必须使用 DELTA PDDL 签名 `goto(robot, room_1, room_2)` 和下面的同签名 JSON 对象。\n- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- `agent` 必须是 `robot`。\n- `room_1` 和 `room_2` 都必须是当前 DELTA 场景中的真实房间。\n- `room_1` 必须等于机器人当前所在房间。\n- `room_1` 与 `room_2` 之间必须在 `delta_room_neighbors`（任务上下文中的房间邻接表）里存在可达路径。\n- 框架会按公开场景图邻接关系自动把房间级 `goto` 展开为具体走廊逐跳，模型不需要输出中间走廊步。\n- 如果机器人已经在目标房间，不要输出同房间 `goto`。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，机器人位置从 `room_1` 更新为 `room_2`。\n\n## 输出格式\n在 DELTA 原生动作 JSON 数组中使用这个动作对象：\n\n```json\n{\"action\":\"goto\",\"agent\":\"robot\",\"room_1\":\"<current_room>\",\"room_2\":\"<destination_room>\"}\n```\n\n- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确房间名。\n- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。\n\n\n---\nname: pick\ndescription: DELTA official executable pick action.\n---\n\n## 参数\n| 参数名 | 类型 | 含义 |\n| --- | --- | --- |\n| agent | string | DELTA PDDL agent，固定为 `robot`。 |\n| item | string | 当前环境中的普通可拾取物品实体名。 |\n| room | string | `item` 所在的 DELTA 房间名。 |\n\n## 前提条件\n- 必须使用 DELTA PDDL 签名 `pick(robot, item, room)` 和下面的同签名 JSON 对象。\n- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- `agent` 必须是 `robot`。\n- `item` 必须是当前环境中的真实实体，并满足可访问、可拾取条件。\n- `room` 必须是当前 DELTA 场景中的真实房间，并且必须是 `item` 所在房间。\n- 机器人必须已经在 `room`，且手中没有物品。\n- 普通物品使用 `pick`；如果任务需要拾取 empty loadable container，应使用 `pick_loadable`。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，机器人持有 `item`，`item` 不再直接位于 `room`。\n\n## 输出格式\n在 DELTA 原生动作 JSON 数组中使用这个动作对象：\n\n```json\n{\"action\":\"pick\",\"agent\":\"robot\",\"item\":\"<item_entity>\",\"room\":\"<item_room>\"}\n```\n\n- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。\n- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。\n\n\n---\nname: place_on\ndescription: DELTA official executable place_on action.\n---\n\n## 参数\n| 参数名 | 类型 | 含义 |\n| --- | --- | --- |\n| agent | string | DELTA PDDL agent，固定为 `robot`。 |\n| item_1 | string | 当前机器人持有的 DELTA 物品实体名。 |\n| item_2 | string | 当前环境中的 dining_table/surface 实体名。 |\n| room | string | `item_2` 所在的 DELTA 房间名。 |\n\n## 前提条件\n- 必须使用 DELTA PDDL 签名 `place_on(robot, item_1, item_2, room)` 和下面的同签名 JSON 对象。\n- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- `agent` 必须是 `robot`。\n- `item_1` 必须是当前环境中的真实实体，且机器人已经持有它。\n- `item_2` 必须是当前环境中的真实实体，且满足 DELTA dining-table/surface 谓词；不要把房间名当作 `item_2`。\n- `room` 必须是当前 DELTA 场景中的真实房间，并且必须是 `item_2` 所在房间。\n- 机器人必须已经在 `room`；如果 `item_1` 不在机器人手中，`place_on` 必须被 sandbox 拒绝。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，`item_1` 位于 `item_2` 上，机器人手变为空；其他位置变化只以 handler.apply(...) 的实际更新为准。\n\n## 输出格式\n在 DELTA 原生动作 JSON 数组中使用这个动作对象：\n\n```json\n{\"action\":\"place_on\",\"agent\":\"robot\",\"item_1\":\"<held_item_entity>\",\"item_2\":\"<dining_table_entity>\",\"room\":\"<surface_room>\"}\n```\n\n- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。\n- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。\n\n</available_skills>\n\n历史失败反馈：\n暂无相关拦截记录\n\n规划边界：\n1. 只使用 <available_skills> 中列出的动作。\n2. 动作参数、前置条件、状态依赖和效果只以对应 skill 契约为准。\n3. 只引用当前环境、任务上下文、任务相关环境事实或理解层结果中出现的实体/房间/对象名。\n4. 如果已有修复反馈或修复状态，只生成尚未验证的后续动作。\n5. 机器人一次只能携带一个物品；拿取下一个物品前，必须先把当前手持物品 drop 到目标位置。\n6. 执行需要多个物品位于同一房间的复合动作（如 assemble）之前，必须先通过 drop 把全部相关物品放到该动作要求的房间；复合动作只会因为物品未就位被拒绝。\n\n输出格式：\n直接输出 DELTA 官方动作 JSON 数组。\n每个元素包含 action 和该动作 skill 契约要求的参数字段；不要输出任何框架包装字段。\n如果任务已经完成，返回 []。"
  },
  {
    "type": "human",
    "content": "开始规划。"
  }
]
```

#### Output
```text
[{"action":"goto","agent":"robot","room_1":"living_room","room_2":"dining_room"},{"action":"goto","agent":"robot","room_1":"dining_room","room_2":"kitchen"},{"action":"pick","agent":"robot","item":"fork","room":"kitchen"},{"action":"goto","agent":"robot","room_1":"kitchen","room_2":"dining_room"},{"action":"place_on","agent":"robot","item_1":"fork","item_2":"dining_table","room":"dining_room"},{"action":"goto","agent":"robot","room_1":"dining_room","room_2":"kitchen"},{"action":"pick","agent":"robot","item":"knife","room":"kitchen"},{"action":"goto","agent":"robot","room_1":"kitchen","room_2":"dining_room"},{"action":"place_on","agent":"robot","item_1":"knife","item_2":"dining_table","room":"dining_room"},{"action":"goto","agent":"robot","room_1":"dining_room","room_2":"kitchen"},{"action":"pick","agent":"robot","item":"spoon","room":"kitchen"},{"action":"goto","agent":"robot","room_1":"kitchen","room_2":"dining_room"},{"action":"place_on","agent":"robot","item_1":"spoon","item_2":"dining_table","room":"dining_room"},{"action":"goto","agent":"robot","room_1":"dining_room","room_2":"bedroom_1"},{"action":"pick","agent":"robot","item":"glass","room":"bedroom_1"},{"action":"goto","agent":"robot","room_1":"bedroom_1","room_2":"dining_room"},{"action":"place_on","agent":"robot","item_1":"glass","item_2":"dining_table","room":"dining_room"},{"action":"goto","agent":"robot","room_1":"dining_room","room_2":"bedroom_2"},{"action":"pick","agent":"robot","item":"plate","room":"bedroom_2"},{"action":"goto","agent":"robot","room_1":"bedroom_2","room_2":"dining_room"},{"action":"place_on","agent":"robot","item_1":"plate","item_2":"dining_table","room":"dining_room"},{"action":"goto","agent":"robot","room_1":"dining_room","room_2":"lobby"},{"action":"pick","agent":"robot","item":"flower","room":"lobby"},{"action":"goto","agent":"robot","room_1":"lobby","room_2":"dining_room"},{"action":"place_on","agent":"robot","item_1":"flower","item_2":"dining_table","room":"dining_room"}]
```

### Turn 4: planning

#### Input
```json
[
  {
    "type": "human",
    "content": "任务：根据 DELTA sandbox 前后状态差异判断任务是否完成。\n只输出 JSON；不要解释，不要生成动作。\n\n任务目标：Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\n\n完整 native action 计划摘要：\n[\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"living_room\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"fork\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"fork\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"knife\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"knife\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"spoon\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"spoon\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"bedroom_1\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"glass\",\n    \"room\": \"bedroom_1\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"bedroom_1\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"glass\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"bedroom_2\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"plate\",\n    \"room\": \"bedroom_2\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"bedroom_2\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"plate\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"lobby\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"flower\",\n    \"room\": \"lobby\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"lobby\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"flower\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  }\n]\n\n本轮实际模拟步骤：\n[\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"living_room\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"fork\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"fork\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"knife\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"knife\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"spoon\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"spoon\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"bedroom_1\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"glass\",\n    \"room\": \"bedroom_1\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"bedroom_1\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"glass\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"bedroom_2\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"plate\",\n    \"room\": \"bedroom_2\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"bedroom_2\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"plate\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"lobby\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"flower\",\n    \"room\": \"lobby\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"lobby\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"flower\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  }\n]\n\n轨迹摘要：\nStep 1: goto([])\nStep 2: goto([])\nStep 3: pick([])\nStep 4: goto([])\nStep 5: place_on([])\nStep 6: goto([])\nStep 7: pick([])\nStep 8: goto([])\nStep 9: place_on([])\nStep 10: goto([])\nStep 11: pick([])\nStep 12: goto([])\nStep 13: place_on([])\nStep 14: goto([])\nStep 15: pick([])\nStep 16: goto([])\nStep 17: place_on([])\nStep 18: goto([])\nStep 19: pick([])\nStep 20: goto([])\nStep 21: place_on([])\nStep 22: goto([])\nStep 23: pick([])\nStep 24: goto([])\nStep 25: place_on([])\n\nDELTA 状态差异 JSON：\n{\n  \"entity_count_compared\": 18,\n  \"changed_entity_count\": 6,\n  \"truncated_entity_count\": 0,\n  \"has_changes\": true,\n  \"robot\": {\n    \"changed\": true,\n    \"before\": {\n      \"robot_location\": \"living_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    },\n    \"after\": {\n      \"robot_location\": \"dining_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    }\n  },\n  \"entities\": [\n    {\n      \"name\": \"flower\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"lobby\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"lobby\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"fork\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"glass\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"bedroom_1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"bedroom_1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"knife\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"plate\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"bedroom_2\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"bedroom_2\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"spoon\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    }\n  ]\n}\n\n状态审计上下文 JSON：\n{\n  \"entity_count_available\": 18,\n  \"entity_count_in_context\": 8,\n  \"truncated_entity_count\": 0,\n  \"note\": \"state_diff only lists changed entities; unchanged entities in this context still prove final goal state when their after state satisfies the task.\",\n  \"robot\": {\n    \"changed\": true,\n    \"before\": {\n      \"robot_location\": \"living_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    },\n    \"after\": {\n      \"robot_location\": \"dining_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    }\n  },\n  \"entities\": [\n    {\n      \"name\": \"dining_table\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"dining_room\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"dining_room\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_predicate:item_is_dining_table\"\n        ]\n      },\n      \"after\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"dining_room\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"dining_room\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_predicate:item_is_dining_table\"\n        ]\n      }\n    },\n    {\n      \"name\": \"plate\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"bedroom_2\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"bedroom_2\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"fork\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"knife\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"spoon\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"glass\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"bedroom_1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"bedroom_1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"flower\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"lobby\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"lobby\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"dining_room\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      },\n      \"after\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      }\n    }\n  ],\n  \"task_context\": {\n    \"dataset\": \"delta\",\n    \"task_name\": \"dining:allensville:episode-01\",\n    \"domain\": \"dining\",\n    \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n    \"task_source\": \"delta_data_example_py\",\n    \"environment_source\": \"delta_data_scene_graph_py\",\n    \"scene_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json\",\n    \"delta_add_obj_types\": [],\n    \"delta_env_state_predicates\": [\n      \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n      \"item_is_dining_table(<item>): <item> is dining_table.\"\n    ],\n    \"delta_initial_predicates\": [\n      \"item_is_dining_table dining_table\",\n      \"item_pickable plate\",\n      \"item_accessible plate\",\n      \"item_pickable fork\",\n      \"item_accessible fork\",\n      \"item_pickable knife\",\n      \"item_accessible knife\",\n      \"item_pickable spoon\",\n      \"item_accessible spoon\",\n      \"item_pickable glass\",\n      \"item_accessible glass\",\n      \"item_pickable flower\",\n      \"item_accessible flower\"\n    ],\n    \"delta_room_neighbors\": {\n      \"bathroom_1\": [\n        \"corridor_2\"\n      ],\n      \"bathroom_2\": [\n        \"corridor_3\"\n      ],\n      \"bedroom_1\": [\n        \"corridor_2\"\n      ],\n      \"bedroom_2\": [\n        \"corridor_3\"\n      ],\n      \"corridor_1\": [\n        \"lobby\",\n        \"corridor_3\"\n      ],\n      \"corridor_2\": [\n        \"bathroom_1\",\n        \"bedroom_1\",\n        \"corridor_3\"\n      ],\n      \"corridor_3\": [\n        \"corridor_1\",\n        \"corridor_2\",\n        \"bathroom_2\",\n        \"bedroom_2\",\n        \"kitchen\",\n        \"living_room\"\n      ],\n      \"dining_room\": [\n        \"kitchen\",\n        \"living_room\"\n      ],\n      \"kitchen\": [\n        \"corridor_3\",\n        \"dining_room\"\n      ],\n      \"living_room\": [\n        \"corridor_3\",\n        \"dining_room\"\n      ],\n      \"lobby\": [\n        \"corridor_1\"\n      ]\n    },\n    \"delta_accessible_items\": [\n      \"psu\",\n      \"sink_1\",\n      \"mop\",\n      \"gpu\",\n      \"sink_2\",\n      \"mainboard\",\n      \"glass\",\n      \"shelf\",\n      \"book\",\n      \"cpu\",\n      \"rotting_apple\",\n      \"plate\",\n      \"lamp\",\n      \"fridge_1\",\n      \"fridge_2\",\n      \"ssd\",\n      \"cola_can\",\n      \"dining_table\",\n      \"knife\",\n      \"fork\",\n      \"spoon\",\n      \"microwave\",\n      \"oven\",\n      \"rubbish_bin\",\n      \"fridge_3\",\n      \"desk\",\n      \"bowl_2\",\n      \"bowl_3\",\n      \"robot_hub\",\n      \"ram\",\n      \"banana_peel\",\n      \"flower\",\n      \"locker\",\n      \"paper\"\n    ],\n    \"loadable_containers\": [\n      {\n        \"name\": \"shelf\",\n        \"room\": \"bedroom_1\",\n        \"is_loaded\": true,\n        \"contents\": [\n          \"book\"\n        ],\n        \"affordances\": [\n          \"drop\",\n          \"load\",\n          \"pick\",\n          \"unload\"\n        ]\n      },\n      {\n        \"name\": \"locker\",\n        \"room\": \"lobby\",\n        \"is_loaded\": true,\n        \"contents\": [\n          \"paper\"\n        ],\n        \"affordances\": [\n          \"drop\",\n          \"load\",\n          \"pick\",\n          \"unload\"\n        ]\n      }\n    ],\n    \"task_environment_mode\": \"understanding_pruned\",\n    \"available_entities\": [\n      \"banana_peel\",\n      \"bathroom_1\",\n      \"bathroom_2\",\n      \"bed_1\",\n      \"bed_2\",\n      \"bedroom_1\",\n      \"bedroom_2\",\n      \"book\",\n      \"bowl_2\",\n      \"bowl_3\",\n      \"chair_1\",\n      \"chair_2\",\n      \"chair_3\",\n      \"chair_4\",\n      \"chair_5\",\n      \"clock\",\n      \"cola_can\",\n      \"corridor_1\",\n      \"corridor_2\",\n      \"corridor_3\",\n      \"couch\",\n      \"cpu\",\n      \"desk\",\n      \"dining_room\",\n      \"dining_table\",\n      \"flower\",\n      \"fork\",\n      \"fridge_1\",\n      \"fridge_2\",\n      \"fridge_3\",\n      \"glass\",\n      \"gpu\",\n      \"kitchen\",\n      \"knife\",\n      \"lamp\",\n      \"living_room\",\n      \"lobby\",\n      \"locker\",\n      \"mainboard\",\n      \"microwave\",\n      \"mop\",\n      \"oven\",\n      \"paper\",\n      \"plant_1\",\n      \"plant_2\",\n      \"plate\",\n      \"psu\",\n      \"ram\",\n      \"robot_hub\",\n      \"rotting_apple\",\n      \"rubbish_bin\",\n      \"shelf\",\n      \"sink_1\",\n      \"sink_2\",\n      \"spoon\",\n      \"ssd\",\n      \"toilet_1\",\n      \"toilet_2\"\n    ]\n  },\n  \"evaluation_context\": {},\n  \"external_goal\": {\n    \"has_external_goal\": true,\n    \"external_goal_state\": {},\n    \"external_goal_text\": \"\",\n    \"structured_goal_state\": {},\n    \"structured_final_state\": {\n      \"predicates\": [\n        \"item_on(plate, dining_table)\",\n        \"item_on(fork, dining_table)\",\n        \"item_on(knife, dining_table)\",\n        \"item_on(spoon, dining_table)\",\n        \"item_on(glass, dining_table)\",\n        \"item_on(flower, dining_table)\"\n      ],\n      \"notes\": \"Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower).\"\n    }\n  },\n  \"benchmark_final_state_compare\": {\n    \"benchmark\": \"DELTA\",\n    \"status\": \"prepared_for_framework_llm_judge\",\n    \"environment_format\": \"DELTA scene_graph 转成 benchmark 本地扁平环境，保留 delta_predicate/delta_affordance 属性\",\n    \"action_format\": \"DELTA 官方原生动作 JSON 对象\",\n    \"official_evaluator\": \"planning 结束后调用 DELTA PDDL/VAL；评测答案字段不进入 understanding/planning/final_state audit\",\n    \"used_fields\": {\n      \"task_context\": [\n        \"dataset\",\n        \"delta_accessible_items\",\n        \"delta_env_state_predicates\",\n        \"domain\",\n        \"instruction\",\n        \"loadable_containers\",\n        \"scene_graph_cache_path\",\n        \"task_environment_mode\",\n        \"task_name\"\n      ],\n      \"evaluation_context\": [],\n      \"external_goal\": [\n        \"has_external_goal\",\n        \"structured_final_state\"\n      ],\n      \"state_diff\": [\n        \"entities\",\n        \"robot\"\n      ]\n    },\n    \"benchmark_goal\": {\n      \"task_context\": {\n        \"dataset\": \"delta\",\n        \"task_name\": \"dining:allensville:episode-01\",\n        \"domain\": \"dining\",\n        \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n        \"scene_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json\",\n        \"delta_env_state_predicates\": [\n          \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n          \"item_is_dining_table(<item>): <item> is dining_table.\"\n        ],\n        \"delta_accessible_items\": [\n          \"psu\",\n          \"sink_1\",\n          \"mop\",\n          \"gpu\",\n          \"sink_2\",\n          \"mainboard\",\n          \"glass\",\n          \"shelf\",\n          \"book\",\n          \"cpu\",\n          \"rotting_apple\",\n          \"plate\",\n          \"lamp\",\n          \"fridge_1\",\n          \"fridge_2\",\n          \"ssd\",\n          \"cola_can\",\n          \"dining_table\",\n          \"knife\",\n          \"fork\",\n          \"spoon\",\n          \"microwave\",\n          \"oven\",\n          \"rubbish_bin\",\n          \"fridge_3\",\n          \"desk\",\n          \"bowl_2\",\n          \"bowl_3\",\n          \"robot_hub\",\n          \"ram\",\n          \"banana_peel\",\n          \"flower\",\n          \"locker\",\n          \"paper\"\n        ],\n        \"loadable_containers\": [\n          {\n            \"name\": \"shelf\",\n            \"room\": \"bedroom_1\",\n            \"is_loaded\": true,\n            \"contents\": [\n              \"book\"\n            ],\n            \"affordances\": [\n              \"drop\",\n              \"load\",\n              \"pick\",\n              \"unload\"\n            ]\n          },\n          {\n            \"name\": \"locker\",\n            \"room\": \"lobby\",\n            \"is_loaded\": true,\n            \"contents\": [\n              \"paper\"\n            ],\n            \"affordances\": [\n              \"drop\",\n              \"load\",\n              \"pick\",\n              \"unload\"\n            ]\n          }\n        ],\n        \"task_environment_mode\": \"understanding_pruned\"\n      },\n      \"evaluation_context\": {},\n      \"goal_projection\": {\n        \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n        \"domain\": \"dining\",\n        \"visible_delta_predicates\": [\n          \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n          \"item_is_dining_table(<item>): <item> is dining_table.\"\n        ],\n        \"loadable_containers\": [\n          {\n            \"name\": \"shelf\",\n            \"room\": \"bedroom_1\",\n            \"is_loaded\": true,\n            \"contents\": [\n              \"book\"\n            ],\n            \"affordances\": [\n              \"drop\",\n              \"load\",\n              \"pick\",\n              \"unload\"\n            ]\n          },\n          {\n            \"name\": \"locker\",\n            \"room\": \"lobby\",\n            \"is_loaded\": true,\n            \"contents\": [\n              \"paper\"\n            ],\n            \"affordances\": [\n              \"drop\",\n              \"load\",\n              \"pick\",\n              \"unload\"\n            ]\n          }\n        ]\n      },\n      \"external_goal\": {\n        \"has_external_goal\": true,\n        \"external_goal_state\": {},\n        \"external_goal_text\": \"\",\n        \"structured_goal_state\": {},\n        \"structured_final_state\": {\n          \"predicates\": [\n            \"item_on(plate, dining_table)\",\n            \"item_on(fork, dining_table)\",\n            \"item_on(knife, dining_table)\",\n            \"item_on(spoon, dining_table)\",\n            \"item_on(glass, dining_table)\",\n            \"item_on(flower, dining_table)\"\n          ],\n          \"notes\": \"Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower).\"\n        }\n      }\n    },\n    \"understanding_final_state\": {\n      \"predicates\": [\n        \"item_on(plate, dining_table)\",\n        \"item_on(fork, dining_table)\",\n        \"item_on(knife, dining_table)\",\n        \"item_on(spoon, dining_table)\",\n        \"item_on(glass, dining_table)\",\n        \"item_on(flower, dining_table)\"\n      ],\n      \"notes\": \"Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower).\"\n    },\n    \"state_diff_summary\": {\n      \"entity_count_compared\": 18,\n      \"changed_entity_count\": 6,\n      \"changed_entities\": [\n        \"flower\",\n        \"fork\",\n        \"glass\",\n        \"knife\",\n        \"plate\",\n        \"spoon\"\n      ],\n      \"changed_entities_truncated\": false,\n      \"robot_changed\": true,\n      \"robot_change\": {\n        \"changed\": true,\n        \"before\": {\n          \"robot_location\": \"living_room\",\n          \"robot_holding\": \"空\",\n          \"delta_room_neighbors\": {\n            \"bathroom_1\": [\n              \"corridor_2\"\n            ],\n            \"bathroom_2\": [\n              \"corridor_3\"\n            ],\n            \"bedroom_1\": [\n              \"corridor_2\"\n            ],\n            \"bedroom_2\": [\n              \"corridor_3\"\n            ],\n            \"corridor_1\": [\n              \"lobby\",\n              \"corridor_3\"\n            ],\n            \"corridor_2\": [\n              \"bathroom_1\",\n              \"bedroom_1\",\n              \"corridor_3\"\n            ],\n            \"corridor_3\": [\n              \"corridor_1\",\n              \"corridor_2\",\n              \"bathroom_2\",\n              \"bedroom_2\",\n              \"kitchen\",\n              \"living_room\"\n            ],\n            \"dining_room\": [\n              \"kitchen\",\n              \"living_room\"\n            ],\n            \"kitchen\": [\n              \"corridor_3\",\n              \"dining_room\"\n            ],\n            \"living_room\": [\n              \"corridor_3\",\n              \"dining_room\"\n            ],\n            \"lobby\": [\n              \"corridor_1\"\n            ]\n          },\n          \"domain\": \"dining\",\n          \"delta_initial_predicates\": [\n            \"item_is_dining_table dining_table\",\n            \"item_pickable plate\",\n            \"item_accessible plate\",\n            \"item_pickable fork\",\n            \"item_accessible fork\",\n            \"item_pickable knife\",\n            \"item_accessible knife\",\n            \"item_pickable spoon\",\n            \"item_accessible spoon\",\n            \"item_pickable glass\",\n            \"item_accessible glass\",\n            \"item_pickable flower\",\n            \"item_accessible flower\"\n          ]\n        },\n        \"after\": {\n          \"robot_location\": \"dining_room\",\n          \"robot_holding\": \"空\",\n          \"delta_room_neighbors\": {\n            \"bathroom_1\": [\n              \"corridor_2\"\n            ],\n            \"bathroom_2\": [\n              \"corridor_3\"\n            ],\n            \"bedroom_1\": [\n              \"corridor_2\"\n            ],\n            \"bedroom_2\": [\n              \"corridor_3\"\n            ],\n            \"corridor_1\": [\n              \"lobby\",\n              \"corridor_3\"\n            ],\n            \"corridor_2\": [\n              \"bathroom_1\",\n              \"bedroom_1\",\n              \"corridor_3\"\n            ],\n            \"corridor_3\": [\n              \"corridor_1\",\n              \"corridor_2\",\n              \"bathroom_2\",\n              \"bedroom_2\",\n              \"kitchen\",\n              \"living_room\"\n            ],\n            \"dining_room\": [\n              \"kitchen\",\n              \"living_room\"\n            ],\n            \"kitchen\": [\n              \"corridor_3\",\n              \"dining_room\"\n            ],\n            \"living_room\": [\n              \"corridor_3\",\n              \"dining_room\"\n            ],\n            \"lobby\": [\n              \"corridor_1\"\n            ]\n          },\n          \"domain\": \"dining\",\n          \"delta_initial_predicates\": [\n            \"item_is_dining_table dining_table\",\n            \"item_pickable plate\",\n            \"item_accessible plate\",\n            \"item_pickable fork\",\n            \"item_accessible fork\",\n            \"item_pickable knife\",\n            \"item_accessible knife\",\n            \"item_pickable spoon\",\n            \"item_accessible spoon\",\n            \"item_pickable glass\",\n            \"item_accessible glass\",\n            \"item_pickable flower\",\n            \"item_accessible flower\"\n          ]\n        }\n      }\n    },\n    \"initial_environment_summary\": {\n      \"available\": true,\n      \"entity_count\": 18,\n      \"type_counts\": {\n        \"receptacle\": 1,\n        \"room\": 11,\n        \"unknown\": 6\n      },\n      \"states_sample\": {},\n      \"relations_sample\": {\n        \"dining_table\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_room\"\n        },\n        \"dining_room\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"plate\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"bedroom_2\"\n        },\n        \"bedroom_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"fork\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen\"\n        },\n        \"kitchen\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"knife\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen\"\n        },\n        \"spoon\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen\"\n        },\n        \"glass\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"bedroom_1\"\n        },\n        \"bedroom_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"flower\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"lobby\"\n        },\n        \"lobby\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"living_room\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"bathroom_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"bathroom_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_3\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        }\n      }\n    },\n    \"final_environment_summary\": {\n      \"available\": true,\n      \"entity_count\": 18,\n      \"type_counts\": {\n        \"receptacle\": 1,\n        \"room\": 11,\n        \"unknown\": 6\n      },\n      \"states_sample\": {},\n      \"relations_sample\": {\n        \"dining_table\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_room\"\n        },\n        \"dining_room\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"plate\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"bedroom_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"fork\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"kitchen\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"knife\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"spoon\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"glass\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"bedroom_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"flower\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"lobby\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"living_room\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"bathroom_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"bathroom_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_3\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        }\n      }\n    },\n    \"initial_robot\": {\n      \"robot_location\": \"living_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    },\n    \"final_robot\": {\n      \"robot_location\": \"dining_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    },\n    \"fairness_notes\": [\n      \"本 comparer 不读取评测答案字段、官方目标字段或参考代价字段。\",\n      \"DELTA 官方目标只在 planning 结束后的官方评测中使用。\"\n    ],\n    \"judge_contract\": \"公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。\",\n    \"enabled\": true,\n    \"comparer_module\": \"benchmark.delta.framework.code.final_state\"\n  }\n}\n\n判定边界：\n1. 优先读取 state_audit_context.benchmark_final_state_compare；其中是 DELTA comparer 基于本地环境和公开任务字段准备的目标材料。\n2. 结合 understanding final_state、任务原文、sandbox final environment/final robot 和 state_diff 判断关键目标是否完成。\n3. 不使用评测答案字段、官方目标字段或参考代价字段；不要把任务转换成其他 benchmark 格式。\n4. 如果关键目标缺失，is_passed=false，并写出缺失的最终状态和后续 planning 应补的动作类型。\n5. 如果当前最终态只需追加动作即可修复，repair_mode=\"continue_from_current\"；如果已验证前缀本身错，repair_mode=\"reset_and_replan\"。\n\n输出 JSON：\n{\"is_passed\": true, \"issue\": \"\", \"fix_advice\": \"\", \"repair_mode\": \"continue_from_current\", \"accepted_diffs\": [], \"unexpected_diffs\": []}"
  }
]
```

#### Output
```text
{"is_passed": true, "issue": "", "fix_advice": "", "repair_mode": "continue_from_current", "accepted_diffs": ["plate", "fork", "knife", "spoon", "glass", "flower"], "unexpected_diffs": []}
```

## 10. 初始提示词与后续修复提示

### Understanding 初始提示
```json
[
  {
    "type": "system",
    "content": "任务：把 DELTA benchmark case 输入抽取成结构化任务理解。\n只返回 JSON；不要解释，不要输出 Markdown。\n\n允许使用的 DELTA 场景实体名：\n[\"banana_peel\", \"bathroom_1\", \"bathroom_2\", \"bed_1\", \"bed_2\", \"bedroom_1\", \"bedroom_2\", \"book\", \"bowl_2\", \"bowl_3\", \"chair_1\", \"chair_2\", \"chair_3\", \"chair_4\", \"chair_5\", \"clock\", \"cola_can\", \"corridor_1\", \"corridor_2\", \"corridor_3\", \"couch\", \"cpu\", \"desk\", \"dining_room\", \"dining_table\", \"flower\", \"fork\", \"fridge_1\", \"fridge_2\", \"fridge_3\", \"glass\", \"gpu\", \"kitchen\", \"knife\", \"lamp\", \"living_room\", \"lobby\", \"locker\", \"mainboard\", \"microwave\", \"mop\", \"oven\", \"paper\", \"plant_1\", \"plant_2\", \"plate\", \"psu\", \"ram\", \"robot_hub\", \"rotting_apple\", \"rubbish_bin\", \"shelf\", \"sink_1\", \"sink_2\", \"spoon\", \"ssd\", \"toilet_1\", \"toilet_2\"]\n\nDELTA 任务上下文 JSON：\n{\n  \"dataset\": \"delta\",\n  \"task_name\": \"dining:allensville:episode-01\",\n  \"domain\": \"dining\",\n  \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n  \"task_source\": \"delta_data_example_py\",\n  \"environment_source\": \"delta_data_scene_graph_py\",\n  \"scene_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json\",\n  \"delta_add_obj_types\": [],\n  \"delta_env_state_predicates\": [\n    \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n    \"item_is_dining_table(<item>): <item> is dining_table.\"\n  ],\n  \"delta_initial_predicates\": [\n    \"item_is_dining_table dining_table\",\n    \"item_pickable plate\",\n    \"item_accessible plate\",\n    \"item_pickable fork\",\n    \"item_accessible fork\",\n    \"item_pickable knife\",\n    \"item_accessible knife\",\n    \"item_pickable spoon\",\n    \"item_accessible spoon\",\n    \"item_pickable glass\",\n    \"item_accessible glass\",\n    \"item_pickable flower\",\n    \"item_accessible flower\"\n  ],\n  \"delta_room_neighbors\": {\n    \"bathroom_1\": [\n      \"corridor_2\"\n    ],\n    \"bathroom_2\": [\n      \"corridor_3\"\n    ],\n    \"bedroom_1\": [\n      \"corridor_2\"\n    ],\n    \"bedroom_2\": [\n      \"corridor_3\"\n    ],\n    \"corridor_1\": [\n      \"lobby\",\n      \"corridor_3\"\n    ],\n    \"corridor_2\": [\n      \"bathroom_1\",\n      \"bedroom_1\",\n      \"corridor_3\"\n    ],\n    \"corridor_3\": [\n      \"corridor_1\",\n      \"corridor_2\",\n      \"bathroom_2\",\n      \"bedroom_2\",\n      \"kitchen\",\n      \"living_room\"\n    ],\n    \"dining_room\": [\n      \"kitchen\",\n      \"living_room\"\n    ],\n    \"kitchen\": [\n      \"corridor_3\",\n      \"dining_room\"\n    ],\n    \"living_room\": [\n      \"corridor_3\",\n      \"dining_room\"\n    ],\n    \"lobby\": [\n      \"corridor_1\"\n    ]\n  },\n  \"delta_accessible_items\": [\n    \"psu\",\n    \"sink_1\",\n    \"mop\",\n    \"gpu\",\n    \"sink_2\",\n    \"mainboard\",\n    \"glass\",\n    \"shelf\",\n    \"book\",\n    \"cpu\",\n    \"rotting_apple\",\n    \"plate\",\n    \"lamp\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"ssd\",\n    \"cola_can\",\n    \"dining_table\",\n    \"knife\",\n    \"fork\",\n    \"spoon\",\n    \"microwave\",\n    \"oven\",\n    \"rubbish_bin\",\n    \"fridge_3\",\n    \"desk\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"robot_hub\",\n    \"ram\",\n    \"banana_peel\",\n    \"flower\",\n    \"locker\",\n    \"paper\"\n  ],\n  \"loadable_containers\": [\n    {\n      \"name\": \"shelf\",\n      \"room\": \"bedroom_1\",\n      \"is_loaded\": true,\n      \"contents\": [\n        \"book\"\n      ],\n      \"affordances\": [\n        \"drop\",\n        \"load\",\n        \"pick\",\n        \"unload\"\n      ]\n    },\n    {\n      \"name\": \"locker\",\n      \"room\": \"lobby\",\n      \"is_loaded\": true,\n      \"contents\": [\n        \"paper\"\n      ],\n      \"affordances\": [\n        \"drop\",\n        \"load\",\n        \"pick\",\n        \"unload\"\n      ]\n    }\n  ],\n  \"task_environment_mode\": \"understanding_pruned\",\n  \"available_entities\": [\n    \"banana_peel\",\n    \"bathroom_1\",\n    \"bathroom_2\",\n    \"bed_1\",\n    \"bed_2\",\n    \"bedroom_1\",\n    \"bedroom_2\",\n    \"book\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"chair_1\",\n    \"chair_2\",\n    \"chair_3\",\n    \"chair_4\",\n    \"chair_5\",\n    \"clock\",\n    \"cola_can\",\n    \"corridor_1\",\n    \"corridor_2\",\n    \"corridor_3\",\n    \"couch\",\n    \"cpu\",\n    \"desk\",\n    \"dining_room\",\n    \"dining_table\",\n    \"flower\",\n    \"fork\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"fridge_3\",\n    \"glass\",\n    \"gpu\",\n    \"kitchen\",\n    \"knife\",\n    \"lamp\",\n    \"living_room\",\n    \"lobby\",\n    \"locker\",\n    \"mainboard\",\n    \"microwave\",\n    \"mop\",\n    \"oven\",\n    \"paper\",\n    \"plant_1\",\n    \"plant_2\",\n    \"plate\",\n    \"psu\",\n    \"ram\",\n    \"robot_hub\",\n    \"rotting_apple\",\n    \"rubbish_bin\",\n    \"shelf\",\n    \"sink_1\",\n    \"sink_2\",\n    \"spoon\",\n    \"ssd\",\n    \"toilet_1\",\n    \"toilet_2\"\n  ]\n}\n任务上下文中的 domain、scene_name、delta_env_state、delta_add_obj_types、delta_accessible_items、delta_env_state_predicates 是本 benchmark 的 grounding 材料；不要把它们改写成其他 benchmark 的字段。\n\nDELTA 可用 skill 摘要：\n[\n  {\n    \"name\": \"goto\",\n    \"description\": \"DELTA official executable goto action.\",\n    \"planning_contract\": {\n      \"planner_location_param\": \"to\",\n      \"planner_action_name\": \"goto\",\n      \"planner_required_fields\": \"action,agent,room_1,room_2\",\n      \"planner_fixed_fields\": \"action=goto;agent=robot\",\n      \"planner_room_fields\": \"room_1,room_2\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean,dining,office,pc\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"pick\",\n    \"description\": \"DELTA official executable pick action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_requires_empty_hand\": \"true\",\n      \"planner_action_name\": \"pick\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=pick;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean,dining,office,pc\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"drop\",\n    \"description\": \"DELTA official executable drop action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"room\",\n      \"planner_action_name\": \"drop\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=drop;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean,dining,office,pc\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"place_on\",\n    \"description\": \"DELTA official executable place_on action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"surface\",\n      \"planner_action_name\": \"place_on\",\n      \"planner_required_fields\": \"action,agent,item_1,item_2,room\",\n      \"planner_fixed_fields\": \"action=place_on;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"dining\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"dispose\",\n    \"description\": \"DELTA official executable dispose action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"disposal\",\n      \"planner_effect_state_key\": \"isDisposed\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"dispose\",\n      \"planner_required_fields\": \"action,agent,item_1,item_2,room\",\n      \"planner_fixed_fields\": \"action=dispose;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"mop_floor\",\n    \"description\": \"DELTA official executable mop_floor action.\",\n    \"planning_contract\": {\n      \"planner_location_param\": \"room\",\n      \"planner_effect_state_key\": \"floor_clean\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"mop_floor\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=mop_floor;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"clean_mop\",\n    \"description\": \"DELTA official executable clean_mop action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"tool\",\n      \"planner_location_param\": \"water_source\",\n      \"planner_effect_state_key\": \"isClean\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"clean_mop\",\n      \"planner_required_fields\": \"action,agent,item_1,item_2,room\",\n      \"planner_fixed_fields\": \"action=clean_mop;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"charge\",\n    \"description\": \"DELTA official executable charge action.\",\n    \"planning_contract\": {\n      \"planner_location_param\": \"station\",\n      \"planner_requires_empty_hand\": \"true\",\n      \"planner_effect_state_key\": \"battery_full\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"charge\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=charge;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"clean\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"assemble\",\n    \"description\": \"DELTA official executable assemble action.\",\n    \"planning_contract\": {\n      \"planner_target_param\": \"target_pc\",\n      \"planner_location_param\": \"room\",\n      \"planner_requires_empty_hand\": \"true\",\n      \"planner_effect_state_key\": \"isAssembled\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"assemble\",\n      \"planner_required_fields\": \"action,agent,room,item_1,item_2,item_3,item_4,item_5,item_6,pc\",\n      \"planner_fixed_fields\": \"action=assemble;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2,item_3,item_4,item_5,item_6\",\n      \"planner_room_fields\": \"room\",\n      \"planner_unchecked_fields\": \"pc\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"pc\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"pick_loadable\",\n    \"description\": \"DELTA official executable pick_loadable action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_requires_empty_hand\": \"true\",\n      \"planner_action_name\": \"pick_loadable\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=pick_loadable;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"office\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"drop_loadable\",\n    \"description\": \"DELTA official executable drop_loadable action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"room\",\n      \"planner_action_name\": \"drop_loadable\",\n      \"planner_required_fields\": \"action,agent,item,room\",\n      \"planner_fixed_fields\": \"action=drop_loadable;agent=robot\",\n      \"planner_entity_fields\": \"item\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"office\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"load\",\n    \"description\": \"DELTA official executable load action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"loadable\",\n      \"planner_action_name\": \"load\",\n      \"planner_required_fields\": \"action,agent,item_1,item_2,room\",\n      \"planner_fixed_fields\": \"action=load;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"office\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"unload\",\n    \"description\": \"DELTA official executable unload action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"item\",\n      \"planner_destination_param\": \"room\",\n      \"planner_action_name\": \"unload\",\n      \"planner_required_fields\": \"action,agent,item_1,item_2,room\",\n      \"planner_fixed_fields\": \"action=unload;agent=robot\",\n      \"planner_entity_fields\": \"item_1,item_2\",\n      \"planner_room_fields\": \"room\",\n      \"planner_context_field\": \"domain\",\n      \"planner_context_values\": \"office\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  }\n]\n\n理解边界：\n1. intent 保留 DELTA 原始任务目标，不生成动作序列。\n2. required_item_names 必须使用允许实体名或 DELTA 任务上下文中的完整实体名；房间、物体、工具和充电/清洁设施不能混用类型。\n3. required_item_names 的角色必须与 DELTA 任务上下文和可用 skill 参数类型一致；不要把非房间实体放进房间类角色。\n4. skill_closure 只能使用 DELTA skills root 中启用的 skill 名，例如 goto、pick、dispose、mop_floor、clean_mop、charge。\n5. 如果原始任务要求多个同类实例或多个位置，primary 必须列出不同真实实体，quantity_constraints 记录数量。\n\n输出 JSON 结构：\n{\"is_complete\": true, \"is_cancel_all\": false, \"clarification_question\": \"\", \"entity_relevance\": {\"directly_related\": [], \"indirectly_related\": [], \"possibly_related\": []}, \"skill_closure\": [], \"structured_task\": {\"intent\": \"\", \"required_item_names\": {\"targets\": {\"primary\": [], \"alternatives\": []}, \"tools\": {\"primary\": [], \"alternatives\": []}, \"receptacles\": {\"primary\": [], \"alternatives\": []}}, \"quantity_constraints\": []}}"
  },
  {
    "type": "human",
    "content": "Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table."
  }
]
```

### Planning 初始提示
```json
[
  {
    "type": "system",
    "content": "任务：生成 DELTA 官方原生动作计划。\n只输出 JSON；不要解释，不要输出 Markdown。\n\n原始任务：\n\n\n规划目标：\nSet up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\n\n机器人状态：\n- 位置：living_room\n- 手持：空\n- 完整状态：{\"robot_location\":\"living_room\",\"robot_holding\":\"空\",\"delta_room_neighbors\":{\"bathroom_1\":[\"corridor_2\"],\"bathroom_2\":[\"corridor_3\"],\"bedroom_1\":[\"corridor_2\"],\"bedroom_2\":[\"corridor_3\"],\"corridor_1\":[\"lobby\",\"corridor_3\"],\"corridor_2\":[\"bathroom_1\",\"bedroom_1\",\"corridor_3\"],\"corridor_3\":[\"corridor_1\",\"corridor_2\",\"bathroom_2\",\"bedroom_2\",\"kitchen\",\"living_room\"],\"dining_room\":[\"kitchen\",\"living_room\"],\"kitchen\":[\"corridor_3\",\"dining_room\"],\"living_room\":[\"corridor_3\",\"dining_room\"],\"lobby\":[\"corridor_1\"]},\"domain\":\"dining\",\"delta_initial_predicates\":[\"item_is_dining_table dining_table\",\"item_pickable plate\",\"item_accessible plate\",\"item_pickable fork\",\"item_accessible fork\",\"item_pickable knife\",\"item_accessible knife\",\"item_pickable spoon\",\"item_accessible spoon\",\"item_pickable glass\",\"item_accessible glass\",\"item_pickable flower\",\"item_accessible flower\"]}\n\n当前环境 JSON：\n{\"dining_table\":{\"direct_parent\":\"dining_room\",\"direct_relation\":\"inside\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_predicate:item_is_dining_table\"],\"is_container\":true,\"full_path\":[\"dining_room\"]},\"dining_room\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"plate\":{\"direct_parent\":\"bedroom_2\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"bedroom_2\"]},\"bedroom_2\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"fork\":{\"direct_parent\":\"kitchen\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"kitchen\"]},\"kitchen\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"knife\":{\"direct_parent\":\"kitchen\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"kitchen\"]},\"spoon\":{\"direct_parent\":\"kitchen\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"kitchen\"]},\"glass\":{\"direct_parent\":\"bedroom_1\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"bedroom_1\"]},\"bedroom_1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"flower\":{\"direct_parent\":\"lobby\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"delta_accessible:true\",\"delta_affordance:drop\",\"delta_affordance:pick\",\"delta_affordance:place_on\",\"delta_predicate:item_pickable\",\"delta_predicate:item_accessible\"],\"is_container\":false,\"full_path\":[\"lobby\"]},\"lobby\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"living_room\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"bathroom_1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"bathroom_2\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"corridor_1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"corridor_2\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"corridor_3\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]}}\n\n目标物品当前位置（来自官方场景图；pick 的 room 必须与此表一致，只能从物体当前所在房间拾取）：\n- dining_table: dining_room\n- flower: lobby\n- fork: kitchen\n- glass: bedroom_1\n- knife: kitchen\n- plate: bedroom_2\n- spoon: kitchen\n\n任务相关环境事实：\n[{\"name\":\"bathroom_1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"bathroom_2\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"bedroom_1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"bedroom_2\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"corridor_1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"corridor_2\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"corridor_3\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"dining_room\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"dining_table\",\"direct_parent\":\"dining_room\",\"full_path\":[\"dining_room\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"flower\",\"direct_parent\":\"lobby\",\"full_path\":[\"lobby\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"fork\",\"direct_parent\":\"kitchen\",\"full_path\":[\"kitchen\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"glass\",\"direct_parent\":\"bedroom_1\",\"full_path\":[\"bedroom_1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"kitchen\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"knife\",\"direct_parent\":\"kitchen\",\"full_path\":[\"kitchen\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"living_room\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"lobby\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"plate\",\"direct_parent\":\"bedroom_2\",\"full_path\":[\"bedroom_2\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"spoon\",\"direct_parent\":\"kitchen\",\"full_path\":[\"kitchen\"],\"states\":{},\"type\":null,\"is_container\":false}]\n\n任务上下文：\n{\n  \"dataset\": \"delta\",\n  \"task_name\": \"dining:allensville:episode-01\",\n  \"domain\": \"dining\",\n  \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n  \"task_source\": \"delta_data_example_py\",\n  \"environment_source\": \"delta_data_scene_graph_py\",\n  \"scene_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json\",\n  \"delta_add_obj_types\": [],\n  \"delta_env_state_predicates\": [\n    \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n    \"item_is_dining_table(<item>): <item> is dining_table.\"\n  ],\n  \"delta_initial_predicates\": [\n    \"item_is_dining_table dining_table\",\n    \"item_pickable plate\",\n    \"item_accessible plate\",\n    \"item_pickable fork\",\n    \"item_accessible fork\",\n    \"item_pickable knife\",\n    \"item_accessible knife\",\n    \"item_pickable spoon\",\n    \"item_accessible spoon\",\n    \"item_pickable glass\",\n    \"item_accessible glass\",\n    \"item_pickable flower\",\n    \"item_accessible flower\"\n  ],\n  \"delta_room_neighbors\": {\n    \"bathroom_1\": [\n      \"corridor_2\"\n    ],\n    \"bathroom_2\": [\n      \"corridor_3\"\n    ],\n    \"bedroom_1\": [\n      \"corridor_2\"\n    ],\n    \"bedroom_2\": [\n      \"corridor_3\"\n    ],\n    \"corridor_1\": [\n      \"lobby\",\n      \"corridor_3\"\n    ],\n    \"corridor_2\": [\n      \"bathroom_1\",\n      \"bedroom_1\",\n      \"corridor_3\"\n    ],\n    \"corridor_3\": [\n      \"corridor_1\",\n      \"corridor_2\",\n      \"bathroom_2\",\n      \"bedroom_2\",\n      \"kitchen\",\n      \"living_room\"\n    ],\n    \"dining_room\": [\n      \"kitchen\",\n      \"living_room\"\n    ],\n    \"kitchen\": [\n      \"corridor_3\",\n      \"dining_room\"\n    ],\n    \"living_room\": [\n      \"corridor_3\",\n      \"dining_room\"\n    ],\n    \"lobby\": [\n      \"corridor_1\"\n    ]\n  },\n  \"delta_accessible_items\": [\n    \"psu\",\n    \"sink_1\",\n    \"mop\",\n    \"gpu\",\n    \"sink_2\",\n    \"mainboard\",\n    \"glass\",\n    \"shelf\",\n    \"book\",\n    \"cpu\",\n    \"rotting_apple\",\n    \"plate\",\n    \"lamp\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"ssd\",\n    \"cola_can\",\n    \"dining_table\",\n    \"knife\",\n    \"fork\",\n    \"spoon\",\n    \"microwave\",\n    \"oven\",\n    \"rubbish_bin\",\n    \"fridge_3\",\n    \"desk\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"robot_hub\",\n    \"ram\",\n    \"banana_peel\",\n    \"flower\",\n    \"locker\",\n    \"paper\"\n  ],\n  \"loadable_containers\": [\n    {\n      \"name\": \"shelf\",\n      \"room\": \"bedroom_1\",\n      \"is_loaded\": true,\n      \"contents\": [\n        \"book\"\n      ],\n      \"affordances\": [\n        \"drop\",\n        \"load\",\n        \"pick\",\n        \"unload\"\n      ]\n    },\n    {\n      \"name\": \"locker\",\n      \"room\": \"lobby\",\n      \"is_loaded\": true,\n      \"contents\": [\n        \"paper\"\n      ],\n      \"affordances\": [\n        \"drop\",\n        \"load\",\n        \"pick\",\n        \"unload\"\n      ]\n    }\n  ],\n  \"task_environment_mode\": \"understanding_pruned\",\n  \"available_entities\": [\n    \"banana_peel\",\n    \"bathroom_1\",\n    \"bathroom_2\",\n    \"bed_1\",\n    \"bed_2\",\n    \"bedroom_1\",\n    \"bedroom_2\",\n    \"book\",\n    \"bowl_2\",\n    \"bowl_3\",\n    \"chair_1\",\n    \"chair_2\",\n    \"chair_3\",\n    \"chair_4\",\n    \"chair_5\",\n    \"clock\",\n    \"cola_can\",\n    \"corridor_1\",\n    \"corridor_2\",\n    \"corridor_3\",\n    \"couch\",\n    \"cpu\",\n    \"desk\",\n    \"dining_room\",\n    \"dining_table\",\n    \"flower\",\n    \"fork\",\n    \"fridge_1\",\n    \"fridge_2\",\n    \"fridge_3\",\n    \"glass\",\n    \"gpu\",\n    \"kitchen\",\n    \"knife\",\n    \"lamp\",\n    \"living_room\",\n    \"lobby\",\n    \"locker\",\n    \"mainboard\",\n    \"microwave\",\n    \"mop\",\n    \"oven\",\n    \"paper\",\n    \"plant_1\",\n    \"plant_2\",\n    \"plate\",\n    \"psu\",\n    \"ram\",\n    \"robot_hub\",\n    \"rotting_apple\",\n    \"rubbish_bin\",\n    \"shelf\",\n    \"sink_1\",\n    \"sink_2\",\n    \"spoon\",\n    \"ssd\",\n    \"toilet_1\",\n    \"toilet_2\"\n  ]\n}\n\n新增对象类型（若有）：\n（无）\n\n\n房间邻接表（goto 的 from/to 之间必须在此表中存在可达路径；框架会自动展开为走廊逐跳）：\n- bathroom_1: corridor_2\n- bathroom_2: corridor_3\n- bedroom_1: corridor_2\n- bedroom_2: corridor_3\n- corridor_1: corridor_3, lobby\n- corridor_2: bathroom_1, bedroom_1, corridor_3\n- corridor_3: bathroom_2, bedroom_2, corridor_1, corridor_2, kitchen, living_room\n- dining_room: kitchen, living_room\n- kitchen: corridor_3, dining_room\n- living_room: corridor_3, dining_room\n- lobby: corridor_1\n\n\n理解层实体选择：\n{\n  \"targets\": {\n    \"primary\": [\n      \"dining_table\"\n    ],\n    \"alternatives\": []\n  },\n  \"tools\": {\n    \"primary\": [\n      \"plate\",\n      \"fork\",\n      \"knife\",\n      \"spoon\",\n      \"glass\"\n    ],\n    \"alternatives\": []\n  },\n  \"receptacles\": {\n    \"primary\": [\n      \"flower\"\n    ],\n    \"alternatives\": []\n  }\n}\n\n可用动作与 skill 契约：\n<available_skills>\n---\nname: goto\ndescription: DELTA official executable goto action.\n---\n\n## 参数\n| 参数名 | 类型 | 含义 |\n| --- | --- | --- |\n| agent | string | DELTA PDDL agent，固定为 `robot`。 |\n| room_1 | string | 机器人当前所在的 DELTA 房间名。 |\n| room_2 | string | 机器人要移动到的 DELTA 房间名。 |\n\n## 前提条件\n- 必须使用 DELTA PDDL 签名 `goto(robot, room_1, room_2)` 和下面的同签名 JSON 对象。\n- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- `agent` 必须是 `robot`。\n- `room_1` 和 `room_2` 都必须是当前 DELTA 场景中的真实房间。\n- `room_1` 必须等于机器人当前所在房间。\n- `room_1` 与 `room_2` 之间必须在 `delta_room_neighbors`（任务上下文中的房间邻接表）里存在可达路径。\n- 框架会按公开场景图邻接关系自动把房间级 `goto` 展开为具体走廊逐跳，模型不需要输出中间走廊步。\n- 如果机器人已经在目标房间，不要输出同房间 `goto`。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，机器人位置从 `room_1` 更新为 `room_2`。\n\n## 输出格式\n在 DELTA 原生动作 JSON 数组中使用这个动作对象：\n\n```json\n{\"action\":\"goto\",\"agent\":\"robot\",\"room_1\":\"<current_room>\",\"room_2\":\"<destination_room>\"}\n```\n\n- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确房间名。\n- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。\n\n\n---\nname: pick\ndescription: DELTA official executable pick action.\n---\n\n## 参数\n| 参数名 | 类型 | 含义 |\n| --- | --- | --- |\n| agent | string | DELTA PDDL agent，固定为 `robot`。 |\n| item | string | 当前环境中的普通可拾取物品实体名。 |\n| room | string | `item` 所在的 DELTA 房间名。 |\n\n## 前提条件\n- 必须使用 DELTA PDDL 签名 `pick(robot, item, room)` 和下面的同签名 JSON 对象。\n- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- `agent` 必须是 `robot`。\n- `item` 必须是当前环境中的真实实体，并满足可访问、可拾取条件。\n- `room` 必须是当前 DELTA 场景中的真实房间，并且必须是 `item` 所在房间。\n- 机器人必须已经在 `room`，且手中没有物品。\n- 普通物品使用 `pick`；如果任务需要拾取 empty loadable container，应使用 `pick_loadable`。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，机器人持有 `item`，`item` 不再直接位于 `room`。\n\n## 输出格式\n在 DELTA 原生动作 JSON 数组中使用这个动作对象：\n\n```json\n{\"action\":\"pick\",\"agent\":\"robot\",\"item\":\"<item_entity>\",\"room\":\"<item_room>\"}\n```\n\n- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。\n- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。\n\n\n---\nname: place_on\ndescription: DELTA official executable place_on action.\n---\n\n## 参数\n| 参数名 | 类型 | 含义 |\n| --- | --- | --- |\n| agent | string | DELTA PDDL agent，固定为 `robot`。 |\n| item_1 | string | 当前机器人持有的 DELTA 物品实体名。 |\n| item_2 | string | 当前环境中的 dining_table/surface 实体名。 |\n| room | string | `item_2` 所在的 DELTA 房间名。 |\n\n## 前提条件\n- 必须使用 DELTA PDDL 签名 `place_on(robot, item_1, item_2, room)` 和下面的同签名 JSON 对象。\n- 当前 DELTA 场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- `agent` 必须是 `robot`。\n- `item_1` 必须是当前环境中的真实实体，且机器人已经持有它。\n- `item_2` 必须是当前环境中的真实实体，且满足 DELTA dining-table/surface 谓词；不要把房间名当作 `item_2`。\n- `room` 必须是当前 DELTA 场景中的真实房间，并且必须是 `item_2` 所在房间。\n- 机器人必须已经在 `room`；如果 `item_1` 不在机器人手中，`place_on` 必须被 sandbox 拒绝。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，`item_1` 位于 `item_2` 上，机器人手变为空；其他位置变化只以 handler.apply(...) 的实际更新为准。\n\n## 输出格式\n在 DELTA 原生动作 JSON 数组中使用这个动作对象：\n\n```json\n{\"action\":\"place_on\",\"agent\":\"robot\",\"item_1\":\"<held_item_entity>\",\"item_2\":\"<dining_table_entity>\",\"room\":\"<surface_room>\"}\n```\n\n- 尖括号中的值只是占位符，真实输出必须替换为当前环境中的精确实体名。\n- 不要输出框架包装字段、公共 todo_list 字段或非 DELTA 动作名。\n\n</available_skills>\n\n历史失败反馈：\n暂无相关拦截记录\n\n规划边界：\n1. 只使用 <available_skills> 中列出的动作。\n2. 动作参数、前置条件、状态依赖和效果只以对应 skill 契约为准。\n3. 只引用当前环境、任务上下文、任务相关环境事实或理解层结果中出现的实体/房间/对象名。\n4. 如果已有修复反馈或修复状态，只生成尚未验证的后续动作。\n5. 机器人一次只能携带一个物品；拿取下一个物品前，必须先把当前手持物品 drop 到目标位置。\n6. 执行需要多个物品位于同一房间的复合动作（如 assemble）之前，必须先通过 drop 把全部相关物品放到该动作要求的房间；复合动作只会因为物品未就位被拒绝。\n\n输出格式：\n直接输出 DELTA 官方动作 JSON 数组。\n每个元素包含 action 和该动作 skill 契约要求的参数字段；不要输出任何框架包装字段。\n如果任务已经完成，返回 []。"
  },
  {
    "type": "human",
    "content": "开始规划。"
  }
]
```

### Planning 后续修复轮
#### Planning Turn 2
```json
[
  {
    "type": "human",
    "content": "任务：根据 DELTA sandbox 前后状态差异判断任务是否完成。\n只输出 JSON；不要解释，不要生成动作。\n\n任务目标：Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\n\n完整 native action 计划摘要：\n[\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"living_room\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"fork\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"fork\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"knife\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"knife\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"spoon\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"spoon\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"bedroom_1\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"glass\",\n    \"room\": \"bedroom_1\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"bedroom_1\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"glass\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"bedroom_2\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"plate\",\n    \"room\": \"bedroom_2\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"bedroom_2\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"plate\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"lobby\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"flower\",\n    \"room\": \"lobby\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"lobby\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"flower\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  }\n]\n\n本轮实际模拟步骤：\n[\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"living_room\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"fork\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"fork\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"knife\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"knife\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"kitchen\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"spoon\",\n    \"room\": \"kitchen\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"kitchen\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"spoon\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"bedroom_1\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"glass\",\n    \"room\": \"bedroom_1\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"bedroom_1\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"glass\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"bedroom_2\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"plate\",\n    \"room\": \"bedroom_2\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"bedroom_2\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"plate\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"dining_room\",\n    \"room_2\": \"lobby\"\n  },\n  {\n    \"action\": \"pick\",\n    \"agent\": \"robot\",\n    \"item\": \"flower\",\n    \"room\": \"lobby\"\n  },\n  {\n    \"action\": \"goto\",\n    \"agent\": \"robot\",\n    \"room_1\": \"lobby\",\n    \"room_2\": \"dining_room\"\n  },\n  {\n    \"action\": \"place_on\",\n    \"agent\": \"robot\",\n    \"item_1\": \"flower\",\n    \"item_2\": \"dining_table\",\n    \"room\": \"dining_room\"\n  }\n]\n\n轨迹摘要：\nStep 1: goto([])\nStep 2: goto([])\nStep 3: pick([])\nStep 4: goto([])\nStep 5: place_on([])\nStep 6: goto([])\nStep 7: pick([])\nStep 8: goto([])\nStep 9: place_on([])\nStep 10: goto([])\nStep 11: pick([])\nStep 12: goto([])\nStep 13: place_on([])\nStep 14: goto([])\nStep 15: pick([])\nStep 16: goto([])\nStep 17: place_on([])\nStep 18: goto([])\nStep 19: pick([])\nStep 20: goto([])\nStep 21: place_on([])\nStep 22: goto([])\nStep 23: pick([])\nStep 24: goto([])\nStep 25: place_on([])\n\nDELTA 状态差异 JSON：\n{\n  \"entity_count_compared\": 18,\n  \"changed_entity_count\": 6,\n  \"truncated_entity_count\": 0,\n  \"has_changes\": true,\n  \"robot\": {\n    \"changed\": true,\n    \"before\": {\n      \"robot_location\": \"living_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    },\n    \"after\": {\n      \"robot_location\": \"dining_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    }\n  },\n  \"entities\": [\n    {\n      \"name\": \"flower\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"lobby\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"lobby\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"fork\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"glass\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"bedroom_1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"bedroom_1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"knife\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"plate\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"bedroom_2\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"bedroom_2\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"spoon\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    }\n  ]\n}\n\n状态审计上下文 JSON：\n{\n  \"entity_count_available\": 18,\n  \"entity_count_in_context\": 8,\n  \"truncated_entity_count\": 0,\n  \"note\": \"state_diff only lists changed entities; unchanged entities in this context still prove final goal state when their after state satisfies the task.\",\n  \"robot\": {\n    \"changed\": true,\n    \"before\": {\n      \"robot_location\": \"living_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    },\n    \"after\": {\n      \"robot_location\": \"dining_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    }\n  },\n  \"entities\": [\n    {\n      \"name\": \"dining_table\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"dining_room\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"dining_room\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_predicate:item_is_dining_table\"\n        ]\n      },\n      \"after\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"dining_room\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"dining_room\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_predicate:item_is_dining_table\"\n        ]\n      }\n    },\n    {\n      \"name\": \"plate\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"bedroom_2\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"bedroom_2\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"fork\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"knife\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"spoon\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"glass\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"bedroom_1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"bedroom_1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"flower\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"lobby\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"lobby\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"dining_table\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"dining_room\",\n          \"dining_table\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"delta_accessible:true\",\n          \"delta_affordance:drop\",\n          \"delta_affordance:pick\",\n          \"delta_affordance:place_on\",\n          \"delta_predicate:item_pickable\",\n          \"delta_predicate:item_accessible\"\n        ]\n      }\n    },\n    {\n      \"name\": \"dining_room\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      },\n      \"after\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      }\n    }\n  ],\n  \"task_context\": {\n    \"dataset\": \"delta\",\n    \"task_name\": \"dining:allensville:episode-01\",\n    \"domain\": \"dining\",\n    \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n    \"task_source\": \"delta_data_example_py\",\n    \"environment_source\": \"delta_data_scene_graph_py\",\n    \"scene_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json\",\n    \"delta_add_obj_types\": [],\n    \"delta_env_state_predicates\": [\n      \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n      \"item_is_dining_table(<item>): <item> is dining_table.\"\n    ],\n    \"delta_initial_predicates\": [\n      \"item_is_dining_table dining_table\",\n      \"item_pickable plate\",\n      \"item_accessible plate\",\n      \"item_pickable fork\",\n      \"item_accessible fork\",\n      \"item_pickable knife\",\n      \"item_accessible knife\",\n      \"item_pickable spoon\",\n      \"item_accessible spoon\",\n      \"item_pickable glass\",\n      \"item_accessible glass\",\n      \"item_pickable flower\",\n      \"item_accessible flower\"\n    ],\n    \"delta_room_neighbors\": {\n      \"bathroom_1\": [\n        \"corridor_2\"\n      ],\n      \"bathroom_2\": [\n        \"corridor_3\"\n      ],\n      \"bedroom_1\": [\n        \"corridor_2\"\n      ],\n      \"bedroom_2\": [\n        \"corridor_3\"\n      ],\n      \"corridor_1\": [\n        \"lobby\",\n        \"corridor_3\"\n      ],\n      \"corridor_2\": [\n        \"bathroom_1\",\n        \"bedroom_1\",\n        \"corridor_3\"\n      ],\n      \"corridor_3\": [\n        \"corridor_1\",\n        \"corridor_2\",\n        \"bathroom_2\",\n        \"bedroom_2\",\n        \"kitchen\",\n        \"living_room\"\n      ],\n      \"dining_room\": [\n        \"kitchen\",\n        \"living_room\"\n      ],\n      \"kitchen\": [\n        \"corridor_3\",\n        \"dining_room\"\n      ],\n      \"living_room\": [\n        \"corridor_3\",\n        \"dining_room\"\n      ],\n      \"lobby\": [\n        \"corridor_1\"\n      ]\n    },\n    \"delta_accessible_items\": [\n      \"psu\",\n      \"sink_1\",\n      \"mop\",\n      \"gpu\",\n      \"sink_2\",\n      \"mainboard\",\n      \"glass\",\n      \"shelf\",\n      \"book\",\n      \"cpu\",\n      \"rotting_apple\",\n      \"plate\",\n      \"lamp\",\n      \"fridge_1\",\n      \"fridge_2\",\n      \"ssd\",\n      \"cola_can\",\n      \"dining_table\",\n      \"knife\",\n      \"fork\",\n      \"spoon\",\n      \"microwave\",\n      \"oven\",\n      \"rubbish_bin\",\n      \"fridge_3\",\n      \"desk\",\n      \"bowl_2\",\n      \"bowl_3\",\n      \"robot_hub\",\n      \"ram\",\n      \"banana_peel\",\n      \"flower\",\n      \"locker\",\n      \"paper\"\n    ],\n    \"loadable_containers\": [\n      {\n        \"name\": \"shelf\",\n        \"room\": \"bedroom_1\",\n        \"is_loaded\": true,\n        \"contents\": [\n          \"book\"\n        ],\n        \"affordances\": [\n          \"drop\",\n          \"load\",\n          \"pick\",\n          \"unload\"\n        ]\n      },\n      {\n        \"name\": \"locker\",\n        \"room\": \"lobby\",\n        \"is_loaded\": true,\n        \"contents\": [\n          \"paper\"\n        ],\n        \"affordances\": [\n          \"drop\",\n          \"load\",\n          \"pick\",\n          \"unload\"\n        ]\n      }\n    ],\n    \"task_environment_mode\": \"understanding_pruned\",\n    \"available_entities\": [\n      \"banana_peel\",\n      \"bathroom_1\",\n      \"bathroom_2\",\n      \"bed_1\",\n      \"bed_2\",\n      \"bedroom_1\",\n      \"bedroom_2\",\n      \"book\",\n      \"bowl_2\",\n      \"bowl_3\",\n      \"chair_1\",\n      \"chair_2\",\n      \"chair_3\",\n      \"chair_4\",\n      \"chair_5\",\n      \"clock\",\n      \"cola_can\",\n      \"corridor_1\",\n      \"corridor_2\",\n      \"corridor_3\",\n      \"couch\",\n      \"cpu\",\n      \"desk\",\n      \"dining_room\",\n      \"dining_table\",\n      \"flower\",\n      \"fork\",\n      \"fridge_1\",\n      \"fridge_2\",\n      \"fridge_3\",\n      \"glass\",\n      \"gpu\",\n      \"kitchen\",\n      \"knife\",\n      \"lamp\",\n      \"living_room\",\n      \"lobby\",\n      \"locker\",\n      \"mainboard\",\n      \"microwave\",\n      \"mop\",\n      \"oven\",\n      \"paper\",\n      \"plant_1\",\n      \"plant_2\",\n      \"plate\",\n      \"psu\",\n      \"ram\",\n      \"robot_hub\",\n      \"rotting_apple\",\n      \"rubbish_bin\",\n      \"shelf\",\n      \"sink_1\",\n      \"sink_2\",\n      \"spoon\",\n      \"ssd\",\n      \"toilet_1\",\n      \"toilet_2\"\n    ]\n  },\n  \"evaluation_context\": {},\n  \"external_goal\": {\n    \"has_external_goal\": true,\n    \"external_goal_state\": {},\n    \"external_goal_text\": \"\",\n    \"structured_goal_state\": {},\n    \"structured_final_state\": {\n      \"predicates\": [\n        \"item_on(plate, dining_table)\",\n        \"item_on(fork, dining_table)\",\n        \"item_on(knife, dining_table)\",\n        \"item_on(spoon, dining_table)\",\n        \"item_on(glass, dining_table)\",\n        \"item_on(flower, dining_table)\"\n      ],\n      \"notes\": \"Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower).\"\n    }\n  },\n  \"benchmark_final_state_compare\": {\n    \"benchmark\": \"DELTA\",\n    \"status\": \"prepared_for_framework_llm_judge\",\n    \"environment_format\": \"DELTA scene_graph 转成 benchmark 本地扁平环境，保留 delta_predicate/delta_affordance 属性\",\n    \"action_format\": \"DELTA 官方原生动作 JSON 对象\",\n    \"official_evaluator\": \"planning 结束后调用 DELTA PDDL/VAL；评测答案字段不进入 understanding/planning/final_state audit\",\n    \"used_fields\": {\n      \"task_context\": [\n        \"dataset\",\n        \"delta_accessible_items\",\n        \"delta_env_state_predicates\",\n        \"domain\",\n        \"instruction\",\n        \"loadable_containers\",\n        \"scene_graph_cache_path\",\n        \"task_environment_mode\",\n        \"task_name\"\n      ],\n      \"evaluation_context\": [],\n      \"external_goal\": [\n        \"has_external_goal\",\n        \"structured_final_state\"\n      ],\n      \"state_diff\": [\n        \"entities\",\n        \"robot\"\n      ]\n    },\n    \"benchmark_goal\": {\n      \"task_context\": {\n        \"dataset\": \"delta\",\n        \"task_name\": \"dining:allensville:episode-01\",\n        \"domain\": \"dining\",\n        \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n        \"scene_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/delta/initial_envs/allensville.json\",\n        \"delta_env_state_predicates\": [\n          \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n          \"item_is_dining_table(<item>): <item> is dining_table.\"\n        ],\n        \"delta_accessible_items\": [\n          \"psu\",\n          \"sink_1\",\n          \"mop\",\n          \"gpu\",\n          \"sink_2\",\n          \"mainboard\",\n          \"glass\",\n          \"shelf\",\n          \"book\",\n          \"cpu\",\n          \"rotting_apple\",\n          \"plate\",\n          \"lamp\",\n          \"fridge_1\",\n          \"fridge_2\",\n          \"ssd\",\n          \"cola_can\",\n          \"dining_table\",\n          \"knife\",\n          \"fork\",\n          \"spoon\",\n          \"microwave\",\n          \"oven\",\n          \"rubbish_bin\",\n          \"fridge_3\",\n          \"desk\",\n          \"bowl_2\",\n          \"bowl_3\",\n          \"robot_hub\",\n          \"ram\",\n          \"banana_peel\",\n          \"flower\",\n          \"locker\",\n          \"paper\"\n        ],\n        \"loadable_containers\": [\n          {\n            \"name\": \"shelf\",\n            \"room\": \"bedroom_1\",\n            \"is_loaded\": true,\n            \"contents\": [\n              \"book\"\n            ],\n            \"affordances\": [\n              \"drop\",\n              \"load\",\n              \"pick\",\n              \"unload\"\n            ]\n          },\n          {\n            \"name\": \"locker\",\n            \"room\": \"lobby\",\n            \"is_loaded\": true,\n            \"contents\": [\n              \"paper\"\n            ],\n            \"affordances\": [\n              \"drop\",\n              \"load\",\n              \"pick\",\n              \"unload\"\n            ]\n          }\n        ],\n        \"task_environment_mode\": \"understanding_pruned\"\n      },\n      \"evaluation_context\": {},\n      \"goal_projection\": {\n        \"instruction\": \"Set up the dining table for dinner, place the tableware/cutleries and glass on the dining table. Also bring something romantic to the dining table.\",\n        \"domain\": \"dining\",\n        \"visible_delta_predicates\": [\n          \"item_on(<item_1>, <item_2>): <item_1> is on <item_2>.\",\n          \"item_is_dining_table(<item>): <item> is dining_table.\"\n        ],\n        \"loadable_containers\": [\n          {\n            \"name\": \"shelf\",\n            \"room\": \"bedroom_1\",\n            \"is_loaded\": true,\n            \"contents\": [\n              \"book\"\n            ],\n            \"affordances\": [\n              \"drop\",\n              \"load\",\n              \"pick\",\n              \"unload\"\n            ]\n          },\n          {\n            \"name\": \"locker\",\n            \"room\": \"lobby\",\n            \"is_loaded\": true,\n            \"contents\": [\n              \"paper\"\n            ],\n            \"affordances\": [\n              \"drop\",\n              \"load\",\n              \"pick\",\n              \"unload\"\n            ]\n          }\n        ]\n      },\n      \"external_goal\": {\n        \"has_external_goal\": true,\n        \"external_goal_state\": {},\n        \"external_goal_text\": \"\",\n        \"structured_goal_state\": {},\n        \"structured_final_state\": {\n          \"predicates\": [\n            \"item_on(plate, dining_table)\",\n            \"item_on(fork, dining_table)\",\n            \"item_on(knife, dining_table)\",\n            \"item_on(spoon, dining_table)\",\n            \"item_on(glass, dining_table)\",\n            \"item_on(flower, dining_table)\"\n          ],\n          \"notes\": \"Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower).\"\n        }\n      }\n    },\n    \"understanding_final_state\": {\n      \"predicates\": [\n        \"item_on(plate, dining_table)\",\n        \"item_on(fork, dining_table)\",\n        \"item_on(knife, dining_table)\",\n        \"item_on(spoon, dining_table)\",\n        \"item_on(glass, dining_table)\",\n        \"item_on(flower, dining_table)\"\n      ],\n      \"notes\": \"Dining table is set up with all required tableware (plate, fork, knife, spoon, glass) and a romantic item (flower).\"\n    },\n    \"state_diff_summary\": {\n      \"entity_count_compared\": 18,\n      \"changed_entity_count\": 6,\n      \"changed_entities\": [\n        \"flower\",\n        \"fork\",\n        \"glass\",\n        \"knife\",\n        \"plate\",\n        \"spoon\"\n      ],\n      \"changed_entities_truncated\": false,\n      \"robot_changed\": true,\n      \"robot_change\": {\n        \"changed\": true,\n        \"before\": {\n          \"robot_location\": \"living_room\",\n          \"robot_holding\": \"空\",\n          \"delta_room_neighbors\": {\n            \"bathroom_1\": [\n              \"corridor_2\"\n            ],\n            \"bathroom_2\": [\n              \"corridor_3\"\n            ],\n            \"bedroom_1\": [\n              \"corridor_2\"\n            ],\n            \"bedroom_2\": [\n              \"corridor_3\"\n            ],\n            \"corridor_1\": [\n              \"lobby\",\n              \"corridor_3\"\n            ],\n            \"corridor_2\": [\n              \"bathroom_1\",\n              \"bedroom_1\",\n              \"corridor_3\"\n            ],\n            \"corridor_3\": [\n              \"corridor_1\",\n              \"corridor_2\",\n              \"bathroom_2\",\n              \"bedroom_2\",\n              \"kitchen\",\n              \"living_room\"\n            ],\n            \"dining_room\": [\n              \"kitchen\",\n              \"living_room\"\n            ],\n            \"kitchen\": [\n              \"corridor_3\",\n              \"dining_room\"\n            ],\n            \"living_room\": [\n              \"corridor_3\",\n              \"dining_room\"\n            ],\n            \"lobby\": [\n              \"corridor_1\"\n            ]\n          },\n          \"domain\": \"dining\",\n          \"delta_initial_predicates\": [\n            \"item_is_dining_table dining_table\",\n            \"item_pickable plate\",\n            \"item_accessible plate\",\n            \"item_pickable fork\",\n            \"item_accessible fork\",\n            \"item_pickable knife\",\n            \"item_accessible knife\",\n            \"item_pickable spoon\",\n            \"item_accessible spoon\",\n            \"item_pickable glass\",\n            \"item_accessible glass\",\n            \"item_pickable flower\",\n            \"item_accessible flower\"\n          ]\n        },\n        \"after\": {\n          \"robot_location\": \"dining_room\",\n          \"robot_holding\": \"空\",\n          \"delta_room_neighbors\": {\n            \"bathroom_1\": [\n              \"corridor_2\"\n            ],\n            \"bathroom_2\": [\n              \"corridor_3\"\n            ],\n            \"bedroom_1\": [\n              \"corridor_2\"\n            ],\n            \"bedroom_2\": [\n              \"corridor_3\"\n            ],\n            \"corridor_1\": [\n              \"lobby\",\n              \"corridor_3\"\n            ],\n            \"corridor_2\": [\n              \"bathroom_1\",\n              \"bedroom_1\",\n              \"corridor_3\"\n            ],\n            \"corridor_3\": [\n              \"corridor_1\",\n              \"corridor_2\",\n              \"bathroom_2\",\n              \"bedroom_2\",\n              \"kitchen\",\n              \"living_room\"\n            ],\n            \"dining_room\": [\n              \"kitchen\",\n              \"living_room\"\n            ],\n            \"kitchen\": [\n              \"corridor_3\",\n              \"dining_room\"\n            ],\n            \"living_room\": [\n              \"corridor_3\",\n              \"dining_room\"\n            ],\n            \"lobby\": [\n              \"corridor_1\"\n            ]\n          },\n          \"domain\": \"dining\",\n          \"delta_initial_predicates\": [\n            \"item_is_dining_table dining_table\",\n            \"item_pickable plate\",\n            \"item_accessible plate\",\n            \"item_pickable fork\",\n            \"item_accessible fork\",\n            \"item_pickable knife\",\n            \"item_accessible knife\",\n            \"item_pickable spoon\",\n            \"item_accessible spoon\",\n            \"item_pickable glass\",\n            \"item_accessible glass\",\n            \"item_pickable flower\",\n            \"item_accessible flower\"\n          ]\n        }\n      }\n    },\n    \"initial_environment_summary\": {\n      \"available\": true,\n      \"entity_count\": 18,\n      \"type_counts\": {\n        \"receptacle\": 1,\n        \"room\": 11,\n        \"unknown\": 6\n      },\n      \"states_sample\": {},\n      \"relations_sample\": {\n        \"dining_table\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_room\"\n        },\n        \"dining_room\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"plate\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"bedroom_2\"\n        },\n        \"bedroom_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"fork\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen\"\n        },\n        \"kitchen\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"knife\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen\"\n        },\n        \"spoon\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen\"\n        },\n        \"glass\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"bedroom_1\"\n        },\n        \"bedroom_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"flower\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"lobby\"\n        },\n        \"lobby\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"living_room\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"bathroom_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"bathroom_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_3\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        }\n      }\n    },\n    \"final_environment_summary\": {\n      \"available\": true,\n      \"entity_count\": 18,\n      \"type_counts\": {\n        \"receptacle\": 1,\n        \"room\": 11,\n        \"unknown\": 6\n      },\n      \"states_sample\": {},\n      \"relations_sample\": {\n        \"dining_table\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_room\"\n        },\n        \"dining_room\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"plate\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"bedroom_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"fork\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"kitchen\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"knife\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"spoon\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"glass\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"bedroom_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"flower\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"dining_table\"\n        },\n        \"lobby\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"living_room\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"bathroom_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"bathroom_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_2\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"corridor_3\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        }\n      }\n    },\n    \"initial_robot\": {\n      \"robot_location\": \"living_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    },\n    \"final_robot\": {\n      \"robot_location\": \"dining_room\",\n      \"robot_holding\": \"空\",\n      \"delta_room_neighbors\": {\n        \"bathroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bathroom_2\": [\n          \"corridor_3\"\n        ],\n        \"bedroom_1\": [\n          \"corridor_2\"\n        ],\n        \"bedroom_2\": [\n          \"corridor_3\"\n        ],\n        \"corridor_1\": [\n          \"lobby\",\n          \"corridor_3\"\n        ],\n        \"corridor_2\": [\n          \"bathroom_1\",\n          \"bedroom_1\",\n          \"corridor_3\"\n        ],\n        \"corridor_3\": [\n          \"corridor_1\",\n          \"corridor_2\",\n          \"bathroom_2\",\n          \"bedroom_2\",\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"dining_room\": [\n          \"kitchen\",\n          \"living_room\"\n        ],\n        \"kitchen\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"living_room\": [\n          \"corridor_3\",\n          \"dining_room\"\n        ],\n        \"lobby\": [\n          \"corridor_1\"\n        ]\n      },\n      \"domain\": \"dining\",\n      \"delta_initial_predicates\": [\n        \"item_is_dining_table dining_table\",\n        \"item_pickable plate\",\n        \"item_accessible plate\",\n        \"item_pickable fork\",\n        \"item_accessible fork\",\n        \"item_pickable knife\",\n        \"item_accessible knife\",\n        \"item_pickable spoon\",\n        \"item_accessible spoon\",\n        \"item_pickable glass\",\n        \"item_accessible glass\",\n        \"item_pickable flower\",\n        \"item_accessible flower\"\n      ]\n    },\n    \"fairness_notes\": [\n      \"本 comparer 不读取评测答案字段、官方目标字段或参考代价字段。\",\n      \"DELTA 官方目标只在 planning 结束后的官方评测中使用。\"\n    ],\n    \"judge_contract\": \"公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。\",\n    \"enabled\": true,\n    \"comparer_module\": \"benchmark.delta.framework.code.final_state\"\n  }\n}\n\n判定边界：\n1. 优先读取 state_audit_context.benchmark_final_state_compare；其中是 DELTA comparer 基于本地环境和公开任务字段准备的目标材料。\n2. 结合 understanding final_state、任务原文、sandbox final environment/final robot 和 state_diff 判断关键目标是否完成。\n3. 不使用评测答案字段、官方目标字段或参考代价字段；不要把任务转换成其他 benchmark 格式。\n4. 如果关键目标缺失，is_passed=false，并写出缺失的最终状态和后续 planning 应补的动作类型。\n5. 如果当前最终态只需追加动作即可修复，repair_mode=\"continue_from_current\"；如果已验证前缀本身错，repair_mode=\"reset_and_replan\"。\n\n输出 JSON：\n{\"is_passed\": true, \"issue\": \"\", \"fix_advice\": \"\", \"repair_mode\": \"continue_from_current\", \"accepted_diffs\": [], \"unexpected_diffs\": []}"
  }
]
```

```text
{"is_passed": true, "issue": "", "fix_advice": "", "repair_mode": "continue_from_current", "accepted_diffs": ["plate", "fork", "knife", "spoon", "glass", "flower"], "unexpected_diffs": []}
```


## 11. DELTA 原生动作 / PDDL / VAL

### DELTA Native Actions
```json
[
  {
    "step": 1,
    "action": "goto",
    "agent": "robot",
    "room_1": "living_room",
    "room_2": "dining_room"
  },
  {
    "step": 2,
    "action": "goto",
    "agent": "robot",
    "room_1": "dining_room",
    "room_2": "kitchen"
  },
  {
    "step": 3,
    "action": "pick",
    "agent": "robot",
    "item": "fork",
    "room": "kitchen"
  },
  {
    "step": 4,
    "action": "goto",
    "agent": "robot",
    "room_1": "kitchen",
    "room_2": "dining_room"
  },
  {
    "step": 5,
    "action": "place_on",
    "agent": "robot",
    "item_1": "fork",
    "item_2": "dining_table",
    "room": "dining_room"
  },
  {
    "step": 6,
    "action": "goto",
    "agent": "robot",
    "room_1": "dining_room",
    "room_2": "kitchen"
  },
  {
    "step": 7,
    "action": "pick",
    "agent": "robot",
    "item": "knife",
    "room": "kitchen"
  },
  {
    "step": 8,
    "action": "goto",
    "agent": "robot",
    "room_1": "kitchen",
    "room_2": "dining_room"
  },
  {
    "step": 9,
    "action": "place_on",
    "agent": "robot",
    "item_1": "knife",
    "item_2": "dining_table",
    "room": "dining_room"
  },
  {
    "step": 10,
    "action": "goto",
    "agent": "robot",
    "room_1": "dining_room",
    "room_2": "kitchen"
  },
  {
    "step": 11,
    "action": "pick",
    "agent": "robot",
    "item": "spoon",
    "room": "kitchen"
  },
  {
    "step": 12,
    "action": "goto",
    "agent": "robot",
    "room_1": "kitchen",
    "room_2": "dining_room"
  },
  {
    "step": 13,
    "action": "place_on",
    "agent": "robot",
    "item_1": "spoon",
    "item_2": "dining_table",
    "room": "dining_room"
  },
  {
    "step": 14,
    "action": "goto",
    "agent": "robot",
    "room_1": "dining_room",
    "room_2": "bedroom_1"
  },
  {
    "step": 15,
    "action": "pick",
    "agent": "robot",
    "item": "glass",
    "room": "bedroom_1"
  },
  {
    "step": 16,
    "action": "goto",
    "agent": "robot",
    "room_1": "bedroom_1",
    "room_2": "dining_room"
  },
  {
    "step": 17,
    "action": "place_on",
    "agent": "robot",
    "item_1": "glass",
    "item_2": "dining_table",
    "room": "dining_room"
  },
  {
    "step": 18,
    "action": "goto",
    "agent": "robot",
    "room_1": "dining_room",
    "room_2": "bedroom_2"
  },
  {
    "step": 19,
    "action": "pick",
    "agent": "robot",
    "item": "plate",
    "room": "bedroom_2"
  },
  {
    "step": 20,
    "action": "goto",
    "agent": "robot",
    "room_1": "bedroom_2",
    "room_2": "dining_room"
  },
  {
    "step": 21,
    "action": "place_on",
    "agent": "robot",
    "item_1": "plate",
    "item_2": "dining_table",
    "room": "dining_room"
  },
  {
    "step": 22,
    "action": "goto",
    "agent": "robot",
    "room_1": "dining_room",
    "room_2": "lobby"
  },
  {
    "step": 23,
    "action": "pick",
    "agent": "robot",
    "item": "flower",
    "room": "lobby"
  },
  {
    "step": 24,
    "action": "goto",
    "agent": "robot",
    "room_1": "lobby",
    "room_2": "dining_room"
  },
  {
    "step": 25,
    "action": "place_on",
    "agent": "robot",
    "item_1": "flower",
    "item_2": "dining_table",
    "room": "dining_room"
  }
]
```

### Evaluator Execution Calls
```json
[
  {
    "step": 1,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "living_room",
        "to": "dining_room"
      }
    }
  },
  {
    "step": 2,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "dining_room",
        "to": "kitchen"
      }
    }
  },
  {
    "step": 3,
    "execution": {
      "skill": "pick",
      "parameters": {
        "item": "fork",
        "room": "kitchen"
      }
    }
  },
  {
    "step": 4,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "kitchen",
        "to": "dining_room"
      }
    }
  },
  {
    "step": 5,
    "execution": {
      "skill": "place_on",
      "parameters": {
        "item": "fork",
        "surface": "dining_table",
        "room": "dining_room"
      }
    }
  },
  {
    "step": 6,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "dining_room",
        "to": "kitchen"
      }
    }
  },
  {
    "step": 7,
    "execution": {
      "skill": "pick",
      "parameters": {
        "item": "knife",
        "room": "kitchen"
      }
    }
  },
  {
    "step": 8,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "kitchen",
        "to": "dining_room"
      }
    }
  },
  {
    "step": 9,
    "execution": {
      "skill": "place_on",
      "parameters": {
        "item": "knife",
        "surface": "dining_table",
        "room": "dining_room"
      }
    }
  },
  {
    "step": 10,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "dining_room",
        "to": "kitchen"
      }
    }
  },
  {
    "step": 11,
    "execution": {
      "skill": "pick",
      "parameters": {
        "item": "spoon",
        "room": "kitchen"
      }
    }
  },
  {
    "step": 12,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "kitchen",
        "to": "dining_room"
      }
    }
  },
  {
    "step": 13,
    "execution": {
      "skill": "place_on",
      "parameters": {
        "item": "spoon",
        "surface": "dining_table",
        "room": "dining_room"
      }
    }
  },
  {
    "step": 14,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "dining_room",
        "to": "bedroom_1"
      }
    }
  },
  {
    "step": 15,
    "execution": {
      "skill": "pick",
      "parameters": {
        "item": "glass",
        "room": "bedroom_1"
      }
    }
  },
  {
    "step": 16,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "bedroom_1",
        "to": "dining_room"
      }
    }
  },
  {
    "step": 17,
    "execution": {
      "skill": "place_on",
      "parameters": {
        "item": "glass",
        "surface": "dining_table",
        "room": "dining_room"
      }
    }
  },
  {
    "step": 18,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "dining_room",
        "to": "bedroom_2"
      }
    }
  },
  {
    "step": 19,
    "execution": {
      "skill": "pick",
      "parameters": {
        "item": "plate",
        "room": "bedroom_2"
      }
    }
  },
  {
    "step": 20,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "bedroom_2",
        "to": "dining_room"
      }
    }
  },
  {
    "step": 21,
    "execution": {
      "skill": "place_on",
      "parameters": {
        "item": "plate",
        "surface": "dining_table",
        "room": "dining_room"
      }
    }
  },
  {
    "step": 22,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "dining_room",
        "to": "lobby"
      }
    }
  },
  {
    "step": 23,
    "execution": {
      "skill": "pick",
      "parameters": {
        "item": "flower",
        "room": "lobby"
      }
    }
  },
  {
    "step": 24,
    "execution": {
      "skill": "goto",
      "parameters": {
        "from": "lobby",
        "to": "dining_room"
      }
    }
  },
  {
    "step": 25,
    "execution": {
      "skill": "place_on",
      "parameters": {
        "item": "flower",
        "surface": "dining_table",
        "room": "dining_room"
      }
    }
  }
]
```

### PDDL Export
```json
{
  "plan_path": "/data/zmy/OurAgent-he1/benchmark/delta/framework/results/delta_audit_smoke_20260806_todo_hooks/cases/dining__allensville__episode-01/plans/dining_allensville_episode-01.plan",
  "plan_lines": [
    "(goto robot living_room dining_room)",
    "(goto robot dining_room kitchen)",
    "(pick robot fork kitchen)",
    "(goto robot kitchen dining_room)",
    "(place_on robot fork dining_table dining_room)",
    "(goto robot dining_room kitchen)",
    "(pick robot knife kitchen)",
    "(goto robot kitchen dining_room)",
    "(place_on robot knife dining_table dining_room)",
    "(goto robot dining_room kitchen)",
    "(pick robot spoon kitchen)",
    "(goto robot kitchen dining_room)",
    "(place_on robot spoon dining_table dining_room)",
    "(goto robot dining_room kitchen)",
    "(goto robot kitchen corridor_3)",
    "(goto robot corridor_3 corridor_2)",
    "(goto robot corridor_2 bedroom_1)",
    "(pick robot glass bedroom_1)",
    "(goto robot bedroom_1 corridor_2)",
    "(goto robot corridor_2 corridor_3)",
    "(goto robot corridor_3 kitchen)",
    "(goto robot kitchen dining_room)",
    "(place_on robot glass dining_table dining_room)",
    "(goto robot dining_room kitchen)",
    "(goto robot kitchen corridor_3)",
    "(goto robot corridor_3 bedroom_2)",
    "(pick robot plate bedroom_2)",
    "(goto robot bedroom_2 corridor_3)",
    "(goto robot corridor_3 kitchen)",
    "(goto robot kitchen dining_room)",
    "(place_on robot plate dining_table dining_room)",
    "(goto robot dining_room kitchen)",
    "(goto robot kitchen corridor_3)",
    "(goto robot corridor_3 corridor_1)",
    "(goto robot corridor_1 lobby)",
    "(pick robot flower lobby)",
    "(goto robot lobby corridor_1)",
    "(goto robot corridor_1 corridor_3)",
    "(goto robot corridor_3 kitchen)",
    "(goto robot kitchen dining_room)",
    "(place_on robot flower dining_table dining_room)"
  ],
  "export_errors": [],
  "domain_file": "/data/zmy/DELTA/data/pddl/domain/dining_domain.pddl",
  "problem_file": "/data/zmy/DELTA/data/pddl/problem/allensville_dining_problem.pddl"
}
```

### VAL Result
```json
{
  "available": true,
  "success": true,
  "validator": "/data/zmy/VAL/build/linux64/Release/install/bin/Validate",
  "returncode": 0,
  "stdout": "Type-checking goto\n...action passes type checking.\nType-checking pick\n...action passes type checking.\nType-checking drop\n...action passes type checking.\nType-checking place_on\n...action passes type checking.\nChecking plan: /data/zmy/OurAgent-he1/benchmark/delta/framework/results/delta_audit_smoke_20260806_todo_hooks/cases/dining__allensville__episode-01/plans/dining_allensville_episode-01.plan\nPlan to validate:\n\nPlan size: 41\n1:\n(goto robot living_room dining_room)\n \n2:\n(goto robot dining_room kitchen)\n \n3:\n(pick robot fork kitchen)\n \n4:\n(goto robot kitchen dining_room)\n \n5:\n(place_on robot fork dining_table dining_room)\n \n6:\n(goto robot dining_room kitchen)\n \n7:\n(pick robot knife kitchen)\n \n8:\n(goto robot kitchen dining_room)\n \n9:\n(place_on robot knife dining_table dining_room)\n \n10:\n(goto robot dining_room kitchen)\n \n11:\n(pick robot spoon kitchen)\n \n12:\n(goto robot kitchen dining_room)\n \n13:\n(place_on robot spoon dining_table dining_room)\n \n14:\n(goto robot dining_room kitchen)\n \n15:\n(goto robot kitchen corridor_3)\n \n16:\n(goto robot corridor_3 corridor_2)\n \n17:\n(goto robot corridor_2 bedroom_1)\n \n18:\n(pick robot glass bedroom_1)\n \n19:\n(goto robot bedroom_1 corridor_2)\n \n20:\n(goto robot corridor_2 corridor_3)\n \n21:\n(goto robot corridor_3 kitchen)\n \n22:\n(goto robot kitchen dining_room)\n \n23:\n(place_on robot glass dining_table dining_room)\n \n24:\n(goto robot dining_room kitchen)\n \n25:\n(goto robot kitchen corridor_3)\n \n26:\n(goto robot corridor_3 bedroom_2)\n \n27:\n(pick robot plate bedroom_2)\n \n28:\n(goto robot bedroom_2 corridor_3)\n \n29:\n(goto robot corridor_3 kitchen)\n \n30:\n(goto robot kitchen dining_room)\n \n31:\n(place_on robot plate dining_table dining_room)\n \n32:\n(goto robot dining_room kitchen)\n \n33:\n(goto robot kitchen corridor_3)\n \n34:\n(goto robot corridor_3 corridor_1)\n \n35:\n(goto robot corridor_1 lobby)\n \n36:\n(pick robot flower lobby)\n \n37:\n(goto robot lobby corridor_1)\n \n38:\n(goto robot corridor_1 corridor_3)\n \n39:\n(goto robot corridor_3 kitchen)\n \n40:\n(goto robot kitchen dining_room)\n \n41:\n(place_on robot flower dining_table dining_room)\n \n\nPlan Validation details\n-----------------------\n\nChecking next happening (time 1)\nDeleting (agent_at robot living_room)\nAdding (agent_at robot dining_room)\n\nChecking next happening (time 2)\nDeleting (agent_at robot dining_room)\nAdding (agent_at robot kitchen)\n\nChecking next happening (time 3)\nDeleting (item_at fork kitchen)\nAdding (agent_at robot kitchen)\nAdding (agent_loaded robot)\nAdding (agent_has_item robot fork)\n\nChecking next happening (time 4)\nDeleting (agent_at robot kitchen)\nAdding (agent_at robot dining_room)\n\nChecking next happening (time 5)\nDeleting (agent_loaded robot)\nDeleting (agent_has_item robot fork)\nAdding (item_on fork dining_table)\n\nChecking next happening (time 6)\nDeleting (agent_at robot dining_room)\nAdding (agent_at robot kitchen)\n\nChecking next happening (time 7)\nDeleting (item_at knife kitchen)\nAdding (agent_at robot kitchen)\nAdding (agent_loaded robot)\nAdding (agent_has_item robot knife)\n\nChecking next happening (time 8)\nDeleting (agent_at robot kitchen)\nAdding (agent_at robot dining_room)\n\nChecking next happening (time 9)\nDeleting (agent_loaded robot)\nDeleting (agent_has_item robot knife)\nAdding (item_on knife dining_table)\n\nChecking next happening (time 10)\nDeleting (agent_at robot dining_room)\nAdding (agent_at robot kitchen)\n\nChecking next happening (time 11)\nDeleting (item_at spoon kitchen)\nAdding (agent_at robot kitchen)\nAdding (agent_loaded robot)\nAdding (agent_has_item robot spoon)\n\nChecking next happening (time 12)\nDeleting (agent_at robot kitchen)\nAdding (agent_at robot dining_room)\n\nChecking next happening (time 13)\nDeleting (agent_loaded robot)\nDeleting (agent_has_item robot spoon)\nAdding (item_on spoon dining_table)\n\nChecking next happening (time 14)\nDeleting (agent_at robot dining_room)\nAdding (agent_at robot kitchen)\n\nChecking next happening (time 15)\nDeleting (agent_at robot kitchen)\nAdding (agent_at robot corridor_3)\n\nChecking next happening (time 16)\nDeleting (agent_at robot corridor_3)\nAdding (agent_at robot corridor_2)\n\nChecking next happening (time 17)\nDeleting (agent_at robot corridor_2)\nAdding (agent_at robot bedroom_1)\n\nChecking next happening (time 18)\nDeleting (item_at glass bedroom_1)\nAdding (agent_at robot bedroom_1)\nAdding (agent_loaded robot)\nAdding (agent_has_item robot glass)\n\nChecking next happening (time 19)\nDeleting (agent_at robot bedroom_1)\nAdding (agent_at robot corridor_2)\n\nChecking next happening (time 20)\nDeleting (agent_at robot corridor_2)\nAdding (agent_at robot corridor_3)\n\nChecking next happening (time 21)\nDeleting (agent_at robot corridor_3)\nAdding (agent_at robot kitchen)\n\nChecking next happening (time 22)\nDeleting (agent_at robot kitchen)\nAdding (agent_at robot dining_room)\n\nChecking next happening (time 23)\nDeleting (agent_loaded robot)\nDeleting (agent_has_item robot glass)\nAdding (item_on glass dining_table)\n\nChecking next happening (time 24)\nDeleting (agent_at robot dining_room)\nAdding (agent_at robot kitchen)\n\nChecking next happening (time 25)\nDeleting (agent_at robot kitchen)\nAdding (agent_at robot corridor_3)\n\nChecking next happening (time 26)\nDeleting (agent_at robot corridor_3)\nAdding (agent_at robot bedroom_2)\n\nChecking next happening (time 27)\nDeleting (item_at plate bedroom_2)\nAdding (agent_at robot bedroom_2)\nAdding (agent_loaded robot)\nAdding (agent_has_item robot plate)\n\nChecking next happening (time 28)\nDeleting (agent_at robot bedroom_2)\nAdding (agent_at robot corridor_3)\n\nChecking next happening (time 29)\nDeleting (agent_at robot corridor_3)\nAdding (agent_at robot kitchen)\n\nChecking next happening (time 30)\nDeleting (agent_at robot kitchen)\nAdding (agent_at robot dining_room)\n\nChecking next happening (time 31)\nDeleting (agent_loaded robot)\nDeleting (agent_has_item robot plate)\nAdding (item_on plate dining_table)\n\nChecking next happening (time 32)\nDeleting (agent_at robot dining_room)\nAdding (agent_at robot kitchen)\n\nChecking next happening (time 33)\nDeleting (agent_at robot kitchen)\nAdding (agent_at robot corridor_3)\n\nChecking next happening (time 34)\nDeleting (agent_at robot corridor_3)\nAdding (agent_at robot corridor_1)\n\nChecking next happening (time 35)\nDeleting (agent_at robot corridor_1)\nAdding (agent_at robot lobby)\n\nChecking next happening (time 36)\nDeleting (item_at flower lobby)\nAdding (agent_at robot lobby)\nAdding (agent_loaded robot)\nAdding (agent_has_item robot flower)\n\nChecking next happening (time 37)\nDeleting (agent_at robot lobby)\nAdding (agent_at robot corridor_1)\n\nChecking next happening (time 38)\nDeleting (agent_at robot corridor_1)\nAdding (agent_at robot corridor_3)\n\nChecking next happening (time 39)\nDeleting (agent_at robot corridor_3)\nAdding (agent_at robot kitchen)\n\nChecking next happening (time 40)\nDeleting (agent_at robot kitchen)\nAdding (agent_at robot dining_room)\n\nChecking next happening (time 41)\nDeleting (agent_loaded robot)\nDeleting (agent_has_item robot flower)\nAdding (item_on flower dining_table)\nPlan executed successfully - checking goal\nPlan valid\nFinal value: 41 \n\nSuccessful plans:\nValue: 41\n /data/zmy/OurAgent-he1/benchmark/delta/framework/results/delta_audit_smoke_20260806_todo_hooks/cases/dining__allensville__episode-01/plans/dining_allensville_episode-01.plan 41 \n\n",
  "stderr": "",
  "error": ""
}
```
