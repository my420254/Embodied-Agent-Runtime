# ReActree WAH Case Report: 0:0

## 1. 文件位置

- 结果文件：`/data/zmy/OurAgent-he1/benchmark/reactree/wah/framework/results/reactree_wah_official_smoke_20260806_todo_hooks/cases/0__0/raw_output.json`
- 完整阶段 artifact：`/data/zmy/OurAgent-he1/benchmark/reactree/wah/framework/results/reactree_wah_official_smoke_20260806_todo_hooks/cases/0__0/artifacts`
- 完整输入输出 / 审计文件：`case_input.json`, `case_input_summary.json`, `prepared_environment.json`, `prepared_environment_summary.json`, `environment_audit.json`, `understanding_input.json`, `understanding_input_summary.json`, `understanding_output.json`, `understanding_output_summary.json`, `planning_input.json`, `planning_input_summary.json`, `planning_output.json`, `planning_output_summary.json`, `contract_audit.json`, `planning_feature_records.json`, `llm_io.json`, `goal_check.json`, `official_eval.json`, `process_summary.json`

## 2. 当前结果摘要

```json
{
  "case_id": "0:0",
  "dataset": "reactree",
  "task_success": true,
  "task_success_rate": 1.0,
  "goal_success_rate": 1.0,
  "subgoal_success_rate": 1.0,
  "evaluation_mode": "reactree_official_wah_unity",
  "official_available": true,
  "execution_success": true,
  "execution_status": "completed",
  "is_feasible": true,
  "feedback": "规划合法，验证环节闭环。",
  "evaluation_error": "",
  "llm_call_count": 4,
  "todo_contract_status": "not_recorded",
  "todo_contract_event_count": 0
}
```

## 3. 要看的关键字段

- `prediction.benchmark_trace.case_input`：这条数据原始输入
- `prediction.benchmark_trace.prepared_environment`：场景准备结果
- `prediction.benchmark_trace.understanding_input / understanding_output`：understanding 前后
- `prediction.benchmark_trace.planning_input / planning_output`：planning 前后
- `artifacts/contract_audit.json`：本次 todo_list 原生动作契约检查、动作格式、命中 skill schema
- `prediction.benchmark_trace.llm_io`：每次模型输入输出
- `prediction.benchmark_trace.planning_output.planning_debug_events`：每次 contract / sandbox / audit 事件
- `prediction.benchmark_trace.planning_output.re_trac_memory`：re_trac 的 failed lessons
- `prediction.benchmark_trace.planning_output.evaluator_findings`：结构化失败摘要

## 4. Benchmark 原始输入

```json
{
  "schema_version": "framework_trace_v3",
  "process_name": "case_input",
  "payload_role": "output",
  "keys": [
    "benchmark_module",
    "benchmark_settings_file",
    "dataset",
    "env_id",
    "environment_source",
    "init_graph_cache_path",
    "init_room",
    "instruction",
    "instruction_idx",
    "task_goal",
    "task_id",
    "task_name",
    "task_source"
  ],
  "dataset": "reactree",
  "task_id": 0,
  "identifier": null,
  "benchmark_settings_file": "/data/zmy/OurAgent-he1/benchmark/reactree/wah/framework/code/config/settings.json",
  "environment_source": "reactree_case_runtime_scene",
  "instruction": "Put one cupcake and one apple on the coffee table",
  "task_goal_keys": [
    "on_apple_coffeetable",
    "on_cupcake_coffeetable"
  ]
}
```

## 5. Framework 各阶段输入输出

### Prepared Environment
```json
{
  "schema_version": "framework_trace_v3",
  "process_name": "environment_preparation",
  "payload_role": "output",
  "instruction": "Put one cupcake and one apple on the coffee table",
  "env_state": {
    "robot_location": "bedroom 1",
    "robot_holding": "空"
  },
  "entity_catalog": {
    "count": 343,
    "sample": [
      "apple 1",
      "apple 2",
      "apple 3",
      "bananas 1",
      "bar soap 1",
      "bathroom 1",
      "bathroom cabinet 1",
      "bathroom counter 1",
      "bed 1",
      "bedroom 1",
      "book 1",
      "book 2",
      "bookshelf 1",
      "bookshelf 2",
      "bookshelf 3",
      "bowl 1",
      "bowl 2",
      "bowl 3",
      "bowl 4",
      "bowl 5",
      "bowl 6",
      "bowl 7",
      "bowl 8",
      "bowl 9",
      "box 1",
      "box 2",
      "box 3",
      "box 4",
      "box 5",
      "bucket 1",
      "cabinet 1",
      "candle 1",
      "candy bar 1",
      "ceiling 1",
      "ceiling 10",
      "ceiling 11",
      "ceiling 12",
      "ceiling 13",
      "ceiling 14",
      "ceiling 15",
      "ceiling 16",
      "ceiling 17",
      "ceiling 18",
      "ceiling 19",
      "ceiling 2",
      "ceiling 20",
      "ceiling 21",
      "ceiling 22",
      "ceiling 23",
      "ceiling 24"
    ],
    "truncated": true
  },
  "scene": {
    "available": true,
    "entity_count": 343,
    "type_counts": {
      "room": 4,
      "unknown": 206,
      "receptacle": 133
    },
    "rooms": {
      "count": 4,
      "sample": [
        "bathroom 1",
        "bedroom 1",
        "kitchen 1",
        "living room 1"
      ],
      "truncated": false
    },
    "receptacles": {
      "count": 133,
      "sample": [
        "bathroom cabinet 1",
        "bathroom counter 1",
        "bed 1",
        "book 1",
        "book 2",
        "bookshelf 1",
        "bookshelf 2",
        "bookshelf 3",
        "bowl 1",
        "bowl 2",
        "bowl 3",
        "bowl 4",
        "bowl 5",
        "bowl 6",
        "bowl 7",
        "bowl 8",
        "bowl 9",
        "box 1",
        "box 2",
        "box 3",
        "box 4",
        "box 5",
        "bucket 1",
        "cabinet 1",
        "chair 1",
        "chair 2",
        "chair 3",
        "chair 4",
        "closet 1",
        "coffee maker 1"
      ],
      "truncated": true
    },
    "entities": {
      "count": 343,
      "sample": [
        "apple 1",
        "apple 2",
        "apple 3",
        "bananas 1",
        "bar soap 1",
        "bathroom 1",
        "bathroom cabinet 1",
        "bathroom counter 1",
        "bed 1",
        "bedroom 1",
        "book 1",
        "book 2",
        "bookshelf 1",
        "bookshelf 2",
        "bookshelf 3",
        "bowl 1",
        "bowl 2",
        "bowl 3",
        "bowl 4",
        "bowl 5",
        "bowl 6",
        "bowl 7",
        "bowl 8",
        "bowl 9",
        "box 1",
        "box 2",
        "box 3",
        "box 4",
        "box 5",
        "bucket 1",
        "cabinet 1",
        "candle 1",
        "candy bar 1",
        "ceiling 1",
        "ceiling 10",
        "ceiling 11",
        "ceiling 12",
        "ceiling 13",
        "ceiling 14",
        "ceiling 15"
      ],
      "truncated": true
    },
    "states_sample": {
      "closet 1": {
        "isOpen": false
      },
      "computer 1": {
        "isToggled": false
      },
      "light switch 4": {
        "isToggled": true
      },
      "curtains 5": {
        "isOpen": false
      },
      "curtains 6": {
        "isOpen": false
      },
      "curtains 7": {
        "isOpen": false
      },
      "bookshelf 3": {
        "isOpen": false
      },
      "pile of clothes 1": {
        "isOpen": false
      },
      "box 4": {
        "isOpen": false
      },
      "bookshelf 2": {
        "isOpen": false
      },
      "pile of clothes 2": {
        "isOpen": false
      },
      "hair product 3": {
        "isOpen": false
      },
      "box 5": {
        "isOpen": false
      },
      "folder 1": {
        "isOpen": false
      },
      "folder 2": {
        "isOpen": false
      },
      "folder 3": {
        "isOpen": false
      },
      "hair product 4": {
        "isOpen": false
      },
      "folder 4": {
        "isOpen": false
      },
      "desk 2": {
        "isOpen": false
      },
      "nightstand 4": {
        "isOpen": false
      }
    },
    "nesting": {
      "available": true,
      "contains_node_count": 67,
      "max_depth": 5
    },
    "flat_schema": {
      "available": true,
      "entity_count": 343,
      "standard_field_counts": {
        "direct_parent": 343,
        "direct_relation": 343,
        "type": 343,
        "states": 343,
        "properties": 343,
        "is_container": 343,
        "full_path": 343
      },
      "relation_entity_count": 339,
      "state_entity_count": 91,
      "property_entity_count": 229,
      "container_count": 133,
      "full_path_entity_count": 339,
      "parent_missing_count": 0,
      "parent_missing_sample": [],
      "parent_reference_missing_count": 0,
      "parent_reference_missing_sample": []
    }
  },
  "context": {
    "task_context": {
      "dataset": "reactree",
      "env_id": 3,
      "task_name": "prepare_snack",
      "instruction": "Put one cupcake and one apple on the coffee table",
      "init_room": "bedroom",
      "task_source": "reactree_wah_testset",
      "environment_source": "reactree_case_runtime_scene",
      "init_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json",
      "task_goal": {
        "on_cupcake_coffeetable": 1,
        "on_apple_coffeetable": 1
      },
      "available_entities": [
        "apple 1",
        "apple 2",
        "apple 3",
        "bananas 1",
        "bar soap 1",
        "bathroom 1",
        "bathroom cabinet 1",
        "bathroom counter 1",
        "bed 1",
        "bedroom 1",
        "book 1",
        "book 2",
        "bookshelf 1",
        "bookshelf 2",
        "bookshelf 3",
        "bowl 1",
        "bowl 2",
        "bowl 3",
        "bowl 4",
        "bowl 5",
        "bowl 6",
        "bowl 7",
        "bowl 8",
        "bowl 9",
        "box 1",
        "box 2",
        "box 3",
        "box 4",
        "box 5",
        "bucket 1",
        "cabinet 1",
        "candle 1",
        "candy bar 1",
        "ceiling 1",
        "ceiling 10",
        "ceiling 11",
        "ceiling 12",
        "ceiling 13",
        "ceiling 14",
        "ceiling 15",
        "ceiling 16",
        "ceiling 17",
        "ceiling 18",
        "ceiling 19",
        "ceiling 2",
        "ceiling 20",
        "ceiling 21",
        "ceiling 22",
        "ceiling 23",
        "ceiling 24",
        "ceiling 25",
        "ceiling 26",
        "ceiling 3",
        "ceiling 4",
        "ceiling 5",
        "ceiling 6",
        "ceiling 7",
        "ceiling 8",
        "ceiling 9",
        "ceiling lamp 1",
        "ceiling lamp 2",
        "ceiling lamp 3",
        "ceiling lamp 4",
        "ceiling lamp 5",
        "cell phone 1",
        "cell phone 2",
        "cereal 1",
        "chair 1",
        "chair 2",
        "chair 3",
        "chair 4",
        "chair 5",
        "chair 6",
        "chips 1",
        "chips 2",
        "chocolate syrup 1",
        "closet 1",
        "closet drawer 1",
        "closet drawer 2",
        "closet drawer 3",
        "closet drawer 4",
        "closet drawer 5",
        "closet drawer 6",
        "closet drawer 7",
        "coffee maker 1",
        "coffee pot 1",
        "coffee table 1",
        "computer 1",
        "condiment bottle 1",
        "condiment bottle 2",
        "condiment bottle 3",
        "condiment bottle 4",
        "condiment shaker 1",
        "condiment shaker 2",
        "condiment shaker 3",
        "condiment shaker 4",
        "cooking pot 1",
        "cooking pot 2",
        "cpu screen 1",
        "crackers 1",
        "crackers 2",
        "creamy buns 1",
        "cupcake 1",
        "cupcake 2",
        "cupcake 3",
        "curtains 1",
        "curtains 2",
        "curtains 3",
        "curtains 4",
        "curtains 5",
        "curtains 6",
        "curtains 7",
        "cutlery fork 1",
        "cutlery fork 2",
        "cutlery fork 3",
        "cutlery fork 4",
        "cutlery knife 1",
        "cutlery knife 2",
        "cutlery knife 3",
        "cutlery knife 4",
        "cutlery knife 5",
        "cutlery knife 6",
        "cutlets 1",
        "deodorant 1",
        "deodorant 2",
        "deodorant 3",
        "desk 1",
        "desk 2",
        "dishwasher 1",
        "dishwashing liquid 1",
        "door 1",
        "door 2",
        "door 3",
        "door jamb 1",
        "door jamb 2",
        "door jamb 3",
        "door jamb 4",
        "face cream 1",
        "face cream 2",
        "face cream 3",
        "faucet 1",
        "faucet 2",
        "floor 1",
        "floor 10",
        "floor 11",
        "floor 12",
        "floor 13",
        "floor 14",
        "floor 15",
        "floor 16",
        "floor 17",
        "floor 18",
        "floor 19",
        "floor 2",
        "floor 20",
        "floor 21",
        "floor 22",
        "floor 23",
        "floor 24",
        "floor 25",
        "floor 26",
        "floor 3",
        "floor 4",
        "floor 5",
        "floor 6",
        "floor 7",
        "floor 8",
        "floor 9",
        "folder 1",
        "folder 2",
        "folder 3",
        "folder 4",
        "fridge 1",
        "frying pan 1",
        "hair product 1",
        "hair product 2",
        "hair product 3",
        "hair product 4",
        "hanger 1",
        "hanger 2",
        "hanger 3",
        "hanger 4",
        "hanger 5",
        "hanger 6",
        "hanger 7",
        "juice 1",
        "juice 2",
        "keyboard 1",
        "kitchen 1",
        "kitchen cabinet 1",
        "kitchen cabinet 2",
        "kitchen cabinet 3",
        "kitchen cabinet 4",
        "kitchen cabinet 5",
        "kitchen cabinet 6",
        "kitchen cabinet 7",
        "kitchen cabinet 8",
        "kitchen counter 1",
        "kitchen counter 2",
        "kitchen counter 3",
        "kitchen counter drawer 1",
        "kitchen counter drawer 2",
        "kitchen counter drawer 3",
        "kitchen counter drawer 4",
        "kitchen counter drawer 5",
        "kitchen counter drawer 6",
        "kitchen counter drawer 7",
        "kitchen counter drawer 8",
        "kitchen table 1",
        "knife block 1",
        "light switch 1",
        "light switch 2",
        "light switch 3",
        "light switch 4",
        "lime 1",
        "living room 1",
        "microwave oven 1",
        "milk 1",
        "mouse 1",
        "mouse mat 1",
        "mug 1",
        "mug 2",
        "mug 3",
        "nightstand 1",
        "nightstand 2",
        "nightstand 3",
        "nightstand 4",
        "notes 1",
        "orchid 1",
        "oven tray 1",
        "painkillers 1",
        "pancake 1",
        "peach 1",
        "peach 2",
        "peach 3",
        "pear 1",
        "perfume 1",
        "perfume 2",
        "photo frame 1",
        "photo frame 2",
        "photo frame 3",
        "pile of clothes 1",
        "pile of clothes 2",
        "pillow 1",
        "pillow 2",
        "pillow 3",
        "pillow 4",
        "pillow 5",
        "pillow 6",
        "plate 1",
        "plate 2",
        "plate 3",
        "plate 4",
        "plate 5",
        "plate 6",
        "plate 7",
        "plum 1",
        "plum 2",
        "power socket 1",
        "power socket 2",
        "power socket 3",
        "pudding 1",
        "pudding 2",
        "radio 1",
        "rug 1",
        "rug 2",
        "rug 3",
        "rug 4",
        "sink 1",
        "sink 2",
        "slice of bread 1",
        "slice of bread 2",
        "sofa 1",
        "sofa 2",
        "sofa 3",
        "stall 1",
        "stall 2",
        "stove 1",
        "stove fan 1",
        "table lamp 1",
        "toaster 1",
        "toilet 1",
        "toilet paper 1",
        "toothbrush 1",
        "toothpaste 1",
        "tv 1",
        "tv stand 1",
        "wall 1",
        "wall 10",
        "wall 11",
        "wall 12",
        "wall 13",
        "wall 14",
        "wall 15",
        "wall 16",
        "wall 17",
        "wall 18",
        "wall 19",
        "wall 2",
        "wall 20",
        "wall 21",
        "wall 22",
        "wall 23",
        "wall 24",
        "wall 25",
        "wall 26",
        "wall 3",
        "wall 4",
        "wall 5",
        "wall 6",
        "wall 7",
        "wall 8",
        "wall 9",
        "wall lamp 1",
        "wall lamp 2",
        "wall lamp 3",
        "wall lamp 4",
        "wall lamp 5",
        "wall lamp 6",
        "wall lamp 7",
        "wall lamp 8",
        "wall lamp 9",
        "wall phone 1",
        "wall picture frame 1",
        "wall picture frame 2",
        "wall picture frame 3",
        "wall picture frame 4",
        "wall picture frame 5",
        "wall picture frame 6",
        "wall picture frame 7",
        "wall picture frame 8",
        "wall shelf 1",
        "wall shelf 2",
        "washing machine 1",
        "washing sponge 1",
        "water glass 1",
        "water glass 2",
        "water glass 3",
        "water glass 4",
        "water glass 5",
        "window 1",
        "window 2",
        "wine 1"
      ]
    },
    "evaluation_context": {
      "task_goal": {
        "on_cupcake_coffeetable": 1,
        "on_apple_coffeetable": 1
      }
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
  "raw_instruction": "Put one cupcake and one apple on the coffee table",
  "original_instruction": "Put one cupcake and one apple on the coffee table",
  "messages": [
    "Put one cupcake and one apple on the coffee table"
  ],
  "task_context": {
    "dataset": "reactree",
    "env_id": 3,
    "task_name": "prepare_snack",
    "instruction": "Put one cupcake and one apple on the coffee table",
    "init_room": "bedroom",
    "task_source": "reactree_wah_testset",
    "environment_source": "reactree_case_runtime_scene",
    "init_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json",
    "task_goal": {
      "on_cupcake_coffeetable": 1,
      "on_apple_coffeetable": 1
    },
    "available_entities": [
      "apple 1",
      "apple 2",
      "apple 3",
      "bananas 1",
      "bar soap 1",
      "bathroom 1",
      "bathroom cabinet 1",
      "bathroom counter 1",
      "bed 1",
      "bedroom 1",
      "book 1",
      "book 2",
      "bookshelf 1",
      "bookshelf 2",
      "bookshelf 3",
      "bowl 1",
      "bowl 2",
      "bowl 3",
      "bowl 4",
      "bowl 5",
      "bowl 6",
      "bowl 7",
      "bowl 8",
      "bowl 9",
      "box 1",
      "box 2",
      "box 3",
      "box 4",
      "box 5",
      "bucket 1",
      "cabinet 1",
      "candle 1",
      "candy bar 1",
      "ceiling 1",
      "ceiling 10",
      "ceiling 11",
      "ceiling 12",
      "ceiling 13",
      "ceiling 14",
      "ceiling 15",
      "ceiling 16",
      "ceiling 17",
      "ceiling 18",
      "ceiling 19",
      "ceiling 2",
      "ceiling 20",
      "ceiling 21",
      "ceiling 22",
      "ceiling 23",
      "ceiling 24",
      "ceiling 25",
      "ceiling 26",
      "ceiling 3",
      "ceiling 4",
      "ceiling 5",
      "ceiling 6",
      "ceiling 7",
      "ceiling 8",
      "ceiling 9",
      "ceiling lamp 1",
      "ceiling lamp 2",
      "ceiling lamp 3",
      "ceiling lamp 4",
      "ceiling lamp 5",
      "cell phone 1",
      "cell phone 2",
      "cereal 1",
      "chair 1",
      "chair 2",
      "chair 3",
      "chair 4",
      "chair 5",
      "chair 6",
      "chips 1",
      "chips 2",
      "chocolate syrup 1",
      "closet 1",
      "closet drawer 1",
      "closet drawer 2",
      "closet drawer 3",
      "closet drawer 4",
      "closet drawer 5",
      "closet drawer 6",
      "closet drawer 7",
      "coffee maker 1",
      "coffee pot 1",
      "coffee table 1",
      "computer 1",
      "condiment bottle 1",
      "condiment bottle 2",
      "condiment bottle 3",
      "condiment bottle 4",
      "condiment shaker 1",
      "condiment shaker 2",
      "condiment shaker 3",
      "condiment shaker 4",
      "cooking pot 1",
      "cooking pot 2",
      "cpu screen 1",
      "crackers 1",
      "crackers 2",
      "creamy buns 1",
      "cupcake 1",
      "cupcake 2",
      "cupcake 3",
      "curtains 1",
      "curtains 2",
      "curtains 3",
      "curtains 4",
      "curtains 5",
      "curtains 6",
      "curtains 7",
      "cutlery fork 1",
      "cutlery fork 2",
      "cutlery fork 3",
      "cutlery fork 4",
      "cutlery knife 1",
      "cutlery knife 2",
      "cutlery knife 3",
      "cutlery knife 4",
      "cutlery knife 5",
      "cutlery knife 6",
      "cutlets 1",
      "deodorant 1",
      "deodorant 2",
      "deodorant 3",
      "desk 1",
      "desk 2",
      "dishwasher 1",
      "dishwashing liquid 1",
      "door 1",
      "door 2",
      "door 3",
      "door jamb 1",
      "door jamb 2",
      "door jamb 3",
      "door jamb 4",
      "face cream 1",
      "face cream 2",
      "face cream 3",
      "faucet 1",
      "faucet 2",
      "floor 1",
      "floor 10",
      "floor 11",
      "floor 12",
      "floor 13",
      "floor 14",
      "floor 15",
      "floor 16",
      "floor 17",
      "floor 18",
      "floor 19",
      "floor 2",
      "floor 20",
      "floor 21",
      "floor 22",
      "floor 23",
      "floor 24",
      "floor 25",
      "floor 26",
      "floor 3",
      "floor 4",
      "floor 5",
      "floor 6",
      "floor 7",
      "floor 8",
      "floor 9",
      "folder 1",
      "folder 2",
      "folder 3",
      "folder 4",
      "fridge 1",
      "frying pan 1",
      "hair product 1",
      "hair product 2",
      "hair product 3",
      "hair product 4",
      "hanger 1",
      "hanger 2",
      "hanger 3",
      "hanger 4",
      "hanger 5",
      "hanger 6",
      "hanger 7",
      "juice 1",
      "juice 2",
      "keyboard 1",
      "kitchen 1",
      "kitchen cabinet 1",
      "kitchen cabinet 2",
      "kitchen cabinet 3",
      "kitchen cabinet 4",
      "kitchen cabinet 5",
      "kitchen cabinet 6",
      "kitchen cabinet 7",
      "kitchen cabinet 8",
      "kitchen counter 1",
      "kitchen counter 2",
      "kitchen counter 3",
      "kitchen counter drawer 1",
      "kitchen counter drawer 2",
      "kitchen counter drawer 3",
      "kitchen counter drawer 4",
      "kitchen counter drawer 5",
      "kitchen counter drawer 6",
      "kitchen counter drawer 7",
      "kitchen counter drawer 8",
      "kitchen table 1",
      "knife block 1",
      "light switch 1",
      "light switch 2",
      "light switch 3",
      "light switch 4",
      "lime 1",
      "living room 1",
      "microwave oven 1",
      "milk 1",
      "mouse 1",
      "mouse mat 1",
      "mug 1",
      "mug 2",
      "mug 3",
      "nightstand 1",
      "nightstand 2",
      "nightstand 3",
      "nightstand 4",
      "notes 1",
      "orchid 1",
      "oven tray 1",
      "painkillers 1",
      "pancake 1",
      "peach 1",
      "peach 2",
      "peach 3",
      "pear 1",
      "perfume 1",
      "perfume 2",
      "photo frame 1",
      "photo frame 2",
      "photo frame 3",
      "pile of clothes 1",
      "pile of clothes 2",
      "pillow 1",
      "pillow 2",
      "pillow 3",
      "pillow 4",
      "pillow 5",
      "pillow 6",
      "plate 1",
      "plate 2",
      "plate 3",
      "plate 4",
      "plate 5",
      "plate 6",
      "plate 7",
      "plum 1",
      "plum 2",
      "power socket 1",
      "power socket 2",
      "power socket 3",
      "pudding 1",
      "pudding 2",
      "radio 1",
      "rug 1",
      "rug 2",
      "rug 3",
      "rug 4",
      "sink 1",
      "sink 2",
      "slice of bread 1",
      "slice of bread 2",
      "sofa 1",
      "sofa 2",
      "sofa 3",
      "stall 1",
      "stall 2",
      "stove 1",
      "stove fan 1",
      "table lamp 1",
      "toaster 1",
      "toilet 1",
      "toilet paper 1",
      "toothbrush 1",
      "toothpaste 1",
      "tv 1",
      "tv stand 1",
      "wall 1",
      "wall 10",
      "wall 11",
      "wall 12",
      "wall 13",
      "wall 14",
      "wall 15",
      "wall 16",
      "wall 17",
      "wall 18",
      "wall 19",
      "wall 2",
      "wall 20",
      "wall 21",
      "wall 22",
      "wall 23",
      "wall 24",
      "wall 25",
      "wall 26",
      "wall 3",
      "wall 4",
      "wall 5",
      "wall 6",
      "wall 7",
      "wall 8",
      "wall 9",
      "wall lamp 1",
      "wall lamp 2",
      "wall lamp 3",
      "wall lamp 4",
      "wall lamp 5",
      "wall lamp 6",
      "wall lamp 7",
      "wall lamp 8",
      "wall lamp 9",
      "wall phone 1",
      "wall picture frame 1",
      "wall picture frame 2",
      "wall picture frame 3",
      "wall picture frame 4",
      "wall picture frame 5",
      "wall picture frame 6",
      "wall picture frame 7",
      "wall picture frame 8",
      "wall shelf 1",
      "wall shelf 2",
      "washing machine 1",
      "washing sponge 1",
      "water glass 1",
      "water glass 2",
      "water glass 3",
      "water glass 4",
      "water glass 5",
      "window 1",
      "window 2",
      "wine 1"
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
      "cupcake 1",
      "cupcake 2",
      "cupcake 3",
      "apple 1",
      "apple 2",
      "apple 3",
      "coffee table 1"
    ],
    "truncated": false
  },
  "structured_task": {
    "intent": "Put one cupcake and one apple on the coffee table",
    "required_item_names": {
      "targets": {
        "primary": [
          "cupcake 1",
          "apple 1"
        ],
        "alternatives": []
      },
      "tools": {
        "primary": [],
        "alternatives": []
      },
      "receptacles": {
        "primary": [
          "coffee table 1"
        ],
        "alternatives": []
      }
    },
    "quantity_constraints": [
      "1 cupcake",
      "1 apple"
    ],
    "final_state": {
      "on_cupcake_coffeetable": 1,
      "on_apple_coffeetable": 1
    }
  },
  "understanding_final_state": {
    "on_cupcake_coffeetable": 1,
    "on_apple_coffeetable": 1
  },
  "entity_repair": {
    "needed": false,
    "invalid_names": [],
    "valid_names": [
      "cupcake 1",
      "apple 1",
      "cupcake 2",
      "cupcake 3",
      "apple 2",
      "apple 3",
      "coffee table 1"
    ]
  },
  "goal_state_extract": {
    "enabled": true,
    "source": "llm",
    "attempts": 1,
    "raw": {
      "final_state": {
        "on_cupcake_coffeetable": 1,
        "on_apple_coffeetable": 1
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
    "todo_output_parser_path": "benchmark.reactree.wah.framework.code.native_actions.parse_wah_native_actions",
    "todo_step_adapter_path": "benchmark.reactree.wah.framework.code.native_actions.wah_native_step_to_skill_call",
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
      "config_file": "/data/zmy/OurAgent-he1/benchmark/reactree/wah/framework/code/config/settings.json",
      "skills_root": "benchmark/reactree/wah/framework/code/skills",
      "enabled_contract_skill_count": 8,
      "raw_contract_count": 8,
      "framework_contract_skills": [
        "go to",
        "pick up",
        "put down",
        "open",
        "close",
        "turn on",
        "turn off",
        "clean"
      ],
      "raw_action_names": [
        "go to",
        "pick up",
        "put down",
        "open",
        "close",
        "turn on",
        "turn off",
        "clean"
      ],
      "raw_actions": [
        {
          "skill": "go to",
          "action_name": "go to",
          "action_field": "action",
          "required_fields": [
            "action",
            "target"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "go to"
            }
          ],
          "entity_fields": [
            "target"
          ],
          "room_fields": [],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "",
          "context_values": []
        },
        {
          "skill": "pick up",
          "action_name": "pick up",
          "action_field": "action",
          "required_fields": [
            "action",
            "target"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "pick up"
            }
          ],
          "entity_fields": [
            "target"
          ],
          "room_fields": [],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "",
          "context_values": []
        },
        {
          "skill": "put down",
          "action_name": "put down",
          "action_field": "action",
          "required_fields": [
            "action",
            "target"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "put down"
            }
          ],
          "entity_fields": [
            "target"
          ],
          "room_fields": [],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "",
          "context_values": []
        },
        {
          "skill": "open",
          "action_name": "open",
          "action_field": "action",
          "required_fields": [
            "action",
            "target"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "open"
            }
          ],
          "entity_fields": [
            "target"
          ],
          "room_fields": [],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "",
          "context_values": []
        },
        {
          "skill": "close",
          "action_name": "close",
          "action_field": "action",
          "required_fields": [
            "action",
            "target"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "close"
            }
          ],
          "entity_fields": [
            "target"
          ],
          "room_fields": [],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "",
          "context_values": []
        },
        {
          "skill": "turn on",
          "action_name": "turn on",
          "action_field": "action",
          "required_fields": [
            "action",
            "target"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "turn on"
            }
          ],
          "entity_fields": [
            "target"
          ],
          "room_fields": [],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "",
          "context_values": []
        },
        {
          "skill": "turn off",
          "action_name": "turn off",
          "action_field": "action",
          "required_fields": [
            "action",
            "target"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "turn off"
            }
          ],
          "entity_fields": [
            "target"
          ],
          "room_fields": [],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "",
          "context_values": []
        },
        {
          "skill": "clean",
          "action_name": "clean",
          "action_field": "action",
          "required_fields": [
            "action",
            "target"
          ],
          "fixed_fields": [
            {
              "field": "action",
              "value": "clean"
            }
          ],
          "entity_fields": [
            "target"
          ],
          "room_fields": [],
          "args_field": "args",
          "args_arity": null,
          "entity_args": [],
          "allow_extra_fields": false,
          "allow_comma_separated_entities": false,
          "entity_pattern": "",
          "dynamic_entity_rule": "",
          "unchecked_fields": [],
          "context_field": "",
          "context_values": []
        }
      ]
    }
  },
  "input": {
    "understanding_stage_executed": true,
    "structured_task": {
      "intent": "Put one cupcake and one apple on the coffee table",
      "required_item_names": {
        "targets": {
          "primary": [
            "cupcake 1",
            "apple 1"
          ],
          "alternatives": []
        },
        "tools": {
          "primary": [],
          "alternatives": []
        },
        "receptacles": {
          "primary": [
            "coffee table 1"
          ],
          "alternatives": []
        }
      },
      "quantity_constraints": [
        "1 cupcake",
        "1 apple"
      ],
      "final_state": {
        "on_cupcake_coffeetable": 1,
        "on_apple_coffeetable": 1
      }
    },
    "env_state": {
      "robot_location": "bedroom 1",
      "robot_holding": "空"
    },
    "task_context": {
      "dataset": "reactree",
      "env_id": 3,
      "task_name": "prepare_snack",
      "instruction": "Put one cupcake and one apple on the coffee table",
      "init_room": "bedroom",
      "task_source": "reactree_wah_testset",
      "environment_source": "reactree_case_runtime_scene",
      "init_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json",
      "task_goal": {
        "on_cupcake_coffeetable": 1,
        "on_apple_coffeetable": 1
      },
      "available_entities": [
        "apple 1",
        "apple 2",
        "apple 3",
        "bananas 1",
        "bar soap 1",
        "bathroom 1",
        "bathroom cabinet 1",
        "bathroom counter 1",
        "bed 1",
        "bedroom 1",
        "book 1",
        "book 2",
        "bookshelf 1",
        "bookshelf 2",
        "bookshelf 3",
        "bowl 1",
        "bowl 2",
        "bowl 3",
        "bowl 4",
        "bowl 5",
        "bowl 6",
        "bowl 7",
        "bowl 8",
        "bowl 9",
        "box 1",
        "box 2",
        "box 3",
        "box 4",
        "box 5",
        "bucket 1",
        "cabinet 1",
        "candle 1",
        "candy bar 1",
        "ceiling 1",
        "ceiling 10",
        "ceiling 11",
        "ceiling 12",
        "ceiling 13",
        "ceiling 14",
        "ceiling 15",
        "ceiling 16",
        "ceiling 17",
        "ceiling 18",
        "ceiling 19",
        "ceiling 2",
        "ceiling 20",
        "ceiling 21",
        "ceiling 22",
        "ceiling 23",
        "ceiling 24",
        "ceiling 25",
        "ceiling 26",
        "ceiling 3",
        "ceiling 4",
        "ceiling 5",
        "ceiling 6",
        "ceiling 7",
        "ceiling 8",
        "ceiling 9",
        "ceiling lamp 1",
        "ceiling lamp 2",
        "ceiling lamp 3",
        "ceiling lamp 4",
        "ceiling lamp 5",
        "cell phone 1",
        "cell phone 2",
        "cereal 1",
        "chair 1",
        "chair 2",
        "chair 3",
        "chair 4",
        "chair 5",
        "chair 6",
        "chips 1",
        "chips 2",
        "chocolate syrup 1",
        "closet 1",
        "closet drawer 1",
        "closet drawer 2",
        "closet drawer 3",
        "closet drawer 4",
        "closet drawer 5",
        "closet drawer 6",
        "closet drawer 7",
        "coffee maker 1",
        "coffee pot 1",
        "coffee table 1",
        "computer 1",
        "condiment bottle 1",
        "condiment bottle 2",
        "condiment bottle 3",
        "condiment bottle 4",
        "condiment shaker 1",
        "condiment shaker 2",
        "condiment shaker 3",
        "condiment shaker 4",
        "cooking pot 1",
        "cooking pot 2",
        "cpu screen 1",
        "crackers 1",
        "crackers 2",
        "creamy buns 1",
        "cupcake 1",
        "cupcake 2",
        "cupcake 3",
        "curtains 1",
        "curtains 2",
        "curtains 3",
        "curtains 4",
        "curtains 5",
        "curtains 6",
        "curtains 7",
        "cutlery fork 1",
        "cutlery fork 2",
        "cutlery fork 3",
        "cutlery fork 4",
        "cutlery knife 1",
        "cutlery knife 2",
        "cutlery knife 3",
        "cutlery knife 4",
        "cutlery knife 5",
        "cutlery knife 6",
        "cutlets 1",
        "deodorant 1",
        "deodorant 2",
        "deodorant 3",
        "desk 1",
        "desk 2",
        "dishwasher 1",
        "dishwashing liquid 1",
        "door 1",
        "door 2",
        "door 3",
        "door jamb 1",
        "door jamb 2",
        "door jamb 3",
        "door jamb 4",
        "face cream 1",
        "face cream 2",
        "face cream 3",
        "faucet 1",
        "faucet 2",
        "floor 1",
        "floor 10",
        "floor 11",
        "floor 12",
        "floor 13",
        "floor 14",
        "floor 15",
        "floor 16",
        "floor 17",
        "floor 18",
        "floor 19",
        "floor 2",
        "floor 20",
        "floor 21",
        "floor 22",
        "floor 23",
        "floor 24",
        "floor 25",
        "floor 26",
        "floor 3",
        "floor 4",
        "floor 5",
        "floor 6",
        "floor 7",
        "floor 8",
        "floor 9",
        "folder 1",
        "folder 2",
        "folder 3",
        "folder 4",
        "fridge 1",
        "frying pan 1",
        "hair product 1",
        "hair product 2",
        "hair product 3",
        "hair product 4",
        "hanger 1",
        "hanger 2",
        "hanger 3",
        "hanger 4",
        "hanger 5",
        "hanger 6",
        "hanger 7",
        "juice 1",
        "juice 2",
        "keyboard 1",
        "kitchen 1",
        "kitchen cabinet 1",
        "kitchen cabinet 2",
        "kitchen cabinet 3",
        "kitchen cabinet 4",
        "kitchen cabinet 5",
        "kitchen cabinet 6",
        "kitchen cabinet 7",
        "kitchen cabinet 8",
        "kitchen counter 1",
        "kitchen counter 2",
        "kitchen counter 3",
        "kitchen counter drawer 1",
        "kitchen counter drawer 2",
        "kitchen counter drawer 3",
        "kitchen counter drawer 4",
        "kitchen counter drawer 5",
        "kitchen counter drawer 6",
        "kitchen counter drawer 7",
        "kitchen counter drawer 8",
        "kitchen table 1",
        "knife block 1",
        "light switch 1",
        "light switch 2",
        "light switch 3",
        "light switch 4",
        "lime 1",
        "living room 1",
        "microwave oven 1",
        "milk 1",
        "mouse 1",
        "mouse mat 1",
        "mug 1",
        "mug 2",
        "mug 3",
        "nightstand 1",
        "nightstand 2",
        "nightstand 3",
        "nightstand 4",
        "notes 1",
        "orchid 1",
        "oven tray 1",
        "painkillers 1",
        "pancake 1",
        "peach 1",
        "peach 2",
        "peach 3",
        "pear 1",
        "perfume 1",
        "perfume 2",
        "photo frame 1",
        "photo frame 2",
        "photo frame 3",
        "pile of clothes 1",
        "pile of clothes 2",
        "pillow 1",
        "pillow 2",
        "pillow 3",
        "pillow 4",
        "pillow 5",
        "pillow 6",
        "plate 1",
        "plate 2",
        "plate 3",
        "plate 4",
        "plate 5",
        "plate 6",
        "plate 7",
        "plum 1",
        "plum 2",
        "power socket 1",
        "power socket 2",
        "power socket 3",
        "pudding 1",
        "pudding 2",
        "radio 1",
        "rug 1",
        "rug 2",
        "rug 3",
        "rug 4",
        "sink 1",
        "sink 2",
        "slice of bread 1",
        "slice of bread 2",
        "sofa 1",
        "sofa 2",
        "sofa 3",
        "stall 1",
        "stall 2",
        "stove 1",
        "stove fan 1",
        "table lamp 1",
        "toaster 1",
        "toilet 1",
        "toilet paper 1",
        "toothbrush 1",
        "toothpaste 1",
        "tv 1",
        "tv stand 1",
        "wall 1",
        "wall 10",
        "wall 11",
        "wall 12",
        "wall 13",
        "wall 14",
        "wall 15",
        "wall 16",
        "wall 17",
        "wall 18",
        "wall 19",
        "wall 2",
        "wall 20",
        "wall 21",
        "wall 22",
        "wall 23",
        "wall 24",
        "wall 25",
        "wall 26",
        "wall 3",
        "wall 4",
        "wall 5",
        "wall 6",
        "wall 7",
        "wall 8",
        "wall 9",
        "wall lamp 1",
        "wall lamp 2",
        "wall lamp 3",
        "wall lamp 4",
        "wall lamp 5",
        "wall lamp 6",
        "wall lamp 7",
        "wall lamp 8",
        "wall lamp 9",
        "wall phone 1",
        "wall picture frame 1",
        "wall picture frame 2",
        "wall picture frame 3",
        "wall picture frame 4",
        "wall picture frame 5",
        "wall picture frame 6",
        "wall picture frame 7",
        "wall picture frame 8",
        "wall shelf 1",
        "wall shelf 2",
        "washing machine 1",
        "washing sponge 1",
        "water glass 1",
        "water glass 2",
        "water glass 3",
        "water glass 4",
        "water glass 5",
        "window 1",
        "window 2",
        "wine 1"
      ]
    },
    "feedback": "",
    "environment": {
      "available": true,
      "entity_count": 17,
      "type_counts": {
        "unknown": 7,
        "room": 3,
        "receptacle": 7
      },
      "entities": {
        "count": 17,
        "sample": [
          "apple 1",
          "apple 2",
          "apple 3",
          "bedroom 1",
          "cabinet 1",
          "coffee table 1",
          "cupcake 1",
          "cupcake 2",
          "cupcake 3",
          "floor 16",
          "floor 2",
          "floor 25",
          "floor 4",
          "fridge 1",
          "kitchen 1",
          "kitchen table 1",
          "living room 1"
        ],
        "truncated": false
      },
      "states_sample": {
        "cabinet 1": {
          "isOpen": false
        },
        "fridge 1": {
          "isOpen": false
        }
      },
      "schema": {
        "available": true,
        "entity_count": 17,
        "standard_field_counts": {
          "direct_parent": 17,
          "direct_relation": 17,
          "type": 17,
          "states": 17,
          "properties": 17,
          "is_container": 17,
          "full_path": 17
        },
        "relation_entity_count": 14,
        "state_entity_count": 2,
        "property_entity_count": 14,
        "container_count": 7,
        "full_path_entity_count": 14,
        "parent_missing_count": 0,
        "parent_missing_sample": [],
        "parent_reference_missing_count": 0,
        "parent_reference_missing_sample": []
      }
    },
    "environment_facts": {
      "available": true,
      "entity_count": 17,
      "facts": [
        {
          "name": "apple 1",
          "direct_parent": "fridge 1",
          "direct_relation": "inside",
          "full_path": [
            "kitchen 1",
            "floor 4",
            "fridge 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "apple 2",
          "direct_parent": "kitchen table 1",
          "direct_relation": "on",
          "full_path": [
            "kitchen 1",
            "floor 2",
            "kitchen table 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "apple 3",
          "direct_parent": "cabinet 1",
          "direct_relation": "inside",
          "full_path": [
            "bedroom 1",
            "floor 16",
            "cabinet 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "bedroom 1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "cabinet 1",
          "direct_parent": "floor 16",
          "direct_relation": "on",
          "full_path": [
            "bedroom 1",
            "floor 16"
          ],
          "states": {
            "isOpen": false
          },
          "properties": [
            "SURFACES",
            "CAN_OPEN",
            "CONTAINERS"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "coffee table 1",
          "direct_parent": "floor 25",
          "direct_relation": "on",
          "full_path": [
            "living room 1",
            "floor 25"
          ],
          "states": {},
          "properties": [
            "SURFACES",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "cupcake 1",
          "direct_parent": "kitchen table 1",
          "direct_relation": "on",
          "full_path": [
            "kitchen 1",
            "floor 2",
            "kitchen table 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "EATABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "cupcake 2",
          "direct_parent": "kitchen table 1",
          "direct_relation": "on",
          "full_path": [
            "kitchen 1",
            "floor 2",
            "kitchen table 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "EATABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "cupcake 3",
          "direct_parent": "cabinet 1",
          "direct_relation": "inside",
          "full_path": [
            "bedroom 1",
            "floor 16",
            "cabinet 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "EATABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "floor 16",
          "direct_parent": "bedroom 1",
          "direct_relation": "inside",
          "full_path": [
            "bedroom 1"
          ],
          "states": {},
          "properties": [
            "SURFACES"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "floor 2",
          "direct_parent": "kitchen 1",
          "direct_relation": "inside",
          "full_path": [
            "kitchen 1"
          ],
          "states": {},
          "properties": [
            "SURFACES"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "floor 25",
          "direct_parent": "living room 1",
          "direct_relation": "inside",
          "full_path": [
            "living room 1"
          ],
          "states": {},
          "properties": [
            "SURFACES"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "floor 4",
          "direct_parent": "kitchen 1",
          "direct_relation": "inside",
          "full_path": [
            "kitchen 1"
          ],
          "states": {},
          "properties": [
            "SURFACES"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "fridge 1",
          "direct_parent": "floor 4",
          "direct_relation": "on",
          "full_path": [
            "kitchen 1",
            "floor 4"
          ],
          "states": {
            "isOpen": false
          },
          "properties": [
            "CAN_OPEN",
            "HAS_SWITCH",
            "CONTAINERS",
            "HAS_PLUG"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "kitchen 1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "kitchen table 1",
          "direct_parent": "floor 2",
          "direct_relation": "on",
          "full_path": [
            "kitchen 1",
            "floor 2"
          ],
          "states": {},
          "properties": [
            "SURFACES",
            "MOVABLE"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "living room 1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        }
      ],
      "truncated": false
    },
    "environment_source": {
      "builder": "build_sandbox_environment",
      "benchmark": "benchmark.reactree.wah"
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
      "count": 8,
      "sample": [
        {
          "step": 1,
          "action": "go to",
          "target": "kitchen table 1"
        },
        {
          "step": 2,
          "action": "pick up",
          "target": "cupcake 1"
        },
        {
          "step": 3,
          "action": "go to",
          "target": "coffee table 1"
        },
        {
          "step": 4,
          "action": "put down",
          "target": "cupcake 1"
        },
        {
          "step": 5,
          "action": "go to",
          "target": "kitchen table 1"
        },
        {
          "step": 6,
          "action": "pick up",
          "target": "apple 2"
        },
        {
          "step": 7,
          "action": "go to",
          "target": "coffee table 1"
        },
        {
          "step": 8,
          "action": "put down",
          "target": "apple 2"
        }
      ],
      "truncated": false
    },
    "validated_steps": {
      "count": 0,
      "sample": [],
      "truncated": false
    },
    "validated_todo_actions": {
      "count": 8,
      "sample": [
        {
          "step": 1,
          "action": "go to",
          "target": "kitchen table 1"
        },
        {
          "step": 2,
          "action": "pick up",
          "target": "cupcake 1"
        },
        {
          "step": 3,
          "action": "go to",
          "target": "coffee table 1"
        },
        {
          "step": 4,
          "action": "put down",
          "target": "cupcake 1"
        },
        {
          "step": 5,
          "action": "go to",
          "target": "kitchen table 1"
        },
        {
          "step": 6,
          "action": "pick up",
          "target": "apple 2"
        },
        {
          "step": 7,
          "action": "go to",
          "target": "coffee table 1"
        },
        {
          "step": 8,
          "action": "put down",
          "target": "apple 2"
        }
      ],
      "truncated": false
    },
    "todo_llm_output": "[\n  {\n    \"action\": \"go to\",\n    \"target\": \"kitchen table 1\"\n  },\n  {\n    \"action\": \"pick up\",\n    \"target\": \"cupcake 1\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"coffee table 1\"\n  },\n  {\n    \"action\": \"put down\",\n    \"target\": \"cupcake 1\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"kitchen table 1\"\n  },\n  {\n    \"action\": \"pick up\",\n    \"target\": \"apple 2\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"coffee table 1\"\n  },\n  {\n    \"action\": \"put down\",\n    \"target\": \"apple 2\"\n  }\n]",
    "todo_parse_error": "",
    "evaluator_findings": {
      "count": 0,
      "sample": [],
      "truncated": false
    }
  },
  "state": {
    "env_state": {
      "robot_location": "coffee table 1",
      "robot_holding": "空"
    },
    "environment": {
      "available": true,
      "entity_count": 17,
      "type_counts": {
        "unknown": 7,
        "room": 3,
        "receptacle": 7
      },
      "entities": {
        "count": 17,
        "sample": [
          "apple 1",
          "apple 2",
          "apple 3",
          "bedroom 1",
          "cabinet 1",
          "coffee table 1",
          "cupcake 1",
          "cupcake 2",
          "cupcake 3",
          "floor 16",
          "floor 2",
          "floor 25",
          "floor 4",
          "fridge 1",
          "kitchen 1",
          "kitchen table 1",
          "living room 1"
        ],
        "truncated": false
      },
      "states_sample": {
        "cabinet 1": {
          "isOpen": false
        },
        "fridge 1": {
          "isOpen": false
        }
      },
      "schema": {
        "available": true,
        "entity_count": 17,
        "standard_field_counts": {
          "direct_parent": 17,
          "direct_relation": 17,
          "type": 17,
          "states": 17,
          "properties": 17,
          "is_container": 17,
          "full_path": 17
        },
        "relation_entity_count": 14,
        "state_entity_count": 2,
        "property_entity_count": 14,
        "container_count": 7,
        "full_path_entity_count": 14,
        "parent_missing_count": 0,
        "parent_missing_sample": [],
        "parent_reference_missing_count": 0,
        "parent_reference_missing_sample": []
      }
    },
    "environment_facts": {
      "available": true,
      "entity_count": 17,
      "facts": [
        {
          "name": "apple 1",
          "direct_parent": "fridge 1",
          "direct_relation": "inside",
          "full_path": [
            "kitchen 1",
            "floor 4",
            "fridge 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "apple 2",
          "direct_parent": "coffee table 1",
          "direct_relation": "on",
          "full_path": [
            "kitchen 1",
            "floor 2",
            "kitchen table 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "apple 3",
          "direct_parent": "cabinet 1",
          "direct_relation": "inside",
          "full_path": [
            "bedroom 1",
            "floor 16",
            "cabinet 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "bedroom 1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "cabinet 1",
          "direct_parent": "floor 16",
          "direct_relation": "on",
          "full_path": [
            "bedroom 1",
            "floor 16"
          ],
          "states": {
            "isOpen": false
          },
          "properties": [
            "SURFACES",
            "CAN_OPEN",
            "CONTAINERS"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "coffee table 1",
          "direct_parent": "floor 25",
          "direct_relation": "on",
          "full_path": [
            "living room 1",
            "floor 25"
          ],
          "states": {},
          "properties": [
            "SURFACES",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "cupcake 1",
          "direct_parent": "coffee table 1",
          "direct_relation": "on",
          "full_path": [
            "kitchen 1",
            "floor 2",
            "kitchen table 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "EATABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "cupcake 2",
          "direct_parent": "kitchen table 1",
          "direct_relation": "on",
          "full_path": [
            "kitchen 1",
            "floor 2",
            "kitchen table 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "EATABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "cupcake 3",
          "direct_parent": "cabinet 1",
          "direct_relation": "inside",
          "full_path": [
            "bedroom 1",
            "floor 16",
            "cabinet 1"
          ],
          "states": {},
          "properties": [
            "GRABBABLE",
            "EATABLE",
            "MOVABLE"
          ],
          "type": null,
          "is_container": false
        },
        {
          "name": "floor 16",
          "direct_parent": "bedroom 1",
          "direct_relation": "inside",
          "full_path": [
            "bedroom 1"
          ],
          "states": {},
          "properties": [
            "SURFACES"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "floor 2",
          "direct_parent": "kitchen 1",
          "direct_relation": "inside",
          "full_path": [
            "kitchen 1"
          ],
          "states": {},
          "properties": [
            "SURFACES"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "floor 25",
          "direct_parent": "living room 1",
          "direct_relation": "inside",
          "full_path": [
            "living room 1"
          ],
          "states": {},
          "properties": [
            "SURFACES"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "floor 4",
          "direct_parent": "kitchen 1",
          "direct_relation": "inside",
          "full_path": [
            "kitchen 1"
          ],
          "states": {},
          "properties": [
            "SURFACES"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "fridge 1",
          "direct_parent": "floor 4",
          "direct_relation": "on",
          "full_path": [
            "kitchen 1",
            "floor 4"
          ],
          "states": {
            "isOpen": false
          },
          "properties": [
            "CAN_OPEN",
            "HAS_SWITCH",
            "CONTAINERS",
            "HAS_PLUG"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "kitchen 1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        },
        {
          "name": "kitchen table 1",
          "direct_parent": "floor 2",
          "direct_relation": "on",
          "full_path": [
            "kitchen 1",
            "floor 2"
          ],
          "states": {},
          "properties": [
            "SURFACES",
            "MOVABLE"
          ],
          "type": "receptacle",
          "is_container": true
        },
        {
          "name": "living room 1",
          "direct_parent": "未知环境",
          "direct_relation": null,
          "full_path": [],
          "states": {},
          "properties": [],
          "type": "room",
          "is_container": false
        }
      ],
      "truncated": false
    },
    "environment_source": {
      "builder": "build_sandbox_environment",
      "benchmark": "benchmark.reactree.wah"
    },
    "checkpoint_env": {
      "available": true,
      "entity_count": 17,
      "type_counts": {
        "unknown": 7,
        "room": 3,
        "receptacle": 7
      },
      "entities": {
        "count": 17,
        "sample": [
          "apple 1",
          "apple 2",
          "apple 3",
          "bedroom 1",
          "cabinet 1",
          "coffee table 1",
          "cupcake 1",
          "cupcake 2",
          "cupcake 3",
          "floor 16",
          "floor 2",
          "floor 25",
          "floor 4",
          "fridge 1",
          "kitchen 1",
          "kitchen table 1",
          "living room 1"
        ],
        "truncated": false
      },
      "states_sample": {
        "cabinet 1": {
          "isOpen": false
        },
        "fridge 1": {
          "isOpen": false
        }
      },
      "schema": {
        "available": true,
        "entity_count": 17,
        "standard_field_counts": {
          "direct_parent": 17,
          "direct_relation": 17,
          "type": 17,
          "states": 17,
          "properties": 17,
          "is_container": 17,
          "full_path": 17
        },
        "relation_entity_count": 14,
        "state_entity_count": 2,
        "property_entity_count": 14,
        "container_count": 7,
        "full_path_entity_count": 14,
        "parent_missing_count": 0,
        "parent_missing_sample": [],
        "parent_reference_missing_count": 0,
        "parent_reference_missing_sample": []
      }
    },
    "checkpoint_robot": {
      "robot_location": "coffee table 1",
      "robot_holding": "空"
    },
    "todo_checkpoint_env": {
      "available": true,
      "entity_count": 17,
      "type_counts": {
        "unknown": 7,
        "room": 3,
        "receptacle": 7
      },
      "entities": {
        "count": 17,
        "sample": [
          "apple 1",
          "apple 2",
          "apple 3",
          "bedroom 1",
          "cabinet 1",
          "coffee table 1",
          "cupcake 1",
          "cupcake 2",
          "cupcake 3",
          "floor 16",
          "floor 2",
          "floor 25",
          "floor 4",
          "fridge 1",
          "kitchen 1",
          "kitchen table 1",
          "living room 1"
        ],
        "truncated": false
      },
      "states_sample": {
        "cabinet 1": {
          "isOpen": false
        },
        "fridge 1": {
          "isOpen": false
        }
      },
      "schema": {
        "available": true,
        "entity_count": 17,
        "standard_field_counts": {
          "direct_parent": 17,
          "direct_relation": 17,
          "type": 17,
          "states": 17,
          "properties": 17,
          "is_container": 17,
          "full_path": 17
        },
        "relation_entity_count": 14,
        "state_entity_count": 2,
        "property_entity_count": 14,
        "container_count": 7,
        "full_path_entity_count": 14,
        "parent_missing_count": 0,
        "parent_missing_sample": [],
        "parent_reference_missing_count": 0,
        "parent_reference_missing_sample": []
      }
    },
    "todo_checkpoint_robot": {
      "robot_location": "coffee table 1",
      "robot_holding": "空"
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
          "cupcake 1 moved to coffee table 1",
          "apple 2 moved to coffee table 1"
        ],
        "unexpected_diffs": [],
        "audit_method": "framework_llm_state_diff",
        "state_audit_context": {
          "entity_count_available": 17,
          "entity_count_in_context": 9,
          "truncated_entity_count": 0,
          "note": "state_diff only lists changed entities; unchanged entities in this context still prove final goal state when their after state satisfies the task.",
          "robot": {
            "changed": true,
            "before": {
              "robot_location": "bedroom 1",
              "robot_holding": "空"
            },
            "after": {
              "robot_location": "coffee table 1",
              "robot_holding": "空"
            }
          },
          "entities": [
            {
              "name": "cupcake 1",
              "changed": true,
              "before": {
                "type": null,
                "direct_parent": "kitchen table 1",
                "direct_relation": "on",
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ],
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "EATABLE",
                  "MOVABLE"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "coffee table 1",
                "direct_relation": "on",
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ],
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "EATABLE",
                  "MOVABLE"
                ]
              }
            },
            {
              "name": "apple 1",
              "changed": false,
              "before": {
                "type": null,
                "direct_parent": "fridge 1",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 4",
                  "fridge 1"
                ],
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "fridge 1",
                "direct_relation": "inside",
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 4",
                  "fridge 1"
                ],
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ]
              }
            },
            {
              "name": "coffee table 1",
              "changed": false,
              "before": {
                "type": null,
                "direct_parent": "floor 25",
                "direct_relation": "on",
                "is_container": false,
                "full_path": [
                  "living room 1",
                  "floor 25"
                ],
                "states": {},
                "properties": [
                  "SURFACES",
                  "MOVABLE"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "floor 25",
                "direct_relation": "on",
                "is_container": false,
                "full_path": [
                  "living room 1",
                  "floor 25"
                ],
                "states": {},
                "properties": [
                  "SURFACES",
                  "MOVABLE"
                ]
              }
            },
            {
              "name": "floor 25",
              "changed": false,
              "before": {
                "type": "receptacle",
                "direct_parent": "living room 1",
                "direct_relation": "inside",
                "is_container": true,
                "full_path": [
                  "living room 1"
                ],
                "states": {},
                "properties": [
                  "SURFACES"
                ]
              },
              "after": {
                "type": "receptacle",
                "direct_parent": "living room 1",
                "direct_relation": "inside",
                "is_container": true,
                "full_path": [
                  "living room 1"
                ],
                "states": {},
                "properties": [
                  "SURFACES"
                ]
              }
            },
            {
              "name": "living room 1",
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
            },
            {
              "name": "fridge 1",
              "changed": false,
              "before": {
                "type": "receptacle",
                "direct_parent": "floor 4",
                "direct_relation": "on",
                "is_container": true,
                "full_path": [
                  "kitchen 1",
                  "floor 4"
                ],
                "states": {
                  "isOpen": false
                },
                "properties": [
                  "CAN_OPEN",
                  "HAS_SWITCH",
                  "CONTAINERS",
                  "HAS_PLUG"
                ]
              },
              "after": {
                "type": "receptacle",
                "direct_parent": "floor 4",
                "direct_relation": "on",
                "is_container": true,
                "full_path": [
                  "kitchen 1",
                  "floor 4"
                ],
                "states": {
                  "isOpen": false
                },
                "properties": [
                  "CAN_OPEN",
                  "HAS_SWITCH",
                  "CONTAINERS",
                  "HAS_PLUG"
                ]
              }
            },
            {
              "name": "floor 4",
              "changed": false,
              "before": {
                "type": "receptacle",
                "direct_parent": "kitchen 1",
                "direct_relation": "inside",
                "is_container": true,
                "full_path": [
                  "kitchen 1"
                ],
                "states": {},
                "properties": [
                  "SURFACES"
                ]
              },
              "after": {
                "type": "receptacle",
                "direct_parent": "kitchen 1",
                "direct_relation": "inside",
                "is_container": true,
                "full_path": [
                  "kitchen 1"
                ],
                "states": {},
                "properties": [
                  "SURFACES"
                ]
              }
            },
            {
              "name": "kitchen 1",
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
            },
            {
              "name": "apple 2",
              "changed": true,
              "before": {
                "type": null,
                "direct_parent": "kitchen table 1",
                "direct_relation": "on",
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ],
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "coffee table 1",
                "direct_relation": "on",
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ],
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ]
              }
            }
          ],
          "task_context": {
            "dataset": "reactree",
            "env_id": 3,
            "task_name": "prepare_snack",
            "instruction": "Put one cupcake and one apple on the coffee table",
            "init_room": "bedroom",
            "task_source": "reactree_wah_testset",
            "environment_source": "reactree_case_runtime_scene",
            "init_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json",
            "task_goal": {
              "on_cupcake_coffeetable": 1,
              "on_apple_coffeetable": 1
            },
            "available_entities": [
              "apple 1",
              "apple 2",
              "apple 3",
              "bananas 1",
              "bar soap 1",
              "bathroom 1",
              "bathroom cabinet 1",
              "bathroom counter 1",
              "bed 1",
              "bedroom 1",
              "book 1",
              "book 2",
              "bookshelf 1",
              "bookshelf 2",
              "bookshelf 3",
              "bowl 1",
              "bowl 2",
              "bowl 3",
              "bowl 4",
              "bowl 5",
              "bowl 6",
              "bowl 7",
              "bowl 8",
              "bowl 9",
              "box 1",
              "box 2",
              "box 3",
              "box 4",
              "box 5",
              "bucket 1",
              "cabinet 1",
              "candle 1",
              "candy bar 1",
              "ceiling 1",
              "ceiling 10",
              "ceiling 11",
              "ceiling 12",
              "ceiling 13",
              "ceiling 14",
              "ceiling 15",
              "ceiling 16",
              "ceiling 17",
              "ceiling 18",
              "ceiling 19",
              "ceiling 2",
              "ceiling 20",
              "ceiling 21",
              "ceiling 22",
              "ceiling 23",
              "ceiling 24",
              "ceiling 25",
              "ceiling 26",
              "ceiling 3",
              "ceiling 4",
              "ceiling 5",
              "ceiling 6",
              "ceiling 7",
              "ceiling 8",
              "ceiling 9",
              "ceiling lamp 1",
              "ceiling lamp 2",
              "ceiling lamp 3",
              "ceiling lamp 4",
              "ceiling lamp 5",
              "cell phone 1",
              "cell phone 2",
              "cereal 1",
              "chair 1",
              "chair 2",
              "chair 3",
              "chair 4",
              "chair 5",
              "chair 6",
              "chips 1",
              "chips 2",
              "chocolate syrup 1",
              "closet 1",
              "closet drawer 1",
              "closet drawer 2",
              "closet drawer 3",
              "closet drawer 4",
              "closet drawer 5",
              "closet drawer 6",
              "closet drawer 7",
              "coffee maker 1",
              "coffee pot 1",
              "coffee table 1",
              "computer 1",
              "condiment bottle 1",
              "condiment bottle 2",
              "condiment bottle 3",
              "condiment bottle 4",
              "condiment shaker 1",
              "condiment shaker 2",
              "condiment shaker 3",
              "condiment shaker 4",
              "cooking pot 1",
              "cooking pot 2",
              "cpu screen 1",
              "crackers 1",
              "crackers 2",
              "creamy buns 1",
              "cupcake 1",
              "cupcake 2",
              "cupcake 3",
              "curtains 1",
              "curtains 2",
              "curtains 3",
              "curtains 4",
              "curtains 5",
              "curtains 6",
              "curtains 7",
              "cutlery fork 1",
              "cutlery fork 2",
              "cutlery fork 3",
              "cutlery fork 4",
              "cutlery knife 1",
              "cutlery knife 2",
              "cutlery knife 3",
              "cutlery knife 4",
              "cutlery knife 5",
              "cutlery knife 6",
              "cutlets 1",
              "deodorant 1",
              "deodorant 2",
              "deodorant 3",
              "desk 1",
              "desk 2",
              "dishwasher 1",
              "dishwashing liquid 1",
              "door 1",
              "door 2",
              "door 3",
              "door jamb 1",
              "door jamb 2",
              "door jamb 3",
              "door jamb 4",
              "face cream 1",
              "face cream 2",
              "face cream 3",
              "faucet 1",
              "faucet 2",
              "floor 1",
              "floor 10",
              "floor 11",
              "floor 12",
              "floor 13",
              "floor 14",
              "floor 15",
              "floor 16",
              "floor 17",
              "floor 18",
              "floor 19",
              "floor 2",
              "floor 20",
              "floor 21",
              "floor 22",
              "floor 23",
              "floor 24",
              "floor 25",
              "floor 26",
              "floor 3",
              "floor 4",
              "floor 5",
              "floor 6",
              "floor 7",
              "floor 8",
              "floor 9",
              "folder 1",
              "folder 2",
              "folder 3",
              "folder 4",
              "fridge 1",
              "frying pan 1",
              "hair product 1",
              "hair product 2",
              "hair product 3",
              "hair product 4",
              "hanger 1",
              "hanger 2",
              "hanger 3",
              "hanger 4",
              "hanger 5",
              "hanger 6",
              "hanger 7",
              "juice 1",
              "juice 2",
              "keyboard 1",
              "kitchen 1",
              "kitchen cabinet 1",
              "kitchen cabinet 2",
              "kitchen cabinet 3",
              "kitchen cabinet 4",
              "kitchen cabinet 5",
              "kitchen cabinet 6",
              "kitchen cabinet 7",
              "kitchen cabinet 8",
              "kitchen counter 1",
              "kitchen counter 2",
              "kitchen counter 3",
              "kitchen counter drawer 1",
              "kitchen counter drawer 2",
              "kitchen counter drawer 3",
              "kitchen counter drawer 4",
              "kitchen counter drawer 5",
              "kitchen counter drawer 6",
              "kitchen counter drawer 7",
              "kitchen counter drawer 8",
              "kitchen table 1",
              "knife block 1",
              "light switch 1",
              "light switch 2",
              "light switch 3",
              "light switch 4",
              "lime 1",
              "living room 1",
              "microwave oven 1",
              "milk 1",
              "mouse 1",
              "mouse mat 1",
              "mug 1",
              "mug 2",
              "mug 3",
              "nightstand 1",
              "nightstand 2",
              "nightstand 3",
              "nightstand 4",
              "notes 1",
              "orchid 1",
              "oven tray 1",
              "painkillers 1",
              "pancake 1",
              "peach 1",
              "peach 2",
              "peach 3",
              "pear 1",
              "perfume 1",
              "perfume 2",
              "photo frame 1",
              "photo frame 2",
              "photo frame 3",
              "pile of clothes 1",
              "pile of clothes 2",
              "pillow 1",
              "pillow 2",
              "pillow 3",
              "pillow 4",
              "pillow 5",
              "pillow 6",
              "plate 1",
              "plate 2",
              "plate 3",
              "plate 4",
              "plate 5",
              "plate 6",
              "plate 7",
              "plum 1",
              "plum 2",
              "power socket 1",
              "power socket 2",
              "power socket 3",
              "pudding 1",
              "pudding 2",
              "radio 1",
              "rug 1",
              "rug 2",
              "rug 3",
              "rug 4",
              "sink 1",
              "sink 2",
              "slice of bread 1",
              "slice of bread 2",
              "sofa 1",
              "sofa 2",
              "sofa 3",
              "stall 1",
              "stall 2",
              "stove 1",
              "stove fan 1",
              "table lamp 1",
              "toaster 1",
              "toilet 1",
              "toilet paper 1",
              "toothbrush 1",
              "toothpaste 1",
              "tv 1",
              "tv stand 1",
              "wall 1",
              "wall 10",
              "wall 11",
              "wall 12",
              "wall 13",
              "wall 14",
              "wall 15",
              "wall 16",
              "wall 17",
              "wall 18",
              "wall 19",
              "wall 2",
              "wall 20",
              "wall 21",
              "wall 22",
              "wall 23",
              "wall 24",
              "wall 25",
              "wall 26",
              "wall 3",
              "wall 4",
              "wall 5",
              "wall 6",
              "wall 7",
              "wall 8",
              "wall 9",
              "wall lamp 1",
              "wall lamp 2",
              "wall lamp 3",
              "wall lamp 4",
              "wall lamp 5",
              "wall lamp 6",
              "wall lamp 7",
              "wall lamp 8",
              "wall lamp 9",
              "wall phone 1",
              "wall picture frame 1",
              "wall picture frame 2",
              "wall picture frame 3",
              "wall picture frame 4",
              "wall picture frame 5",
              "wall picture frame 6",
              "wall picture frame 7",
              "wall picture frame 8",
              "wall shelf 1",
              "wall shelf 2",
              "washing machine 1",
              "washing sponge 1",
              "water glass 1",
              "water glass 2",
              "water glass 3",
              "water glass 4",
              "water glass 5",
              "window 1",
              "window 2",
              "wine 1"
            ]
          },
          "evaluation_context": {},
          "external_goal": {
            "has_external_goal": true,
            "external_goal_state": {},
            "external_goal_text": "",
            "structured_goal_state": {},
            "structured_final_state": {
              "on_cupcake_coffeetable": 1,
              "on_apple_coffeetable": 1
            }
          },
          "benchmark_final_state_compare": {
            "benchmark": "ReAcTree-WAH",
            "status": "prepared_for_framework_llm_judge",
            "environment_format": "WAH runtime_initial_environment 的 scene/env_state，保留 WAH/VirtualHome 对象标签",
            "action_format": "WAH/ReAcTree 原生动作 JSON 对象：{action, target}",
            "official_evaluator": "ReAcTree WAH 官方 Unity evaluator",
            "used_fields": {
              "task_context": [
                "available_entities",
                "dataset",
                "env_id",
                "environment_source",
                "init_graph_cache_path",
                "init_room",
                "instruction",
                "task_goal",
                "task_name",
                "task_source"
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
                "dataset": "reactree",
                "env_id": 3,
                "task_name": "prepare_snack",
                "instruction": "Put one cupcake and one apple on the coffee table",
                "init_room": "bedroom",
                "task_source": "reactree_wah_testset",
                "environment_source": "reactree_case_runtime_scene",
                "init_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json",
                "task_goal": {
                  "on_cupcake_coffeetable": 1,
                  "on_apple_coffeetable": 1
                },
                "available_entities": [
                  "apple 1",
                  "apple 2",
                  "apple 3",
                  "bananas 1",
                  "bar soap 1",
                  "bathroom 1",
                  "bathroom cabinet 1",
                  "bathroom counter 1",
                  "bed 1",
                  "bedroom 1",
                  "book 1",
                  "book 2",
                  "bookshelf 1",
                  "bookshelf 2",
                  "bookshelf 3",
                  "bowl 1",
                  "bowl 2",
                  "bowl 3",
                  "bowl 4",
                  "bowl 5",
                  "bowl 6",
                  "bowl 7",
                  "bowl 8",
                  "bowl 9",
                  "box 1",
                  "box 2",
                  "box 3",
                  "box 4",
                  "box 5",
                  "bucket 1",
                  "cabinet 1",
                  "candle 1",
                  "candy bar 1",
                  "ceiling 1",
                  "ceiling 10",
                  "ceiling 11",
                  "ceiling 12",
                  "ceiling 13",
                  "ceiling 14",
                  "ceiling 15",
                  {
                    "_truncated": 303
                  }
                ]
              },
              "evaluation_context": {},
              "goal_projection": {},
              "external_goal": {
                "has_external_goal": true,
                "external_goal_state": {},
                "external_goal_text": "",
                "structured_goal_state": {},
                "structured_final_state": {
                  "on_cupcake_coffeetable": 1,
                  "on_apple_coffeetable": 1
                }
              }
            },
            "understanding_final_state": {
              "on_cupcake_coffeetable": 1,
              "on_apple_coffeetable": 1
            },
            "state_diff_summary": {
              "entity_count_compared": 17,
              "changed_entity_count": 2,
              "changed_entities": [
                "apple 2",
                "cupcake 1"
              ],
              "changed_entities_truncated": false,
              "robot_changed": true,
              "robot_change": {
                "changed": true,
                "before": {
                  "robot_location": "bedroom 1",
                  "robot_holding": "空"
                },
                "after": {
                  "robot_location": "coffee table 1",
                  "robot_holding": "空"
                }
              }
            },
            "initial_environment_summary": {
              "available": true,
              "entity_count": 17,
              "type_counts": {
                "unknown": 7,
                "room": 3,
                "receptacle": 7
              },
              "states_sample": {
                "cabinet 1": {
                  "isOpen": false
                },
                "fridge 1": {
                  "isOpen": false
                }
              },
              "relations_sample": {
                "cupcake 1": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "kitchen 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 2": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "kitchen table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 2"
                },
                "cupcake 2": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "cupcake 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "bedroom 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 16": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom 1"
                },
                "cabinet 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 16"
                },
                "apple 1": {
                  "direct_relation": "inside",
                  "direct_parent": "fridge 1"
                },
                "floor 4": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "fridge 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 4"
                },
                "apple 2": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "apple 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "coffee table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 25"
                },
                "living room 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 25": {
                  "direct_relation": "inside",
                  "direct_parent": "living room 1"
                }
              }
            },
            "final_environment_summary": {
              "available": true,
              "entity_count": 17,
              "type_counts": {
                "unknown": 7,
                "room": 3,
                "receptacle": 7
              },
              "states_sample": {
                "cabinet 1": {
                  "isOpen": false
                },
                "fridge 1": {
                  "isOpen": false
                }
              },
              "relations_sample": {
                "cupcake 1": {
                  "direct_relation": "on",
                  "direct_parent": "coffee table 1"
                },
                "kitchen 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 2": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "kitchen table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 2"
                },
                "cupcake 2": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "cupcake 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "bedroom 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 16": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom 1"
                },
                "cabinet 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 16"
                },
                "apple 1": {
                  "direct_relation": "inside",
                  "direct_parent": "fridge 1"
                },
                "floor 4": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "fridge 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 4"
                },
                "apple 2": {
                  "direct_relation": "on",
                  "direct_parent": "coffee table 1"
                },
                "apple 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "coffee table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 25"
                },
                "living room 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 25": {
                  "direct_relation": "inside",
                  "direct_parent": "living room 1"
                }
              }
            },
            "initial_robot": {
              "robot_location": "bedroom 1",
              "robot_holding": "空"
            },
            "final_robot": {
              "robot_location": "coffee table 1",
              "robot_holding": "空"
            },
            "fairness_notes": [
              "task_goal 来自 WAH 官方评测目标，只作为最终态审计目标投影，不作为动作序列答案。"
            ],
            "judge_contract": "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。",
            "enabled": true,
            "comparer_module": "benchmark.reactree.wah.framework.code.final_state"
          }
        },
        "llm_result": {
          "is_passed": true,
          "issue": "",
          "fix_advice": "",
          "repair_mode": "continue_from_current",
          "accepted_diffs": [
            "cupcake 1 moved to coffee table 1",
            "apple 2 moved to coffee table 1"
          ],
          "unexpected_diffs": []
        },
        "benchmark_final_state_compare": {
          "benchmark": "ReAcTree-WAH",
          "status": "prepared_for_framework_llm_judge",
          "environment_format": "WAH runtime_initial_environment 的 scene/env_state，保留 WAH/VirtualHome 对象标签",
          "action_format": "WAH/ReAcTree 原生动作 JSON 对象：{action, target}",
          "official_evaluator": "ReAcTree WAH 官方 Unity evaluator",
          "used_fields": {
            "task_context": [
              "available_entities",
              "dataset",
              "env_id",
              "environment_source",
              "init_graph_cache_path",
              "init_room",
              "instruction",
              "task_goal",
              "task_name",
              "task_source"
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
              "dataset": "reactree",
              "env_id": 3,
              "task_name": "prepare_snack",
              "instruction": "Put one cupcake and one apple on the coffee table",
              "init_room": "bedroom",
              "task_source": "reactree_wah_testset",
              "environment_source": "reactree_case_runtime_scene",
              "init_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json",
              "task_goal": {
                "on_cupcake_coffeetable": 1,
                "on_apple_coffeetable": 1
              },
              "available_entities": [
                "apple 1",
                "apple 2",
                "apple 3",
                "bananas 1",
                "bar soap 1",
                "bathroom 1",
                "bathroom cabinet 1",
                "bathroom counter 1",
                "bed 1",
                "bedroom 1",
                "book 1",
                "book 2",
                "bookshelf 1",
                "bookshelf 2",
                "bookshelf 3",
                "bowl 1",
                "bowl 2",
                "bowl 3",
                "bowl 4",
                "bowl 5",
                "bowl 6",
                "bowl 7",
                "bowl 8",
                "bowl 9",
                "box 1",
                "box 2",
                "box 3",
                "box 4",
                "box 5",
                "bucket 1",
                "cabinet 1",
                "candle 1",
                "candy bar 1",
                "ceiling 1",
                "ceiling 10",
                "ceiling 11",
                "ceiling 12",
                "ceiling 13",
                "ceiling 14",
                "ceiling 15",
                {
                  "_truncated": 303
                }
              ]
            },
            "evaluation_context": {},
            "goal_projection": {},
            "external_goal": {
              "has_external_goal": true,
              "external_goal_state": {},
              "external_goal_text": "",
              "structured_goal_state": {},
              "structured_final_state": {
                "on_cupcake_coffeetable": 1,
                "on_apple_coffeetable": 1
              }
            }
          },
          "understanding_final_state": {
            "on_cupcake_coffeetable": 1,
            "on_apple_coffeetable": 1
          },
          "state_diff_summary": {
            "entity_count_compared": 17,
            "changed_entity_count": 2,
            "changed_entities": [
              "apple 2",
              "cupcake 1"
            ],
            "changed_entities_truncated": false,
            "robot_changed": true,
            "robot_change": {
              "changed": true,
              "before": {
                "robot_location": "bedroom 1",
                "robot_holding": "空"
              },
              "after": {
                "robot_location": "coffee table 1",
                "robot_holding": "空"
              }
            }
          },
          "initial_environment_summary": {
            "available": true,
            "entity_count": 17,
            "type_counts": {
              "unknown": 7,
              "room": 3,
              "receptacle": 7
            },
            "states_sample": {
              "cabinet 1": {
                "isOpen": false
              },
              "fridge 1": {
                "isOpen": false
              }
            },
            "relations_sample": {
              "cupcake 1": {
                "direct_relation": "on",
                "direct_parent": "kitchen table 1"
              },
              "kitchen 1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "floor 2": {
                "direct_relation": "inside",
                "direct_parent": "kitchen 1"
              },
              "kitchen table 1": {
                "direct_relation": "on",
                "direct_parent": "floor 2"
              },
              "cupcake 2": {
                "direct_relation": "on",
                "direct_parent": "kitchen table 1"
              },
              "cupcake 3": {
                "direct_relation": "inside",
                "direct_parent": "cabinet 1"
              },
              "bedroom 1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "floor 16": {
                "direct_relation": "inside",
                "direct_parent": "bedroom 1"
              },
              "cabinet 1": {
                "direct_relation": "on",
                "direct_parent": "floor 16"
              },
              "apple 1": {
                "direct_relation": "inside",
                "direct_parent": "fridge 1"
              },
              "floor 4": {
                "direct_relation": "inside",
                "direct_parent": "kitchen 1"
              },
              "fridge 1": {
                "direct_relation": "on",
                "direct_parent": "floor 4"
              },
              "apple 2": {
                "direct_relation": "on",
                "direct_parent": "kitchen table 1"
              },
              "apple 3": {
                "direct_relation": "inside",
                "direct_parent": "cabinet 1"
              },
              "coffee table 1": {
                "direct_relation": "on",
                "direct_parent": "floor 25"
              },
              "living room 1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "floor 25": {
                "direct_relation": "inside",
                "direct_parent": "living room 1"
              }
            }
          },
          "final_environment_summary": {
            "available": true,
            "entity_count": 17,
            "type_counts": {
              "unknown": 7,
              "room": 3,
              "receptacle": 7
            },
            "states_sample": {
              "cabinet 1": {
                "isOpen": false
              },
              "fridge 1": {
                "isOpen": false
              }
            },
            "relations_sample": {
              "cupcake 1": {
                "direct_relation": "on",
                "direct_parent": "coffee table 1"
              },
              "kitchen 1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "floor 2": {
                "direct_relation": "inside",
                "direct_parent": "kitchen 1"
              },
              "kitchen table 1": {
                "direct_relation": "on",
                "direct_parent": "floor 2"
              },
              "cupcake 2": {
                "direct_relation": "on",
                "direct_parent": "kitchen table 1"
              },
              "cupcake 3": {
                "direct_relation": "inside",
                "direct_parent": "cabinet 1"
              },
              "bedroom 1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "floor 16": {
                "direct_relation": "inside",
                "direct_parent": "bedroom 1"
              },
              "cabinet 1": {
                "direct_relation": "on",
                "direct_parent": "floor 16"
              },
              "apple 1": {
                "direct_relation": "inside",
                "direct_parent": "fridge 1"
              },
              "floor 4": {
                "direct_relation": "inside",
                "direct_parent": "kitchen 1"
              },
              "fridge 1": {
                "direct_relation": "on",
                "direct_parent": "floor 4"
              },
              "apple 2": {
                "direct_relation": "on",
                "direct_parent": "coffee table 1"
              },
              "apple 3": {
                "direct_relation": "inside",
                "direct_parent": "cabinet 1"
              },
              "coffee table 1": {
                "direct_relation": "on",
                "direct_parent": "floor 25"
              },
              "living room 1": {
                "direct_relation": "",
                "direct_parent": "未知环境"
              },
              "floor 25": {
                "direct_relation": "inside",
                "direct_parent": "living room 1"
              }
            }
          },
          "initial_robot": {
            "robot_location": "bedroom 1",
            "robot_holding": "空"
          },
          "final_robot": {
            "robot_location": "coffee table 1",
            "robot_holding": "空"
          },
          "fairness_notes": [
            "task_goal 来自 WAH 官方评测目标，只作为最终态审计目标投影，不作为动作序列答案。"
          ],
          "judge_contract": "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。",
          "enabled": true,
          "comparer_module": "benchmark.reactree.wah.framework.code.final_state"
        },
        "has_external_goal": true,
        "final_state_packet": {
          "task_source_text": "",
          "task_context": {
            "dataset": "reactree",
            "env_id": 3,
            "task_name": "prepare_snack",
            "instruction": "Put one cupcake and one apple on the coffee table",
            "init_room": "bedroom",
            "task_source": "reactree_wah_testset",
            "environment_source": "reactree_case_runtime_scene",
            "init_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json",
            "task_goal": {
              "on_cupcake_coffeetable": 1,
              "on_apple_coffeetable": 1
            },
            "available_entities": [
              "apple 1",
              "apple 2",
              "apple 3",
              "bananas 1",
              "bar soap 1",
              "bathroom 1",
              "bathroom cabinet 1",
              "bathroom counter 1",
              "bed 1",
              "bedroom 1",
              "book 1",
              "book 2",
              "bookshelf 1",
              "bookshelf 2",
              "bookshelf 3",
              "bowl 1",
              "bowl 2",
              "bowl 3",
              "bowl 4",
              "bowl 5",
              "bowl 6",
              "bowl 7",
              "bowl 8",
              "bowl 9",
              "box 1",
              "box 2",
              "box 3",
              "box 4",
              "box 5",
              "bucket 1",
              "cabinet 1",
              "candle 1",
              "candy bar 1",
              "ceiling 1",
              "ceiling 10",
              "ceiling 11",
              "ceiling 12",
              "ceiling 13",
              "ceiling 14",
              "ceiling 15",
              "ceiling 16",
              "ceiling 17",
              "ceiling 18",
              "ceiling 19",
              "ceiling 2",
              "ceiling 20",
              "ceiling 21",
              "ceiling 22",
              "ceiling 23",
              "ceiling 24",
              "ceiling 25",
              "ceiling 26",
              "ceiling 3",
              "ceiling 4",
              "ceiling 5",
              "ceiling 6",
              "ceiling 7",
              "ceiling 8",
              "ceiling 9",
              "ceiling lamp 1",
              "ceiling lamp 2",
              "ceiling lamp 3",
              "ceiling lamp 4",
              "ceiling lamp 5",
              "cell phone 1",
              "cell phone 2",
              "cereal 1",
              "chair 1",
              "chair 2",
              "chair 3",
              "chair 4",
              "chair 5",
              "chair 6",
              "chips 1",
              "chips 2",
              "chocolate syrup 1",
              "closet 1",
              "closet drawer 1",
              "closet drawer 2",
              "closet drawer 3",
              "closet drawer 4",
              "closet drawer 5",
              "closet drawer 6",
              "closet drawer 7",
              "coffee maker 1",
              "coffee pot 1",
              "coffee table 1",
              "computer 1",
              "condiment bottle 1",
              "condiment bottle 2",
              "condiment bottle 3",
              "condiment bottle 4",
              "condiment shaker 1",
              "condiment shaker 2",
              "condiment shaker 3",
              "condiment shaker 4",
              "cooking pot 1",
              "cooking pot 2",
              "cpu screen 1",
              "crackers 1",
              "crackers 2",
              "creamy buns 1",
              "cupcake 1",
              "cupcake 2",
              "cupcake 3",
              "curtains 1",
              "curtains 2",
              "curtains 3",
              "curtains 4",
              "curtains 5",
              "curtains 6",
              "curtains 7",
              "cutlery fork 1",
              "cutlery fork 2",
              "cutlery fork 3",
              "cutlery fork 4",
              "cutlery knife 1",
              "cutlery knife 2",
              "cutlery knife 3",
              "cutlery knife 4",
              "cutlery knife 5",
              "cutlery knife 6",
              "cutlets 1",
              "deodorant 1",
              "deodorant 2",
              "deodorant 3",
              "desk 1",
              "desk 2",
              "dishwasher 1",
              "dishwashing liquid 1",
              "door 1",
              "door 2",
              "door 3",
              "door jamb 1",
              "door jamb 2",
              "door jamb 3",
              "door jamb 4",
              "face cream 1",
              "face cream 2",
              "face cream 3",
              "faucet 1",
              "faucet 2",
              "floor 1",
              "floor 10",
              "floor 11",
              "floor 12",
              "floor 13",
              "floor 14",
              "floor 15",
              "floor 16",
              "floor 17",
              "floor 18",
              "floor 19",
              "floor 2",
              "floor 20",
              "floor 21",
              "floor 22",
              "floor 23",
              "floor 24",
              "floor 25",
              "floor 26",
              "floor 3",
              "floor 4",
              "floor 5",
              "floor 6",
              "floor 7",
              "floor 8",
              "floor 9",
              "folder 1",
              "folder 2",
              "folder 3",
              "folder 4",
              "fridge 1",
              "frying pan 1",
              "hair product 1",
              "hair product 2",
              "hair product 3",
              "hair product 4",
              "hanger 1",
              "hanger 2",
              "hanger 3",
              "hanger 4",
              "hanger 5",
              "hanger 6",
              "hanger 7",
              "juice 1",
              "juice 2",
              "keyboard 1",
              "kitchen 1",
              "kitchen cabinet 1",
              "kitchen cabinet 2",
              "kitchen cabinet 3",
              "kitchen cabinet 4",
              "kitchen cabinet 5",
              "kitchen cabinet 6",
              "kitchen cabinet 7",
              "kitchen cabinet 8",
              "kitchen counter 1",
              "kitchen counter 2",
              "kitchen counter 3",
              "kitchen counter drawer 1",
              "kitchen counter drawer 2",
              "kitchen counter drawer 3",
              "kitchen counter drawer 4",
              "kitchen counter drawer 5",
              "kitchen counter drawer 6",
              "kitchen counter drawer 7",
              "kitchen counter drawer 8",
              "kitchen table 1",
              "knife block 1",
              "light switch 1",
              "light switch 2",
              "light switch 3",
              "light switch 4",
              "lime 1",
              "living room 1",
              "microwave oven 1",
              "milk 1",
              "mouse 1",
              "mouse mat 1",
              "mug 1",
              "mug 2",
              "mug 3",
              "nightstand 1",
              "nightstand 2",
              "nightstand 3",
              "nightstand 4",
              "notes 1",
              "orchid 1",
              "oven tray 1",
              "painkillers 1",
              "pancake 1",
              "peach 1",
              "peach 2",
              "peach 3",
              "pear 1",
              "perfume 1",
              "perfume 2",
              "photo frame 1",
              "photo frame 2",
              "photo frame 3",
              "pile of clothes 1",
              "pile of clothes 2",
              "pillow 1",
              "pillow 2",
              "pillow 3",
              "pillow 4",
              "pillow 5",
              "pillow 6",
              "plate 1",
              "plate 2",
              "plate 3",
              "plate 4",
              "plate 5",
              "plate 6",
              "plate 7",
              "plum 1",
              "plum 2",
              "power socket 1",
              "power socket 2",
              "power socket 3",
              "pudding 1",
              "pudding 2",
              "radio 1",
              "rug 1",
              "rug 2",
              "rug 3",
              "rug 4",
              "sink 1",
              "sink 2",
              "slice of bread 1",
              "slice of bread 2",
              "sofa 1",
              "sofa 2",
              "sofa 3",
              "stall 1",
              "stall 2",
              "stove 1",
              "stove fan 1",
              "table lamp 1",
              "toaster 1",
              "toilet 1",
              "toilet paper 1",
              "toothbrush 1",
              "toothpaste 1",
              "tv 1",
              "tv stand 1",
              "wall 1",
              "wall 10",
              "wall 11",
              "wall 12",
              "wall 13",
              "wall 14",
              "wall 15",
              "wall 16",
              "wall 17",
              "wall 18",
              "wall 19",
              "wall 2",
              "wall 20",
              "wall 21",
              "wall 22",
              "wall 23",
              "wall 24",
              "wall 25",
              "wall 26",
              "wall 3",
              "wall 4",
              "wall 5",
              "wall 6",
              "wall 7",
              "wall 8",
              "wall 9",
              "wall lamp 1",
              "wall lamp 2",
              "wall lamp 3",
              "wall lamp 4",
              "wall lamp 5",
              "wall lamp 6",
              "wall lamp 7",
              "wall lamp 8",
              "wall lamp 9",
              "wall phone 1",
              "wall picture frame 1",
              "wall picture frame 2",
              "wall picture frame 3",
              "wall picture frame 4",
              "wall picture frame 5",
              "wall picture frame 6",
              "wall picture frame 7",
              "wall picture frame 8",
              "wall shelf 1",
              "wall shelf 2",
              "washing machine 1",
              "washing sponge 1",
              "water glass 1",
              "water glass 2",
              "water glass 3",
              "water glass 4",
              "water glass 5",
              "window 1",
              "window 2",
              "wine 1"
            ]
          },
          "evaluation_context": {},
          "external_goal": {
            "has_external_goal": true,
            "external_goal_state": {},
            "external_goal_text": "",
            "structured_goal_state": {},
            "structured_final_state": {
              "on_cupcake_coffeetable": 1,
              "on_apple_coffeetable": 1
            }
          },
          "initial": {
            "environment": {
              "cupcake 1": {
                "direct_parent": "kitchen table 1",
                "direct_relation": "on",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "EATABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ]
              },
              "kitchen 1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "floor 2": {
                "direct_parent": "kitchen 1",
                "direct_relation": "inside",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "SURFACES"
                ],
                "is_container": true,
                "full_path": [
                  "kitchen 1"
                ]
              },
              "kitchen table 1": {
                "direct_parent": "floor 2",
                "direct_relation": "on",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "SURFACES",
                  "MOVABLE"
                ],
                "is_container": true,
                "full_path": [
                  "kitchen 1",
                  "floor 2"
                ]
              },
              "cupcake 2": {
                "direct_parent": "kitchen table 1",
                "direct_relation": "on",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "EATABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ]
              },
              "cupcake 3": {
                "direct_parent": "cabinet 1",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "EATABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "bedroom 1",
                  "floor 16",
                  "cabinet 1"
                ]
              },
              "bedroom 1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "floor 16": {
                "direct_parent": "bedroom 1",
                "direct_relation": "inside",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "SURFACES"
                ],
                "is_container": true,
                "full_path": [
                  "bedroom 1"
                ]
              },
              "cabinet 1": {
                "direct_parent": "floor 16",
                "direct_relation": "on",
                "type": "receptacle",
                "states": {
                  "isOpen": false
                },
                "properties": [
                  "SURFACES",
                  "CAN_OPEN",
                  "CONTAINERS"
                ],
                "is_container": true,
                "full_path": [
                  "bedroom 1",
                  "floor 16"
                ]
              },
              "apple 1": {
                "direct_parent": "fridge 1",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 4",
                  "fridge 1"
                ]
              },
              "floor 4": {
                "direct_parent": "kitchen 1",
                "direct_relation": "inside",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "SURFACES"
                ],
                "is_container": true,
                "full_path": [
                  "kitchen 1"
                ]
              },
              "fridge 1": {
                "direct_parent": "floor 4",
                "direct_relation": "on",
                "type": "receptacle",
                "states": {
                  "isOpen": false
                },
                "properties": [
                  "CAN_OPEN",
                  "HAS_SWITCH",
                  "CONTAINERS",
                  "HAS_PLUG"
                ],
                "is_container": true,
                "full_path": [
                  "kitchen 1",
                  "floor 4"
                ]
              },
              "apple 2": {
                "direct_parent": "kitchen table 1",
                "direct_relation": "on",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ]
              },
              "apple 3": {
                "direct_parent": "cabinet 1",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "bedroom 1",
                  "floor 16",
                  "cabinet 1"
                ]
              },
              "coffee table 1": {
                "direct_parent": "floor 25",
                "direct_relation": "on",
                "type": null,
                "states": {},
                "properties": [
                  "SURFACES",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "living room 1",
                  "floor 25"
                ]
              },
              "living room 1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "floor 25": {
                "direct_parent": "living room 1",
                "direct_relation": "inside",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "SURFACES"
                ],
                "is_container": true,
                "full_path": [
                  "living room 1"
                ]
              }
            },
            "robot": {
              "robot_location": "bedroom 1",
              "robot_holding": "空"
            }
          },
          "final": {
            "environment": {
              "cupcake 1": {
                "direct_parent": "coffee table 1",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "EATABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ],
                "direct_relation": "on"
              },
              "kitchen 1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "floor 2": {
                "direct_parent": "kitchen 1",
                "direct_relation": "inside",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "SURFACES"
                ],
                "is_container": true,
                "full_path": [
                  "kitchen 1"
                ]
              },
              "kitchen table 1": {
                "direct_parent": "floor 2",
                "direct_relation": "on",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "SURFACES",
                  "MOVABLE"
                ],
                "is_container": true,
                "full_path": [
                  "kitchen 1",
                  "floor 2"
                ]
              },
              "cupcake 2": {
                "direct_parent": "kitchen table 1",
                "direct_relation": "on",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "EATABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ]
              },
              "cupcake 3": {
                "direct_parent": "cabinet 1",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "EATABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "bedroom 1",
                  "floor 16",
                  "cabinet 1"
                ]
              },
              "bedroom 1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "floor 16": {
                "direct_parent": "bedroom 1",
                "direct_relation": "inside",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "SURFACES"
                ],
                "is_container": true,
                "full_path": [
                  "bedroom 1"
                ]
              },
              "cabinet 1": {
                "direct_parent": "floor 16",
                "direct_relation": "on",
                "type": "receptacle",
                "states": {
                  "isOpen": false
                },
                "properties": [
                  "SURFACES",
                  "CAN_OPEN",
                  "CONTAINERS"
                ],
                "is_container": true,
                "full_path": [
                  "bedroom 1",
                  "floor 16"
                ]
              },
              "apple 1": {
                "direct_parent": "fridge 1",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 4",
                  "fridge 1"
                ]
              },
              "floor 4": {
                "direct_parent": "kitchen 1",
                "direct_relation": "inside",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "SURFACES"
                ],
                "is_container": true,
                "full_path": [
                  "kitchen 1"
                ]
              },
              "fridge 1": {
                "direct_parent": "floor 4",
                "direct_relation": "on",
                "type": "receptacle",
                "states": {
                  "isOpen": false
                },
                "properties": [
                  "CAN_OPEN",
                  "HAS_SWITCH",
                  "CONTAINERS",
                  "HAS_PLUG"
                ],
                "is_container": true,
                "full_path": [
                  "kitchen 1",
                  "floor 4"
                ]
              },
              "apple 2": {
                "direct_parent": "coffee table 1",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ],
                "direct_relation": "on"
              },
              "apple 3": {
                "direct_parent": "cabinet 1",
                "direct_relation": "inside",
                "type": null,
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "bedroom 1",
                  "floor 16",
                  "cabinet 1"
                ]
              },
              "coffee table 1": {
                "direct_parent": "floor 25",
                "direct_relation": "on",
                "type": null,
                "states": {},
                "properties": [
                  "SURFACES",
                  "MOVABLE"
                ],
                "is_container": false,
                "full_path": [
                  "living room 1",
                  "floor 25"
                ]
              },
              "living room 1": {
                "direct_parent": "未知环境",
                "direct_relation": null,
                "type": "room",
                "states": {},
                "properties": [],
                "is_container": false,
                "full_path": []
              },
              "floor 25": {
                "direct_parent": "living room 1",
                "direct_relation": "inside",
                "type": "receptacle",
                "states": {},
                "properties": [
                  "SURFACES"
                ],
                "is_container": true,
                "full_path": [
                  "living room 1"
                ]
              }
            },
            "robot": {
              "robot_location": "coffee table 1",
              "robot_holding": "空"
            }
          },
          "state_diff": {
            "entity_count_compared": 17,
            "changed_entity_count": 2,
            "truncated_entity_count": 0,
            "has_changes": true,
            "robot": {
              "changed": true,
              "before": {
                "robot_location": "bedroom 1",
                "robot_holding": "空"
              },
              "after": {
                "robot_location": "coffee table 1",
                "robot_holding": "空"
              }
            },
            "entities": [
              {
                "name": "apple 2",
                "change_type": "updated",
                "before": {
                  "type": null,
                  "direct_parent": "kitchen table 1",
                  "direct_relation": "on",
                  "is_container": false,
                  "full_path": [
                    "kitchen 1",
                    "floor 2",
                    "kitchen table 1"
                  ],
                  "states": {},
                  "properties": [
                    "GRABBABLE",
                    "MOVABLE"
                  ]
                },
                "after": {
                  "type": null,
                  "direct_parent": "coffee table 1",
                  "direct_relation": "on",
                  "is_container": false,
                  "full_path": [
                    "kitchen 1",
                    "floor 2",
                    "kitchen table 1"
                  ],
                  "states": {},
                  "properties": [
                    "GRABBABLE",
                    "MOVABLE"
                  ]
                }
              },
              {
                "name": "cupcake 1",
                "change_type": "updated",
                "before": {
                  "type": null,
                  "direct_parent": "kitchen table 1",
                  "direct_relation": "on",
                  "is_container": false,
                  "full_path": [
                    "kitchen 1",
                    "floor 2",
                    "kitchen table 1"
                  ],
                  "states": {},
                  "properties": [
                    "GRABBABLE",
                    "EATABLE",
                    "MOVABLE"
                  ]
                },
                "after": {
                  "type": null,
                  "direct_parent": "coffee table 1",
                  "direct_relation": "on",
                  "is_container": false,
                  "full_path": [
                    "kitchen 1",
                    "floor 2",
                    "kitchen table 1"
                  ],
                  "states": {},
                  "properties": [
                    "GRABBABLE",
                    "EATABLE",
                    "MOVABLE"
                  ]
                }
              }
            ]
          },
          "trajectory": "Step 1: go to([])\nStep 2: pick up([])\nStep 3: go to([])\nStep 4: put down([])\nStep 5: go to([])\nStep 6: pick up([])\nStep 7: go to([])\nStep 8: put down([])",
          "benchmark_final_state_compare": {
            "benchmark": "ReAcTree-WAH",
            "status": "prepared_for_framework_llm_judge",
            "environment_format": "WAH runtime_initial_environment 的 scene/env_state，保留 WAH/VirtualHome 对象标签",
            "action_format": "WAH/ReAcTree 原生动作 JSON 对象：{action, target}",
            "official_evaluator": "ReAcTree WAH 官方 Unity evaluator",
            "used_fields": {
              "task_context": [
                "available_entities",
                "dataset",
                "env_id",
                "environment_source",
                "init_graph_cache_path",
                "init_room",
                "instruction",
                "task_goal",
                "task_name",
                "task_source"
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
                "dataset": "reactree",
                "env_id": 3,
                "task_name": "prepare_snack",
                "instruction": "Put one cupcake and one apple on the coffee table",
                "init_room": "bedroom",
                "task_source": "reactree_wah_testset",
                "environment_source": "reactree_case_runtime_scene",
                "init_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json",
                "task_goal": {
                  "on_cupcake_coffeetable": 1,
                  "on_apple_coffeetable": 1
                },
                "available_entities": [
                  "apple 1",
                  "apple 2",
                  "apple 3",
                  "bananas 1",
                  "bar soap 1",
                  "bathroom 1",
                  "bathroom cabinet 1",
                  "bathroom counter 1",
                  "bed 1",
                  "bedroom 1",
                  "book 1",
                  "book 2",
                  "bookshelf 1",
                  "bookshelf 2",
                  "bookshelf 3",
                  "bowl 1",
                  "bowl 2",
                  "bowl 3",
                  "bowl 4",
                  "bowl 5",
                  "bowl 6",
                  "bowl 7",
                  "bowl 8",
                  "bowl 9",
                  "box 1",
                  "box 2",
                  "box 3",
                  "box 4",
                  "box 5",
                  "bucket 1",
                  "cabinet 1",
                  "candle 1",
                  "candy bar 1",
                  "ceiling 1",
                  "ceiling 10",
                  "ceiling 11",
                  "ceiling 12",
                  "ceiling 13",
                  "ceiling 14",
                  "ceiling 15",
                  {
                    "_truncated": 303
                  }
                ]
              },
              "evaluation_context": {},
              "goal_projection": {},
              "external_goal": {
                "has_external_goal": true,
                "external_goal_state": {},
                "external_goal_text": "",
                "structured_goal_state": {},
                "structured_final_state": {
                  "on_cupcake_coffeetable": 1,
                  "on_apple_coffeetable": 1
                }
              }
            },
            "understanding_final_state": {
              "on_cupcake_coffeetable": 1,
              "on_apple_coffeetable": 1
            },
            "state_diff_summary": {
              "entity_count_compared": 17,
              "changed_entity_count": 2,
              "changed_entities": [
                "apple 2",
                "cupcake 1"
              ],
              "changed_entities_truncated": false,
              "robot_changed": true,
              "robot_change": {
                "changed": true,
                "before": {
                  "robot_location": "bedroom 1",
                  "robot_holding": "空"
                },
                "after": {
                  "robot_location": "coffee table 1",
                  "robot_holding": "空"
                }
              }
            },
            "initial_environment_summary": {
              "available": true,
              "entity_count": 17,
              "type_counts": {
                "unknown": 7,
                "room": 3,
                "receptacle": 7
              },
              "states_sample": {
                "cabinet 1": {
                  "isOpen": false
                },
                "fridge 1": {
                  "isOpen": false
                }
              },
              "relations_sample": {
                "cupcake 1": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "kitchen 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 2": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "kitchen table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 2"
                },
                "cupcake 2": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "cupcake 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "bedroom 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 16": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom 1"
                },
                "cabinet 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 16"
                },
                "apple 1": {
                  "direct_relation": "inside",
                  "direct_parent": "fridge 1"
                },
                "floor 4": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "fridge 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 4"
                },
                "apple 2": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "apple 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "coffee table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 25"
                },
                "living room 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 25": {
                  "direct_relation": "inside",
                  "direct_parent": "living room 1"
                }
              }
            },
            "final_environment_summary": {
              "available": true,
              "entity_count": 17,
              "type_counts": {
                "unknown": 7,
                "room": 3,
                "receptacle": 7
              },
              "states_sample": {
                "cabinet 1": {
                  "isOpen": false
                },
                "fridge 1": {
                  "isOpen": false
                }
              },
              "relations_sample": {
                "cupcake 1": {
                  "direct_relation": "on",
                  "direct_parent": "coffee table 1"
                },
                "kitchen 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 2": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "kitchen table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 2"
                },
                "cupcake 2": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "cupcake 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "bedroom 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 16": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom 1"
                },
                "cabinet 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 16"
                },
                "apple 1": {
                  "direct_relation": "inside",
                  "direct_parent": "fridge 1"
                },
                "floor 4": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "fridge 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 4"
                },
                "apple 2": {
                  "direct_relation": "on",
                  "direct_parent": "coffee table 1"
                },
                "apple 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "coffee table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 25"
                },
                "living room 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 25": {
                  "direct_relation": "inside",
                  "direct_parent": "living room 1"
                }
              }
            },
            "initial_robot": {
              "robot_location": "bedroom 1",
              "robot_holding": "空"
            },
            "final_robot": {
              "robot_location": "coffee table 1",
              "robot_holding": "空"
            },
            "fairness_notes": [
              "task_goal 来自 WAH 官方评测目标，只作为最终态审计目标投影，不作为动作序列答案。"
            ],
            "judge_contract": "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。",
            "enabled": true,
            "comparer_module": "benchmark.reactree.wah.framework.code.final_state"
          }
        },
        "state_diff": {
          "entity_count_compared": 17,
          "changed_entity_count": 2,
          "truncated_entity_count": 0,
          "has_changes": true,
          "robot": {
            "changed": true,
            "before": {
              "robot_location": "bedroom 1",
              "robot_holding": "空"
            },
            "after": {
              "robot_location": "coffee table 1",
              "robot_holding": "空"
            }
          },
          "entities": [
            {
              "name": "apple 2",
              "change_type": "updated",
              "before": {
                "type": null,
                "direct_parent": "kitchen table 1",
                "direct_relation": "on",
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ],
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "coffee table 1",
                "direct_relation": "on",
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ],
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "MOVABLE"
                ]
              }
            },
            {
              "name": "cupcake 1",
              "change_type": "updated",
              "before": {
                "type": null,
                "direct_parent": "kitchen table 1",
                "direct_relation": "on",
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ],
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "EATABLE",
                  "MOVABLE"
                ]
              },
              "after": {
                "type": null,
                "direct_parent": "coffee table 1",
                "direct_relation": "on",
                "is_container": false,
                "full_path": [
                  "kitchen 1",
                  "floor 2",
                  "kitchen table 1"
                ],
                "states": {},
                "properties": [
                  "GRABBABLE",
                  "EATABLE",
                  "MOVABLE"
                ]
              }
            }
          ]
        }
      },
      "state_diff": {
        "entity_count_compared": 17,
        "changed_entity_count": 2,
        "truncated_entity_count": 0,
        "has_changes": true,
        "robot": {
          "changed": true,
          "before": {
            "robot_location": "bedroom 1",
            "robot_holding": "空"
          },
          "after": {
            "robot_location": "coffee table 1",
            "robot_holding": "空"
          }
        },
        "entities": [
          {
            "name": "apple 2",
            "change_type": "updated",
            "before": {
              "type": null,
              "direct_parent": "kitchen table 1",
              "direct_relation": "on",
              "is_container": false,
              "full_path": [
                "kitchen 1",
                "floor 2",
                "kitchen table 1"
              ],
              "states": {},
              "properties": [
                "GRABBABLE",
                "MOVABLE"
              ]
            },
            "after": {
              "type": null,
              "direct_parent": "coffee table 1",
              "direct_relation": "on",
              "is_container": false,
              "full_path": [
                "kitchen 1",
                "floor 2",
                "kitchen table 1"
              ],
              "states": {},
              "properties": [
                "GRABBABLE",
                "MOVABLE"
              ]
            }
          },
          {
            "name": "cupcake 1",
            "change_type": "updated",
            "before": {
              "type": null,
              "direct_parent": "kitchen table 1",
              "direct_relation": "on",
              "is_container": false,
              "full_path": [
                "kitchen 1",
                "floor 2",
                "kitchen table 1"
              ],
              "states": {},
              "properties": [
                "GRABBABLE",
                "EATABLE",
                "MOVABLE"
              ]
            },
            "after": {
              "type": null,
              "direct_parent": "coffee table 1",
              "direct_relation": "on",
              "is_container": false,
              "full_path": [
                "kitchen 1",
                "floor 2",
                "kitchen table 1"
              ],
              "states": {},
              "properties": [
                "GRABBABLE",
                "EATABLE",
                "MOVABLE"
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
          "todo_step_adapter_path": "benchmark.reactree.wah.framework.code.native_actions.wah_native_step_to_skill_call",
          "validator": "todo_schema"
        },
        "inputs": {
          "todo_list": {
            "count": 8,
            "sample": [
              {
                "step": 1,
                "action": "go to",
                "target": "kitchen table 1"
              },
              {
                "step": 2,
                "action": "pick up",
                "target": "cupcake 1"
              },
              {
                "step": 3,
                "action": "go to",
                "target": "coffee table 1"
              },
              {
                "step": 4,
                "action": "put down",
                "target": "cupcake 1"
              },
              {
                "step": 5,
                "action": "go to",
                "target": "kitchen table 1"
              },
              {
                "step": 6,
                "action": "pick up",
                "target": "apple 2"
              },
              {
                "step": 7,
                "action": "go to",
                "target": "coffee table 1"
              },
              {
                "step": 8,
                "action": "put down",
                "target": "apple 2"
              }
            ],
            "truncated": false
          },
          "initial_environment": {
            "available": true,
            "entity_count": 17,
            "type_counts": {
              "unknown": 7,
              "room": 3,
              "receptacle": 7
            },
            "entities_sample": [
              "apple 1",
              "apple 2",
              "apple 3",
              "bedroom 1",
              "cabinet 1",
              "coffee table 1",
              "cupcake 1",
              "cupcake 2",
              "cupcake 3",
              "floor 16",
              "floor 2",
              "floor 25",
              "floor 4",
              "fridge 1",
              "kitchen 1",
              "kitchen table 1",
              "living room 1"
            ],
            "entities_truncated": false,
            "states_sample": {
              "cabinet 1": {
                "isOpen": false
              },
              "fridge 1": {
                "isOpen": false
              }
            }
          },
          "initial_robot": {
            "robot_location": "bedroom 1",
            "robot_holding": "空"
          }
        },
        "outputs": {
          "validated_steps": {
            "count": 0,
            "sample": [],
            "truncated": false
          },
          "validated_todo_actions": {
            "count": 8,
            "sample": [
              {
                "step": 1,
                "action": "go to",
                "target": "kitchen table 1"
              },
              {
                "step": 2,
                "action": "pick up",
                "target": "cupcake 1"
              },
              {
                "step": 3,
                "action": "go to",
                "target": "coffee table 1"
              },
              {
                "step": 4,
                "action": "put down",
                "target": "cupcake 1"
              },
              {
                "step": 5,
                "action": "go to",
                "target": "kitchen table 1"
              },
              {
                "step": 6,
                "action": "pick up",
                "target": "apple 2"
              },
              {
                "step": 7,
                "action": "go to",
                "target": "coffee table 1"
              },
              {
                "step": 8,
                "action": "put down",
                "target": "apple 2"
              }
            ],
            "truncated": false
          },
          "validated_audit_steps": {
            "count": 8,
            "sample": [
              {
                "step": 1,
                "action": "go to",
                "target": "kitchen table 1",
                "execution": {
                  "skill": "go to",
                  "parameters": {
                    "target": "kitchen table 1"
                  }
                }
              },
              {
                "step": 2,
                "action": "pick up",
                "target": "cupcake 1",
                "execution": {
                  "skill": "pick up",
                  "parameters": {
                    "target": "cupcake 1"
                  }
                }
              },
              {
                "step": 3,
                "action": "go to",
                "target": "coffee table 1",
                "execution": {
                  "skill": "go to",
                  "parameters": {
                    "target": "coffee table 1"
                  }
                }
              },
              {
                "step": 4,
                "action": "put down",
                "target": "cupcake 1",
                "execution": {
                  "skill": "put down",
                  "parameters": {
                    "target": "cupcake 1"
                  }
                }
              },
              {
                "step": 5,
                "action": "go to",
                "target": "kitchen table 1",
                "execution": {
                  "skill": "go to",
                  "parameters": {
                    "target": "kitchen table 1"
                  }
                }
              },
              {
                "step": 6,
                "action": "pick up",
                "target": "apple 2",
                "execution": {
                  "skill": "pick up",
                  "parameters": {
                    "target": "apple 2"
                  }
                }
              },
              {
                "step": 7,
                "action": "go to",
                "target": "coffee table 1",
                "execution": {
                  "skill": "go to",
                  "parameters": {
                    "target": "coffee table 1"
                  }
                }
              },
              {
                "step": 8,
                "action": "put down",
                "target": "apple 2",
                "execution": {
                  "skill": "put down",
                  "parameters": {
                    "target": "apple 2"
                  }
                }
              }
            ],
            "truncated": false
          },
          "final_environment": {
            "available": true,
            "entity_count": 17,
            "type_counts": {
              "unknown": 7,
              "room": 3,
              "receptacle": 7
            },
            "entities_sample": [
              "apple 1",
              "apple 2",
              "apple 3",
              "bedroom 1",
              "cabinet 1",
              "coffee table 1",
              "cupcake 1",
              "cupcake 2",
              "cupcake 3",
              "floor 16",
              "floor 2",
              "floor 25",
              "floor 4",
              "fridge 1",
              "kitchen 1",
              "kitchen table 1",
              "living room 1"
            ],
            "entities_truncated": false,
            "states_sample": {
              "cabinet 1": {
                "isOpen": false
              },
              "fridge 1": {
                "isOpen": false
              }
            }
          },
          "final_robot": {
            "robot_location": "coffee table 1",
            "robot_holding": "空"
          },
          "debug_event_counts": {
            "step_check": 8
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
            "count": 8,
            "sample": [
              {
                "step": 1,
                "action": "go to",
                "target": "kitchen table 1"
              },
              {
                "step": 2,
                "action": "pick up",
                "target": "cupcake 1"
              },
              {
                "step": 3,
                "action": "go to",
                "target": "coffee table 1"
              },
              {
                "step": 4,
                "action": "put down",
                "target": "cupcake 1"
              },
              {
                "step": 5,
                "action": "go to",
                "target": "kitchen table 1"
              },
              {
                "step": 6,
                "action": "pick up",
                "target": "apple 2"
              },
              {
                "step": 7,
                "action": "go to",
                "target": "coffee table 1"
              },
              {
                "step": 8,
                "action": "put down",
                "target": "apple 2"
              }
            ],
            "truncated": false
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
          "benchmark_comparer": "benchmark.reactree.wah.framework.code.final_state"
        },
        "inputs": {
          "understanding_goal": {
            "intent": "Put one cupcake and one apple on the coffee table",
            "required_item_names": {
              "targets": {
                "primary": [
                  "cupcake 1",
                  "apple 1"
                ],
                "alternatives": []
              },
              "tools": {
                "primary": [],
                "alternatives": []
              },
              "receptacles": {
                "primary": [
                  "coffee table 1"
                ],
                "alternatives": []
              }
            },
            "quantity_constraints": [
              "1 cupcake",
              "1 apple"
            ],
            "goal_state": {},
            "desired_state": {},
            "target_state": {},
            "final_state": {
              "on_cupcake_coffeetable": 1,
              "on_apple_coffeetable": 1
            }
          },
          "has_external_goal": false,
          "external_goal_state": {},
          "simulated_steps": {
            "count": 8,
            "sample": [
              {
                "step": 1,
                "action": "go to",
                "target": "kitchen table 1"
              },
              {
                "step": 2,
                "action": "pick up",
                "target": "cupcake 1"
              },
              {
                "step": 3,
                "action": "go to",
                "target": "coffee table 1"
              },
              {
                "step": 4,
                "action": "put down",
                "target": "cupcake 1"
              },
              {
                "step": 5,
                "action": "go to",
                "target": "kitchen table 1"
              },
              {
                "step": 6,
                "action": "pick up",
                "target": "apple 2"
              },
              {
                "step": 7,
                "action": "go to",
                "target": "coffee table 1"
              },
              {
                "step": 8,
                "action": "put down",
                "target": "apple 2"
              }
            ],
            "truncated": false
          },
          "initial_environment": {
            "available": true,
            "entity_count": 17,
            "type_counts": {
              "unknown": 7,
              "room": 3,
              "receptacle": 7
            },
            "entities_sample": [
              "apple 1",
              "apple 2",
              "apple 3",
              "bedroom 1",
              "cabinet 1",
              "coffee table 1",
              "cupcake 1",
              "cupcake 2",
              "cupcake 3",
              "floor 16",
              "floor 2",
              "floor 25",
              "floor 4",
              "fridge 1",
              "kitchen 1",
              "kitchen table 1",
              "living room 1"
            ],
            "entities_truncated": false,
            "states_sample": {
              "cabinet 1": {
                "isOpen": false
              },
              "fridge 1": {
                "isOpen": false
              }
            }
          },
          "initial_robot": {
            "robot_location": "bedroom 1",
            "robot_holding": "空"
          },
          "final_environment": {
            "available": true,
            "entity_count": 17,
            "type_counts": {
              "unknown": 7,
              "room": 3,
              "receptacle": 7
            },
            "entities_sample": [
              "apple 1",
              "apple 2",
              "apple 3",
              "bedroom 1",
              "cabinet 1",
              "coffee table 1",
              "cupcake 1",
              "cupcake 2",
              "cupcake 3",
              "floor 16",
              "floor 2",
              "floor 25",
              "floor 4",
              "fridge 1",
              "kitchen 1",
              "kitchen table 1",
              "living room 1"
            ],
            "entities_truncated": false,
            "states_sample": {
              "cabinet 1": {
                "isOpen": false
              },
              "fridge 1": {
                "isOpen": false
              }
            }
          },
          "final_robot": {
            "robot_location": "coffee table 1",
            "robot_holding": "空"
          }
        },
        "outputs": {
          "state_diff": {
            "available": true,
            "entity_count_compared": 17,
            "changed_entity_count": 2,
            "changed_entities_sample": [
              "apple 2",
              "cupcake 1"
            ],
            "changed_entities_truncated": false,
            "robot_changed": true
          },
          "audit_passed": true,
          "issue": "",
          "repair_mode": "continue_from_current",
          "benchmark_compare": {
            "benchmark": "ReAcTree-WAH",
            "status": "prepared_for_framework_llm_judge",
            "environment_format": "WAH runtime_initial_environment 的 scene/env_state，保留 WAH/VirtualHome 对象标签",
            "action_format": "WAH/ReAcTree 原生动作 JSON 对象：{action, target}",
            "official_evaluator": "ReAcTree WAH 官方 Unity evaluator",
            "used_fields": {
              "task_context": [
                "available_entities",
                "dataset",
                "env_id",
                "environment_source",
                "init_graph_cache_path",
                "init_room",
                "instruction",
                "task_goal",
                "task_name",
                "task_source"
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
                "dataset": "reactree",
                "env_id": 3,
                "task_name": "prepare_snack",
                "instruction": "Put one cupcake and one apple on the coffee table",
                "init_room": "bedroom",
                "task_source": "reactree_wah_testset",
                "environment_source": "reactree_case_runtime_scene",
                "init_graph_cache_path": "/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json",
                "task_goal": {
                  "on_cupcake_coffeetable": 1,
                  "on_apple_coffeetable": 1
                },
                "available_entities": [
                  "apple 1",
                  "apple 2",
                  "apple 3",
                  "bananas 1",
                  "bar soap 1",
                  "bathroom 1",
                  "bathroom cabinet 1",
                  "bathroom counter 1",
                  "bed 1",
                  "bedroom 1",
                  "book 1",
                  "book 2",
                  "bookshelf 1",
                  "bookshelf 2",
                  "bookshelf 3",
                  "bowl 1",
                  "bowl 2",
                  "bowl 3",
                  "bowl 4",
                  "bowl 5",
                  {
                    "_truncated": 21
                  }
                ]
              },
              "evaluation_context": {},
              "goal_projection": {},
              "external_goal": {
                "has_external_goal": true,
                "external_goal_state": {},
                "external_goal_text": "",
                "structured_goal_state": {},
                "structured_final_state": {
                  "on_cupcake_coffeetable": 1,
                  "on_apple_coffeetable": 1
                }
              }
            },
            "understanding_final_state": {
              "on_cupcake_coffeetable": 1,
              "on_apple_coffeetable": 1
            },
            "state_diff_summary": {
              "entity_count_compared": 17,
              "changed_entity_count": 2,
              "changed_entities": [
                "apple 2",
                "cupcake 1"
              ],
              "changed_entities_truncated": false,
              "robot_changed": true,
              "robot_change": {
                "changed": true,
                "before": {
                  "robot_location": "bedroom 1",
                  "robot_holding": "空"
                },
                "after": {
                  "robot_location": "coffee table 1",
                  "robot_holding": "空"
                }
              }
            },
            "initial_environment_summary": {
              "available": true,
              "entity_count": 17,
              "type_counts": {
                "unknown": 7,
                "room": 3,
                "receptacle": 7
              },
              "states_sample": {
                "cabinet 1": {
                  "isOpen": false
                },
                "fridge 1": {
                  "isOpen": false
                }
              },
              "relations_sample": {
                "cupcake 1": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "kitchen 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 2": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "kitchen table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 2"
                },
                "cupcake 2": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "cupcake 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "bedroom 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 16": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom 1"
                },
                "cabinet 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 16"
                },
                "apple 1": {
                  "direct_relation": "inside",
                  "direct_parent": "fridge 1"
                },
                "floor 4": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "fridge 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 4"
                },
                "apple 2": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "apple 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "coffee table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 25"
                },
                "living room 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 25": {
                  "direct_relation": "inside",
                  "direct_parent": "living room 1"
                }
              }
            },
            "final_environment_summary": {
              "available": true,
              "entity_count": 17,
              "type_counts": {
                "unknown": 7,
                "room": 3,
                "receptacle": 7
              },
              "states_sample": {
                "cabinet 1": {
                  "isOpen": false
                },
                "fridge 1": {
                  "isOpen": false
                }
              },
              "relations_sample": {
                "cupcake 1": {
                  "direct_relation": "on",
                  "direct_parent": "coffee table 1"
                },
                "kitchen 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 2": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "kitchen table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 2"
                },
                "cupcake 2": {
                  "direct_relation": "on",
                  "direct_parent": "kitchen table 1"
                },
                "cupcake 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "bedroom 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 16": {
                  "direct_relation": "inside",
                  "direct_parent": "bedroom 1"
                },
                "cabinet 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 16"
                },
                "apple 1": {
                  "direct_relation": "inside",
                  "direct_parent": "fridge 1"
                },
                "floor 4": {
                  "direct_relation": "inside",
                  "direct_parent": "kitchen 1"
                },
                "fridge 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 4"
                },
                "apple 2": {
                  "direct_relation": "on",
                  "direct_parent": "coffee table 1"
                },
                "apple 3": {
                  "direct_relation": "inside",
                  "direct_parent": "cabinet 1"
                },
                "coffee table 1": {
                  "direct_relation": "on",
                  "direct_parent": "floor 25"
                },
                "living room 1": {
                  "direct_relation": "",
                  "direct_parent": "未知环境"
                },
                "floor 25": {
                  "direct_relation": "inside",
                  "direct_parent": "living room 1"
                }
              }
            },
            "initial_robot": {
              "robot_location": "bedroom 1",
              "robot_holding": "空"
            },
            "final_robot": {
              "robot_location": "coffee table 1",
              "robot_holding": "空"
            },
            "fairness_notes": [
              "task_goal 来自 WAH 官方评测目标，只作为最终态审计目标投影，不作为动作序列答案。"
            ],
            "judge_contract": "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。",
            "enabled": true,
            "comparer_module": "benchmark.reactree.wah.framework.code.final_state"
          }
        }
      }
    ],
    "planning_debug_events": {
      "count": 12,
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
          "todo_count": 8
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "go to",
          "parameters": {
            "target": "kitchen table 1"
          },
          "todo_step": {
            "step": 1,
            "action": "go to",
            "target": "kitchen table 1"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "pick up",
          "parameters": {
            "target": "cupcake 1"
          },
          "todo_step": {
            "step": 2,
            "action": "pick up",
            "target": "cupcake 1"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "go to",
          "parameters": {
            "target": "coffee table 1"
          },
          "todo_step": {
            "step": 3,
            "action": "go to",
            "target": "coffee table 1"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "put down",
          "parameters": {
            "target": "cupcake 1"
          },
          "todo_step": {
            "step": 4,
            "action": "put down",
            "target": "cupcake 1"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "go to",
          "parameters": {
            "target": "kitchen table 1"
          },
          "todo_step": {
            "step": 5,
            "action": "go to",
            "target": "kitchen table 1"
          },
          "ok": true,
          "issue_type": "",
          "fix": ""
        },
        {
          "layer": "sandbox",
          "type": "step_check",
          "skill": "pick up",
          "parameters": {
            "target": "apple 2"
          },
          "todo_step": {
            "step": 6,
            "action": "pick up",
            "target": "apple 2"
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

## 6. Sandbox / ReTrac 统计

```json
{
  "sandbox_check_count": 0,
  "sandbox_failed_count": 0,
  "todo_contract_status": "not_recorded",
  "todo_contract_events": [],
  "re_trac_failed_lessons": {},
  "validated_steps_count": null,
  "evaluator_findings": [],
  "failure_layer": null,
  "failed_action": null,
  "checkpoint_env": null,
  "checkpoint_robot": null
}
```

## 7. Contract / Sandbox / Audit 逐事件记录

```json
[]
```

## 8. LLM 全量输入输出

### Turn 1: understanding

#### Input
```json
[
  {
    "type": "system",
    "content": "任务：把 WAH/ReAcTree benchmark case 输入抽取成结构化任务理解。\n只返回 JSON；不要解释，不要输出 Markdown。\n\n允许使用的 WAH 场景实体名：\n[\"apple 1\", \"apple 2\", \"apple 3\", \"bananas 1\", \"bar soap 1\", \"bathroom 1\", \"bathroom cabinet 1\", \"bathroom counter 1\", \"bed 1\", \"bedroom 1\", \"book 1\", \"book 2\", \"bookshelf 1\", \"bookshelf 2\", \"bookshelf 3\", \"bowl 1\", \"bowl 2\", \"bowl 3\", \"bowl 4\", \"bowl 5\", \"bowl 6\", \"bowl 7\", \"bowl 8\", \"bowl 9\", \"box 1\", \"box 2\", \"box 3\", \"box 4\", \"box 5\", \"bucket 1\", \"cabinet 1\", \"candle 1\", \"candy bar 1\", \"ceiling 1\", \"ceiling 10\", \"ceiling 11\", \"ceiling 12\", \"ceiling 13\", \"ceiling 14\", \"ceiling 15\", \"ceiling 16\", \"ceiling 17\", \"ceiling 18\", \"ceiling 19\", \"ceiling 2\", \"ceiling 20\", \"ceiling 21\", \"ceiling 22\", \"ceiling 23\", \"ceiling 24\", \"ceiling 25\", \"ceiling 26\", \"ceiling 3\", \"ceiling 4\", \"ceiling 5\", \"ceiling 6\", \"ceiling 7\", \"ceiling 8\", \"ceiling 9\", \"ceiling lamp 1\", \"ceiling lamp 2\", \"ceiling lamp 3\", \"ceiling lamp 4\", \"ceiling lamp 5\", \"cell phone 1\", \"cell phone 2\", \"cereal 1\", \"chair 1\", \"chair 2\", \"chair 3\", \"chair 4\", \"chair 5\", \"chair 6\", \"chips 1\", \"chips 2\", \"chocolate syrup 1\", \"closet 1\", \"closet drawer 1\", \"closet drawer 2\", \"closet drawer 3\", \"closet drawer 4\", \"closet drawer 5\", \"closet drawer 6\", \"closet drawer 7\", \"coffee maker 1\", \"coffee pot 1\", \"coffee table 1\", \"computer 1\", \"condiment bottle 1\", \"condiment bottle 2\", \"condiment bottle 3\", \"condiment bottle 4\", \"condiment shaker 1\", \"condiment shaker 2\", \"condiment shaker 3\", \"condiment shaker 4\", \"cooking pot 1\", \"cooking pot 2\", \"cpu screen 1\", \"crackers 1\", \"crackers 2\", \"creamy buns 1\", \"cupcake 1\", \"cupcake 2\", \"cupcake 3\", \"curtains 1\", \"curtains 2\", \"curtains 3\", \"curtains 4\", \"curtains 5\", \"curtains 6\", \"curtains 7\", \"cutlery fork 1\", \"cutlery fork 2\", \"cutlery fork 3\", \"cutlery fork 4\", \"cutlery knife 1\", \"cutlery knife 2\", \"cutlery knife 3\", \"cutlery knife 4\", \"cutlery knife 5\", \"cutlery knife 6\", \"cutlets 1\", \"deodorant 1\", \"deodorant 2\", \"deodorant 3\", \"desk 1\", \"desk 2\", \"dishwasher 1\", \"dishwashing liquid 1\", \"door 1\", \"door 2\", \"door 3\", \"door jamb 1\", \"door jamb 2\", \"door jamb 3\", \"door jamb 4\", \"face cream 1\", \"face cream 2\", \"face cream 3\", \"faucet 1\", \"faucet 2\", \"floor 1\", \"floor 10\", \"floor 11\", \"floor 12\", \"floor 13\", \"floor 14\", \"floor 15\", \"floor 16\", \"floor 17\", \"floor 18\", \"floor 19\", \"floor 2\", \"floor 20\", \"floor 21\", \"floor 22\", \"floor 23\", \"floor 24\", \"floor 25\", \"floor 26\", \"floor 3\", \"floor 4\", \"floor 5\", \"floor 6\", \"floor 7\", \"floor 8\", \"floor 9\", \"folder 1\", \"folder 2\", \"folder 3\", \"folder 4\", \"fridge 1\", \"frying pan 1\", \"hair product 1\", \"hair product 2\", \"hair product 3\", \"hair product 4\", \"hanger 1\", \"hanger 2\", \"hanger 3\", \"hanger 4\", \"hanger 5\", \"hanger 6\", \"hanger 7\", \"juice 1\", \"juice 2\", \"keyboard 1\", \"kitchen 1\", \"kitchen cabinet 1\", \"kitchen cabinet 2\", \"kitchen cabinet 3\", \"kitchen cabinet 4\", \"kitchen cabinet 5\", \"kitchen cabinet 6\", \"kitchen cabinet 7\", \"kitchen cabinet 8\", \"kitchen counter 1\", \"kitchen counter 2\", \"kitchen counter 3\", \"kitchen counter drawer 1\", \"kitchen counter drawer 2\", \"kitchen counter drawer 3\", \"kitchen counter drawer 4\", \"kitchen counter drawer 5\", \"kitchen counter drawer 6\", \"kitchen counter drawer 7\", \"kitchen counter drawer 8\", \"kitchen table 1\", \"knife block 1\", \"light switch 1\", \"light switch 2\", \"light switch 3\", \"light switch 4\", \"lime 1\", \"living room 1\", \"microwave oven 1\", \"milk 1\", \"mouse 1\", \"mouse mat 1\", \"mug 1\", \"mug 2\", \"mug 3\", \"nightstand 1\", \"nightstand 2\", \"nightstand 3\", \"nightstand 4\", \"notes 1\", \"orchid 1\", \"oven tray 1\", \"painkillers 1\", \"pancake 1\", \"peach 1\", \"peach 2\", \"peach 3\", \"pear 1\", \"perfume 1\", \"perfume 2\", \"photo frame 1\", \"photo frame 2\", \"photo frame 3\", \"pile of clothes 1\", \"pile of clothes 2\", \"pillow 1\", \"pillow 2\", \"pillow 3\", \"pillow 4\", \"pillow 5\", \"pillow 6\", \"plate 1\", \"plate 2\", \"plate 3\", \"plate 4\", \"plate 5\", \"plate 6\", \"plate 7\", \"plum 1\", \"plum 2\", \"power socket 1\", \"power socket 2\", \"power socket 3\", \"pudding 1\", \"pudding 2\", \"radio 1\", \"rug 1\", \"rug 2\", \"rug 3\", \"rug 4\", \"sink 1\", \"sink 2\", \"slice of bread 1\", \"slice of bread 2\", \"sofa 1\", \"sofa 2\", \"sofa 3\", \"stall 1\", \"stall 2\", \"stove 1\", \"stove fan 1\", \"table lamp 1\", \"toaster 1\", \"toilet 1\", \"toilet paper 1\", \"toothbrush 1\", \"toothpaste 1\", \"tv 1\", \"tv stand 1\", \"wall 1\", \"wall 10\", \"wall 11\", \"wall 12\", \"wall 13\", \"wall 14\", \"wall 15\", \"wall 16\", \"wall 17\", \"wall 18\", \"wall 19\", \"wall 2\", \"wall 20\", \"wall 21\", \"wall 22\", \"wall 23\", \"wall 24\", \"wall 25\", \"wall 26\", \"wall 3\", \"wall 4\", \"wall 5\", \"wall 6\", \"wall 7\", \"wall 8\", \"wall 9\", \"wall lamp 1\", \"wall lamp 2\", \"wall lamp 3\", \"wall lamp 4\", \"wall lamp 5\", \"wall lamp 6\", \"wall lamp 7\", \"wall lamp 8\", \"wall lamp 9\", \"wall phone 1\", \"wall picture frame 1\", \"wall picture frame 2\", \"wall picture frame 3\", \"wall picture frame 4\", \"wall picture frame 5\", \"wall picture frame 6\", \"wall picture frame 7\", \"wall picture frame 8\", \"wall shelf 1\", \"wall shelf 2\", \"washing machine 1\", \"washing sponge 1\", \"water glass 1\", \"water glass 2\", \"water glass 3\", \"water glass 4\", \"water glass 5\", \"window 1\", \"window 2\", \"wine 1\"]\n\nWAH 任务上下文 JSON：\n{\n  \"dataset\": \"reactree\",\n  \"env_id\": 3,\n  \"task_name\": \"prepare_snack\",\n  \"instruction\": \"Put one cupcake and one apple on the coffee table\",\n  \"init_room\": \"bedroom\",\n  \"task_source\": \"reactree_wah_testset\",\n  \"environment_source\": \"reactree_case_runtime_scene\",\n  \"init_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json\",\n  \"task_goal\": {\n    \"on_cupcake_coffeetable\": 1,\n    \"on_apple_coffeetable\": 1\n  },\n  \"available_entities\": [\n    \"apple 1\",\n    \"apple 2\",\n    \"apple 3\",\n    \"bananas 1\",\n    \"bar soap 1\",\n    \"bathroom 1\",\n    \"bathroom cabinet 1\",\n    \"bathroom counter 1\",\n    \"bed 1\",\n    \"bedroom 1\",\n    \"book 1\",\n    \"book 2\",\n    \"bookshelf 1\",\n    \"bookshelf 2\",\n    \"bookshelf 3\",\n    \"bowl 1\",\n    \"bowl 2\",\n    \"bowl 3\",\n    \"bowl 4\",\n    \"bowl 5\",\n    \"bowl 6\",\n    \"bowl 7\",\n    \"bowl 8\",\n    \"bowl 9\",\n    \"box 1\",\n    \"box 2\",\n    \"box 3\",\n    \"box 4\",\n    \"box 5\",\n    \"bucket 1\",\n    \"cabinet 1\",\n    \"candle 1\",\n    \"candy bar 1\",\n    \"ceiling 1\",\n    \"ceiling 10\",\n    \"ceiling 11\",\n    \"ceiling 12\",\n    \"ceiling 13\",\n    \"ceiling 14\",\n    \"ceiling 15\",\n    \"ceiling 16\",\n    \"ceiling 17\",\n    \"ceiling 18\",\n    \"ceiling 19\",\n    \"ceiling 2\",\n    \"ceiling 20\",\n    \"ceiling 21\",\n    \"ceiling 22\",\n    \"ceiling 23\",\n    \"ceiling 24\",\n    \"ceiling 25\",\n    \"ceiling 26\",\n    \"ceiling 3\",\n    \"ceiling 4\",\n    \"ceiling 5\",\n    \"ceiling 6\",\n    \"ceiling 7\",\n    \"ceiling 8\",\n    \"ceiling 9\",\n    \"ceiling lamp 1\",\n    \"ceiling lamp 2\",\n    \"ceiling lamp 3\",\n    \"ceiling lamp 4\",\n    \"ceiling lamp 5\",\n    \"cell phone 1\",\n    \"cell phone 2\",\n    \"cereal 1\",\n    \"chair 1\",\n    \"chair 2\",\n    \"chair 3\",\n    \"chair 4\",\n    \"chair 5\",\n    \"chair 6\",\n    \"chips 1\",\n    \"chips 2\",\n    \"chocolate syrup 1\",\n    \"closet 1\",\n    \"closet drawer 1\",\n    \"closet drawer 2\",\n    \"closet drawer 3\",\n    \"closet drawer 4\",\n    \"closet drawer 5\",\n    \"closet drawer 6\",\n    \"closet drawer 7\",\n    \"coffee maker 1\",\n    \"coffee pot 1\",\n    \"coffee table 1\",\n    \"computer 1\",\n    \"condiment bottle 1\",\n    \"condiment bottle 2\",\n    \"condiment bottle 3\",\n    \"condiment bottle 4\",\n    \"condiment shaker 1\",\n    \"condiment shaker 2\",\n    \"condiment shaker 3\",\n    \"condiment shaker 4\",\n    \"cooking pot 1\",\n    \"cooking pot 2\",\n    \"cpu screen 1\",\n    \"crackers 1\",\n    \"crackers 2\",\n    \"creamy buns 1\",\n    \"cupcake 1\",\n    \"cupcake 2\",\n    \"cupcake 3\",\n    \"curtains 1\",\n    \"curtains 2\",\n    \"curtains 3\",\n    \"curtains 4\",\n    \"curtains 5\",\n    \"curtains 6\",\n    \"curtains 7\",\n    \"cutlery fork 1\",\n    \"cutlery fork 2\",\n    \"cutlery fork 3\",\n    \"cutlery fork 4\",\n    \"cutlery knife 1\",\n    \"cutlery knife 2\",\n    \"cutlery knife 3\",\n    \"cutlery knife 4\",\n    \"cutlery knife 5\",\n    \"cutlery knife 6\",\n    \"cutlets 1\",\n    \"deodorant 1\",\n    \"deodorant 2\",\n    \"deodorant 3\",\n    \"desk 1\",\n    \"desk 2\",\n    \"dishwasher 1\",\n    \"dishwashing liquid 1\",\n    \"door 1\",\n    \"door 2\",\n    \"door 3\",\n    \"door jamb 1\",\n    \"door jamb 2\",\n    \"door jamb 3\",\n    \"door jamb 4\",\n    \"face cream 1\",\n    \"face cream 2\",\n    \"face cream 3\",\n    \"faucet 1\",\n    \"faucet 2\",\n    \"floor 1\",\n    \"floor 10\",\n    \"floor 11\",\n    \"floor 12\",\n    \"floor 13\",\n    \"floor 14\",\n    \"floor 15\",\n    \"floor 16\",\n    \"floor 17\",\n    \"floor 18\",\n    \"floor 19\",\n    \"floor 2\",\n    \"floor 20\",\n    \"floor 21\",\n    \"floor 22\",\n    \"floor 23\",\n    \"floor 24\",\n    \"floor 25\",\n    \"floor 26\",\n    \"floor 3\",\n    \"floor 4\",\n    \"floor 5\",\n    \"floor 6\",\n    \"floor 7\",\n    \"floor 8\",\n    \"floor 9\",\n    \"folder 1\",\n    \"folder 2\",\n    \"folder 3\",\n    \"folder 4\",\n    \"fridge 1\",\n    \"frying pan 1\",\n    \"hair product 1\",\n    \"hair product 2\",\n    \"hair product 3\",\n    \"hair product 4\",\n    \"hanger 1\",\n    \"hanger 2\",\n    \"hanger 3\",\n    \"hanger 4\",\n    \"hanger 5\",\n    \"hanger 6\",\n    \"hanger 7\",\n    \"juice 1\",\n    \"juice 2\",\n    \"keyboard 1\",\n    \"kitchen 1\",\n    \"kitchen cabinet 1\",\n    \"kitchen cabinet 2\",\n    \"kitchen cabinet 3\",\n    \"kitchen cabinet 4\",\n    \"kitchen cabinet 5\",\n    \"kitchen cabinet 6\",\n    \"kitchen cabinet 7\",\n    \"kitchen cabinet 8\",\n    \"kitchen counter 1\",\n    \"kitchen counter 2\",\n    \"kitchen counter 3\",\n    \"kitchen counter drawer 1\",\n    \"kitchen counter drawer 2\",\n    \"kitchen counter drawer 3\",\n    \"kitchen counter drawer 4\",\n    \"kitchen counter drawer 5\",\n    \"kitchen counter drawer 6\",\n    \"kitchen counter drawer 7\",\n    \"kitchen counter drawer 8\",\n    \"kitchen table 1\",\n    \"knife block 1\",\n    \"light switch 1\",\n    \"light switch 2\",\n    \"light switch 3\",\n    \"light switch 4\",\n    \"lime 1\",\n    \"living room 1\",\n    \"microwave oven 1\",\n    \"milk 1\",\n    \"mouse 1\",\n    \"mouse mat 1\",\n    \"mug 1\",\n    \"mug 2\",\n    \"mug 3\",\n    \"nightstand 1\",\n    \"nightstand 2\",\n    \"nightstand 3\",\n    \"nightstand 4\",\n    \"notes 1\",\n    \"orchid 1\",\n    \"oven tray 1\",\n    \"painkillers 1\",\n    \"pancake 1\",\n    \"peach 1\",\n    \"peach 2\",\n    \"peach 3\",\n    \"pear 1\",\n    \"perfume 1\",\n    \"perfume 2\",\n    \"photo frame 1\",\n    \"photo frame 2\",\n    \"photo frame 3\",\n    \"pile of clothes 1\",\n    \"pile of clothes 2\",\n    \"pillow 1\",\n    \"pillow 2\",\n    \"pillow 3\",\n    \"pillow 4\",\n    \"pillow 5\",\n    \"pillow 6\",\n    \"plate 1\",\n    \"plate 2\",\n    \"plate 3\",\n    \"plate 4\",\n    \"plate 5\",\n    \"plate 6\",\n    \"plate 7\",\n    \"plum 1\",\n    \"plum 2\",\n    \"power socket 1\",\n    \"power socket 2\",\n    \"power socket 3\",\n    \"pudding 1\",\n    \"pudding 2\",\n    \"radio 1\",\n    \"rug 1\",\n    \"rug 2\",\n    \"rug 3\",\n    \"rug 4\",\n    \"sink 1\",\n    \"sink 2\",\n    \"slice of bread 1\",\n    \"slice of bread 2\",\n    \"sofa 1\",\n    \"sofa 2\",\n    \"sofa 3\",\n    \"stall 1\",\n    \"stall 2\",\n    \"stove 1\",\n    \"stove fan 1\",\n    \"table lamp 1\",\n    \"toaster 1\",\n    \"toilet 1\",\n    \"toilet paper 1\",\n    \"toothbrush 1\",\n    \"toothpaste 1\",\n    \"tv 1\",\n    \"tv stand 1\",\n    \"wall 1\",\n    \"wall 10\",\n    \"wall 11\",\n    \"wall 12\",\n    \"wall 13\",\n    \"wall 14\",\n    \"wall 15\",\n    \"wall 16\",\n    \"wall 17\",\n    \"wall 18\",\n    \"wall 19\",\n    \"wall 2\",\n    \"wall 20\",\n    \"wall 21\",\n    \"wall 22\",\n    \"wall 23\",\n    \"wall 24\",\n    \"wall 25\",\n    \"wall 26\",\n    \"wall 3\",\n    \"wall 4\",\n    \"wall 5\",\n    \"wall 6\",\n    \"wall 7\",\n    \"wall 8\",\n    \"wall 9\",\n    \"wall lamp 1\",\n    \"wall lamp 2\",\n    \"wall lamp 3\",\n    \"wall lamp 4\",\n    \"wall lamp 5\",\n    \"wall lamp 6\",\n    \"wall lamp 7\",\n    \"wall lamp 8\",\n    \"wall lamp 9\",\n    \"wall phone 1\",\n    \"wall picture frame 1\",\n    \"wall picture frame 2\",\n    \"wall picture frame 3\",\n    \"wall picture frame 4\",\n    \"wall picture frame 5\",\n    \"wall picture frame 6\",\n    \"wall picture frame 7\",\n    \"wall picture frame 8\",\n    \"wall shelf 1\",\n    \"wall shelf 2\",\n    \"washing machine 1\",\n    \"washing sponge 1\",\n    \"water glass 1\",\n    \"water glass 2\",\n    \"water glass 3\",\n    \"water glass 4\",\n    \"water glass 5\",\n    \"window 1\",\n    \"window 2\",\n    \"wine 1\"\n  ]\n}\n任务上下文中的 env_id、init_room、init_graph_cache_path、task_goal、available_entities 是 WAH/ReAcTree grounding；task_goal 是官方目标谓词，必须保持 WAH 目标语义。\n\nWAH 可用 skill 摘要：\n[\n  {\n    \"name\": \"go to\",\n    \"description\": \"Official ReAcTree WAH navigation action.\",\n    \"planning_contract\": {\n      \"planner_location_param\": \"target\",\n      \"planner_action_name\": \"go to\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=go to\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"pick up\",\n    \"description\": \"Official ReAcTree WAH pickup action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"target\",\n      \"planner_requires_empty_hand\": \"true\",\n      \"planner_action_name\": \"pick up\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=pick up\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"put down\",\n    \"description\": \"Official ReAcTree WAH put-down action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"target\",\n      \"planner_action_name\": \"put down\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=put down\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"open\",\n    \"description\": \"Official ReAcTree WAH open action.\",\n    \"planning_contract\": {\n      \"planner_target_param\": \"target\",\n      \"planner_location_param\": \"target\",\n      \"planner_state_key\": \"isOpen\",\n      \"planner_state_value\": \"true\",\n      \"planner_reversible_state\": \"true\",\n      \"planner_action_name\": \"open\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=open\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"close\",\n    \"description\": \"Official ReAcTree WAH close action.\",\n    \"planning_contract\": {\n      \"planner_target_param\": \"target\",\n      \"planner_location_param\": \"target\",\n      \"planner_state_key\": \"isOpen\",\n      \"planner_state_value\": \"false\",\n      \"planner_reversible_state\": \"true\",\n      \"planner_action_name\": \"close\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=close\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"turn on\",\n    \"description\": \"Official ReAcTree WAH turn-on action.\",\n    \"planning_contract\": {\n      \"planner_target_param\": \"target\",\n      \"planner_location_param\": \"target\",\n      \"planner_state_key\": \"isToggled\",\n      \"planner_state_value\": \"true\",\n      \"planner_reversible_state\": \"true\",\n      \"planner_action_name\": \"turn on\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=turn on\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"turn off\",\n    \"description\": \"Official ReAcTree WAH turn-off action.\",\n    \"planning_contract\": {\n      \"planner_target_param\": \"target\",\n      \"planner_location_param\": \"target\",\n      \"planner_state_key\": \"isToggled\",\n      \"planner_state_value\": \"false\",\n      \"planner_reversible_state\": \"true\",\n      \"planner_action_name\": \"turn off\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=turn off\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"clean\",\n    \"description\": \"Official ReAcTree WAH clean action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"target\",\n      \"planner_effect_state_key\": \"isClean\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"clean\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=clean\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  }\n]\n\n理解边界：\n1. intent 保留 WAH 自然语言任务目标，不输出动作序列。\n2. required_item_names 必须使用允许实体名，或使用 task_goal 指向的真实对象/容器类别从允许实体中选择实例；不要发明编号。\n3. WAH 官方目标通常是类级关系；understanding 可以选目标类别和候选实例，但必须标明数量约束。\n4. skill_closure 只能使用 WAH skills root 中启用的 skill，例如 go_to、pick_up、put_down、open、close、turn_on、turn_off、clean。\n\n输出 JSON 结构：\n{\"is_complete\": true, \"is_cancel_all\": false, \"clarification_question\": \"\", \"entity_relevance\": {\"directly_related\": [], \"indirectly_related\": [], \"possibly_related\": []}, \"skill_closure\": [], \"structured_task\": {\"intent\": \"\", \"required_item_names\": {\"targets\": {\"primary\": [], \"alternatives\": []}, \"tools\": {\"primary\": [], \"alternatives\": []}, \"receptacles\": {\"primary\": [], \"alternatives\": []}}, \"quantity_constraints\": []}}"
  },
  {
    "type": "human",
    "content": "Put one cupcake and one apple on the coffee table"
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
      "cupcake 1",
      "cupcake 2",
      "cupcake 3",
      "apple 1",
      "apple 2",
      "apple 3",
      "coffee table 1"
    ],
    "indirectly_related": [],
    "possibly_related": []
  },
  "skill_closure": [
    "go to",
    "pick up",
    "put down"
  ],
  "structured_task": {
    "intent": "Put one cupcake and one apple on the coffee table",
    "required_item_names": {
      "targets": {
        "primary": [
          "cupcake 1",
          "apple 1"
        ],
        "alternatives": [
          "cupcake 2",
          "cupcake 3",
          "apple 2",
          "apple 3"
        ]
      },
      "tools": {
        "primary": [],
        "alternatives": []
      },
      "receptacles": {
        "primary": [
          "coffee table 1"
        ],
        "alternatives": []
      }
    },
    "quantity_constraints": [
      "1 cupcake",
      "1 apple"
    ]
  }
}
```

### Turn 2: understanding

#### Input
```json
[
  {
    "type": "system",
    "content": "任务：为 WAH/ReAcTree benchmark case 抽取框架内部 final_state。\n只返回 JSON；不要解释，不要输出 Markdown。\n\n允许参考的 WAH 场景实体：\n[\n  \"apple 1\",\n  \"apple 2\",\n  \"apple 3\",\n  \"bananas 1\",\n  \"bar soap 1\",\n  \"bathroom 1\",\n  \"bathroom cabinet 1\",\n  \"bathroom counter 1\",\n  \"bed 1\",\n  \"bedroom 1\",\n  \"book 1\",\n  \"book 2\",\n  \"bookshelf 1\",\n  \"bookshelf 2\",\n  \"bookshelf 3\",\n  \"bowl 1\",\n  \"bowl 2\",\n  \"bowl 3\",\n  \"bowl 4\",\n  \"bowl 5\",\n  \"bowl 6\",\n  \"bowl 7\",\n  \"bowl 8\",\n  \"bowl 9\",\n  \"box 1\",\n  \"box 2\",\n  \"box 3\",\n  \"box 4\",\n  \"box 5\",\n  \"bucket 1\",\n  \"cabinet 1\",\n  \"candle 1\",\n  \"candy bar 1\",\n  \"ceiling 1\",\n  \"ceiling 10\",\n  \"ceiling 11\",\n  \"ceiling 12\",\n  \"ceiling 13\",\n  \"ceiling 14\",\n  \"ceiling 15\",\n  \"ceiling 16\",\n  \"ceiling 17\",\n  \"ceiling 18\",\n  \"ceiling 19\",\n  \"ceiling 2\",\n  \"ceiling 20\",\n  \"ceiling 21\",\n  \"ceiling 22\",\n  \"ceiling 23\",\n  \"ceiling 24\",\n  \"ceiling 25\",\n  \"ceiling 26\",\n  \"ceiling 3\",\n  \"ceiling 4\",\n  \"ceiling 5\",\n  \"ceiling 6\",\n  \"ceiling 7\",\n  \"ceiling 8\",\n  \"ceiling 9\",\n  \"ceiling lamp 1\",\n  \"ceiling lamp 2\",\n  \"ceiling lamp 3\",\n  \"ceiling lamp 4\",\n  \"ceiling lamp 5\",\n  \"cell phone 1\",\n  \"cell phone 2\",\n  \"cereal 1\",\n  \"chair 1\",\n  \"chair 2\",\n  \"chair 3\",\n  \"chair 4\",\n  \"chair 5\",\n  \"chair 6\",\n  \"chips 1\",\n  \"chips 2\",\n  \"chocolate syrup 1\",\n  \"closet 1\",\n  \"closet drawer 1\",\n  \"closet drawer 2\",\n  \"closet drawer 3\",\n  \"closet drawer 4\",\n  \"closet drawer 5\",\n  \"closet drawer 6\",\n  \"closet drawer 7\",\n  \"coffee maker 1\",\n  \"coffee pot 1\",\n  \"coffee table 1\",\n  \"computer 1\",\n  \"condiment bottle 1\",\n  \"condiment bottle 2\",\n  \"condiment bottle 3\",\n  \"condiment bottle 4\",\n  \"condiment shaker 1\",\n  \"condiment shaker 2\",\n  \"condiment shaker 3\",\n  \"condiment shaker 4\",\n  \"cooking pot 1\",\n  \"cooking pot 2\",\n  \"cpu screen 1\",\n  \"crackers 1\",\n  \"crackers 2\",\n  \"creamy buns 1\",\n  \"cupcake 1\",\n  \"cupcake 2\",\n  \"cupcake 3\",\n  \"curtains 1\",\n  \"curtains 2\",\n  \"curtains 3\",\n  \"curtains 4\",\n  \"curtains 5\",\n  \"curtains 6\",\n  \"curtains 7\",\n  \"cutlery fork 1\",\n  \"cutlery fork 2\",\n  \"cutlery fork 3\",\n  \"cutlery fork 4\",\n  \"cutlery knife 1\",\n  \"cutlery knife 2\",\n  \"cutlery knife 3\",\n  \"cutlery knife 4\",\n  \"cutlery knife 5\",\n  \"cutlery knife 6\",\n  \"cutlets 1\",\n  \"deodorant 1\",\n  \"deodorant 2\",\n  \"deodorant 3\",\n  \"desk 1\",\n  \"desk 2\",\n  \"dishwasher 1\",\n  \"dishwashing liquid 1\",\n  \"door 1\",\n  \"door 2\",\n  \"door 3\",\n  \"door jamb 1\",\n  \"door jamb 2\",\n  \"door jamb 3\",\n  \"door jamb 4\",\n  \"face cream 1\",\n  \"face cream 2\",\n  \"face cream 3\",\n  \"faucet 1\",\n  \"faucet 2\",\n  \"floor 1\",\n  \"floor 10\",\n  \"floor 11\",\n  \"floor 12\",\n  \"floor 13\",\n  \"floor 14\",\n  \"floor 15\",\n  \"floor 16\",\n  \"floor 17\",\n  \"floor 18\",\n  \"floor 19\",\n  \"floor 2\",\n  \"floor 20\",\n  \"floor 21\",\n  \"floor 22\",\n  \"floor 23\",\n  \"floor 24\",\n  \"floor 25\",\n  \"floor 26\",\n  \"floor 3\",\n  \"floor 4\",\n  \"floor 5\",\n  \"floor 6\",\n  \"floor 7\",\n  \"floor 8\",\n  \"floor 9\",\n  \"folder 1\",\n  \"folder 2\",\n  \"folder 3\",\n  \"folder 4\",\n  \"fridge 1\",\n  \"frying pan 1\",\n  \"hair product 1\",\n  \"hair product 2\",\n  \"hair product 3\",\n  \"hair product 4\",\n  \"hanger 1\",\n  \"hanger 2\",\n  \"hanger 3\",\n  \"hanger 4\",\n  \"hanger 5\",\n  \"hanger 6\",\n  \"hanger 7\",\n  \"juice 1\",\n  \"juice 2\",\n  \"keyboard 1\",\n  \"kitchen 1\",\n  \"kitchen cabinet 1\",\n  \"kitchen cabinet 2\",\n  \"kitchen cabinet 3\",\n  \"kitchen cabinet 4\",\n  \"kitchen cabinet 5\",\n  \"kitchen cabinet 6\",\n  \"kitchen cabinet 7\",\n  \"kitchen cabinet 8\",\n  \"kitchen counter 1\",\n  \"kitchen counter 2\",\n  \"kitchen counter 3\",\n  \"kitchen counter drawer 1\",\n  \"kitchen counter drawer 2\",\n  \"kitchen counter drawer 3\",\n  \"kitchen counter drawer 4\",\n  \"kitchen counter drawer 5\",\n  \"kitchen counter drawer 6\",\n  \"kitchen counter drawer 7\",\n  \"kitchen counter drawer 8\",\n  \"kitchen table 1\",\n  \"knife block 1\",\n  \"light switch 1\",\n  \"light switch 2\",\n  \"light switch 3\",\n  \"light switch 4\",\n  \"lime 1\",\n  \"living room 1\",\n  \"microwave oven 1\",\n  \"milk 1\",\n  \"mouse 1\",\n  \"mouse mat 1\",\n  \"mug 1\",\n  \"mug 2\",\n  \"mug 3\",\n  \"nightstand 1\",\n  \"nightstand 2\",\n  \"nightstand 3\",\n  \"nightstand 4\",\n  \"notes 1\",\n  \"orchid 1\",\n  \"oven tray 1\",\n  \"painkillers 1\",\n  \"pancake 1\",\n  \"peach 1\",\n  \"peach 2\",\n  \"peach 3\",\n  \"pear 1\",\n  \"perfume 1\",\n  \"perfume 2\",\n  \"photo frame 1\",\n  \"photo frame 2\",\n  \"photo frame 3\",\n  \"pile of clothes 1\",\n  \"pile of clothes 2\",\n  \"pillow 1\",\n  \"pillow 2\",\n  \"pillow 3\",\n  \"pillow 4\",\n  \"pillow 5\",\n  \"pillow 6\",\n  \"plate 1\",\n  \"plate 2\",\n  \"plate 3\",\n  \"plate 4\",\n  \"plate 5\",\n  \"plate 6\",\n  \"plate 7\",\n  \"plum 1\",\n  \"plum 2\",\n  \"power socket 1\",\n  \"power socket 2\",\n  \"power socket 3\",\n  \"pudding 1\",\n  \"pudding 2\",\n  \"radio 1\",\n  \"rug 1\",\n  \"rug 2\",\n  \"rug 3\",\n  \"rug 4\",\n  \"sink 1\",\n  \"sink 2\",\n  \"slice of bread 1\",\n  \"slice of bread 2\",\n  \"sofa 1\",\n  \"sofa 2\",\n  \"sofa 3\",\n  \"stall 1\",\n  \"stall 2\",\n  \"stove 1\",\n  \"stove fan 1\",\n  \"table lamp 1\",\n  \"toaster 1\",\n  \"toilet 1\",\n  \"toilet paper 1\",\n  \"toothbrush 1\",\n  \"toothpaste 1\",\n  \"tv 1\",\n  \"tv stand 1\",\n  \"wall 1\",\n  \"wall 10\",\n  \"wall 11\",\n  \"wall 12\",\n  \"wall 13\",\n  \"wall 14\",\n  \"wall 15\",\n  \"wall 16\",\n  \"wall 17\",\n  \"wall 18\",\n  \"wall 19\",\n  \"wall 2\",\n  \"wall 20\",\n  \"wall 21\",\n  \"wall 22\",\n  \"wall 23\",\n  \"wall 24\",\n  \"wall 25\",\n  \"wall 26\",\n  \"wall 3\",\n  \"wall 4\",\n  \"wall 5\",\n  \"wall 6\",\n  \"wall 7\",\n  \"wall 8\",\n  \"wall 9\",\n  \"wall lamp 1\",\n  \"wall lamp 2\",\n  \"wall lamp 3\",\n  \"wall lamp 4\",\n  \"wall lamp 5\",\n  \"wall lamp 6\",\n  \"wall lamp 7\",\n  \"wall lamp 8\",\n  \"wall lamp 9\",\n  \"wall phone 1\",\n  \"wall picture frame 1\",\n  \"wall picture frame 2\",\n  \"wall picture frame 3\",\n  \"wall picture frame 4\",\n  \"wall picture frame 5\",\n  \"wall picture frame 6\",\n  \"wall picture frame 7\",\n  \"wall picture frame 8\",\n  \"wall shelf 1\",\n  \"wall shelf 2\",\n  \"washing machine 1\",\n  \"washing sponge 1\",\n  \"water glass 1\",\n  \"water glass 2\",\n  \"water glass 3\",\n  \"water glass 4\",\n  \"water glass 5\",\n  \"window 1\",\n  \"window 2\",\n  \"wine 1\"\n]\n\n当前理解结果：\n{\n  \"intent\": \"Put one cupcake and one apple on the coffee table\",\n  \"required_item_names\": {\n    \"targets\": {\n      \"primary\": [\n        \"cupcake 1\",\n        \"apple 1\"\n      ],\n      \"alternatives\": [\n        \"cupcake 2\",\n        \"cupcake 3\",\n        \"apple 2\",\n        \"apple 3\"\n      ]\n    },\n    \"tools\": {\n      \"primary\": [],\n      \"alternatives\": []\n    },\n    \"receptacles\": {\n      \"primary\": [\n        \"coffee table 1\"\n      ],\n      \"alternatives\": []\n    }\n  },\n  \"quantity_constraints\": [\n    \"1 cupcake\",\n    \"1 apple\"\n  ]\n}\n\n当前选择摘要：\n{\n  \"structured_task\": {\n    \"intent\": \"Put one cupcake and one apple on the coffee table\",\n    \"required_item_names\": {\n      \"targets\": {\n        \"primary\": [\n          \"cupcake 1\",\n          \"apple 1\"\n        ],\n        \"alternatives\": [\n          \"cupcake 2\",\n          \"cupcake 3\",\n          \"apple 2\",\n          \"apple 3\"\n        ]\n      },\n      \"tools\": {\n        \"primary\": [],\n        \"alternatives\": []\n      },\n      \"receptacles\": {\n        \"primary\": [\n          \"coffee table 1\"\n        ],\n        \"alternatives\": []\n      }\n    },\n    \"quantity_constraints\": [\n      \"1 cupcake\",\n      \"1 apple\"\n    ]\n  },\n  \"current_final_state\": {},\n  \"scene_entities\": [\n    \"apple 1\",\n    \"apple 2\",\n    \"apple 3\",\n    \"bananas 1\",\n    \"bar soap 1\",\n    \"bathroom 1\",\n    \"bathroom cabinet 1\",\n    \"bathroom counter 1\",\n    \"bed 1\",\n    \"bedroom 1\",\n    \"book 1\",\n    \"book 2\",\n    \"bookshelf 1\",\n    \"bookshelf 2\",\n    \"bookshelf 3\",\n    \"bowl 1\",\n    \"bowl 2\",\n    \"bowl 3\",\n    \"bowl 4\",\n    \"bowl 5\",\n    \"bowl 6\",\n    \"bowl 7\",\n    \"bowl 8\",\n    \"bowl 9\",\n    \"box 1\",\n    \"box 2\",\n    \"box 3\",\n    \"box 4\",\n    \"box 5\",\n    \"bucket 1\",\n    \"cabinet 1\",\n    \"candle 1\",\n    \"candy bar 1\",\n    \"ceiling 1\",\n    \"ceiling 10\",\n    \"ceiling 11\",\n    \"ceiling 12\",\n    \"ceiling 13\",\n    \"ceiling 14\",\n    \"ceiling 15\",\n    \"ceiling 16\",\n    \"ceiling 17\",\n    \"ceiling 18\",\n    \"ceiling 19\",\n    \"ceiling 2\",\n    \"ceiling 20\",\n    \"ceiling 21\",\n    \"ceiling 22\",\n    \"ceiling 23\",\n    \"ceiling 24\",\n    \"ceiling 25\",\n    \"ceiling 26\",\n    \"ceiling 3\",\n    \"ceiling 4\",\n    \"ceiling 5\",\n    \"ceiling 6\",\n    \"ceiling 7\",\n    \"ceiling 8\",\n    \"ceiling 9\",\n    \"ceiling lamp 1\",\n    \"ceiling lamp 2\",\n    \"ceiling lamp 3\",\n    \"ceiling lamp 4\",\n    \"ceiling lamp 5\",\n    \"cell phone 1\",\n    \"cell phone 2\",\n    \"cereal 1\",\n    \"chair 1\",\n    \"chair 2\",\n    \"chair 3\",\n    \"chair 4\",\n    \"chair 5\",\n    \"chair 6\",\n    \"chips 1\",\n    \"chips 2\",\n    \"chocolate syrup 1\",\n    \"closet 1\",\n    \"closet drawer 1\",\n    \"closet drawer 2\",\n    \"closet drawer 3\",\n    \"closet drawer 4\",\n    \"closet drawer 5\",\n    \"closet drawer 6\",\n    \"closet drawer 7\",\n    \"coffee maker 1\",\n    \"coffee pot 1\",\n    \"coffee table 1\",\n    \"computer 1\",\n    \"condiment bottle 1\",\n    \"condiment bottle 2\",\n    \"condiment bottle 3\",\n    \"condiment bottle 4\",\n    \"condiment shaker 1\",\n    \"condiment shaker 2\",\n    \"condiment shaker 3\",\n    \"condiment shaker 4\",\n    \"cooking pot 1\",\n    \"cooking pot 2\",\n    \"cpu screen 1\",\n    \"crackers 1\",\n    \"crackers 2\",\n    \"creamy buns 1\",\n    \"cupcake 1\",\n    \"cupcake 2\",\n    \"cupcake 3\",\n    \"curtains 1\",\n    \"curtains 2\",\n    \"curtains 3\",\n    \"curtains 4\",\n    \"curtains 5\",\n    \"curtains 6\",\n    \"curtains 7\",\n    \"cutlery fork 1\",\n    \"cutlery fork 2\",\n    \"cutlery fork 3\",\n    \"cutlery fork 4\",\n    \"cutlery knife 1\",\n    \"cutlery knife 2\",\n    \"cutlery knife 3\",\n    \"cutlery knife 4\",\n    \"cutlery knife 5\",\n    \"cutlery knife 6\",\n    \"cutlets 1\",\n    \"deodorant 1\",\n    \"deodorant 2\",\n    \"deodorant 3\",\n    \"desk 1\",\n    \"desk 2\",\n    \"dishwasher 1\",\n    \"dishwashing liquid 1\",\n    \"door 1\",\n    \"door 2\",\n    \"door 3\",\n    \"door jamb 1\",\n    \"door jamb 2\",\n    \"door jamb 3\",\n    \"door jamb 4\",\n    \"face cream 1\",\n    \"face cream 2\",\n    \"face cream 3\",\n    \"faucet 1\",\n    \"faucet 2\",\n    \"floor 1\",\n    \"floor 10\",\n    \"floor 11\",\n    \"floor 12\",\n    \"floor 13\",\n    \"floor 14\",\n    \"floor 15\",\n    \"floor 16\",\n    \"floor 17\",\n    \"floor 18\",\n    \"floor 19\",\n    \"floor 2\",\n    \"floor 20\",\n    \"floor 21\",\n    \"floor 22\",\n    \"floor 23\",\n    \"floor 24\",\n    \"floor 25\",\n    \"floor 26\",\n    \"floor 3\",\n    \"floor 4\",\n    \"floor 5\",\n    \"floor 6\",\n    \"floor 7\",\n    \"floor 8\",\n    \"floor 9\",\n    \"folder 1\",\n    \"folder 2\",\n    \"folder 3\",\n    \"folder 4\",\n    \"fridge 1\",\n    \"frying pan 1\",\n    \"hair product 1\",\n    \"hair product 2\",\n    \"hair product 3\",\n    \"hair product 4\",\n    \"hanger 1\",\n    \"hanger 2\",\n    \"hanger 3\",\n    \"hanger 4\",\n    \"hanger 5\",\n    \"hanger 6\",\n    \"hanger 7\",\n    \"juice 1\",\n    \"juice 2\",\n    \"keyboard 1\",\n    \"kitchen 1\",\n    \"kitchen cabinet 1\",\n    \"kitchen cabinet 2\",\n    \"kitchen cabinet 3\",\n    \"kitchen cabinet 4\",\n    \"kitchen cabinet 5\",\n    \"kitchen cabinet 6\",\n    \"kitchen cabinet 7\",\n    \"kitchen cabinet 8\",\n    \"kitchen counter 1\",\n    \"kitchen counter 2\",\n    \"kitchen counter 3\",\n    \"kitchen counter drawer 1\",\n    \"kitchen counter drawer 2\",\n    \"kitchen counter drawer 3\",\n    \"kitchen counter drawer 4\",\n    \"kitchen counter drawer 5\",\n    \"kitchen counter drawer 6\",\n    \"kitchen counter drawer 7\",\n    \"kitchen counter drawer 8\",\n    \"kitchen table 1\",\n    \"knife block 1\",\n    \"light switch 1\",\n    \"light switch 2\",\n    \"light switch 3\",\n    \"light switch 4\",\n    \"lime 1\",\n    \"living room 1\",\n    \"microwave oven 1\",\n    \"milk 1\",\n    \"mouse 1\",\n    \"mouse mat 1\",\n    \"mug 1\",\n    \"mug 2\",\n    \"mug 3\",\n    \"nightstand 1\",\n    \"nightstand 2\",\n    \"nightstand 3\",\n    \"nightstand 4\",\n    \"notes 1\",\n    \"orchid 1\",\n    \"oven tray 1\",\n    \"painkillers 1\",\n    \"pancake 1\",\n    \"peach 1\",\n    \"peach 2\",\n    \"peach 3\",\n    \"pear 1\",\n    \"perfume 1\",\n    \"perfume 2\",\n    \"photo frame 1\",\n    \"photo frame 2\",\n    \"photo frame 3\",\n    \"pile of clothes 1\",\n    \"pile of clothes 2\",\n    \"pillow 1\",\n    \"pillow 2\",\n    \"pillow 3\",\n    \"pillow 4\",\n    \"pillow 5\",\n    \"pillow 6\",\n    \"plate 1\",\n    \"plate 2\",\n    \"plate 3\",\n    \"plate 4\",\n    \"plate 5\",\n    \"plate 6\",\n    \"plate 7\",\n    \"plum 1\",\n    \"plum 2\",\n    \"power socket 1\",\n    \"power socket 2\",\n    \"power socket 3\",\n    \"pudding 1\",\n    \"pudding 2\",\n    \"radio 1\",\n    \"rug 1\",\n    \"rug 2\",\n    \"rug 3\",\n    \"rug 4\",\n    \"sink 1\",\n    \"sink 2\",\n    \"slice of bread 1\",\n    \"slice of bread 2\",\n    \"sofa 1\",\n    \"sofa 2\",\n    \"sofa 3\",\n    \"stall 1\",\n    \"stall 2\",\n    \"stove 1\",\n    \"stove fan 1\",\n    \"table lamp 1\",\n    \"toaster 1\",\n    \"toilet 1\",\n    \"toilet paper 1\",\n    \"toothbrush 1\",\n    \"toothpaste 1\",\n    \"tv 1\",\n    \"tv stand 1\",\n    \"wall 1\",\n    \"wall 10\",\n    \"wall 11\",\n    \"wall 12\",\n    \"wall 13\",\n    \"wall 14\",\n    \"wall 15\",\n    \"wall 16\",\n    \"wall 17\",\n    \"wall 18\",\n    \"wall 19\",\n    \"wall 2\",\n    \"wall 20\",\n    \"wall 21\",\n    \"wall 22\",\n    \"wall 23\",\n    \"wall 24\",\n    \"wall 25\",\n    \"wall 26\",\n    \"wall 3\",\n    \"wall 4\",\n    \"wall 5\",\n    \"wall 6\",\n    \"wall 7\",\n    \"wall 8\",\n    \"wall 9\",\n    \"wall lamp 1\",\n    \"wall lamp 2\",\n    \"wall lamp 3\",\n    \"wall lamp 4\",\n    \"wall lamp 5\",\n    \"wall lamp 6\",\n    \"wall lamp 7\",\n    \"wall lamp 8\",\n    \"wall lamp 9\",\n    \"wall phone 1\",\n    \"wall picture frame 1\",\n    \"wall picture frame 2\",\n    \"wall picture frame 3\",\n    \"wall picture frame 4\",\n    \"wall picture frame 5\",\n    \"wall picture frame 6\",\n    \"wall picture frame 7\",\n    \"wall picture frame 8\",\n    \"wall shelf 1\",\n    \"wall shelf 2\",\n    \"washing machine 1\",\n    \"washing sponge 1\",\n    \"water glass 1\",\n    \"water glass 2\",\n    \"water glass 3\",\n    \"water glass 4\",\n    \"water glass 5\",\n    \"window 1\",\n    \"window 2\",\n    \"wine 1\"\n  ]\n}\n\nWAH 任务上下文：\n{\n  \"dataset\": \"reactree\",\n  \"env_id\": 3,\n  \"task_name\": \"prepare_snack\",\n  \"instruction\": \"Put one cupcake and one apple on the coffee table\",\n  \"init_room\": \"bedroom\",\n  \"task_source\": \"reactree_wah_testset\",\n  \"environment_source\": \"reactree_case_runtime_scene\",\n  \"init_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json\",\n  \"task_goal\": {\n    \"on_cupcake_coffeetable\": 1,\n    \"on_apple_coffeetable\": 1\n  },\n  \"available_entities\": [\n    \"apple 1\",\n    \"apple 2\",\n    \"apple 3\",\n    \"bananas 1\",\n    \"bar soap 1\",\n    \"bathroom 1\",\n    \"bathroom cabinet 1\",\n    \"bathroom counter 1\",\n    \"bed 1\",\n    \"bedroom 1\",\n    \"book 1\",\n    \"book 2\",\n    \"bookshelf 1\",\n    \"bookshelf 2\",\n    \"bookshelf 3\",\n    \"bowl 1\",\n    \"bowl 2\",\n    \"bowl 3\",\n    \"bowl 4\",\n    \"bowl 5\",\n    \"bowl 6\",\n    \"bowl 7\",\n    \"bowl 8\",\n    \"bowl 9\",\n    \"box 1\",\n    \"box 2\",\n    \"box 3\",\n    \"box 4\",\n    \"box 5\",\n    \"bucket 1\",\n    \"cabinet 1\",\n    \"candle 1\",\n    \"candy bar 1\",\n    \"ceiling 1\",\n    \"ceiling 10\",\n    \"ceiling 11\",\n    \"ceiling 12\",\n    \"ceiling 13\",\n    \"ceiling 14\",\n    \"ceiling 15\",\n    \"ceiling 16\",\n    \"ceiling 17\",\n    \"ceiling 18\",\n    \"ceiling 19\",\n    \"ceiling 2\",\n    \"ceiling 20\",\n    \"ceiling 21\",\n    \"ceiling 22\",\n    \"ceiling 23\",\n    \"ceiling 24\",\n    \"ceiling 25\",\n    \"ceiling 26\",\n    \"ceiling 3\",\n    \"ceiling 4\",\n    \"ceiling 5\",\n    \"ceiling 6\",\n    \"ceiling 7\",\n    \"ceiling 8\",\n    \"ceiling 9\",\n    \"ceiling lamp 1\",\n    \"ceiling lamp 2\",\n    \"ceiling lamp 3\",\n    \"ceiling lamp 4\",\n    \"ceiling lamp 5\",\n    \"cell phone 1\",\n    \"cell phone 2\",\n    \"cereal 1\",\n    \"chair 1\",\n    \"chair 2\",\n    \"chair 3\",\n    \"chair 4\",\n    \"chair 5\",\n    \"chair 6\",\n    \"chips 1\",\n    \"chips 2\",\n    \"chocolate syrup 1\",\n    \"closet 1\",\n    \"closet drawer 1\",\n    \"closet drawer 2\",\n    \"closet drawer 3\",\n    \"closet drawer 4\",\n    \"closet drawer 5\",\n    \"closet drawer 6\",\n    \"closet drawer 7\",\n    \"coffee maker 1\",\n    \"coffee pot 1\",\n    \"coffee table 1\",\n    \"computer 1\",\n    \"condiment bottle 1\",\n    \"condiment bottle 2\",\n    \"condiment bottle 3\",\n    \"condiment bottle 4\",\n    \"condiment shaker 1\",\n    \"condiment shaker 2\",\n    \"condiment shaker 3\",\n    \"condiment shaker 4\",\n    \"cooking pot 1\",\n    \"cooking pot 2\",\n    \"cpu screen 1\",\n    \"crackers 1\",\n    \"crackers 2\",\n    \"creamy buns 1\",\n    \"cupcake 1\",\n    \"cupcake 2\",\n    \"cupcake 3\",\n    \"curtains 1\",\n    \"curtains 2\",\n    \"curtains 3\",\n    \"curtains 4\",\n    \"curtains 5\",\n    \"curtains 6\",\n    \"curtains 7\",\n    \"cutlery fork 1\",\n    \"cutlery fork 2\",\n    \"cutlery fork 3\",\n    \"cutlery fork 4\",\n    \"cutlery knife 1\",\n    \"cutlery knife 2\",\n    \"cutlery knife 3\",\n    \"cutlery knife 4\",\n    \"cutlery knife 5\",\n    \"cutlery knife 6\",\n    \"cutlets 1\",\n    \"deodorant 1\",\n    \"deodorant 2\",\n    \"deodorant 3\",\n    \"desk 1\",\n    \"desk 2\",\n    \"dishwasher 1\",\n    \"dishwashing liquid 1\",\n    \"door 1\",\n    \"door 2\",\n    \"door 3\",\n    \"door jamb 1\",\n    \"door jamb 2\",\n    \"door jamb 3\",\n    \"door jamb 4\",\n    \"face cream 1\",\n    \"face cream 2\",\n    \"face cream 3\",\n    \"faucet 1\",\n    \"faucet 2\",\n    \"floor 1\",\n    \"floor 10\",\n    \"floor 11\",\n    \"floor 12\",\n    \"floor 13\",\n    \"floor 14\",\n    \"floor 15\",\n    \"floor 16\",\n    \"floor 17\",\n    \"floor 18\",\n    \"floor 19\",\n    \"floor 2\",\n    \"floor 20\",\n    \"floor 21\",\n    \"floor 22\",\n    \"floor 23\",\n    \"floor 24\",\n    \"floor 25\",\n    \"floor 26\",\n    \"floor 3\",\n    \"floor 4\",\n    \"floor 5\",\n    \"floor 6\",\n    \"floor 7\",\n    \"floor 8\",\n    \"floor 9\",\n    \"folder 1\",\n    \"folder 2\",\n    \"folder 3\",\n    \"folder 4\",\n    \"fridge 1\",\n    \"frying pan 1\",\n    \"hair product 1\",\n    \"hair product 2\",\n    \"hair product 3\",\n    \"hair product 4\",\n    \"hanger 1\",\n    \"hanger 2\",\n    \"hanger 3\",\n    \"hanger 4\",\n    \"hanger 5\",\n    \"hanger 6\",\n    \"hanger 7\",\n    \"juice 1\",\n    \"juice 2\",\n    \"keyboard 1\",\n    \"kitchen 1\",\n    \"kitchen cabinet 1\",\n    \"kitchen cabinet 2\",\n    \"kitchen cabinet 3\",\n    \"kitchen cabinet 4\",\n    \"kitchen cabinet 5\",\n    \"kitchen cabinet 6\",\n    \"kitchen cabinet 7\",\n    \"kitchen cabinet 8\",\n    \"kitchen counter 1\",\n    \"kitchen counter 2\",\n    \"kitchen counter 3\",\n    \"kitchen counter drawer 1\",\n    \"kitchen counter drawer 2\",\n    \"kitchen counter drawer 3\",\n    \"kitchen counter drawer 4\",\n    \"kitchen counter drawer 5\",\n    \"kitchen counter drawer 6\",\n    \"kitchen counter drawer 7\",\n    \"kitchen counter drawer 8\",\n    \"kitchen table 1\",\n    \"knife block 1\",\n    \"light switch 1\",\n    \"light switch 2\",\n    \"light switch 3\",\n    \"light switch 4\",\n    \"lime 1\",\n    \"living room 1\",\n    \"microwave oven 1\",\n    \"milk 1\",\n    \"mouse 1\",\n    \"mouse mat 1\",\n    \"mug 1\",\n    \"mug 2\",\n    \"mug 3\",\n    \"nightstand 1\",\n    \"nightstand 2\",\n    \"nightstand 3\",\n    \"nightstand 4\",\n    \"notes 1\",\n    \"orchid 1\",\n    \"oven tray 1\",\n    \"painkillers 1\",\n    \"pancake 1\",\n    \"peach 1\",\n    \"peach 2\",\n    \"peach 3\",\n    \"pear 1\",\n    \"perfume 1\",\n    \"perfume 2\",\n    \"photo frame 1\",\n    \"photo frame 2\",\n    \"photo frame 3\",\n    \"pile of clothes 1\",\n    \"pile of clothes 2\",\n    \"pillow 1\",\n    \"pillow 2\",\n    \"pillow 3\",\n    \"pillow 4\",\n    \"pillow 5\",\n    \"pillow 6\",\n    \"plate 1\",\n    \"plate 2\",\n    \"plate 3\",\n    \"plate 4\",\n    \"plate 5\",\n    \"plate 6\",\n    \"plate 7\",\n    \"plum 1\",\n    \"plum 2\",\n    \"power socket 1\",\n    \"power socket 2\",\n    \"power socket 3\",\n    \"pudding 1\",\n    \"pudding 2\",\n    \"radio 1\",\n    \"rug 1\",\n    \"rug 2\",\n    \"rug 3\",\n    \"rug 4\",\n    \"sink 1\",\n    \"sink 2\",\n    \"slice of bread 1\",\n    \"slice of bread 2\",\n    \"sofa 1\",\n    \"sofa 2\",\n    \"sofa 3\",\n    \"stall 1\",\n    \"stall 2\",\n    \"stove 1\",\n    \"stove fan 1\",\n    \"table lamp 1\",\n    \"toaster 1\",\n    \"toilet 1\",\n    \"toilet paper 1\",\n    \"toothbrush 1\",\n    \"toothpaste 1\",\n    \"tv 1\",\n    \"tv stand 1\",\n    \"wall 1\",\n    \"wall 10\",\n    \"wall 11\",\n    \"wall 12\",\n    \"wall 13\",\n    \"wall 14\",\n    \"wall 15\",\n    \"wall 16\",\n    \"wall 17\",\n    \"wall 18\",\n    \"wall 19\",\n    \"wall 2\",\n    \"wall 20\",\n    \"wall 21\",\n    \"wall 22\",\n    \"wall 23\",\n    \"wall 24\",\n    \"wall 25\",\n    \"wall 26\",\n    \"wall 3\",\n    \"wall 4\",\n    \"wall 5\",\n    \"wall 6\",\n    \"wall 7\",\n    \"wall 8\",\n    \"wall 9\",\n    \"wall lamp 1\",\n    \"wall lamp 2\",\n    \"wall lamp 3\",\n    \"wall lamp 4\",\n    \"wall lamp 5\",\n    \"wall lamp 6\",\n    \"wall lamp 7\",\n    \"wall lamp 8\",\n    \"wall lamp 9\",\n    \"wall phone 1\",\n    \"wall picture frame 1\",\n    \"wall picture frame 2\",\n    \"wall picture frame 3\",\n    \"wall picture frame 4\",\n    \"wall picture frame 5\",\n    \"wall picture frame 6\",\n    \"wall picture frame 7\",\n    \"wall picture frame 8\",\n    \"wall shelf 1\",\n    \"wall shelf 2\",\n    \"washing machine 1\",\n    \"washing sponge 1\",\n    \"water glass 1\",\n    \"water glass 2\",\n    \"water glass 3\",\n    \"water glass 4\",\n    \"water glass 5\",\n    \"window 1\",\n    \"window 2\",\n    \"wine 1\"\n  ]\n}\n\n抽取边界：\n1. final_state 保持 WAH/ReAcTree 语义，可表达 task_goal 对象类别、目标关系、目标容器和数量。\n2. 只使用任务输入、task_goal、允许实体和当前理解结果；不要读取 expert trajectory 或官方动作答案。\n3. 不输出动作序列，不改写为其他 benchmark 的动作或环境格式。\n\n输出 JSON：\n{\"final_state\": {}}"
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
    "on_cupcake_coffeetable": 1,
    "on_apple_coffeetable": 1
  }
}
```

### Turn 3: planning

#### Input
```json
[
  {
    "type": "system",
    "content": "任务：生成 WAH/ReAcTree 官方原生动作计划。\n只输出 JSON；不要解释，不要输出 Markdown。\n\n原始任务：\n\n\n规划目标：\nPut one cupcake and one apple on the coffee table\n\n机器人状态：\n- 位置：bedroom 1\n- 手持：空\n- 完整状态：{\"robot_location\":\"bedroom 1\",\"robot_holding\":\"空\"}\n\n当前环境 JSON：\n{\"cupcake 1\":{\"direct_parent\":\"kitchen table 1\",\"direct_relation\":\"on\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"EATABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"]},\"kitchen 1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"floor 2\":{\"direct_parent\":\"kitchen 1\",\"direct_relation\":\"inside\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"SURFACES\"],\"is_container\":true,\"full_path\":[\"kitchen 1\"]},\"kitchen table 1\":{\"direct_parent\":\"floor 2\",\"direct_relation\":\"on\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"SURFACES\",\"MOVABLE\"],\"is_container\":true,\"full_path\":[\"kitchen 1\",\"floor 2\"]},\"cupcake 2\":{\"direct_parent\":\"kitchen table 1\",\"direct_relation\":\"on\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"EATABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"]},\"cupcake 3\":{\"direct_parent\":\"cabinet 1\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"EATABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"bedroom 1\",\"floor 16\",\"cabinet 1\"]},\"bedroom 1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"floor 16\":{\"direct_parent\":\"bedroom 1\",\"direct_relation\":\"inside\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"SURFACES\"],\"is_container\":true,\"full_path\":[\"bedroom 1\"]},\"cabinet 1\":{\"direct_parent\":\"floor 16\",\"direct_relation\":\"on\",\"type\":\"receptacle\",\"states\":{\"isOpen\":false},\"properties\":[\"SURFACES\",\"CAN_OPEN\",\"CONTAINERS\"],\"is_container\":true,\"full_path\":[\"bedroom 1\",\"floor 16\"]},\"apple 1\":{\"direct_parent\":\"fridge 1\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"kitchen 1\",\"floor 4\",\"fridge 1\"]},\"floor 4\":{\"direct_parent\":\"kitchen 1\",\"direct_relation\":\"inside\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"SURFACES\"],\"is_container\":true,\"full_path\":[\"kitchen 1\"]},\"fridge 1\":{\"direct_parent\":\"floor 4\",\"direct_relation\":\"on\",\"type\":\"receptacle\",\"states\":{\"isOpen\":false},\"properties\":[\"CAN_OPEN\",\"HAS_SWITCH\",\"CONTAINERS\",\"HAS_PLUG\"],\"is_container\":true,\"full_path\":[\"kitchen 1\",\"floor 4\"]},\"apple 2\":{\"direct_parent\":\"kitchen table 1\",\"direct_relation\":\"on\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"]},\"apple 3\":{\"direct_parent\":\"cabinet 1\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"bedroom 1\",\"floor 16\",\"cabinet 1\"]},\"coffee table 1\":{\"direct_parent\":\"floor 25\",\"direct_relation\":\"on\",\"type\":null,\"states\":{},\"properties\":[\"SURFACES\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"living room 1\",\"floor 25\"]},\"living room 1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"floor 25\":{\"direct_parent\":\"living room 1\",\"direct_relation\":\"inside\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"SURFACES\"],\"is_container\":true,\"full_path\":[\"living room 1\"]}}\n\n任务相关环境事实：\n[{\"name\":\"apple 1\",\"direct_parent\":\"fridge 1\",\"full_path\":[\"kitchen 1\",\"floor 4\",\"fridge 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"apple 2\",\"direct_parent\":\"kitchen table 1\",\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"apple 3\",\"direct_parent\":\"cabinet 1\",\"full_path\":[\"bedroom 1\",\"floor 16\",\"cabinet 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"bedroom 1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"cabinet 1\",\"direct_parent\":\"floor 16\",\"full_path\":[\"bedroom 1\",\"floor 16\"],\"states\":{\"isOpen\":false},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"coffee table 1\",\"direct_parent\":\"floor 25\",\"full_path\":[\"living room 1\",\"floor 25\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"cupcake 1\",\"direct_parent\":\"kitchen table 1\",\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"cupcake 2\",\"direct_parent\":\"kitchen table 1\",\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"cupcake 3\",\"direct_parent\":\"cabinet 1\",\"full_path\":[\"bedroom 1\",\"floor 16\",\"cabinet 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"floor 16\",\"direct_parent\":\"bedroom 1\",\"full_path\":[\"bedroom 1\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"floor 2\",\"direct_parent\":\"kitchen 1\",\"full_path\":[\"kitchen 1\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"floor 25\",\"direct_parent\":\"living room 1\",\"full_path\":[\"living room 1\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"floor 4\",\"direct_parent\":\"kitchen 1\",\"full_path\":[\"kitchen 1\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"fridge 1\",\"direct_parent\":\"floor 4\",\"full_path\":[\"kitchen 1\",\"floor 4\"],\"states\":{\"isOpen\":false},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"kitchen 1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"kitchen table 1\",\"direct_parent\":\"floor 2\",\"full_path\":[\"kitchen 1\",\"floor 2\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"living room 1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false}]\n\n任务上下文：\n{\n  \"dataset\": \"reactree\",\n  \"env_id\": 3,\n  \"task_name\": \"prepare_snack\",\n  \"instruction\": \"Put one cupcake and one apple on the coffee table\",\n  \"init_room\": \"bedroom\",\n  \"task_source\": \"reactree_wah_testset\",\n  \"environment_source\": \"reactree_case_runtime_scene\",\n  \"init_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json\",\n  \"task_goal\": {\n    \"on_cupcake_coffeetable\": 1,\n    \"on_apple_coffeetable\": 1\n  },\n  \"available_entities\": [\n    \"apple 1\",\n    \"apple 2\",\n    \"apple 3\",\n    \"bananas 1\",\n    \"bar soap 1\",\n    \"bathroom 1\",\n    \"bathroom cabinet 1\",\n    \"bathroom counter 1\",\n    \"bed 1\",\n    \"bedroom 1\",\n    \"book 1\",\n    \"book 2\",\n    \"bookshelf 1\",\n    \"bookshelf 2\",\n    \"bookshelf 3\",\n    \"bowl 1\",\n    \"bowl 2\",\n    \"bowl 3\",\n    \"bowl 4\",\n    \"bowl 5\",\n    \"bowl 6\",\n    \"bowl 7\",\n    \"bowl 8\",\n    \"bowl 9\",\n    \"box 1\",\n    \"box 2\",\n    \"box 3\",\n    \"box 4\",\n    \"box 5\",\n    \"bucket 1\",\n    \"cabinet 1\",\n    \"candle 1\",\n    \"candy bar 1\",\n    \"ceiling 1\",\n    \"ceiling 10\",\n    \"ceiling 11\",\n    \"ceiling 12\",\n    \"ceiling 13\",\n    \"ceiling 14\",\n    \"ceiling 15\",\n    \"ceiling 16\",\n    \"ceiling 17\",\n    \"ceiling 18\",\n    \"ceiling 19\",\n    \"ceiling 2\",\n    \"ceiling 20\",\n    \"ceiling 21\",\n    \"ceiling 22\",\n    \"ceiling 23\",\n    \"ceiling 24\",\n    \"ceiling 25\",\n    \"ceiling 26\",\n    \"ceiling 3\",\n    \"ceiling 4\",\n    \"ceiling 5\",\n    \"ceiling 6\",\n    \"ceiling 7\",\n    \"ceiling 8\",\n    \"ceiling 9\",\n    \"ceiling lamp 1\",\n    \"ceiling lamp 2\",\n    \"ceiling lamp 3\",\n    \"ceiling lamp 4\",\n    \"ceiling lamp 5\",\n    \"cell phone 1\",\n    \"cell phone 2\",\n    \"cereal 1\",\n    \"chair 1\",\n    \"chair 2\",\n    \"chair 3\",\n    \"chair 4\",\n    \"chair 5\",\n    \"chair 6\",\n    \"chips 1\",\n    \"chips 2\",\n    \"chocolate syrup 1\",\n    \"closet 1\",\n    \"closet drawer 1\",\n    \"closet drawer 2\",\n    \"closet drawer 3\",\n    \"closet drawer 4\",\n    \"closet drawer 5\",\n    \"closet drawer 6\",\n    \"closet drawer 7\",\n    \"coffee maker 1\",\n    \"coffee pot 1\",\n    \"coffee table 1\",\n    \"computer 1\",\n    \"condiment bottle 1\",\n    \"condiment bottle 2\",\n    \"condiment bottle 3\",\n    \"condiment bottle 4\",\n    \"condiment shaker 1\",\n    \"condiment shaker 2\",\n    \"condiment shaker 3\",\n    \"condiment shaker 4\",\n    \"cooking pot 1\",\n    \"cooking pot 2\",\n    \"cpu screen 1\",\n    \"crackers 1\",\n    \"crackers 2\",\n    \"creamy buns 1\",\n    \"cupcake 1\",\n    \"cupcake 2\",\n    \"cupcake 3\",\n    \"curtains 1\",\n    \"curtains 2\",\n    \"curtains 3\",\n    \"curtains 4\",\n    \"curtains 5\",\n    \"curtains 6\",\n    \"curtains 7\",\n    \"cutlery fork 1\",\n    \"cutlery fork 2\",\n    \"cutlery fork 3\",\n    \"cutlery fork 4\",\n    \"cutlery knife 1\",\n    \"cutlery knife 2\",\n    \"cutlery knife 3\",\n    \"cutlery knife 4\",\n    \"cutlery knife 5\",\n    \"cutlery knife 6\",\n    \"cutlets 1\",\n    \"deodorant 1\",\n    \"deodorant 2\",\n    \"deodorant 3\",\n    \"desk 1\",\n    \"desk 2\",\n    \"dishwasher 1\",\n    \"dishwashing liquid 1\",\n    \"door 1\",\n    \"door 2\",\n    \"door 3\",\n    \"door jamb 1\",\n    \"door jamb 2\",\n    \"door jamb 3\",\n    \"door jamb 4\",\n    \"face cream 1\",\n    \"face cream 2\",\n    \"face cream 3\",\n    \"faucet 1\",\n    \"faucet 2\",\n    \"floor 1\",\n    \"floor 10\",\n    \"floor 11\",\n    \"floor 12\",\n    \"floor 13\",\n    \"floor 14\",\n    \"floor 15\",\n    \"floor 16\",\n    \"floor 17\",\n    \"floor 18\",\n    \"floor 19\",\n    \"floor 2\",\n    \"floor 20\",\n    \"floor 21\",\n    \"floor 22\",\n    \"floor 23\",\n    \"floor 24\",\n    \"floor 25\",\n    \"floor 26\",\n    \"floor 3\",\n    \"floor 4\",\n    \"floor 5\",\n    \"floor 6\",\n    \"floor 7\",\n    \"floor 8\",\n    \"floor 9\",\n    \"folder 1\",\n    \"folder 2\",\n    \"folder 3\",\n    \"folder 4\",\n    \"fridge 1\",\n    \"frying pan 1\",\n    \"hair product 1\",\n    \"hair product 2\",\n    \"hair product 3\",\n    \"hair product 4\",\n    \"hanger 1\",\n    \"hanger 2\",\n    \"hanger 3\",\n    \"hanger 4\",\n    \"hanger 5\",\n    \"hanger 6\",\n    \"hanger 7\",\n    \"juice 1\",\n    \"juice 2\",\n    \"keyboard 1\",\n    \"kitchen 1\",\n    \"kitchen cabinet 1\",\n    \"kitchen cabinet 2\",\n    \"kitchen cabinet 3\",\n    \"kitchen cabinet 4\",\n    \"kitchen cabinet 5\",\n    \"kitchen cabinet 6\",\n    \"kitchen cabinet 7\",\n    \"kitchen cabinet 8\",\n    \"kitchen counter 1\",\n    \"kitchen counter 2\",\n    \"kitchen counter 3\",\n    \"kitchen counter drawer 1\",\n    \"kitchen counter drawer 2\",\n    \"kitchen counter drawer 3\",\n    \"kitchen counter drawer 4\",\n    \"kitchen counter drawer 5\",\n    \"kitchen counter drawer 6\",\n    \"kitchen counter drawer 7\",\n    \"kitchen counter drawer 8\",\n    \"kitchen table 1\",\n    \"knife block 1\",\n    \"light switch 1\",\n    \"light switch 2\",\n    \"light switch 3\",\n    \"light switch 4\",\n    \"lime 1\",\n    \"living room 1\",\n    \"microwave oven 1\",\n    \"milk 1\",\n    \"mouse 1\",\n    \"mouse mat 1\",\n    \"mug 1\",\n    \"mug 2\",\n    \"mug 3\",\n    \"nightstand 1\",\n    \"nightstand 2\",\n    \"nightstand 3\",\n    \"nightstand 4\",\n    \"notes 1\",\n    \"orchid 1\",\n    \"oven tray 1\",\n    \"painkillers 1\",\n    \"pancake 1\",\n    \"peach 1\",\n    \"peach 2\",\n    \"peach 3\",\n    \"pear 1\",\n    \"perfume 1\",\n    \"perfume 2\",\n    \"photo frame 1\",\n    \"photo frame 2\",\n    \"photo frame 3\",\n    \"pile of clothes 1\",\n    \"pile of clothes 2\",\n    \"pillow 1\",\n    \"pillow 2\",\n    \"pillow 3\",\n    \"pillow 4\",\n    \"pillow 5\",\n    \"pillow 6\",\n    \"plate 1\",\n    \"plate 2\",\n    \"plate 3\",\n    \"plate 4\",\n    \"plate 5\",\n    \"plate 6\",\n    \"plate 7\",\n    \"plum 1\",\n    \"plum 2\",\n    \"power socket 1\",\n    \"power socket 2\",\n    \"power socket 3\",\n    \"pudding 1\",\n    \"pudding 2\",\n    \"radio 1\",\n    \"rug 1\",\n    \"rug 2\",\n    \"rug 3\",\n    \"rug 4\",\n    \"sink 1\",\n    \"sink 2\",\n    \"slice of bread 1\",\n    \"slice of bread 2\",\n    \"sofa 1\",\n    \"sofa 2\",\n    \"sofa 3\",\n    \"stall 1\",\n    \"stall 2\",\n    \"stove 1\",\n    \"stove fan 1\",\n    \"table lamp 1\",\n    \"toaster 1\",\n    \"toilet 1\",\n    \"toilet paper 1\",\n    \"toothbrush 1\",\n    \"toothpaste 1\",\n    \"tv 1\",\n    \"tv stand 1\",\n    \"wall 1\",\n    \"wall 10\",\n    \"wall 11\",\n    \"wall 12\",\n    \"wall 13\",\n    \"wall 14\",\n    \"wall 15\",\n    \"wall 16\",\n    \"wall 17\",\n    \"wall 18\",\n    \"wall 19\",\n    \"wall 2\",\n    \"wall 20\",\n    \"wall 21\",\n    \"wall 22\",\n    \"wall 23\",\n    \"wall 24\",\n    \"wall 25\",\n    \"wall 26\",\n    \"wall 3\",\n    \"wall 4\",\n    \"wall 5\",\n    \"wall 6\",\n    \"wall 7\",\n    \"wall 8\",\n    \"wall 9\",\n    \"wall lamp 1\",\n    \"wall lamp 2\",\n    \"wall lamp 3\",\n    \"wall lamp 4\",\n    \"wall lamp 5\",\n    \"wall lamp 6\",\n    \"wall lamp 7\",\n    \"wall lamp 8\",\n    \"wall lamp 9\",\n    \"wall phone 1\",\n    \"wall picture frame 1\",\n    \"wall picture frame 2\",\n    \"wall picture frame 3\",\n    \"wall picture frame 4\",\n    \"wall picture frame 5\",\n    \"wall picture frame 6\",\n    \"wall picture frame 7\",\n    \"wall picture frame 8\",\n    \"wall shelf 1\",\n    \"wall shelf 2\",\n    \"washing machine 1\",\n    \"washing sponge 1\",\n    \"water glass 1\",\n    \"water glass 2\",\n    \"water glass 3\",\n    \"water glass 4\",\n    \"water glass 5\",\n    \"window 1\",\n    \"window 2\",\n    \"wine 1\"\n  ]\n}\n\n理解层实体选择：\n{\n  \"targets\": {\n    \"primary\": [\n      \"cupcake 1\",\n      \"apple 1\"\n    ],\n    \"alternatives\": []\n  },\n  \"tools\": {\n    \"primary\": [],\n    \"alternatives\": []\n  },\n  \"receptacles\": {\n    \"primary\": [\n      \"coffee table 1\"\n    ],\n    \"alternatives\": []\n  }\n}\n\n可用动作与 skill 契约：\n<available_skills>\n---\nname: go to\ndescription: Official ReAcTree WAH navigation action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `go to`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `go to` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的房间或对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 只有在目标位置或交互锚点当前不可直接到达时，才应导航。\n- 如果机器人已经处于同一个可交互位置簇，不要重复导航。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，模拟机器人位置应更新到该 WAH 官方实体。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"go to\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: pick up\ndescription: Official ReAcTree WAH pickup action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `pick up`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `pick up` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 目标必须具备 WAH `GRABBABLE` 属性；桌面、房间、灯、容器本身不能被当作普通可拿取物。\n- 目标物体必须可达；当前机器人位置、目标父节点以及对应手或携带槽位必须满足 handler 校验。\n- 如果目标位于关闭的 `CAN_OPEN` 容器内，`pick up` 会被 handler 拒绝。\n- 如果 benchmark 使用多只手，必须依据各只手的占用状态判断，而不是假设只有一个抓手。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，目标物体会进入对应手或携带槽位。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"pick up\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: put down\ndescription: Official ReAcTree WAH put-down action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `put down`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `put down` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 机器人当前必须已经持有或携带该步引用的物体。\n- `put down` 的目标位置由当前机器人位置决定；当前位置不满足放置条件时 handler 必须拒绝。\n- 如果当前位置是关闭的 `CAN_OPEN` 容器，handler 必须拒绝该步。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"put down\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: open\ndescription: Official ReAcTree WAH open action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `open`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `open` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 目标对象必须具备 WAH `CAN_OPEN` 属性，且当前不是已打开状态。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"open\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: close\ndescription: Official ReAcTree WAH close action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `close`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `close` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 目标对象必须具备 WAH `CAN_OPEN` 属性，且当前不是已关闭状态。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"close\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: turn on\ndescription: Official ReAcTree WAH turn-on action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `turn on`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `turn on` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 目标对象必须具备 WAH `HAS_SWITCH` 属性，当前不是已开启状态，并且机器人必须空手。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"turn on\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: turn off\ndescription: Official ReAcTree WAH turn-off action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `turn off`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `turn off` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 目标对象必须具备 WAH `HAS_SWITCH` 属性，当前不是已关闭状态，并且机器人必须空手。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"turn off\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: clean\ndescription: Official ReAcTree WAH clean action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `clean`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `clean` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 所需工具、液体状态或清洁装置状态，必须已经满足 handler 的校验规则。\n- 不要假设工具会自动变湿、变干净或自动可用；只有已验证步骤造成的状态变化才有效。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，会按 handler 约定更新清洁、浸湿或相关状态标志。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"clean\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n</available_skills>\n\n历史失败反馈：\n暂无相关拦截记录\n\n规划边界：\n1. 只使用 <available_skills> 中列出的动作。\n2. 动作参数、前置条件、状态依赖和效果只以对应 skill 契约为准。\n3. 只引用当前环境、任务上下文、任务相关环境事实或理解层结果中出现的实体/房间/对象名。\n4. 如果已有修复反馈或修复状态，只生成尚未验证的后续动作。\n\n输出格式：\n直接输出 WAH/ReAcTree 原生动作 JSON 数组。\n每个元素只能包含 action 和 target。\n如果任务已经完成，返回 []。"
  },
  {
    "type": "human",
    "content": "开始规划。"
  }
]
```

#### Output
```text
[
  {"action": "go to", "target": "kitchen table 1"},
  {"action": "pick up", "target": "cupcake 1"},
  {"action": "go to", "target": "coffee table 1"},
  {"action": "put down", "target": "cupcake 1"},
  {"action": "go to", "target": "kitchen table 1"},
  {"action": "pick up", "target": "apple 2"},
  {"action": "go to", "target": "coffee table 1"},
  {"action": "put down", "target": "apple 2"}
]
```

### Turn 4: planning

#### Input
```json
[
  {
    "type": "human",
    "content": "任务：根据 WAH/ReAcTree sandbox 前后状态差异判断任务是否完成。\n只输出 JSON；不要解释，不要生成动作。\n\n任务目标：Put one cupcake and one apple on the coffee table\n\n完整 native action 计划摘要：\n[\n  {\n    \"action\": \"go to\",\n    \"target\": \"kitchen table 1\"\n  },\n  {\n    \"action\": \"pick up\",\n    \"target\": \"cupcake 1\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"coffee table 1\"\n  },\n  {\n    \"action\": \"put down\",\n    \"target\": \"cupcake 1\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"kitchen table 1\"\n  },\n  {\n    \"action\": \"pick up\",\n    \"target\": \"apple 2\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"coffee table 1\"\n  },\n  {\n    \"action\": \"put down\",\n    \"target\": \"apple 2\"\n  }\n]\n\n本轮实际模拟步骤：\n[\n  {\n    \"action\": \"go to\",\n    \"target\": \"kitchen table 1\"\n  },\n  {\n    \"action\": \"pick up\",\n    \"target\": \"cupcake 1\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"coffee table 1\"\n  },\n  {\n    \"action\": \"put down\",\n    \"target\": \"cupcake 1\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"kitchen table 1\"\n  },\n  {\n    \"action\": \"pick up\",\n    \"target\": \"apple 2\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"coffee table 1\"\n  },\n  {\n    \"action\": \"put down\",\n    \"target\": \"apple 2\"\n  }\n]\n\n轨迹摘要：\nStep 1: go to([])\nStep 2: pick up([])\nStep 3: go to([])\nStep 4: put down([])\nStep 5: go to([])\nStep 6: pick up([])\nStep 7: go to([])\nStep 8: put down([])\n\nWAH 状态差异 JSON：\n{\n  \"entity_count_compared\": 17,\n  \"changed_entity_count\": 2,\n  \"truncated_entity_count\": 0,\n  \"has_changes\": true,\n  \"robot\": {\n    \"changed\": true,\n    \"before\": {\n      \"robot_location\": \"bedroom 1\",\n      \"robot_holding\": \"空\"\n    },\n    \"after\": {\n      \"robot_location\": \"coffee table 1\",\n      \"robot_holding\": \"空\"\n    }\n  },\n  \"entities\": [\n    {\n      \"name\": \"apple 2\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"coffee table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      }\n    },\n    {\n      \"name\": \"cupcake 1\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"EATABLE\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"coffee table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"EATABLE\",\n          \"MOVABLE\"\n        ]\n      }\n    }\n  ]\n}\n\n状态审计上下文 JSON：\n{\n  \"entity_count_available\": 17,\n  \"entity_count_in_context\": 9,\n  \"truncated_entity_count\": 0,\n  \"note\": \"state_diff only lists changed entities; unchanged entities in this context still prove final goal state when their after state satisfies the task.\",\n  \"robot\": {\n    \"changed\": true,\n    \"before\": {\n      \"robot_location\": \"bedroom 1\",\n      \"robot_holding\": \"空\"\n    },\n    \"after\": {\n      \"robot_location\": \"coffee table 1\",\n      \"robot_holding\": \"空\"\n    }\n  },\n  \"entities\": [\n    {\n      \"name\": \"cupcake 1\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"EATABLE\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"coffee table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"EATABLE\",\n          \"MOVABLE\"\n        ]\n      }\n    },\n    {\n      \"name\": \"apple 1\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"fridge 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 4\",\n          \"fridge 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"fridge 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 4\",\n          \"fridge 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      }\n    },\n    {\n      \"name\": \"coffee table 1\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"floor 25\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"living room 1\",\n          \"floor 25\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"floor 25\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"living room 1\",\n          \"floor 25\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\",\n          \"MOVABLE\"\n        ]\n      }\n    },\n    {\n      \"name\": \"floor 25\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"living room 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"living room 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\"\n        ]\n      },\n      \"after\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"living room 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"living room 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\"\n        ]\n      }\n    },\n    {\n      \"name\": \"living room 1\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      },\n      \"after\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      }\n    },\n    {\n      \"name\": \"fridge 1\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"floor 4\",\n        \"direct_relation\": \"on\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 4\"\n        ],\n        \"states\": {\n          \"isOpen\": false\n        },\n        \"properties\": [\n          \"CAN_OPEN\",\n          \"HAS_SWITCH\",\n          \"CONTAINERS\",\n          \"HAS_PLUG\"\n        ]\n      },\n      \"after\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"floor 4\",\n        \"direct_relation\": \"on\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 4\"\n        ],\n        \"states\": {\n          \"isOpen\": false\n        },\n        \"properties\": [\n          \"CAN_OPEN\",\n          \"HAS_SWITCH\",\n          \"CONTAINERS\",\n          \"HAS_PLUG\"\n        ]\n      }\n    },\n    {\n      \"name\": \"floor 4\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"kitchen 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"kitchen 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\"\n        ]\n      },\n      \"after\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"kitchen 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"kitchen 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\"\n        ]\n      }\n    },\n    {\n      \"name\": \"kitchen 1\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      },\n      \"after\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      }\n    },\n    {\n      \"name\": \"apple 2\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"coffee table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      }\n    }\n  ],\n  \"task_context\": {\n    \"dataset\": \"reactree\",\n    \"env_id\": 3,\n    \"task_name\": \"prepare_snack\",\n    \"instruction\": \"Put one cupcake and one apple on the coffee table\",\n    \"init_room\": \"bedroom\",\n    \"task_source\": \"reactree_wah_testset\",\n    \"environment_source\": \"reactree_case_runtime_scene\",\n    \"init_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json\",\n    \"task_goal\": {\n      \"on_cupcake_coffeetable\": 1,\n      \"on_apple_coffeetable\": 1\n    },\n    \"available_entities\": [\n      \"apple 1\",\n      \"apple 2\",\n      \"apple 3\",\n      \"bananas 1\",\n      \"bar soap 1\",\n      \"bathroom 1\",\n      \"bathroom cabinet 1\",\n      \"bathroom counter 1\",\n      \"bed 1\",\n      \"bedroom 1\",\n      \"book 1\",\n      \"book 2\",\n      \"bookshelf 1\",\n      \"bookshelf 2\",\n      \"bookshelf 3\",\n      \"bowl 1\",\n      \"bowl 2\",\n      \"bowl 3\",\n      \"bowl 4\",\n      \"bowl 5\",\n      \"bowl 6\",\n      \"bowl 7\",\n      \"bowl 8\",\n      \"bowl 9\",\n      \"box 1\",\n      \"box 2\",\n      \"box 3\",\n      \"box 4\",\n      \"box 5\",\n      \"bucket 1\",\n      \"cabinet 1\",\n      \"candle 1\",\n      \"candy bar 1\",\n      \"ceiling 1\",\n      \"ceiling 10\",\n      \"ceiling 11\",\n      \"ceiling 12\",\n      \"ceiling 13\",\n      \"ceiling 14\",\n      \"ceiling 15\",\n      \"ceiling 16\",\n      \"ceiling 17\",\n      \"ceiling 18\",\n      \"ceiling 19\",\n      \"ceiling 2\",\n      \"ceiling 20\",\n      \"ceiling 21\",\n      \"ceiling 22\",\n      \"ceiling 23\",\n      \"ceiling 24\",\n      \"ceiling 25\",\n      \"ceiling 26\",\n      \"ceiling 3\",\n      \"ceiling 4\",\n      \"ceiling 5\",\n      \"ceiling 6\",\n      \"ceiling 7\",\n      \"ceiling 8\",\n      \"ceiling 9\",\n      \"ceiling lamp 1\",\n      \"ceiling lamp 2\",\n      \"ceiling lamp 3\",\n      \"ceiling lamp 4\",\n      \"ceiling lamp 5\",\n      \"cell phone 1\",\n      \"cell phone 2\",\n      \"cereal 1\",\n      \"chair 1\",\n      \"chair 2\",\n      \"chair 3\",\n      \"chair 4\",\n      \"chair 5\",\n      \"chair 6\",\n      \"chips 1\",\n      \"chips 2\",\n      \"chocolate syrup 1\",\n      \"closet 1\",\n      \"closet drawer 1\",\n      \"closet drawer 2\",\n      \"closet drawer 3\",\n      \"closet drawer 4\",\n      \"closet drawer 5\",\n      \"closet drawer 6\",\n      \"closet drawer 7\",\n      \"coffee maker 1\",\n      \"coffee pot 1\",\n      \"coffee table 1\",\n      \"computer 1\",\n      \"condiment bottle 1\",\n      \"condiment bottle 2\",\n      \"condiment bottle 3\",\n      \"condiment bottle 4\",\n      \"condiment shaker 1\",\n      \"condiment shaker 2\",\n      \"condiment shaker 3\",\n      \"condiment shaker 4\",\n      \"cooking pot 1\",\n      \"cooking pot 2\",\n      \"cpu screen 1\",\n      \"crackers 1\",\n      \"crackers 2\",\n      \"creamy buns 1\",\n      \"cupcake 1\",\n      \"cupcake 2\",\n      \"cupcake 3\",\n      \"curtains 1\",\n      \"curtains 2\",\n      \"curtains 3\",\n      \"curtains 4\",\n      \"curtains 5\",\n      \"curtains 6\",\n      \"curtains 7\",\n      \"cutlery fork 1\",\n      \"cutlery fork 2\",\n      \"cutlery fork 3\",\n      \"cutlery fork 4\",\n      \"cutlery knife 1\",\n      \"cutlery knife 2\",\n      \"cutlery knife 3\",\n      \"cutlery knife 4\",\n      \"cutlery knife 5\",\n      \"cutlery knife 6\",\n      \"cutlets 1\",\n      \"deodorant 1\",\n      \"deodorant 2\",\n      \"deodorant 3\",\n      \"desk 1\",\n      \"desk 2\",\n      \"dishwasher 1\",\n      \"dishwashing liquid 1\",\n      \"door 1\",\n      \"door 2\",\n      \"door 3\",\n      \"door jamb 1\",\n      \"door jamb 2\",\n      \"door jamb 3\",\n      \"door jamb 4\",\n      \"face cream 1\",\n      \"face cream 2\",\n      \"face cream 3\",\n      \"faucet 1\",\n      \"faucet 2\",\n      \"floor 1\",\n      \"floor 10\",\n      \"floor 11\",\n      \"floor 12\",\n      \"floor 13\",\n      \"floor 14\",\n      \"floor 15\",\n      \"floor 16\",\n      \"floor 17\",\n      \"floor 18\",\n      \"floor 19\",\n      \"floor 2\",\n      \"floor 20\",\n      \"floor 21\",\n      \"floor 22\",\n      \"floor 23\",\n      \"floor 24\",\n      \"floor 25\",\n      \"floor 26\",\n      \"floor 3\",\n      \"floor 4\",\n      \"floor 5\",\n      \"floor 6\",\n      \"floor 7\",\n      \"floor 8\",\n      \"floor 9\",\n      \"folder 1\",\n      \"folder 2\",\n      \"folder 3\",\n      \"folder 4\",\n      \"fridge 1\",\n      \"frying pan 1\",\n      \"hair product 1\",\n      \"hair product 2\",\n      \"hair product 3\",\n      \"hair product 4\",\n      \"hanger 1\",\n      \"hanger 2\",\n      \"hanger 3\",\n      \"hanger 4\",\n      \"hanger 5\",\n      \"hanger 6\",\n      \"hanger 7\",\n      \"juice 1\",\n      \"juice 2\",\n      \"keyboard 1\",\n      \"kitchen 1\",\n      \"kitchen cabinet 1\",\n      \"kitchen cabinet 2\",\n      \"kitchen cabinet 3\",\n      \"kitchen cabinet 4\",\n      \"kitchen cabinet 5\",\n      \"kitchen cabinet 6\",\n      \"kitchen cabinet 7\",\n      \"kitchen cabinet 8\",\n      \"kitchen counter 1\",\n      \"kitchen counter 2\",\n      \"kitchen counter 3\",\n      \"kitchen counter drawer 1\",\n      \"kitchen counter drawer 2\",\n      \"kitchen counter drawer 3\",\n      \"kitchen counter drawer 4\",\n      \"kitchen counter drawer 5\",\n      \"kitchen counter drawer 6\",\n      \"kitchen counter drawer 7\",\n      \"kitchen counter drawer 8\",\n      \"kitchen table 1\",\n      \"knife block 1\",\n      \"light switch 1\",\n      \"light switch 2\",\n      \"light switch 3\",\n      \"light switch 4\",\n      \"lime 1\",\n      \"living room 1\",\n      \"microwave oven 1\",\n      \"milk 1\",\n      \"mouse 1\",\n      \"mouse mat 1\",\n      \"mug 1\",\n      \"mug 2\",\n      \"mug 3\",\n      \"nightstand 1\",\n      \"nightstand 2\",\n      \"nightstand 3\",\n      \"nightstand 4\",\n      \"notes 1\",\n      \"orchid 1\",\n      \"oven tray 1\",\n      \"painkillers 1\",\n      \"pancake 1\",\n      \"peach 1\",\n      \"peach 2\",\n      \"peach 3\",\n      \"pear 1\",\n      \"perfume 1\",\n      \"perfume 2\",\n      \"photo frame 1\",\n      \"photo frame 2\",\n      \"photo frame 3\",\n      \"pile of clothes 1\",\n      \"pile of clothes 2\",\n      \"pillow 1\",\n      \"pillow 2\",\n      \"pillow 3\",\n      \"pillow 4\",\n      \"pillow 5\",\n      \"pillow 6\",\n      \"plate 1\",\n      \"plate 2\",\n      \"plate 3\",\n      \"plate 4\",\n      \"plate 5\",\n      \"plate 6\",\n      \"plate 7\",\n      \"plum 1\",\n      \"plum 2\",\n      \"power socket 1\",\n      \"power socket 2\",\n      \"power socket 3\",\n      \"pudding 1\",\n      \"pudding 2\",\n      \"radio 1\",\n      \"rug 1\",\n      \"rug 2\",\n      \"rug 3\",\n      \"rug 4\",\n      \"sink 1\",\n      \"sink 2\",\n      \"slice of bread 1\",\n      \"slice of bread 2\",\n      \"sofa 1\",\n      \"sofa 2\",\n      \"sofa 3\",\n      \"stall 1\",\n      \"stall 2\",\n      \"stove 1\",\n      \"stove fan 1\",\n      \"table lamp 1\",\n      \"toaster 1\",\n      \"toilet 1\",\n      \"toilet paper 1\",\n      \"toothbrush 1\",\n      \"toothpaste 1\",\n      \"tv 1\",\n      \"tv stand 1\",\n      \"wall 1\",\n      \"wall 10\",\n      \"wall 11\",\n      \"wall 12\",\n      \"wall 13\",\n      \"wall 14\",\n      \"wall 15\",\n      \"wall 16\",\n      \"wall 17\",\n      \"wall 18\",\n      \"wall 19\",\n      \"wall 2\",\n      \"wall 20\",\n      \"wall 21\",\n      \"wall 22\",\n      \"wall 23\",\n      \"wall 24\",\n      \"wall 25\",\n      \"wall 26\",\n      \"wall 3\",\n      \"wall 4\",\n      \"wall 5\",\n      \"wall 6\",\n      \"wall 7\",\n      \"wall 8\",\n      \"wall 9\",\n      \"wall lamp 1\",\n      \"wall lamp 2\",\n      \"wall lamp 3\",\n      \"wall lamp 4\",\n      \"wall lamp 5\",\n      \"wall lamp 6\",\n      \"wall lamp 7\",\n      \"wall lamp 8\",\n      \"wall lamp 9\",\n      \"wall phone 1\",\n      \"wall picture frame 1\",\n      \"wall picture frame 2\",\n      \"wall picture frame 3\",\n      \"wall picture frame 4\",\n      \"wall picture frame 5\",\n      \"wall picture frame 6\",\n      \"wall picture frame 7\",\n      \"wall picture frame 8\",\n      \"wall shelf 1\",\n      \"wall shelf 2\",\n      \"washing machine 1\",\n      \"washing sponge 1\",\n      \"water glass 1\",\n      \"water glass 2\",\n      \"water glass 3\",\n      \"water glass 4\",\n      \"water glass 5\",\n      \"window 1\",\n      \"window 2\",\n      \"wine 1\"\n    ]\n  },\n  \"evaluation_context\": {},\n  \"external_goal\": {\n    \"has_external_goal\": true,\n    \"external_goal_state\": {},\n    \"external_goal_text\": \"\",\n    \"structured_goal_state\": {},\n    \"structured_final_state\": {\n      \"on_cupcake_coffeetable\": 1,\n      \"on_apple_coffeetable\": 1\n    }\n  },\n  \"benchmark_final_state_compare\": {\n    \"benchmark\": \"ReAcTree-WAH\",\n    \"status\": \"prepared_for_framework_llm_judge\",\n    \"environment_format\": \"WAH runtime_initial_environment 的 scene/env_state，保留 WAH/VirtualHome 对象标签\",\n    \"action_format\": \"WAH/ReAcTree 原生动作 JSON 对象：{action, target}\",\n    \"official_evaluator\": \"ReAcTree WAH 官方 Unity evaluator\",\n    \"used_fields\": {\n      \"task_context\": [\n        \"available_entities\",\n        \"dataset\",\n        \"env_id\",\n        \"environment_source\",\n        \"init_graph_cache_path\",\n        \"init_room\",\n        \"instruction\",\n        \"task_goal\",\n        \"task_name\",\n        \"task_source\"\n      ],\n      \"evaluation_context\": [],\n      \"external_goal\": [\n        \"has_external_goal\",\n        \"structured_final_state\"\n      ],\n      \"state_diff\": [\n        \"entities\",\n        \"robot\"\n      ]\n    },\n    \"benchmark_goal\": {\n      \"task_context\": {\n        \"dataset\": \"reactree\",\n        \"env_id\": 3,\n        \"task_name\": \"prepare_snack\",\n        \"instruction\": \"Put one cupcake and one apple on the coffee table\",\n        \"init_room\": \"bedroom\",\n        \"task_source\": \"reactree_wah_testset\",\n        \"environment_source\": \"reactree_case_runtime_scene\",\n        \"init_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json\",\n        \"task_goal\": {\n          \"on_cupcake_coffeetable\": 1,\n          \"on_apple_coffeetable\": 1\n        },\n        \"available_entities\": [\n          \"apple 1\",\n          \"apple 2\",\n          \"apple 3\",\n          \"bananas 1\",\n          \"bar soap 1\",\n          \"bathroom 1\",\n          \"bathroom cabinet 1\",\n          \"bathroom counter 1\",\n          \"bed 1\",\n          \"bedroom 1\",\n          \"book 1\",\n          \"book 2\",\n          \"bookshelf 1\",\n          \"bookshelf 2\",\n          \"bookshelf 3\",\n          \"bowl 1\",\n          \"bowl 2\",\n          \"bowl 3\",\n          \"bowl 4\",\n          \"bowl 5\",\n          \"bowl 6\",\n          \"bowl 7\",\n          \"bowl 8\",\n          \"bowl 9\",\n          \"box 1\",\n          \"box 2\",\n          \"box 3\",\n          \"box 4\",\n          \"box 5\",\n          \"bucket 1\",\n          \"cabinet 1\",\n          \"candle 1\",\n          \"candy bar 1\",\n          \"ceiling 1\",\n          \"ceiling 10\",\n          \"ceiling 11\",\n          \"ceiling 12\",\n          \"ceiling 13\",\n          \"ceiling 14\",\n          \"ceiling 15\",\n          {\n            \"_truncated\": 303\n          }\n        ]\n      },\n      \"evaluation_context\": {},\n      \"goal_projection\": {},\n      \"external_goal\": {\n        \"has_external_goal\": true,\n        \"external_goal_state\": {},\n        \"external_goal_text\": \"\",\n        \"structured_goal_state\": {},\n        \"structured_final_state\": {\n          \"on_cupcake_coffeetable\": 1,\n          \"on_apple_coffeetable\": 1\n        }\n      }\n    },\n    \"understanding_final_state\": {\n      \"on_cupcake_coffeetable\": 1,\n      \"on_apple_coffeetable\": 1\n    },\n    \"state_diff_summary\": {\n      \"entity_count_compared\": 17,\n      \"changed_entity_count\": 2,\n      \"changed_entities\": [\n        \"apple 2\",\n        \"cupcake 1\"\n      ],\n      \"changed_entities_truncated\": false,\n      \"robot_changed\": true,\n      \"robot_change\": {\n        \"changed\": true,\n        \"before\": {\n          \"robot_location\": \"bedroom 1\",\n          \"robot_holding\": \"空\"\n        },\n        \"after\": {\n          \"robot_location\": \"coffee table 1\",\n          \"robot_holding\": \"空\"\n        }\n      }\n    },\n    \"initial_environment_summary\": {\n      \"available\": true,\n      \"entity_count\": 17,\n      \"type_counts\": {\n        \"unknown\": 7,\n        \"room\": 3,\n        \"receptacle\": 7\n      },\n      \"states_sample\": {\n        \"cabinet 1\": {\n          \"isOpen\": false\n        },\n        \"fridge 1\": {\n          \"isOpen\": false\n        }\n      },\n      \"relations_sample\": {\n        \"cupcake 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"kitchen table 1\"\n        },\n        \"kitchen 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 2\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen 1\"\n        },\n        \"kitchen table 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 2\"\n        },\n        \"cupcake 2\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"kitchen table 1\"\n        },\n        \"cupcake 3\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"cabinet 1\"\n        },\n        \"bedroom 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 16\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"bedroom 1\"\n        },\n        \"cabinet 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 16\"\n        },\n        \"apple 1\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"fridge 1\"\n        },\n        \"floor 4\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen 1\"\n        },\n        \"fridge 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 4\"\n        },\n        \"apple 2\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"kitchen table 1\"\n        },\n        \"apple 3\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"cabinet 1\"\n        },\n        \"coffee table 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 25\"\n        },\n        \"living room 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 25\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"living room 1\"\n        }\n      }\n    },\n    \"final_environment_summary\": {\n      \"available\": true,\n      \"entity_count\": 17,\n      \"type_counts\": {\n        \"unknown\": 7,\n        \"room\": 3,\n        \"receptacle\": 7\n      },\n      \"states_sample\": {\n        \"cabinet 1\": {\n          \"isOpen\": false\n        },\n        \"fridge 1\": {\n          \"isOpen\": false\n        }\n      },\n      \"relations_sample\": {\n        \"cupcake 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"coffee table 1\"\n        },\n        \"kitchen 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 2\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen 1\"\n        },\n        \"kitchen table 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 2\"\n        },\n        \"cupcake 2\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"kitchen table 1\"\n        },\n        \"cupcake 3\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"cabinet 1\"\n        },\n        \"bedroom 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 16\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"bedroom 1\"\n        },\n        \"cabinet 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 16\"\n        },\n        \"apple 1\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"fridge 1\"\n        },\n        \"floor 4\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen 1\"\n        },\n        \"fridge 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 4\"\n        },\n        \"apple 2\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"coffee table 1\"\n        },\n        \"apple 3\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"cabinet 1\"\n        },\n        \"coffee table 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 25\"\n        },\n        \"living room 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 25\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"living room 1\"\n        }\n      }\n    },\n    \"initial_robot\": {\n      \"robot_location\": \"bedroom 1\",\n      \"robot_holding\": \"空\"\n    },\n    \"final_robot\": {\n      \"robot_location\": \"coffee table 1\",\n      \"robot_holding\": \"空\"\n    },\n    \"fairness_notes\": [\n      \"task_goal 来自 WAH 官方评测目标，只作为最终态审计目标投影，不作为动作序列答案。\"\n    ],\n    \"judge_contract\": \"公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。\",\n    \"enabled\": true,\n    \"comparer_module\": \"benchmark.reactree.wah.framework.code.final_state\"\n  }\n}\n\n判定边界：\n1. 优先读取 state_audit_context.benchmark_final_state_compare；其中包含 WAH task_goal 和本地环境差异摘要。\n2. 结合 understanding final_state、task_goal、sandbox final environment/final robot 和 state_diff 判断关键目标是否完成。\n3. 不使用 expert trajectory 或官方动作答案；保持 WAH/ReAcTree 的对象命名和关系语义。\n4. 如果关键目标缺失，is_passed=false，并写出缺失的最终状态和后续 planning 应补的动作类型。\n5. 如果当前最终态只需追加动作即可修复，repair_mode=\"continue_from_current\"；如果已验证前缀本身错，repair_mode=\"reset_and_replan\"。\n\n输出 JSON：\n{\"is_passed\": true, \"issue\": \"\", \"fix_advice\": \"\", \"repair_mode\": \"continue_from_current\", \"accepted_diffs\": [], \"unexpected_diffs\": []}"
  }
]
```

#### Output
```text
{
  "is_passed": true,
  "issue": "",
  "fix_advice": "",
  "repair_mode": "continue_from_current",
  "accepted_diffs": [
    "cupcake 1 moved to coffee table 1",
    "apple 2 moved to coffee table 1"
  ],
  "unexpected_diffs": []
}
```

## 9. 初始提示词与后续修复提示

### Understanding 初始提示
```json
[
  {
    "type": "system",
    "content": "任务：把 WAH/ReAcTree benchmark case 输入抽取成结构化任务理解。\n只返回 JSON；不要解释，不要输出 Markdown。\n\n允许使用的 WAH 场景实体名：\n[\"apple 1\", \"apple 2\", \"apple 3\", \"bananas 1\", \"bar soap 1\", \"bathroom 1\", \"bathroom cabinet 1\", \"bathroom counter 1\", \"bed 1\", \"bedroom 1\", \"book 1\", \"book 2\", \"bookshelf 1\", \"bookshelf 2\", \"bookshelf 3\", \"bowl 1\", \"bowl 2\", \"bowl 3\", \"bowl 4\", \"bowl 5\", \"bowl 6\", \"bowl 7\", \"bowl 8\", \"bowl 9\", \"box 1\", \"box 2\", \"box 3\", \"box 4\", \"box 5\", \"bucket 1\", \"cabinet 1\", \"candle 1\", \"candy bar 1\", \"ceiling 1\", \"ceiling 10\", \"ceiling 11\", \"ceiling 12\", \"ceiling 13\", \"ceiling 14\", \"ceiling 15\", \"ceiling 16\", \"ceiling 17\", \"ceiling 18\", \"ceiling 19\", \"ceiling 2\", \"ceiling 20\", \"ceiling 21\", \"ceiling 22\", \"ceiling 23\", \"ceiling 24\", \"ceiling 25\", \"ceiling 26\", \"ceiling 3\", \"ceiling 4\", \"ceiling 5\", \"ceiling 6\", \"ceiling 7\", \"ceiling 8\", \"ceiling 9\", \"ceiling lamp 1\", \"ceiling lamp 2\", \"ceiling lamp 3\", \"ceiling lamp 4\", \"ceiling lamp 5\", \"cell phone 1\", \"cell phone 2\", \"cereal 1\", \"chair 1\", \"chair 2\", \"chair 3\", \"chair 4\", \"chair 5\", \"chair 6\", \"chips 1\", \"chips 2\", \"chocolate syrup 1\", \"closet 1\", \"closet drawer 1\", \"closet drawer 2\", \"closet drawer 3\", \"closet drawer 4\", \"closet drawer 5\", \"closet drawer 6\", \"closet drawer 7\", \"coffee maker 1\", \"coffee pot 1\", \"coffee table 1\", \"computer 1\", \"condiment bottle 1\", \"condiment bottle 2\", \"condiment bottle 3\", \"condiment bottle 4\", \"condiment shaker 1\", \"condiment shaker 2\", \"condiment shaker 3\", \"condiment shaker 4\", \"cooking pot 1\", \"cooking pot 2\", \"cpu screen 1\", \"crackers 1\", \"crackers 2\", \"creamy buns 1\", \"cupcake 1\", \"cupcake 2\", \"cupcake 3\", \"curtains 1\", \"curtains 2\", \"curtains 3\", \"curtains 4\", \"curtains 5\", \"curtains 6\", \"curtains 7\", \"cutlery fork 1\", \"cutlery fork 2\", \"cutlery fork 3\", \"cutlery fork 4\", \"cutlery knife 1\", \"cutlery knife 2\", \"cutlery knife 3\", \"cutlery knife 4\", \"cutlery knife 5\", \"cutlery knife 6\", \"cutlets 1\", \"deodorant 1\", \"deodorant 2\", \"deodorant 3\", \"desk 1\", \"desk 2\", \"dishwasher 1\", \"dishwashing liquid 1\", \"door 1\", \"door 2\", \"door 3\", \"door jamb 1\", \"door jamb 2\", \"door jamb 3\", \"door jamb 4\", \"face cream 1\", \"face cream 2\", \"face cream 3\", \"faucet 1\", \"faucet 2\", \"floor 1\", \"floor 10\", \"floor 11\", \"floor 12\", \"floor 13\", \"floor 14\", \"floor 15\", \"floor 16\", \"floor 17\", \"floor 18\", \"floor 19\", \"floor 2\", \"floor 20\", \"floor 21\", \"floor 22\", \"floor 23\", \"floor 24\", \"floor 25\", \"floor 26\", \"floor 3\", \"floor 4\", \"floor 5\", \"floor 6\", \"floor 7\", \"floor 8\", \"floor 9\", \"folder 1\", \"folder 2\", \"folder 3\", \"folder 4\", \"fridge 1\", \"frying pan 1\", \"hair product 1\", \"hair product 2\", \"hair product 3\", \"hair product 4\", \"hanger 1\", \"hanger 2\", \"hanger 3\", \"hanger 4\", \"hanger 5\", \"hanger 6\", \"hanger 7\", \"juice 1\", \"juice 2\", \"keyboard 1\", \"kitchen 1\", \"kitchen cabinet 1\", \"kitchen cabinet 2\", \"kitchen cabinet 3\", \"kitchen cabinet 4\", \"kitchen cabinet 5\", \"kitchen cabinet 6\", \"kitchen cabinet 7\", \"kitchen cabinet 8\", \"kitchen counter 1\", \"kitchen counter 2\", \"kitchen counter 3\", \"kitchen counter drawer 1\", \"kitchen counter drawer 2\", \"kitchen counter drawer 3\", \"kitchen counter drawer 4\", \"kitchen counter drawer 5\", \"kitchen counter drawer 6\", \"kitchen counter drawer 7\", \"kitchen counter drawer 8\", \"kitchen table 1\", \"knife block 1\", \"light switch 1\", \"light switch 2\", \"light switch 3\", \"light switch 4\", \"lime 1\", \"living room 1\", \"microwave oven 1\", \"milk 1\", \"mouse 1\", \"mouse mat 1\", \"mug 1\", \"mug 2\", \"mug 3\", \"nightstand 1\", \"nightstand 2\", \"nightstand 3\", \"nightstand 4\", \"notes 1\", \"orchid 1\", \"oven tray 1\", \"painkillers 1\", \"pancake 1\", \"peach 1\", \"peach 2\", \"peach 3\", \"pear 1\", \"perfume 1\", \"perfume 2\", \"photo frame 1\", \"photo frame 2\", \"photo frame 3\", \"pile of clothes 1\", \"pile of clothes 2\", \"pillow 1\", \"pillow 2\", \"pillow 3\", \"pillow 4\", \"pillow 5\", \"pillow 6\", \"plate 1\", \"plate 2\", \"plate 3\", \"plate 4\", \"plate 5\", \"plate 6\", \"plate 7\", \"plum 1\", \"plum 2\", \"power socket 1\", \"power socket 2\", \"power socket 3\", \"pudding 1\", \"pudding 2\", \"radio 1\", \"rug 1\", \"rug 2\", \"rug 3\", \"rug 4\", \"sink 1\", \"sink 2\", \"slice of bread 1\", \"slice of bread 2\", \"sofa 1\", \"sofa 2\", \"sofa 3\", \"stall 1\", \"stall 2\", \"stove 1\", \"stove fan 1\", \"table lamp 1\", \"toaster 1\", \"toilet 1\", \"toilet paper 1\", \"toothbrush 1\", \"toothpaste 1\", \"tv 1\", \"tv stand 1\", \"wall 1\", \"wall 10\", \"wall 11\", \"wall 12\", \"wall 13\", \"wall 14\", \"wall 15\", \"wall 16\", \"wall 17\", \"wall 18\", \"wall 19\", \"wall 2\", \"wall 20\", \"wall 21\", \"wall 22\", \"wall 23\", \"wall 24\", \"wall 25\", \"wall 26\", \"wall 3\", \"wall 4\", \"wall 5\", \"wall 6\", \"wall 7\", \"wall 8\", \"wall 9\", \"wall lamp 1\", \"wall lamp 2\", \"wall lamp 3\", \"wall lamp 4\", \"wall lamp 5\", \"wall lamp 6\", \"wall lamp 7\", \"wall lamp 8\", \"wall lamp 9\", \"wall phone 1\", \"wall picture frame 1\", \"wall picture frame 2\", \"wall picture frame 3\", \"wall picture frame 4\", \"wall picture frame 5\", \"wall picture frame 6\", \"wall picture frame 7\", \"wall picture frame 8\", \"wall shelf 1\", \"wall shelf 2\", \"washing machine 1\", \"washing sponge 1\", \"water glass 1\", \"water glass 2\", \"water glass 3\", \"water glass 4\", \"water glass 5\", \"window 1\", \"window 2\", \"wine 1\"]\n\nWAH 任务上下文 JSON：\n{\n  \"dataset\": \"reactree\",\n  \"env_id\": 3,\n  \"task_name\": \"prepare_snack\",\n  \"instruction\": \"Put one cupcake and one apple on the coffee table\",\n  \"init_room\": \"bedroom\",\n  \"task_source\": \"reactree_wah_testset\",\n  \"environment_source\": \"reactree_case_runtime_scene\",\n  \"init_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json\",\n  \"task_goal\": {\n    \"on_cupcake_coffeetable\": 1,\n    \"on_apple_coffeetable\": 1\n  },\n  \"available_entities\": [\n    \"apple 1\",\n    \"apple 2\",\n    \"apple 3\",\n    \"bananas 1\",\n    \"bar soap 1\",\n    \"bathroom 1\",\n    \"bathroom cabinet 1\",\n    \"bathroom counter 1\",\n    \"bed 1\",\n    \"bedroom 1\",\n    \"book 1\",\n    \"book 2\",\n    \"bookshelf 1\",\n    \"bookshelf 2\",\n    \"bookshelf 3\",\n    \"bowl 1\",\n    \"bowl 2\",\n    \"bowl 3\",\n    \"bowl 4\",\n    \"bowl 5\",\n    \"bowl 6\",\n    \"bowl 7\",\n    \"bowl 8\",\n    \"bowl 9\",\n    \"box 1\",\n    \"box 2\",\n    \"box 3\",\n    \"box 4\",\n    \"box 5\",\n    \"bucket 1\",\n    \"cabinet 1\",\n    \"candle 1\",\n    \"candy bar 1\",\n    \"ceiling 1\",\n    \"ceiling 10\",\n    \"ceiling 11\",\n    \"ceiling 12\",\n    \"ceiling 13\",\n    \"ceiling 14\",\n    \"ceiling 15\",\n    \"ceiling 16\",\n    \"ceiling 17\",\n    \"ceiling 18\",\n    \"ceiling 19\",\n    \"ceiling 2\",\n    \"ceiling 20\",\n    \"ceiling 21\",\n    \"ceiling 22\",\n    \"ceiling 23\",\n    \"ceiling 24\",\n    \"ceiling 25\",\n    \"ceiling 26\",\n    \"ceiling 3\",\n    \"ceiling 4\",\n    \"ceiling 5\",\n    \"ceiling 6\",\n    \"ceiling 7\",\n    \"ceiling 8\",\n    \"ceiling 9\",\n    \"ceiling lamp 1\",\n    \"ceiling lamp 2\",\n    \"ceiling lamp 3\",\n    \"ceiling lamp 4\",\n    \"ceiling lamp 5\",\n    \"cell phone 1\",\n    \"cell phone 2\",\n    \"cereal 1\",\n    \"chair 1\",\n    \"chair 2\",\n    \"chair 3\",\n    \"chair 4\",\n    \"chair 5\",\n    \"chair 6\",\n    \"chips 1\",\n    \"chips 2\",\n    \"chocolate syrup 1\",\n    \"closet 1\",\n    \"closet drawer 1\",\n    \"closet drawer 2\",\n    \"closet drawer 3\",\n    \"closet drawer 4\",\n    \"closet drawer 5\",\n    \"closet drawer 6\",\n    \"closet drawer 7\",\n    \"coffee maker 1\",\n    \"coffee pot 1\",\n    \"coffee table 1\",\n    \"computer 1\",\n    \"condiment bottle 1\",\n    \"condiment bottle 2\",\n    \"condiment bottle 3\",\n    \"condiment bottle 4\",\n    \"condiment shaker 1\",\n    \"condiment shaker 2\",\n    \"condiment shaker 3\",\n    \"condiment shaker 4\",\n    \"cooking pot 1\",\n    \"cooking pot 2\",\n    \"cpu screen 1\",\n    \"crackers 1\",\n    \"crackers 2\",\n    \"creamy buns 1\",\n    \"cupcake 1\",\n    \"cupcake 2\",\n    \"cupcake 3\",\n    \"curtains 1\",\n    \"curtains 2\",\n    \"curtains 3\",\n    \"curtains 4\",\n    \"curtains 5\",\n    \"curtains 6\",\n    \"curtains 7\",\n    \"cutlery fork 1\",\n    \"cutlery fork 2\",\n    \"cutlery fork 3\",\n    \"cutlery fork 4\",\n    \"cutlery knife 1\",\n    \"cutlery knife 2\",\n    \"cutlery knife 3\",\n    \"cutlery knife 4\",\n    \"cutlery knife 5\",\n    \"cutlery knife 6\",\n    \"cutlets 1\",\n    \"deodorant 1\",\n    \"deodorant 2\",\n    \"deodorant 3\",\n    \"desk 1\",\n    \"desk 2\",\n    \"dishwasher 1\",\n    \"dishwashing liquid 1\",\n    \"door 1\",\n    \"door 2\",\n    \"door 3\",\n    \"door jamb 1\",\n    \"door jamb 2\",\n    \"door jamb 3\",\n    \"door jamb 4\",\n    \"face cream 1\",\n    \"face cream 2\",\n    \"face cream 3\",\n    \"faucet 1\",\n    \"faucet 2\",\n    \"floor 1\",\n    \"floor 10\",\n    \"floor 11\",\n    \"floor 12\",\n    \"floor 13\",\n    \"floor 14\",\n    \"floor 15\",\n    \"floor 16\",\n    \"floor 17\",\n    \"floor 18\",\n    \"floor 19\",\n    \"floor 2\",\n    \"floor 20\",\n    \"floor 21\",\n    \"floor 22\",\n    \"floor 23\",\n    \"floor 24\",\n    \"floor 25\",\n    \"floor 26\",\n    \"floor 3\",\n    \"floor 4\",\n    \"floor 5\",\n    \"floor 6\",\n    \"floor 7\",\n    \"floor 8\",\n    \"floor 9\",\n    \"folder 1\",\n    \"folder 2\",\n    \"folder 3\",\n    \"folder 4\",\n    \"fridge 1\",\n    \"frying pan 1\",\n    \"hair product 1\",\n    \"hair product 2\",\n    \"hair product 3\",\n    \"hair product 4\",\n    \"hanger 1\",\n    \"hanger 2\",\n    \"hanger 3\",\n    \"hanger 4\",\n    \"hanger 5\",\n    \"hanger 6\",\n    \"hanger 7\",\n    \"juice 1\",\n    \"juice 2\",\n    \"keyboard 1\",\n    \"kitchen 1\",\n    \"kitchen cabinet 1\",\n    \"kitchen cabinet 2\",\n    \"kitchen cabinet 3\",\n    \"kitchen cabinet 4\",\n    \"kitchen cabinet 5\",\n    \"kitchen cabinet 6\",\n    \"kitchen cabinet 7\",\n    \"kitchen cabinet 8\",\n    \"kitchen counter 1\",\n    \"kitchen counter 2\",\n    \"kitchen counter 3\",\n    \"kitchen counter drawer 1\",\n    \"kitchen counter drawer 2\",\n    \"kitchen counter drawer 3\",\n    \"kitchen counter drawer 4\",\n    \"kitchen counter drawer 5\",\n    \"kitchen counter drawer 6\",\n    \"kitchen counter drawer 7\",\n    \"kitchen counter drawer 8\",\n    \"kitchen table 1\",\n    \"knife block 1\",\n    \"light switch 1\",\n    \"light switch 2\",\n    \"light switch 3\",\n    \"light switch 4\",\n    \"lime 1\",\n    \"living room 1\",\n    \"microwave oven 1\",\n    \"milk 1\",\n    \"mouse 1\",\n    \"mouse mat 1\",\n    \"mug 1\",\n    \"mug 2\",\n    \"mug 3\",\n    \"nightstand 1\",\n    \"nightstand 2\",\n    \"nightstand 3\",\n    \"nightstand 4\",\n    \"notes 1\",\n    \"orchid 1\",\n    \"oven tray 1\",\n    \"painkillers 1\",\n    \"pancake 1\",\n    \"peach 1\",\n    \"peach 2\",\n    \"peach 3\",\n    \"pear 1\",\n    \"perfume 1\",\n    \"perfume 2\",\n    \"photo frame 1\",\n    \"photo frame 2\",\n    \"photo frame 3\",\n    \"pile of clothes 1\",\n    \"pile of clothes 2\",\n    \"pillow 1\",\n    \"pillow 2\",\n    \"pillow 3\",\n    \"pillow 4\",\n    \"pillow 5\",\n    \"pillow 6\",\n    \"plate 1\",\n    \"plate 2\",\n    \"plate 3\",\n    \"plate 4\",\n    \"plate 5\",\n    \"plate 6\",\n    \"plate 7\",\n    \"plum 1\",\n    \"plum 2\",\n    \"power socket 1\",\n    \"power socket 2\",\n    \"power socket 3\",\n    \"pudding 1\",\n    \"pudding 2\",\n    \"radio 1\",\n    \"rug 1\",\n    \"rug 2\",\n    \"rug 3\",\n    \"rug 4\",\n    \"sink 1\",\n    \"sink 2\",\n    \"slice of bread 1\",\n    \"slice of bread 2\",\n    \"sofa 1\",\n    \"sofa 2\",\n    \"sofa 3\",\n    \"stall 1\",\n    \"stall 2\",\n    \"stove 1\",\n    \"stove fan 1\",\n    \"table lamp 1\",\n    \"toaster 1\",\n    \"toilet 1\",\n    \"toilet paper 1\",\n    \"toothbrush 1\",\n    \"toothpaste 1\",\n    \"tv 1\",\n    \"tv stand 1\",\n    \"wall 1\",\n    \"wall 10\",\n    \"wall 11\",\n    \"wall 12\",\n    \"wall 13\",\n    \"wall 14\",\n    \"wall 15\",\n    \"wall 16\",\n    \"wall 17\",\n    \"wall 18\",\n    \"wall 19\",\n    \"wall 2\",\n    \"wall 20\",\n    \"wall 21\",\n    \"wall 22\",\n    \"wall 23\",\n    \"wall 24\",\n    \"wall 25\",\n    \"wall 26\",\n    \"wall 3\",\n    \"wall 4\",\n    \"wall 5\",\n    \"wall 6\",\n    \"wall 7\",\n    \"wall 8\",\n    \"wall 9\",\n    \"wall lamp 1\",\n    \"wall lamp 2\",\n    \"wall lamp 3\",\n    \"wall lamp 4\",\n    \"wall lamp 5\",\n    \"wall lamp 6\",\n    \"wall lamp 7\",\n    \"wall lamp 8\",\n    \"wall lamp 9\",\n    \"wall phone 1\",\n    \"wall picture frame 1\",\n    \"wall picture frame 2\",\n    \"wall picture frame 3\",\n    \"wall picture frame 4\",\n    \"wall picture frame 5\",\n    \"wall picture frame 6\",\n    \"wall picture frame 7\",\n    \"wall picture frame 8\",\n    \"wall shelf 1\",\n    \"wall shelf 2\",\n    \"washing machine 1\",\n    \"washing sponge 1\",\n    \"water glass 1\",\n    \"water glass 2\",\n    \"water glass 3\",\n    \"water glass 4\",\n    \"water glass 5\",\n    \"window 1\",\n    \"window 2\",\n    \"wine 1\"\n  ]\n}\n任务上下文中的 env_id、init_room、init_graph_cache_path、task_goal、available_entities 是 WAH/ReAcTree grounding；task_goal 是官方目标谓词，必须保持 WAH 目标语义。\n\nWAH 可用 skill 摘要：\n[\n  {\n    \"name\": \"go to\",\n    \"description\": \"Official ReAcTree WAH navigation action.\",\n    \"planning_contract\": {\n      \"planner_location_param\": \"target\",\n      \"planner_action_name\": \"go to\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=go to\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"pick up\",\n    \"description\": \"Official ReAcTree WAH pickup action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"target\",\n      \"planner_requires_empty_hand\": \"true\",\n      \"planner_action_name\": \"pick up\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=pick up\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"put down\",\n    \"description\": \"Official ReAcTree WAH put-down action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"target\",\n      \"planner_action_name\": \"put down\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=put down\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"open\",\n    \"description\": \"Official ReAcTree WAH open action.\",\n    \"planning_contract\": {\n      \"planner_target_param\": \"target\",\n      \"planner_location_param\": \"target\",\n      \"planner_state_key\": \"isOpen\",\n      \"planner_state_value\": \"true\",\n      \"planner_reversible_state\": \"true\",\n      \"planner_action_name\": \"open\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=open\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"close\",\n    \"description\": \"Official ReAcTree WAH close action.\",\n    \"planning_contract\": {\n      \"planner_target_param\": \"target\",\n      \"planner_location_param\": \"target\",\n      \"planner_state_key\": \"isOpen\",\n      \"planner_state_value\": \"false\",\n      \"planner_reversible_state\": \"true\",\n      \"planner_action_name\": \"close\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=close\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"turn on\",\n    \"description\": \"Official ReAcTree WAH turn-on action.\",\n    \"planning_contract\": {\n      \"planner_target_param\": \"target\",\n      \"planner_location_param\": \"target\",\n      \"planner_state_key\": \"isToggled\",\n      \"planner_state_value\": \"true\",\n      \"planner_reversible_state\": \"true\",\n      \"planner_action_name\": \"turn on\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=turn on\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"turn off\",\n    \"description\": \"Official ReAcTree WAH turn-off action.\",\n    \"planning_contract\": {\n      \"planner_target_param\": \"target\",\n      \"planner_location_param\": \"target\",\n      \"planner_state_key\": \"isToggled\",\n      \"planner_state_value\": \"false\",\n      \"planner_reversible_state\": \"true\",\n      \"planner_action_name\": \"turn off\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=turn off\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  },\n  {\n    \"name\": \"clean\",\n    \"description\": \"Official ReAcTree WAH clean action.\",\n    \"planning_contract\": {\n      \"planner_item_param\": \"target\",\n      \"planner_effect_state_key\": \"isClean\",\n      \"planner_effect_state_value\": \"true\",\n      \"planner_action_name\": \"clean\",\n      \"planner_required_fields\": \"action,target\",\n      \"planner_fixed_fields\": \"action=clean\",\n      \"planner_entity_fields\": \"target\",\n      \"planner_allow_extra_fields\": \"false\"\n    }\n  }\n]\n\n理解边界：\n1. intent 保留 WAH 自然语言任务目标，不输出动作序列。\n2. required_item_names 必须使用允许实体名，或使用 task_goal 指向的真实对象/容器类别从允许实体中选择实例；不要发明编号。\n3. WAH 官方目标通常是类级关系；understanding 可以选目标类别和候选实例，但必须标明数量约束。\n4. skill_closure 只能使用 WAH skills root 中启用的 skill，例如 go_to、pick_up、put_down、open、close、turn_on、turn_off、clean。\n\n输出 JSON 结构：\n{\"is_complete\": true, \"is_cancel_all\": false, \"clarification_question\": \"\", \"entity_relevance\": {\"directly_related\": [], \"indirectly_related\": [], \"possibly_related\": []}, \"skill_closure\": [], \"structured_task\": {\"intent\": \"\", \"required_item_names\": {\"targets\": {\"primary\": [], \"alternatives\": []}, \"tools\": {\"primary\": [], \"alternatives\": []}, \"receptacles\": {\"primary\": [], \"alternatives\": []}}, \"quantity_constraints\": []}}"
  },
  {
    "type": "human",
    "content": "Put one cupcake and one apple on the coffee table"
  }
]
```

### Planning 初始提示
```json
[
  {
    "type": "system",
    "content": "任务：生成 WAH/ReAcTree 官方原生动作计划。\n只输出 JSON；不要解释，不要输出 Markdown。\n\n原始任务：\n\n\n规划目标：\nPut one cupcake and one apple on the coffee table\n\n机器人状态：\n- 位置：bedroom 1\n- 手持：空\n- 完整状态：{\"robot_location\":\"bedroom 1\",\"robot_holding\":\"空\"}\n\n当前环境 JSON：\n{\"cupcake 1\":{\"direct_parent\":\"kitchen table 1\",\"direct_relation\":\"on\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"EATABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"]},\"kitchen 1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"floor 2\":{\"direct_parent\":\"kitchen 1\",\"direct_relation\":\"inside\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"SURFACES\"],\"is_container\":true,\"full_path\":[\"kitchen 1\"]},\"kitchen table 1\":{\"direct_parent\":\"floor 2\",\"direct_relation\":\"on\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"SURFACES\",\"MOVABLE\"],\"is_container\":true,\"full_path\":[\"kitchen 1\",\"floor 2\"]},\"cupcake 2\":{\"direct_parent\":\"kitchen table 1\",\"direct_relation\":\"on\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"EATABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"]},\"cupcake 3\":{\"direct_parent\":\"cabinet 1\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"EATABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"bedroom 1\",\"floor 16\",\"cabinet 1\"]},\"bedroom 1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"floor 16\":{\"direct_parent\":\"bedroom 1\",\"direct_relation\":\"inside\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"SURFACES\"],\"is_container\":true,\"full_path\":[\"bedroom 1\"]},\"cabinet 1\":{\"direct_parent\":\"floor 16\",\"direct_relation\":\"on\",\"type\":\"receptacle\",\"states\":{\"isOpen\":false},\"properties\":[\"SURFACES\",\"CAN_OPEN\",\"CONTAINERS\"],\"is_container\":true,\"full_path\":[\"bedroom 1\",\"floor 16\"]},\"apple 1\":{\"direct_parent\":\"fridge 1\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"kitchen 1\",\"floor 4\",\"fridge 1\"]},\"floor 4\":{\"direct_parent\":\"kitchen 1\",\"direct_relation\":\"inside\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"SURFACES\"],\"is_container\":true,\"full_path\":[\"kitchen 1\"]},\"fridge 1\":{\"direct_parent\":\"floor 4\",\"direct_relation\":\"on\",\"type\":\"receptacle\",\"states\":{\"isOpen\":false},\"properties\":[\"CAN_OPEN\",\"HAS_SWITCH\",\"CONTAINERS\",\"HAS_PLUG\"],\"is_container\":true,\"full_path\":[\"kitchen 1\",\"floor 4\"]},\"apple 2\":{\"direct_parent\":\"kitchen table 1\",\"direct_relation\":\"on\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"]},\"apple 3\":{\"direct_parent\":\"cabinet 1\",\"direct_relation\":\"inside\",\"type\":null,\"states\":{},\"properties\":[\"GRABBABLE\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"bedroom 1\",\"floor 16\",\"cabinet 1\"]},\"coffee table 1\":{\"direct_parent\":\"floor 25\",\"direct_relation\":\"on\",\"type\":null,\"states\":{},\"properties\":[\"SURFACES\",\"MOVABLE\"],\"is_container\":false,\"full_path\":[\"living room 1\",\"floor 25\"]},\"living room 1\":{\"direct_parent\":\"未知环境\",\"direct_relation\":null,\"type\":\"room\",\"states\":{},\"properties\":[],\"is_container\":false,\"full_path\":[]},\"floor 25\":{\"direct_parent\":\"living room 1\",\"direct_relation\":\"inside\",\"type\":\"receptacle\",\"states\":{},\"properties\":[\"SURFACES\"],\"is_container\":true,\"full_path\":[\"living room 1\"]}}\n\n任务相关环境事实：\n[{\"name\":\"apple 1\",\"direct_parent\":\"fridge 1\",\"full_path\":[\"kitchen 1\",\"floor 4\",\"fridge 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"apple 2\",\"direct_parent\":\"kitchen table 1\",\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"apple 3\",\"direct_parent\":\"cabinet 1\",\"full_path\":[\"bedroom 1\",\"floor 16\",\"cabinet 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"bedroom 1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"cabinet 1\",\"direct_parent\":\"floor 16\",\"full_path\":[\"bedroom 1\",\"floor 16\"],\"states\":{\"isOpen\":false},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"coffee table 1\",\"direct_parent\":\"floor 25\",\"full_path\":[\"living room 1\",\"floor 25\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"cupcake 1\",\"direct_parent\":\"kitchen table 1\",\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"cupcake 2\",\"direct_parent\":\"kitchen table 1\",\"full_path\":[\"kitchen 1\",\"floor 2\",\"kitchen table 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"cupcake 3\",\"direct_parent\":\"cabinet 1\",\"full_path\":[\"bedroom 1\",\"floor 16\",\"cabinet 1\"],\"states\":{},\"type\":null,\"is_container\":false},{\"name\":\"floor 16\",\"direct_parent\":\"bedroom 1\",\"full_path\":[\"bedroom 1\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"floor 2\",\"direct_parent\":\"kitchen 1\",\"full_path\":[\"kitchen 1\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"floor 25\",\"direct_parent\":\"living room 1\",\"full_path\":[\"living room 1\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"floor 4\",\"direct_parent\":\"kitchen 1\",\"full_path\":[\"kitchen 1\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"fridge 1\",\"direct_parent\":\"floor 4\",\"full_path\":[\"kitchen 1\",\"floor 4\"],\"states\":{\"isOpen\":false},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"kitchen 1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false},{\"name\":\"kitchen table 1\",\"direct_parent\":\"floor 2\",\"full_path\":[\"kitchen 1\",\"floor 2\"],\"states\":{},\"type\":\"receptacle\",\"is_container\":true},{\"name\":\"living room 1\",\"direct_parent\":\"未知环境\",\"full_path\":[],\"states\":{},\"type\":\"room\",\"is_container\":false}]\n\n任务上下文：\n{\n  \"dataset\": \"reactree\",\n  \"env_id\": 3,\n  \"task_name\": \"prepare_snack\",\n  \"instruction\": \"Put one cupcake and one apple on the coffee table\",\n  \"init_room\": \"bedroom\",\n  \"task_source\": \"reactree_wah_testset\",\n  \"environment_source\": \"reactree_case_runtime_scene\",\n  \"init_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json\",\n  \"task_goal\": {\n    \"on_cupcake_coffeetable\": 1,\n    \"on_apple_coffeetable\": 1\n  },\n  \"available_entities\": [\n    \"apple 1\",\n    \"apple 2\",\n    \"apple 3\",\n    \"bananas 1\",\n    \"bar soap 1\",\n    \"bathroom 1\",\n    \"bathroom cabinet 1\",\n    \"bathroom counter 1\",\n    \"bed 1\",\n    \"bedroom 1\",\n    \"book 1\",\n    \"book 2\",\n    \"bookshelf 1\",\n    \"bookshelf 2\",\n    \"bookshelf 3\",\n    \"bowl 1\",\n    \"bowl 2\",\n    \"bowl 3\",\n    \"bowl 4\",\n    \"bowl 5\",\n    \"bowl 6\",\n    \"bowl 7\",\n    \"bowl 8\",\n    \"bowl 9\",\n    \"box 1\",\n    \"box 2\",\n    \"box 3\",\n    \"box 4\",\n    \"box 5\",\n    \"bucket 1\",\n    \"cabinet 1\",\n    \"candle 1\",\n    \"candy bar 1\",\n    \"ceiling 1\",\n    \"ceiling 10\",\n    \"ceiling 11\",\n    \"ceiling 12\",\n    \"ceiling 13\",\n    \"ceiling 14\",\n    \"ceiling 15\",\n    \"ceiling 16\",\n    \"ceiling 17\",\n    \"ceiling 18\",\n    \"ceiling 19\",\n    \"ceiling 2\",\n    \"ceiling 20\",\n    \"ceiling 21\",\n    \"ceiling 22\",\n    \"ceiling 23\",\n    \"ceiling 24\",\n    \"ceiling 25\",\n    \"ceiling 26\",\n    \"ceiling 3\",\n    \"ceiling 4\",\n    \"ceiling 5\",\n    \"ceiling 6\",\n    \"ceiling 7\",\n    \"ceiling 8\",\n    \"ceiling 9\",\n    \"ceiling lamp 1\",\n    \"ceiling lamp 2\",\n    \"ceiling lamp 3\",\n    \"ceiling lamp 4\",\n    \"ceiling lamp 5\",\n    \"cell phone 1\",\n    \"cell phone 2\",\n    \"cereal 1\",\n    \"chair 1\",\n    \"chair 2\",\n    \"chair 3\",\n    \"chair 4\",\n    \"chair 5\",\n    \"chair 6\",\n    \"chips 1\",\n    \"chips 2\",\n    \"chocolate syrup 1\",\n    \"closet 1\",\n    \"closet drawer 1\",\n    \"closet drawer 2\",\n    \"closet drawer 3\",\n    \"closet drawer 4\",\n    \"closet drawer 5\",\n    \"closet drawer 6\",\n    \"closet drawer 7\",\n    \"coffee maker 1\",\n    \"coffee pot 1\",\n    \"coffee table 1\",\n    \"computer 1\",\n    \"condiment bottle 1\",\n    \"condiment bottle 2\",\n    \"condiment bottle 3\",\n    \"condiment bottle 4\",\n    \"condiment shaker 1\",\n    \"condiment shaker 2\",\n    \"condiment shaker 3\",\n    \"condiment shaker 4\",\n    \"cooking pot 1\",\n    \"cooking pot 2\",\n    \"cpu screen 1\",\n    \"crackers 1\",\n    \"crackers 2\",\n    \"creamy buns 1\",\n    \"cupcake 1\",\n    \"cupcake 2\",\n    \"cupcake 3\",\n    \"curtains 1\",\n    \"curtains 2\",\n    \"curtains 3\",\n    \"curtains 4\",\n    \"curtains 5\",\n    \"curtains 6\",\n    \"curtains 7\",\n    \"cutlery fork 1\",\n    \"cutlery fork 2\",\n    \"cutlery fork 3\",\n    \"cutlery fork 4\",\n    \"cutlery knife 1\",\n    \"cutlery knife 2\",\n    \"cutlery knife 3\",\n    \"cutlery knife 4\",\n    \"cutlery knife 5\",\n    \"cutlery knife 6\",\n    \"cutlets 1\",\n    \"deodorant 1\",\n    \"deodorant 2\",\n    \"deodorant 3\",\n    \"desk 1\",\n    \"desk 2\",\n    \"dishwasher 1\",\n    \"dishwashing liquid 1\",\n    \"door 1\",\n    \"door 2\",\n    \"door 3\",\n    \"door jamb 1\",\n    \"door jamb 2\",\n    \"door jamb 3\",\n    \"door jamb 4\",\n    \"face cream 1\",\n    \"face cream 2\",\n    \"face cream 3\",\n    \"faucet 1\",\n    \"faucet 2\",\n    \"floor 1\",\n    \"floor 10\",\n    \"floor 11\",\n    \"floor 12\",\n    \"floor 13\",\n    \"floor 14\",\n    \"floor 15\",\n    \"floor 16\",\n    \"floor 17\",\n    \"floor 18\",\n    \"floor 19\",\n    \"floor 2\",\n    \"floor 20\",\n    \"floor 21\",\n    \"floor 22\",\n    \"floor 23\",\n    \"floor 24\",\n    \"floor 25\",\n    \"floor 26\",\n    \"floor 3\",\n    \"floor 4\",\n    \"floor 5\",\n    \"floor 6\",\n    \"floor 7\",\n    \"floor 8\",\n    \"floor 9\",\n    \"folder 1\",\n    \"folder 2\",\n    \"folder 3\",\n    \"folder 4\",\n    \"fridge 1\",\n    \"frying pan 1\",\n    \"hair product 1\",\n    \"hair product 2\",\n    \"hair product 3\",\n    \"hair product 4\",\n    \"hanger 1\",\n    \"hanger 2\",\n    \"hanger 3\",\n    \"hanger 4\",\n    \"hanger 5\",\n    \"hanger 6\",\n    \"hanger 7\",\n    \"juice 1\",\n    \"juice 2\",\n    \"keyboard 1\",\n    \"kitchen 1\",\n    \"kitchen cabinet 1\",\n    \"kitchen cabinet 2\",\n    \"kitchen cabinet 3\",\n    \"kitchen cabinet 4\",\n    \"kitchen cabinet 5\",\n    \"kitchen cabinet 6\",\n    \"kitchen cabinet 7\",\n    \"kitchen cabinet 8\",\n    \"kitchen counter 1\",\n    \"kitchen counter 2\",\n    \"kitchen counter 3\",\n    \"kitchen counter drawer 1\",\n    \"kitchen counter drawer 2\",\n    \"kitchen counter drawer 3\",\n    \"kitchen counter drawer 4\",\n    \"kitchen counter drawer 5\",\n    \"kitchen counter drawer 6\",\n    \"kitchen counter drawer 7\",\n    \"kitchen counter drawer 8\",\n    \"kitchen table 1\",\n    \"knife block 1\",\n    \"light switch 1\",\n    \"light switch 2\",\n    \"light switch 3\",\n    \"light switch 4\",\n    \"lime 1\",\n    \"living room 1\",\n    \"microwave oven 1\",\n    \"milk 1\",\n    \"mouse 1\",\n    \"mouse mat 1\",\n    \"mug 1\",\n    \"mug 2\",\n    \"mug 3\",\n    \"nightstand 1\",\n    \"nightstand 2\",\n    \"nightstand 3\",\n    \"nightstand 4\",\n    \"notes 1\",\n    \"orchid 1\",\n    \"oven tray 1\",\n    \"painkillers 1\",\n    \"pancake 1\",\n    \"peach 1\",\n    \"peach 2\",\n    \"peach 3\",\n    \"pear 1\",\n    \"perfume 1\",\n    \"perfume 2\",\n    \"photo frame 1\",\n    \"photo frame 2\",\n    \"photo frame 3\",\n    \"pile of clothes 1\",\n    \"pile of clothes 2\",\n    \"pillow 1\",\n    \"pillow 2\",\n    \"pillow 3\",\n    \"pillow 4\",\n    \"pillow 5\",\n    \"pillow 6\",\n    \"plate 1\",\n    \"plate 2\",\n    \"plate 3\",\n    \"plate 4\",\n    \"plate 5\",\n    \"plate 6\",\n    \"plate 7\",\n    \"plum 1\",\n    \"plum 2\",\n    \"power socket 1\",\n    \"power socket 2\",\n    \"power socket 3\",\n    \"pudding 1\",\n    \"pudding 2\",\n    \"radio 1\",\n    \"rug 1\",\n    \"rug 2\",\n    \"rug 3\",\n    \"rug 4\",\n    \"sink 1\",\n    \"sink 2\",\n    \"slice of bread 1\",\n    \"slice of bread 2\",\n    \"sofa 1\",\n    \"sofa 2\",\n    \"sofa 3\",\n    \"stall 1\",\n    \"stall 2\",\n    \"stove 1\",\n    \"stove fan 1\",\n    \"table lamp 1\",\n    \"toaster 1\",\n    \"toilet 1\",\n    \"toilet paper 1\",\n    \"toothbrush 1\",\n    \"toothpaste 1\",\n    \"tv 1\",\n    \"tv stand 1\",\n    \"wall 1\",\n    \"wall 10\",\n    \"wall 11\",\n    \"wall 12\",\n    \"wall 13\",\n    \"wall 14\",\n    \"wall 15\",\n    \"wall 16\",\n    \"wall 17\",\n    \"wall 18\",\n    \"wall 19\",\n    \"wall 2\",\n    \"wall 20\",\n    \"wall 21\",\n    \"wall 22\",\n    \"wall 23\",\n    \"wall 24\",\n    \"wall 25\",\n    \"wall 26\",\n    \"wall 3\",\n    \"wall 4\",\n    \"wall 5\",\n    \"wall 6\",\n    \"wall 7\",\n    \"wall 8\",\n    \"wall 9\",\n    \"wall lamp 1\",\n    \"wall lamp 2\",\n    \"wall lamp 3\",\n    \"wall lamp 4\",\n    \"wall lamp 5\",\n    \"wall lamp 6\",\n    \"wall lamp 7\",\n    \"wall lamp 8\",\n    \"wall lamp 9\",\n    \"wall phone 1\",\n    \"wall picture frame 1\",\n    \"wall picture frame 2\",\n    \"wall picture frame 3\",\n    \"wall picture frame 4\",\n    \"wall picture frame 5\",\n    \"wall picture frame 6\",\n    \"wall picture frame 7\",\n    \"wall picture frame 8\",\n    \"wall shelf 1\",\n    \"wall shelf 2\",\n    \"washing machine 1\",\n    \"washing sponge 1\",\n    \"water glass 1\",\n    \"water glass 2\",\n    \"water glass 3\",\n    \"water glass 4\",\n    \"water glass 5\",\n    \"window 1\",\n    \"window 2\",\n    \"wine 1\"\n  ]\n}\n\n理解层实体选择：\n{\n  \"targets\": {\n    \"primary\": [\n      \"cupcake 1\",\n      \"apple 1\"\n    ],\n    \"alternatives\": []\n  },\n  \"tools\": {\n    \"primary\": [],\n    \"alternatives\": []\n  },\n  \"receptacles\": {\n    \"primary\": [\n      \"coffee table 1\"\n    ],\n    \"alternatives\": []\n  }\n}\n\n可用动作与 skill 契约：\n<available_skills>\n---\nname: go to\ndescription: Official ReAcTree WAH navigation action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `go to`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `go to` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的房间或对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 只有在目标位置或交互锚点当前不可直接到达时，才应导航。\n- 如果机器人已经处于同一个可交互位置簇，不要重复导航。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，模拟机器人位置应更新到该 WAH 官方实体。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"go to\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: pick up\ndescription: Official ReAcTree WAH pickup action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `pick up`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `pick up` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 目标必须具备 WAH `GRABBABLE` 属性；桌面、房间、灯、容器本身不能被当作普通可拿取物。\n- 目标物体必须可达；当前机器人位置、目标父节点以及对应手或携带槽位必须满足 handler 校验。\n- 如果目标位于关闭的 `CAN_OPEN` 容器内，`pick up` 会被 handler 拒绝。\n- 如果 benchmark 使用多只手，必须依据各只手的占用状态判断，而不是假设只有一个抓手。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，目标物体会进入对应手或携带槽位。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"pick up\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: put down\ndescription: Official ReAcTree WAH put-down action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `put down`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `put down` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 机器人当前必须已经持有或携带该步引用的物体。\n- `put down` 的目标位置由当前机器人位置决定；当前位置不满足放置条件时 handler 必须拒绝。\n- 如果当前位置是关闭的 `CAN_OPEN` 容器，handler 必须拒绝该步。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"put down\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: open\ndescription: Official ReAcTree WAH open action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `open`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `open` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 目标对象必须具备 WAH `CAN_OPEN` 属性，且当前不是已打开状态。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"open\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: close\ndescription: Official ReAcTree WAH close action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `close`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `close` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 目标对象必须具备 WAH `CAN_OPEN` 属性，且当前不是已关闭状态。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"close\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: turn on\ndescription: Official ReAcTree WAH turn-on action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `turn on`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `turn on` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 目标对象必须具备 WAH `HAS_SWITCH` 属性，当前不是已开启状态，并且机器人必须空手。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"turn on\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: turn off\ndescription: Official ReAcTree WAH turn-off action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `turn off`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `turn off` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 目标对象必须具备 WAH `HAS_SWITCH` 属性，当前不是已关闭状态，并且机器人必须空手。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"turn off\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n\n---\nname: clean\ndescription: Official ReAcTree WAH clean action.\n---\n\n## 参数\nplanning、handler 和官方导出均使用 WAH 原生动作对象。\n\n| 字段 | 类型 | 含义 |\n| --- | --- | --- |\n| action | string | 固定为 `clean`。 |\n| target | string | 当前 WAH 场景中的精确目标实体名。 |\n## 前提条件\n- 必须使用官方 WAH 原生动作名 `clean` 和字段 schema。\n- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。\n- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。\n- 所需工具、液体状态或清洁装置状态，必须已经满足 handler 的校验规则。\n- 不要假设工具会自动变湿、变干净或自动可用；只有已验证步骤造成的状态变化才有效。\n\n## 执行效果\n- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。\n- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。\n- 成功执行后，会按 handler 约定更新清洁、浸湿或相关状态标志。\n\n## 输出格式\n- planning 最终输出必须是 WAH 原生动作 JSON 数组；本技能的一步写成：\n```json\n{\"action\": \"clean\", \"target\": \"<target>\"}\n```\n- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。\n</available_skills>\n\n历史失败反馈：\n暂无相关拦截记录\n\n规划边界：\n1. 只使用 <available_skills> 中列出的动作。\n2. 动作参数、前置条件、状态依赖和效果只以对应 skill 契约为准。\n3. 只引用当前环境、任务上下文、任务相关环境事实或理解层结果中出现的实体/房间/对象名。\n4. 如果已有修复反馈或修复状态，只生成尚未验证的后续动作。\n\n输出格式：\n直接输出 WAH/ReAcTree 原生动作 JSON 数组。\n每个元素只能包含 action 和 target。\n如果任务已经完成，返回 []。"
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
    "content": "任务：根据 WAH/ReAcTree sandbox 前后状态差异判断任务是否完成。\n只输出 JSON；不要解释，不要生成动作。\n\n任务目标：Put one cupcake and one apple on the coffee table\n\n完整 native action 计划摘要：\n[\n  {\n    \"action\": \"go to\",\n    \"target\": \"kitchen table 1\"\n  },\n  {\n    \"action\": \"pick up\",\n    \"target\": \"cupcake 1\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"coffee table 1\"\n  },\n  {\n    \"action\": \"put down\",\n    \"target\": \"cupcake 1\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"kitchen table 1\"\n  },\n  {\n    \"action\": \"pick up\",\n    \"target\": \"apple 2\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"coffee table 1\"\n  },\n  {\n    \"action\": \"put down\",\n    \"target\": \"apple 2\"\n  }\n]\n\n本轮实际模拟步骤：\n[\n  {\n    \"action\": \"go to\",\n    \"target\": \"kitchen table 1\"\n  },\n  {\n    \"action\": \"pick up\",\n    \"target\": \"cupcake 1\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"coffee table 1\"\n  },\n  {\n    \"action\": \"put down\",\n    \"target\": \"cupcake 1\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"kitchen table 1\"\n  },\n  {\n    \"action\": \"pick up\",\n    \"target\": \"apple 2\"\n  },\n  {\n    \"action\": \"go to\",\n    \"target\": \"coffee table 1\"\n  },\n  {\n    \"action\": \"put down\",\n    \"target\": \"apple 2\"\n  }\n]\n\n轨迹摘要：\nStep 1: go to([])\nStep 2: pick up([])\nStep 3: go to([])\nStep 4: put down([])\nStep 5: go to([])\nStep 6: pick up([])\nStep 7: go to([])\nStep 8: put down([])\n\nWAH 状态差异 JSON：\n{\n  \"entity_count_compared\": 17,\n  \"changed_entity_count\": 2,\n  \"truncated_entity_count\": 0,\n  \"has_changes\": true,\n  \"robot\": {\n    \"changed\": true,\n    \"before\": {\n      \"robot_location\": \"bedroom 1\",\n      \"robot_holding\": \"空\"\n    },\n    \"after\": {\n      \"robot_location\": \"coffee table 1\",\n      \"robot_holding\": \"空\"\n    }\n  },\n  \"entities\": [\n    {\n      \"name\": \"apple 2\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"coffee table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      }\n    },\n    {\n      \"name\": \"cupcake 1\",\n      \"change_type\": \"updated\",\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"EATABLE\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"coffee table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"EATABLE\",\n          \"MOVABLE\"\n        ]\n      }\n    }\n  ]\n}\n\n状态审计上下文 JSON：\n{\n  \"entity_count_available\": 17,\n  \"entity_count_in_context\": 9,\n  \"truncated_entity_count\": 0,\n  \"note\": \"state_diff only lists changed entities; unchanged entities in this context still prove final goal state when their after state satisfies the task.\",\n  \"robot\": {\n    \"changed\": true,\n    \"before\": {\n      \"robot_location\": \"bedroom 1\",\n      \"robot_holding\": \"空\"\n    },\n    \"after\": {\n      \"robot_location\": \"coffee table 1\",\n      \"robot_holding\": \"空\"\n    }\n  },\n  \"entities\": [\n    {\n      \"name\": \"cupcake 1\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"EATABLE\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"coffee table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"EATABLE\",\n          \"MOVABLE\"\n        ]\n      }\n    },\n    {\n      \"name\": \"apple 1\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"fridge 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 4\",\n          \"fridge 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"fridge 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 4\",\n          \"fridge 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      }\n    },\n    {\n      \"name\": \"coffee table 1\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"floor 25\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"living room 1\",\n          \"floor 25\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"floor 25\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"living room 1\",\n          \"floor 25\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\",\n          \"MOVABLE\"\n        ]\n      }\n    },\n    {\n      \"name\": \"floor 25\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"living room 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"living room 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\"\n        ]\n      },\n      \"after\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"living room 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"living room 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\"\n        ]\n      }\n    },\n    {\n      \"name\": \"living room 1\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      },\n      \"after\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      }\n    },\n    {\n      \"name\": \"fridge 1\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"floor 4\",\n        \"direct_relation\": \"on\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 4\"\n        ],\n        \"states\": {\n          \"isOpen\": false\n        },\n        \"properties\": [\n          \"CAN_OPEN\",\n          \"HAS_SWITCH\",\n          \"CONTAINERS\",\n          \"HAS_PLUG\"\n        ]\n      },\n      \"after\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"floor 4\",\n        \"direct_relation\": \"on\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 4\"\n        ],\n        \"states\": {\n          \"isOpen\": false\n        },\n        \"properties\": [\n          \"CAN_OPEN\",\n          \"HAS_SWITCH\",\n          \"CONTAINERS\",\n          \"HAS_PLUG\"\n        ]\n      }\n    },\n    {\n      \"name\": \"floor 4\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"kitchen 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"kitchen 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\"\n        ]\n      },\n      \"after\": {\n        \"type\": \"receptacle\",\n        \"direct_parent\": \"kitchen 1\",\n        \"direct_relation\": \"inside\",\n        \"is_container\": true,\n        \"full_path\": [\n          \"kitchen 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"SURFACES\"\n        ]\n      }\n    },\n    {\n      \"name\": \"kitchen 1\",\n      \"changed\": false,\n      \"before\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      },\n      \"after\": {\n        \"type\": \"room\",\n        \"direct_parent\": \"未知环境\",\n        \"direct_relation\": null,\n        \"is_container\": false,\n        \"full_path\": [],\n        \"states\": {},\n        \"properties\": []\n      }\n    },\n    {\n      \"name\": \"apple 2\",\n      \"changed\": true,\n      \"before\": {\n        \"type\": null,\n        \"direct_parent\": \"kitchen table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      },\n      \"after\": {\n        \"type\": null,\n        \"direct_parent\": \"coffee table 1\",\n        \"direct_relation\": \"on\",\n        \"is_container\": false,\n        \"full_path\": [\n          \"kitchen 1\",\n          \"floor 2\",\n          \"kitchen table 1\"\n        ],\n        \"states\": {},\n        \"properties\": [\n          \"GRABBABLE\",\n          \"MOVABLE\"\n        ]\n      }\n    }\n  ],\n  \"task_context\": {\n    \"dataset\": \"reactree\",\n    \"env_id\": 3,\n    \"task_name\": \"prepare_snack\",\n    \"instruction\": \"Put one cupcake and one apple on the coffee table\",\n    \"init_room\": \"bedroom\",\n    \"task_source\": \"reactree_wah_testset\",\n    \"environment_source\": \"reactree_case_runtime_scene\",\n    \"init_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json\",\n    \"task_goal\": {\n      \"on_cupcake_coffeetable\": 1,\n      \"on_apple_coffeetable\": 1\n    },\n    \"available_entities\": [\n      \"apple 1\",\n      \"apple 2\",\n      \"apple 3\",\n      \"bananas 1\",\n      \"bar soap 1\",\n      \"bathroom 1\",\n      \"bathroom cabinet 1\",\n      \"bathroom counter 1\",\n      \"bed 1\",\n      \"bedroom 1\",\n      \"book 1\",\n      \"book 2\",\n      \"bookshelf 1\",\n      \"bookshelf 2\",\n      \"bookshelf 3\",\n      \"bowl 1\",\n      \"bowl 2\",\n      \"bowl 3\",\n      \"bowl 4\",\n      \"bowl 5\",\n      \"bowl 6\",\n      \"bowl 7\",\n      \"bowl 8\",\n      \"bowl 9\",\n      \"box 1\",\n      \"box 2\",\n      \"box 3\",\n      \"box 4\",\n      \"box 5\",\n      \"bucket 1\",\n      \"cabinet 1\",\n      \"candle 1\",\n      \"candy bar 1\",\n      \"ceiling 1\",\n      \"ceiling 10\",\n      \"ceiling 11\",\n      \"ceiling 12\",\n      \"ceiling 13\",\n      \"ceiling 14\",\n      \"ceiling 15\",\n      \"ceiling 16\",\n      \"ceiling 17\",\n      \"ceiling 18\",\n      \"ceiling 19\",\n      \"ceiling 2\",\n      \"ceiling 20\",\n      \"ceiling 21\",\n      \"ceiling 22\",\n      \"ceiling 23\",\n      \"ceiling 24\",\n      \"ceiling 25\",\n      \"ceiling 26\",\n      \"ceiling 3\",\n      \"ceiling 4\",\n      \"ceiling 5\",\n      \"ceiling 6\",\n      \"ceiling 7\",\n      \"ceiling 8\",\n      \"ceiling 9\",\n      \"ceiling lamp 1\",\n      \"ceiling lamp 2\",\n      \"ceiling lamp 3\",\n      \"ceiling lamp 4\",\n      \"ceiling lamp 5\",\n      \"cell phone 1\",\n      \"cell phone 2\",\n      \"cereal 1\",\n      \"chair 1\",\n      \"chair 2\",\n      \"chair 3\",\n      \"chair 4\",\n      \"chair 5\",\n      \"chair 6\",\n      \"chips 1\",\n      \"chips 2\",\n      \"chocolate syrup 1\",\n      \"closet 1\",\n      \"closet drawer 1\",\n      \"closet drawer 2\",\n      \"closet drawer 3\",\n      \"closet drawer 4\",\n      \"closet drawer 5\",\n      \"closet drawer 6\",\n      \"closet drawer 7\",\n      \"coffee maker 1\",\n      \"coffee pot 1\",\n      \"coffee table 1\",\n      \"computer 1\",\n      \"condiment bottle 1\",\n      \"condiment bottle 2\",\n      \"condiment bottle 3\",\n      \"condiment bottle 4\",\n      \"condiment shaker 1\",\n      \"condiment shaker 2\",\n      \"condiment shaker 3\",\n      \"condiment shaker 4\",\n      \"cooking pot 1\",\n      \"cooking pot 2\",\n      \"cpu screen 1\",\n      \"crackers 1\",\n      \"crackers 2\",\n      \"creamy buns 1\",\n      \"cupcake 1\",\n      \"cupcake 2\",\n      \"cupcake 3\",\n      \"curtains 1\",\n      \"curtains 2\",\n      \"curtains 3\",\n      \"curtains 4\",\n      \"curtains 5\",\n      \"curtains 6\",\n      \"curtains 7\",\n      \"cutlery fork 1\",\n      \"cutlery fork 2\",\n      \"cutlery fork 3\",\n      \"cutlery fork 4\",\n      \"cutlery knife 1\",\n      \"cutlery knife 2\",\n      \"cutlery knife 3\",\n      \"cutlery knife 4\",\n      \"cutlery knife 5\",\n      \"cutlery knife 6\",\n      \"cutlets 1\",\n      \"deodorant 1\",\n      \"deodorant 2\",\n      \"deodorant 3\",\n      \"desk 1\",\n      \"desk 2\",\n      \"dishwasher 1\",\n      \"dishwashing liquid 1\",\n      \"door 1\",\n      \"door 2\",\n      \"door 3\",\n      \"door jamb 1\",\n      \"door jamb 2\",\n      \"door jamb 3\",\n      \"door jamb 4\",\n      \"face cream 1\",\n      \"face cream 2\",\n      \"face cream 3\",\n      \"faucet 1\",\n      \"faucet 2\",\n      \"floor 1\",\n      \"floor 10\",\n      \"floor 11\",\n      \"floor 12\",\n      \"floor 13\",\n      \"floor 14\",\n      \"floor 15\",\n      \"floor 16\",\n      \"floor 17\",\n      \"floor 18\",\n      \"floor 19\",\n      \"floor 2\",\n      \"floor 20\",\n      \"floor 21\",\n      \"floor 22\",\n      \"floor 23\",\n      \"floor 24\",\n      \"floor 25\",\n      \"floor 26\",\n      \"floor 3\",\n      \"floor 4\",\n      \"floor 5\",\n      \"floor 6\",\n      \"floor 7\",\n      \"floor 8\",\n      \"floor 9\",\n      \"folder 1\",\n      \"folder 2\",\n      \"folder 3\",\n      \"folder 4\",\n      \"fridge 1\",\n      \"frying pan 1\",\n      \"hair product 1\",\n      \"hair product 2\",\n      \"hair product 3\",\n      \"hair product 4\",\n      \"hanger 1\",\n      \"hanger 2\",\n      \"hanger 3\",\n      \"hanger 4\",\n      \"hanger 5\",\n      \"hanger 6\",\n      \"hanger 7\",\n      \"juice 1\",\n      \"juice 2\",\n      \"keyboard 1\",\n      \"kitchen 1\",\n      \"kitchen cabinet 1\",\n      \"kitchen cabinet 2\",\n      \"kitchen cabinet 3\",\n      \"kitchen cabinet 4\",\n      \"kitchen cabinet 5\",\n      \"kitchen cabinet 6\",\n      \"kitchen cabinet 7\",\n      \"kitchen cabinet 8\",\n      \"kitchen counter 1\",\n      \"kitchen counter 2\",\n      \"kitchen counter 3\",\n      \"kitchen counter drawer 1\",\n      \"kitchen counter drawer 2\",\n      \"kitchen counter drawer 3\",\n      \"kitchen counter drawer 4\",\n      \"kitchen counter drawer 5\",\n      \"kitchen counter drawer 6\",\n      \"kitchen counter drawer 7\",\n      \"kitchen counter drawer 8\",\n      \"kitchen table 1\",\n      \"knife block 1\",\n      \"light switch 1\",\n      \"light switch 2\",\n      \"light switch 3\",\n      \"light switch 4\",\n      \"lime 1\",\n      \"living room 1\",\n      \"microwave oven 1\",\n      \"milk 1\",\n      \"mouse 1\",\n      \"mouse mat 1\",\n      \"mug 1\",\n      \"mug 2\",\n      \"mug 3\",\n      \"nightstand 1\",\n      \"nightstand 2\",\n      \"nightstand 3\",\n      \"nightstand 4\",\n      \"notes 1\",\n      \"orchid 1\",\n      \"oven tray 1\",\n      \"painkillers 1\",\n      \"pancake 1\",\n      \"peach 1\",\n      \"peach 2\",\n      \"peach 3\",\n      \"pear 1\",\n      \"perfume 1\",\n      \"perfume 2\",\n      \"photo frame 1\",\n      \"photo frame 2\",\n      \"photo frame 3\",\n      \"pile of clothes 1\",\n      \"pile of clothes 2\",\n      \"pillow 1\",\n      \"pillow 2\",\n      \"pillow 3\",\n      \"pillow 4\",\n      \"pillow 5\",\n      \"pillow 6\",\n      \"plate 1\",\n      \"plate 2\",\n      \"plate 3\",\n      \"plate 4\",\n      \"plate 5\",\n      \"plate 6\",\n      \"plate 7\",\n      \"plum 1\",\n      \"plum 2\",\n      \"power socket 1\",\n      \"power socket 2\",\n      \"power socket 3\",\n      \"pudding 1\",\n      \"pudding 2\",\n      \"radio 1\",\n      \"rug 1\",\n      \"rug 2\",\n      \"rug 3\",\n      \"rug 4\",\n      \"sink 1\",\n      \"sink 2\",\n      \"slice of bread 1\",\n      \"slice of bread 2\",\n      \"sofa 1\",\n      \"sofa 2\",\n      \"sofa 3\",\n      \"stall 1\",\n      \"stall 2\",\n      \"stove 1\",\n      \"stove fan 1\",\n      \"table lamp 1\",\n      \"toaster 1\",\n      \"toilet 1\",\n      \"toilet paper 1\",\n      \"toothbrush 1\",\n      \"toothpaste 1\",\n      \"tv 1\",\n      \"tv stand 1\",\n      \"wall 1\",\n      \"wall 10\",\n      \"wall 11\",\n      \"wall 12\",\n      \"wall 13\",\n      \"wall 14\",\n      \"wall 15\",\n      \"wall 16\",\n      \"wall 17\",\n      \"wall 18\",\n      \"wall 19\",\n      \"wall 2\",\n      \"wall 20\",\n      \"wall 21\",\n      \"wall 22\",\n      \"wall 23\",\n      \"wall 24\",\n      \"wall 25\",\n      \"wall 26\",\n      \"wall 3\",\n      \"wall 4\",\n      \"wall 5\",\n      \"wall 6\",\n      \"wall 7\",\n      \"wall 8\",\n      \"wall 9\",\n      \"wall lamp 1\",\n      \"wall lamp 2\",\n      \"wall lamp 3\",\n      \"wall lamp 4\",\n      \"wall lamp 5\",\n      \"wall lamp 6\",\n      \"wall lamp 7\",\n      \"wall lamp 8\",\n      \"wall lamp 9\",\n      \"wall phone 1\",\n      \"wall picture frame 1\",\n      \"wall picture frame 2\",\n      \"wall picture frame 3\",\n      \"wall picture frame 4\",\n      \"wall picture frame 5\",\n      \"wall picture frame 6\",\n      \"wall picture frame 7\",\n      \"wall picture frame 8\",\n      \"wall shelf 1\",\n      \"wall shelf 2\",\n      \"washing machine 1\",\n      \"washing sponge 1\",\n      \"water glass 1\",\n      \"water glass 2\",\n      \"water glass 3\",\n      \"water glass 4\",\n      \"water glass 5\",\n      \"window 1\",\n      \"window 2\",\n      \"wine 1\"\n    ]\n  },\n  \"evaluation_context\": {},\n  \"external_goal\": {\n    \"has_external_goal\": true,\n    \"external_goal_state\": {},\n    \"external_goal_text\": \"\",\n    \"structured_goal_state\": {},\n    \"structured_final_state\": {\n      \"on_cupcake_coffeetable\": 1,\n      \"on_apple_coffeetable\": 1\n    }\n  },\n  \"benchmark_final_state_compare\": {\n    \"benchmark\": \"ReAcTree-WAH\",\n    \"status\": \"prepared_for_framework_llm_judge\",\n    \"environment_format\": \"WAH runtime_initial_environment 的 scene/env_state，保留 WAH/VirtualHome 对象标签\",\n    \"action_format\": \"WAH/ReAcTree 原生动作 JSON 对象：{action, target}\",\n    \"official_evaluator\": \"ReAcTree WAH 官方 Unity evaluator\",\n    \"used_fields\": {\n      \"task_context\": [\n        \"available_entities\",\n        \"dataset\",\n        \"env_id\",\n        \"environment_source\",\n        \"init_graph_cache_path\",\n        \"init_room\",\n        \"instruction\",\n        \"task_goal\",\n        \"task_name\",\n        \"task_source\"\n      ],\n      \"evaluation_context\": [],\n      \"external_goal\": [\n        \"has_external_goal\",\n        \"structured_final_state\"\n      ],\n      \"state_diff\": [\n        \"entities\",\n        \"robot\"\n      ]\n    },\n    \"benchmark_goal\": {\n      \"task_context\": {\n        \"dataset\": \"reactree\",\n        \"env_id\": 3,\n        \"task_name\": \"prepare_snack\",\n        \"instruction\": \"Put one cupcake and one apple on the coffee table\",\n        \"init_room\": \"bedroom\",\n        \"task_source\": \"reactree_wah_testset\",\n        \"environment_source\": \"reactree_case_runtime_scene\",\n        \"init_graph_cache_path\": \"/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/initial_envs/0.json\",\n        \"task_goal\": {\n          \"on_cupcake_coffeetable\": 1,\n          \"on_apple_coffeetable\": 1\n        },\n        \"available_entities\": [\n          \"apple 1\",\n          \"apple 2\",\n          \"apple 3\",\n          \"bananas 1\",\n          \"bar soap 1\",\n          \"bathroom 1\",\n          \"bathroom cabinet 1\",\n          \"bathroom counter 1\",\n          \"bed 1\",\n          \"bedroom 1\",\n          \"book 1\",\n          \"book 2\",\n          \"bookshelf 1\",\n          \"bookshelf 2\",\n          \"bookshelf 3\",\n          \"bowl 1\",\n          \"bowl 2\",\n          \"bowl 3\",\n          \"bowl 4\",\n          \"bowl 5\",\n          \"bowl 6\",\n          \"bowl 7\",\n          \"bowl 8\",\n          \"bowl 9\",\n          \"box 1\",\n          \"box 2\",\n          \"box 3\",\n          \"box 4\",\n          \"box 5\",\n          \"bucket 1\",\n          \"cabinet 1\",\n          \"candle 1\",\n          \"candy bar 1\",\n          \"ceiling 1\",\n          \"ceiling 10\",\n          \"ceiling 11\",\n          \"ceiling 12\",\n          \"ceiling 13\",\n          \"ceiling 14\",\n          \"ceiling 15\",\n          {\n            \"_truncated\": 303\n          }\n        ]\n      },\n      \"evaluation_context\": {},\n      \"goal_projection\": {},\n      \"external_goal\": {\n        \"has_external_goal\": true,\n        \"external_goal_state\": {},\n        \"external_goal_text\": \"\",\n        \"structured_goal_state\": {},\n        \"structured_final_state\": {\n          \"on_cupcake_coffeetable\": 1,\n          \"on_apple_coffeetable\": 1\n        }\n      }\n    },\n    \"understanding_final_state\": {\n      \"on_cupcake_coffeetable\": 1,\n      \"on_apple_coffeetable\": 1\n    },\n    \"state_diff_summary\": {\n      \"entity_count_compared\": 17,\n      \"changed_entity_count\": 2,\n      \"changed_entities\": [\n        \"apple 2\",\n        \"cupcake 1\"\n      ],\n      \"changed_entities_truncated\": false,\n      \"robot_changed\": true,\n      \"robot_change\": {\n        \"changed\": true,\n        \"before\": {\n          \"robot_location\": \"bedroom 1\",\n          \"robot_holding\": \"空\"\n        },\n        \"after\": {\n          \"robot_location\": \"coffee table 1\",\n          \"robot_holding\": \"空\"\n        }\n      }\n    },\n    \"initial_environment_summary\": {\n      \"available\": true,\n      \"entity_count\": 17,\n      \"type_counts\": {\n        \"unknown\": 7,\n        \"room\": 3,\n        \"receptacle\": 7\n      },\n      \"states_sample\": {\n        \"cabinet 1\": {\n          \"isOpen\": false\n        },\n        \"fridge 1\": {\n          \"isOpen\": false\n        }\n      },\n      \"relations_sample\": {\n        \"cupcake 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"kitchen table 1\"\n        },\n        \"kitchen 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 2\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen 1\"\n        },\n        \"kitchen table 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 2\"\n        },\n        \"cupcake 2\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"kitchen table 1\"\n        },\n        \"cupcake 3\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"cabinet 1\"\n        },\n        \"bedroom 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 16\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"bedroom 1\"\n        },\n        \"cabinet 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 16\"\n        },\n        \"apple 1\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"fridge 1\"\n        },\n        \"floor 4\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen 1\"\n        },\n        \"fridge 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 4\"\n        },\n        \"apple 2\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"kitchen table 1\"\n        },\n        \"apple 3\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"cabinet 1\"\n        },\n        \"coffee table 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 25\"\n        },\n        \"living room 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 25\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"living room 1\"\n        }\n      }\n    },\n    \"final_environment_summary\": {\n      \"available\": true,\n      \"entity_count\": 17,\n      \"type_counts\": {\n        \"unknown\": 7,\n        \"room\": 3,\n        \"receptacle\": 7\n      },\n      \"states_sample\": {\n        \"cabinet 1\": {\n          \"isOpen\": false\n        },\n        \"fridge 1\": {\n          \"isOpen\": false\n        }\n      },\n      \"relations_sample\": {\n        \"cupcake 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"coffee table 1\"\n        },\n        \"kitchen 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 2\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen 1\"\n        },\n        \"kitchen table 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 2\"\n        },\n        \"cupcake 2\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"kitchen table 1\"\n        },\n        \"cupcake 3\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"cabinet 1\"\n        },\n        \"bedroom 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 16\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"bedroom 1\"\n        },\n        \"cabinet 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 16\"\n        },\n        \"apple 1\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"fridge 1\"\n        },\n        \"floor 4\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"kitchen 1\"\n        },\n        \"fridge 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 4\"\n        },\n        \"apple 2\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"coffee table 1\"\n        },\n        \"apple 3\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"cabinet 1\"\n        },\n        \"coffee table 1\": {\n          \"direct_relation\": \"on\",\n          \"direct_parent\": \"floor 25\"\n        },\n        \"living room 1\": {\n          \"direct_relation\": \"\",\n          \"direct_parent\": \"未知环境\"\n        },\n        \"floor 25\": {\n          \"direct_relation\": \"inside\",\n          \"direct_parent\": \"living room 1\"\n        }\n      }\n    },\n    \"initial_robot\": {\n      \"robot_location\": \"bedroom 1\",\n      \"robot_holding\": \"空\"\n    },\n    \"final_robot\": {\n      \"robot_location\": \"coffee table 1\",\n      \"robot_holding\": \"空\"\n    },\n    \"fairness_notes\": [\n      \"task_goal 来自 WAH 官方评测目标，只作为最终态审计目标投影，不作为动作序列答案。\"\n    ],\n    \"judge_contract\": \"公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。\",\n    \"enabled\": true,\n    \"comparer_module\": \"benchmark.reactree.wah.framework.code.final_state\"\n  }\n}\n\n判定边界：\n1. 优先读取 state_audit_context.benchmark_final_state_compare；其中包含 WAH task_goal 和本地环境差异摘要。\n2. 结合 understanding final_state、task_goal、sandbox final environment/final robot 和 state_diff 判断关键目标是否完成。\n3. 不使用 expert trajectory 或官方动作答案；保持 WAH/ReAcTree 的对象命名和关系语义。\n4. 如果关键目标缺失，is_passed=false，并写出缺失的最终状态和后续 planning 应补的动作类型。\n5. 如果当前最终态只需追加动作即可修复，repair_mode=\"continue_from_current\"；如果已验证前缀本身错，repair_mode=\"reset_and_replan\"。\n\n输出 JSON：\n{\"is_passed\": true, \"issue\": \"\", \"fix_advice\": \"\", \"repair_mode\": \"continue_from_current\", \"accepted_diffs\": [], \"unexpected_diffs\": []}"
  }
]
```

```text
{
  "is_passed": true,
  "issue": "",
  "fix_advice": "",
  "repair_mode": "continue_from_current",
  "accepted_diffs": [
    "cupcake 1 moved to coffee table 1",
    "apple 2 moved to coffee table 1"
  ],
  "unexpected_diffs": []
}
```


## 10. 官方原生动作 / 官方评测摘要

### Official Actions
```json
[
  "go to kitchen table 1",
  "pick up cupcake 1",
  "go to coffee table 1",
  "put down cupcake 1",
  "go to kitchen table 1",
  "pick up apple 2",
  "go to coffee table 1",
  "put down apple 2"
]
```

### Evaluator Execution Calls
```json
[
  {
    "skill": "go to",
    "parameters": {
      "target": "kitchen table 1"
    }
  },
  {
    "skill": "pick up",
    "parameters": {
      "target": "cupcake 1"
    }
  },
  {
    "skill": "go to",
    "parameters": {
      "target": "coffee table 1"
    }
  },
  {
    "skill": "put down",
    "parameters": {
      "target": "cupcake 1"
    }
  },
  {
    "skill": "go to",
    "parameters": {
      "target": "kitchen table 1"
    }
  },
  {
    "skill": "pick up",
    "parameters": {
      "target": "apple 2"
    }
  },
  {
    "skill": "go to",
    "parameters": {
      "target": "coffee table 1"
    }
  },
  {
    "skill": "put down",
    "parameters": {
      "target": "apple 2"
    }
  }
]
```

### Evaluation Summary
```json
{
  "goal_success_rate": 1.0,
  "subgoal_success_rate": 1.0,
  "evaluation_mode": "reactree_official_wah_unity",
  "official_available": true,
  "execution_success": true,
  "action_trace": [
    {
      "feedback": "You arrive at the kitchen table (1).",
      "official_skill": "go to kitchen table 1",
      "possible": true,
      "source_skill": "go",
      "source_step": 1
    },
    {
      "feedback": "You pick up cupcake.",
      "official_skill": "pick up cupcake 1",
      "possible": true,
      "source_skill": "pick",
      "source_step": 2
    },
    {
      "feedback": "You arrive at the coffee table (1).",
      "official_skill": "go to coffee table 1",
      "possible": true,
      "source_skill": "go",
      "source_step": 3
    },
    {
      "feedback": "You put down cupcake on coffee table",
      "official_skill": "put down cupcake 1",
      "possible": true,
      "source_skill": "put",
      "source_step": 4
    },
    {
      "feedback": "You arrive at the kitchen table (1).",
      "official_skill": "go to kitchen table 1",
      "possible": true,
      "source_skill": "go",
      "source_step": 5
    },
    {
      "feedback": "You pick up apple.",
      "official_skill": "pick up apple 2",
      "possible": true,
      "source_skill": "pick",
      "source_step": 6
    },
    {
      "feedback": "You arrive at the coffee table (1).",
      "official_skill": "go to coffee table 1",
      "possible": true,
      "source_skill": "go",
      "source_step": 7
    },
    {
      "feedback": "You put down apple on coffee table",
      "official_skill": "put down apple 2",
      "possible": true,
      "source_skill": "put",
      "source_step": 8
    }
  ]
}
```
