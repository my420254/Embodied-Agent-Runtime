# Round 3 planning.main_system Input

## Message 1: system

任务：生成 VirtualHome 官方原生动作计划。
只输出 JSON；不要解释，不要输出 Markdown。

原始任务：


规划目标：
Relax on sofa

机器人状态：
- 位置：bedroom_anchor
- 手持：空
- 完整状态：{"robot_location":"bedroom_anchor","robot_holding":"空","robot_hands":{"left":"空","right":"空"},"manipulator_mode":"dual_arm"}

当前环境 JSON：
{"couch":{"direct_parent":"mat_401","direct_relation":"ontop","type":"receptacle","states":{"isClean":true,"isDirty":false},"properties":["SITTABLE","MOVABLE","SURFACES","LIEABLE"],"is_container":true,"full_path":["home_office","home_office_anchor","mat_401"]},"home_office":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"home_office_anchor":{"direct_parent":"home_office","direct_relation":"inside","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["home_office"]},"mat_401":{"direct_parent":"home_office_anchor","direct_relation":"inside","type":"receptacle","states":{"isDirty":true,"isClean":false},"properties":["GRABBABLE","SURFACES","MOVABLE","SITTABLE","LIEABLE"],"is_container":true,"full_path":["home_office","home_office_anchor"]},"bedroom_anchor":{"direct_parent":"bedroom","direct_relation":"inside","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["bedroom"]},"bedroom":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"bathroom":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]},"dining_room":{"direct_parent":"未知环境","direct_relation":null,"type":"room","states":{},"properties":[],"is_container":false,"full_path":[]}}

任务相关环境事实：
[{"name":"bathroom","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"bedroom","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"bedroom_anchor","direct_parent":"bedroom","full_path":["bedroom"],"states":{},"type":"receptacle","is_container":true},{"name":"couch","direct_parent":"mat_401","full_path":["home_office","home_office_anchor","mat_401"],"states":{"isClean":true,"isDirty":false},"type":"receptacle","is_container":true},{"name":"dining_room","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"home_office","direct_parent":"未知环境","full_path":[],"states":{},"type":"room","is_container":false},{"name":"home_office_anchor","direct_parent":"home_office","full_path":["home_office"],"states":{},"type":"receptacle","is_container":true},{"name":"mat_401","direct_parent":"home_office_anchor","full_path":["home_office","home_office_anchor"],"states":{"isDirty":true,"isClean":false},"type":"receptacle","is_container":true}]

任务上下文：
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

理解层实体选择：
{
  "targets": {
    "primary": [
      "couch"
    ],
    "alternatives": []
  },
  "tools": {
    "primary": [],
    "alternatives": []
  },
  "receptacles": {
    "primary": [],
    "alternatives": []
  }
}

可用动作与 skill 契约：
<available_skills>
---
name: WALK
description: Official VirtualHome WALK action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `WALK`。 |
| args | array[string] | 长度为 1；args[0] 是要靠近的 VirtualHome 场景对象或位置。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 只有在目标位置或交互锚点当前不可直接到达时，才应导航。
- 如果机器人已经处于同一个可交互位置簇，不要重复导航。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，模拟机器人位置应更新到目标位置或可交互锚点。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "WALK", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: FIND
description: Official VirtualHome FIND action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `FIND`。 |
| args | array[string] | 长度为 1；args[0] 是要寻找或靠近的 VirtualHome 场景对象或位置。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 只有在目标位置或交互锚点当前不可直接到达时，才应导航。
- 如果机器人已经处于同一个可交互位置簇，不要重复导航。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，模拟机器人位置应更新到目标位置或可交互锚点。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "FIND", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: RUN
description: Official VirtualHome RUN action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RUN`。 |
| args | array[string] | 长度为 1；args[0] 是要快速靠近的 VirtualHome 场景对象或位置。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 只有在目标位置或交互锚点当前不可直接到达时，才应导航。
- 如果机器人已经处于同一个可交互位置簇，不要重复导航。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，模拟机器人位置应更新到目标位置或可交互锚点。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RUN", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: GRAB
description: Official VirtualHome GRAB action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `GRAB`。 |
| args | array[string] | 长度为 1；args[0] 是要抓取的 VirtualHome 场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标物体必须可达，并且对应手或携带槽位必须可用。
- 如果 benchmark 使用多只手，必须依据各只手的占用状态判断，而不是假设只有一个抓手。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标物体会进入对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "GRAB", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: PUTIN
description: Official VirtualHome PUTIN action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `PUTIN`。 |
| args | array[string] | 长度为 2；args[0] 是当前已持有的源对象，args[1] 是目标容器。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "PUTIN", "args": ["<source>", "<destination>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: PUTON
description: Official VirtualHome PUTON action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `PUTON`。 |
| args | array[string] | 长度为 1；args[0] 是要穿戴或放到 character 身上的对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "PUTON", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: PUTBACK
description: Official VirtualHome PUTBACK action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `PUTBACK`。 |
| args | array[string] | 长度为 2；args[0] 是当前已持有的源对象，args[1] 是要放回的目标位置。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带该步引用的物体。
- 如果目标位置是容器类对象，则其开闭状态和容量约束必须满足 handler 的校验规则。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到目标位置，并在需要时释放对应手或携带槽位。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "PUTBACK", "args": ["<source>", "<destination>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: OPEN
description: Official VirtualHome OPEN action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `OPEN`。 |
| args | array[string] | 长度为 1；args[0] 是要打开的 VirtualHome 容器或可开合对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须支持当前请求的状态切换。
- 如果 benchmark 区分 open/close 或 on/off 的先决条件，则以 `handler.validate(...)` 的检查为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "OPEN", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: CLOSE
description: Official VirtualHome CLOSE action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `CLOSE`。 |
| args | array[string] | 长度为 1；args[0] 是要关闭的 VirtualHome 容器或可开合对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须支持当前请求的状态切换。
- 如果 benchmark 区分 open/close 或 on/off 的先决条件，则以 `handler.validate(...)` 的检查为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "CLOSE", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。

---
name: SWITCHON
description: Official VirtualHome SWITCHON action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `SWITCHON`。 |
| args | array[string] | 长度为 1；args[0] 是要打开开关的 VirtualHome 设备对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须支持当前请求的状态切换。
- 如果 benchmark 区分 open/close 或 on/off 的先决条件，则以 `handler.validate(...)` 的检查为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "SWITCHON", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: SWITCHOFF
description: Official VirtualHome SWITCHOFF action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `SWITCHOFF`。 |
| args | array[string] | 长度为 1；args[0] 是要关闭开关的 VirtualHome 设备对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须支持当前请求的状态切换。
- 如果 benchmark 区分 open/close 或 on/off 的先决条件，则以 `handler.validate(...)` 的检查为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "SWITCHOFF", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: PLUGIN
description: Official VirtualHome PLUGIN action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `PLUGIN`。 |
| args | array[string] | 长度为 1；args[0] 是要接通电源的 VirtualHome 设备对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须支持插电语义，例如带有 `HAS_PLUG` 或 `PLUGGABLE` 属性。
- 如果对象已经处于插电状态，不应重复执行。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的插电状态应更新为 true。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "PLUGIN", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: WATCH
description: Official VirtualHome WATCH action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `WATCH`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须从当前机器人状态可交互，并满足 benchmark-local handler 的前提约束。
- `handler.validate(...)` 要求当前 `robot_facing` 已经是目标。
- 如果该交互依赖 holding、wearing、sitting、lying 或 facing 等状态，则以 handler 校验为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，只会更新 handler 明确规定的机器人状态和场景状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "WATCH", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: LOOKAT
description: Official VirtualHome LOOKAT action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LOOKAT`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须从当前机器人状态可交互，并满足 benchmark-local handler 的前提约束。
- `handler.validate(...)` 要求当前 `robot_facing` 已经是目标。
- 如果该交互依赖 holding、wearing、sitting、lying 或 facing 等状态，则以 handler 校验为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，只会更新 handler 明确规定的机器人状态和场景状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LOOKAT", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: LOOKAT_SHORT
description: VirtualHome LOOKAT_SHORT action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LOOKAT_SHORT`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 与 `LOOKAT` 相同。

## 执行效果
- 与 `LOOKAT` 相同。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LOOKAT_SHORT", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: LOOKAT_MEDIUM
description: VirtualHome LOOKAT_MEDIUM action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LOOKAT_MEDIUM`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 与 `LOOKAT` 相同。

## 执行效果
- 与 `LOOKAT` 相同。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LOOKAT_MEDIUM", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: LOOKAT_LONG
description: VirtualHome LOOKAT_LONG action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LOOKAT_LONG`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 与 `LOOKAT` 相同。

## 执行效果
- 与 `LOOKAT` 相同。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LOOKAT_LONG", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: TOUCH
description: Official VirtualHome TOUCH action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `TOUCH`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须从当前机器人状态可交互，并满足 benchmark-local handler 的前提约束。
- 如果该交互依赖 holding、wearing、sitting、lying 或 facing 等状态，则以 handler 校验为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，只会更新 handler 明确规定的机器人状态和场景状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "TOUCH", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: POINTAT
description: Official VirtualHome POINTAT action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `POINTAT`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须从当前机器人状态可交互，并满足 benchmark-local handler 的前提约束。
- 如果该交互依赖 holding、wearing、sitting、lying 或 facing 等状态，则以 handler 校验为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，只会更新 handler 明确规定的机器人状态和场景状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "POINTAT", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: TURNTO
description: Official VirtualHome TURNTO action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `TURNTO`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须从当前机器人状态可交互，并满足 benchmark-local handler 的前提约束。
- 如果该交互依赖 holding、wearing、sitting、lying 或 facing 等状态，则以 handler 校验为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，只会更新 handler 明确规定的机器人状态和场景状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "TURNTO", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: READ
description: Official VirtualHome READ action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `READ`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须从当前机器人状态可交互，并满足 benchmark-local handler 的前提约束。
- 如果该交互依赖 holding、wearing、sitting、lying 或 facing 等状态，则以 handler 校验为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，只会更新 handler 明确规定的机器人状态和场景状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "READ", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: TYPE
description: Official VirtualHome TYPE action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `TYPE`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须从当前机器人状态可交互，并满足 benchmark-local handler 的前提约束。
- 如果该交互依赖 holding、wearing、sitting、lying 或 facing 等状态，则以 handler 校验为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，只会更新 handler 明确规定的机器人状态和场景状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "TYPE", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: DRINK
description: Official VirtualHome DRINK action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `DRINK`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须从当前机器人状态可交互，并满足 benchmark-local handler 的前提约束。
- 如果该交互依赖 holding、wearing、sitting、lying 或 facing 等状态，则以 handler 校验为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，只会更新 handler 明确规定的机器人状态和场景状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "DRINK", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: SIT
description: Official VirtualHome SIT action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `SIT`。 |
| args | array[string] | 长度为 1；args[0] 是要坐下的座椅、沙发或床等对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须从当前机器人状态可交互，并满足 benchmark-local handler 的前提约束。
- 如果该交互依赖 holding、wearing、sitting、lying 或 facing 等状态，则以 handler 校验为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，只会更新 handler 明确规定的机器人状态和场景状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "SIT", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: LIE
description: Official VirtualHome LIE action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `LIE`。 |
| args | array[string] | 长度为 1；args[0] 是要躺下的床或可躺对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须从当前机器人状态可交互，并满足 benchmark-local handler 的前提约束。
- 如果该交互依赖 holding、wearing、sitting、lying 或 facing 等状态，则以 handler 校验为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，只会更新 handler 明确规定的机器人状态和场景状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "LIE", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: SLEEP
description: Official VirtualHome SLEEP action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `SLEEP`。 |
| args | array[string] | 长度为 0；必须写成空数组 []。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 执行 `SLEEP` 前，机器人必须已经处于 `lying` 或 `sitting` 状态。

## 执行效果
- 如果校验通过，`SLEEP` 作为 0 参数动作通过。
- `SLEEP` 本身不重新选择床位目标，它只确认“已经躺下/坐下后进入睡眠动作”。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "SLEEP", "args": []}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: STANDUP
description: Official VirtualHome STANDUP action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `STANDUP`。 |
| args | array[string] | 长度为 0；必须写成空数组 []。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 机器人必须当前处于 sitting / lying / sleeping 状态。

## 执行效果
- 机器人恢复站立状态。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "STANDUP", "args": []}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: WAKEUP
description: Official VirtualHome WAKEUP action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `WAKEUP`。 |
| args | array[string] | 长度为 0；必须写成空数组 []。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 机器人必须当前处于 lying / sleeping / sitting 状态。

## 执行效果
- 机器人从睡眠/休息状态恢复站立。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "WAKEUP", "args": []}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: DROP
description: Official VirtualHome DROP action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `DROP`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标物体必须存在。
- 机器人当前必须持有该物体。

## 执行效果
- 释放当前持有的目标物体。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "DROP", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: RELEASE
description: Official VirtualHome RELEASE action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RELEASE`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标必须存在。
- 机器人当前必须持有该物体。

## 执行效果
- 在当前交互位置释放目标物体。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RELEASE", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: PUTOBJBACK
description: Official VirtualHome PUTOBJBACK action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `PUTOBJBACK`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标必须存在。
- 机器人当前必须持有该物体。

## 执行效果
- 将当前持有物放回当前交互位置。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "PUTOBJBACK", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: PUTOFF
description: Official VirtualHome PUTOFF action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `PUTOFF`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标必须存在。
- 目标必须当前穿在 character 身上，并满足 CLOTHES。

## 执行效果
- 将衣物从 character 身上移除到当前交互位置。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "PUTOFF", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: GREET
description: Official VirtualHome GREET action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `GREET`。 |
| args | array[string] | 长度为 1；args[0] 是要问候的 VirtualHome 人物对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标必须存在。
- 目标必须是 PERSON。
- `handler.validate(...)` 要求机器人当前已在目标或目标父节点位置。

## 执行效果
- 记录最近被问候的目标。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "GREET", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: POUR
description: Official VirtualHome POUR action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `POUR`。 |
| args | array[string] | 长度为 2；args[0] 是当前已持有的源对象，args[1] 是接受内容物的目标容器。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 源物体必须存在并被持有。
- 源物体应满足 POURABLE/DRINKABLE。
- 目标物体必须是 RECIPIENT，且机器人已靠近目标。

## 执行效果
- 将源物体倾倒到目标容器。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "POUR", "args": ["<source>", "<destination>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: MOVE
description: Official VirtualHome MOVE action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `MOVE`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标必须存在。
- 目标应满足 MOVABLE 或等价可移动条件。
- `handler.validate(...)` 要求机器人当前已在目标或目标父节点位置，并且至少有一只空闲手。

## 执行效果
- 记录最近被移动的目标。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "MOVE", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: PUSH
description: Official VirtualHome PUSH action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `PUSH`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标必须存在。
- `handler.validate(...)` 要求机器人当前已在目标或目标父节点位置，并且至少有一只空闲手。

## 执行效果
- 记录最近被推动的目标。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "PUSH", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: PULL
description: Official VirtualHome PULL action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `PULL`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标必须存在。
- `handler.validate(...)` 要求机器人当前已在目标或目标父节点位置，并且至少有一只空闲手。

## 执行效果
- 记录最近被拉动的目标。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "PULL", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: SQUEEZE
description: Official VirtualHome SQUEEZE action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `SQUEEZE`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标必须存在。
- 机器人必须已靠近或持有该物体，并留有空闲手。
- 目标应满足 CLOTHES 或布类物体语义。

## 执行效果
- 将目标标记为不再 soaked。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "SQUEEZE", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: PLUGOUT
description: Official VirtualHome PLUGOUT action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `PLUGOUT`。 |
| args | array[string] | 长度为 1；args[0] 是要断开电源的 VirtualHome 设备对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标必须存在，并且支持插头。
- `handler.validate(...)` 要求机器人当前已在目标或目标父节点位置，并且至少有一只空闲手。
- 目标当前必须处于已插电且关闭状态。

## 执行效果
- 将目标设备标记为已断电。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "PLUGOUT", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: EAT
description: Official VirtualHome EAT action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `EAT`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 目标必须是可食用物体。
- 机器人必须已经靠近或持有该物体。

## 执行效果
- 将目标标记为已消费。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "EAT", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: WASH
description: Official VirtualHome WASH action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `WASH`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 所需工具、液体状态或清洁装置状态，必须已经满足 handler 的校验规则。
- 不要假设工具会自动变湿、变干净或自动可用；只有已验证步骤造成的状态变化才有效。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会按 handler 约定更新清洁、浸湿或相关状态标志。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "WASH", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: WIPE
description: Official VirtualHome WIPE action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `WIPE`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 所需工具、液体状态或清洁装置状态，必须已经满足 handler 的校验规则。
- 不要假设工具会自动变湿、变干净或自动可用；只有已验证步骤造成的状态变化才有效。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会按 handler 约定更新清洁、浸湿或相关状态标志。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "WIPE", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: SCRUB
description: Official VirtualHome SCRUB action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `SCRUB`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 所需工具、液体状态或清洁装置状态，必须已经满足 handler 的校验规则。
- 不要假设工具会自动变湿、变干净或自动可用；只有已验证步骤造成的状态变化才有效。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会按 handler 约定更新清洁、浸湿或相关状态标志。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "SCRUB", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: RINSE
description: Official VirtualHome RINSE action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `RINSE`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 所需工具、液体状态或清洁装置状态，必须已经满足 handler 的校验规则。
- 不要假设工具会自动变湿、变干净或自动可用；只有已验证步骤造成的状态变化才有效。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会按 handler 约定更新清洁、浸湿或相关状态标志。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "RINSE", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: CUT
description: Official VirtualHome CUT action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `CUT`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 任何所需工具、支撑平面或放置前提，都必须已由更早的已验证步骤满足。
- 如果 benchmark 会生成切片后的 part 对象，则后续必须在 handler 要求时改用这些 part 对象。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会更新切片状态，并可能生成新的 part 对象或改变后续可用的目标对象名。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "CUT", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: COOK
description: Official VirtualHome COOK action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `COOK`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象以及任何依赖的支持状态，必须已经满足 benchmark-local handler 的校验。
- 不要假设隐藏设备、隐藏工具或隐藏容器；只依赖当前场景状态和已验证动作。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会更新相关状态标志，例如 cooked、frozen、heated、cooled、charged 或 assembled。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "COOK", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。


---
name: FREEZE
description: Official VirtualHome FREEZE action.
---

## 参数
planning、handler 和官方导出均使用 VirtualHome 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `FREEZE`。 |
| args | array[string] | 长度为 1；按 VirtualHome 官方动作语义填写当前场景对象。 |
## 前提条件
- 动作参数只能引用当前 VirtualHome 环境事实中的精确实体名；CUT 后由本序列生成的 `<target>_part_0`、`<target>_part_1` 可在后续步骤引用。
- 必须使用当前 settings 启用的精确原生动作名和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象以及任何依赖的支持状态，必须已经满足 benchmark-local handler 的校验。
- 不要假设隐藏设备、隐藏工具或隐藏容器；只依赖当前场景状态和已验证动作。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会更新相关状态标志，例如 cooked、frozen、heated、cooled、charged 或 assembled。

## 输出格式
- planning 最终输出必须是 VirtualHome 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "FREEZE", "args": ["<target>"]}
```
- 除 `action`、`args` 外不要输出其他字段；不要输出解释或 Markdown。
- `handler.validate(...)` 和 `handler.apply(...)` 读取同一个 `args` 字段执行前提校验和环境更新。

</available_skills>

历史失败反馈：
暂无相关拦截记录

规划边界：
1. 只使用 <available_skills> 中列出的动作。
2. 动作参数、前置条件、状态依赖和效果只以对应 skill 契约为准。
3. 只引用当前环境、任务上下文、任务相关环境事实或理解层结果中出现的实体/房间/对象名。
4. 如果已有修复反馈或修复状态，只生成尚未验证的后续动作。

输出格式：
直接输出 VirtualHome 原生动作 JSON 数组。
每个元素只能包含 action 和 args；args 是该动作的官方参数数组。
如果任务已经完成，返回 []。

## Message 2: human

开始规划。
