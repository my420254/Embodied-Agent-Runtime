# Round 4 planning.state_diff_audit Input

## Message 1: human

任务：根据 BEHAVIOR sandbox 前后状态差异判断任务是否完成。
只输出 JSON；不要解释，不要生成动作。

任务目标：Assemble gift baskets by placing one candle, one cheese, one cookie, and one bow inside each basket.

完整 native action 计划摘要：
[
  {
    "action": "LEFT_GRASP",
    "object": "candle_0"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_0"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "cheese_0"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_0"
  },
  {
    "action": "LEFT_GRASP",
    "object": "cookie_0"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_0"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "bow_0"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_0"
  },
  {
    "action": "LEFT_GRASP",
    "object": "candle_1"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_1"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "cheese_1"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_1"
  },
  {
    "action": "LEFT_GRASP",
    "object": "cookie_1"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_1"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "bow_1"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_1"
  },
  {
    "action": "LEFT_GRASP",
    "object": "candle_2"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_2"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "cheese_2"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_2"
  },
  {
    "action": "LEFT_GRASP",
    "object": "cookie_2"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_2"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "bow_2"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_2"
  },
  {
    "action": "LEFT_GRASP",
    "object": "candle_3"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_3"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "cheese_3"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_3"
  },
  {
    "action": "LEFT_GRASP",
    "object": "cookie_3"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_3"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "bow_3"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_3"
  }
]

本轮实际模拟步骤：
[
  {
    "action": "LEFT_GRASP",
    "object": "candle_0"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_0"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "cheese_0"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_0"
  },
  {
    "action": "LEFT_GRASP",
    "object": "cookie_0"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_0"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "bow_0"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_0"
  },
  {
    "action": "LEFT_GRASP",
    "object": "candle_1"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_1"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "cheese_1"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_1"
  },
  {
    "action": "LEFT_GRASP",
    "object": "cookie_1"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_1"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "bow_1"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_1"
  },
  {
    "action": "LEFT_GRASP",
    "object": "candle_2"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_2"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "cheese_2"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_2"
  },
  {
    "action": "LEFT_GRASP",
    "object": "cookie_2"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_2"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "bow_2"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_2"
  },
  {
    "action": "LEFT_GRASP",
    "object": "candle_3"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_3"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "cheese_3"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_3"
  },
  {
    "action": "LEFT_GRASP",
    "object": "cookie_3"
  },
  {
    "action": "LEFT_PLACE_INSIDE",
    "object": "basket_3"
  },
  {
    "action": "RIGHT_GRASP",
    "object": "bow_3"
  },
  {
    "action": "RIGHT_PLACE_INSIDE",
    "object": "basket_3"
  }
]

轨迹摘要：
Step 1: LEFT_GRASP(candle_0)
Step 2: LEFT_PLACE_INSIDE(basket_0)
Step 3: RIGHT_GRASP(cheese_0)
Step 4: RIGHT_PLACE_INSIDE(basket_0)
Step 5: LEFT_GRASP(cookie_0)
Step 6: LEFT_PLACE_INSIDE(basket_0)
Step 7: RIGHT_GRASP(bow_0)
Step 8: RIGHT_PLACE_INSIDE(basket_0)
Step 9: LEFT_GRASP(candle_1)
Step 10: LEFT_PLACE_INSIDE(basket_1)
Step 11: RIGHT_GRASP(cheese_1)
Step 12: RIGHT_PLACE_INSIDE(basket_1)
Step 13: LEFT_GRASP(cookie_1)
Step 14: LEFT_PLACE_INSIDE(basket_1)
Step 15: RIGHT_GRASP(bow_1)
Step 16: RIGHT_PLACE_INSIDE(basket_1)
Step 17: LEFT_GRASP(candle_2)
Step 18: LEFT_PLACE_INSIDE(basket_2)
Step 19: RIGHT_GRASP(cheese_2)
Step 20: RIGHT_PLACE_INSIDE(basket_2)
Step 21: LEFT_GRASP(cookie_2)
Step 22: LEFT_PLACE_INSIDE(basket_2)
Step 23: RIGHT_GRASP(bow_2)
Step 24: RIGHT_PLACE_INSIDE(basket_2)
Step 25: LEFT_GRASP(candle_3)
Step 26: LEFT_PLACE_INSIDE(basket_3)
Step 27: RIGHT_GRASP(cheese_3)
Step 28: RIGHT_PLACE_INSIDE(basket_3)
Step 29: LEFT_GRASP(cookie_3)
Step 30: LEFT_PLACE_INSIDE(basket_3)
Step 31: RIGHT_GRASP(bow_3)
Step 32: RIGHT_PLACE_INSIDE(basket_3)

BEHAVIOR 状态差异 JSON：
{
  "entity_count_compared": 25,
  "changed_entity_count": 16,
  "truncated_entity_count": 0,
  "has_changes": true,
  "robot": {
    "changed": false
  },
  "entities": [
    {
      "name": "bow_0",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_0",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "bow_1",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_1",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "bow_2",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_2",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "bow_3",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_3",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "candle_0",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_0",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "candle_1",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_1",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "candle_2",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_2",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "candle_3",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_3",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cheese_0",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_0",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cheese_1",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_1",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cheese_2",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_2",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cheese_3",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_3",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cookie_0",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_0",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cookie_1",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_1",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cookie_2",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_2",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cookie_3",
      "change_type": "updated",
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_3",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    }
  ]
}

状态审计上下文 JSON：
{
  "entity_count_available": 25,
  "entity_count_in_context": 23,
  "truncated_entity_count": 0,
  "note": "state_diff only lists changed entities; unchanged entities in this context still prove final goal state when their after state satisfies the task.",
  "robot": {
    "changed": false,
    "before": {
      "robot_location": "room_floor_living_room_0",
      "robot_holding": "空",
      "robot_hands": {
        "left": "空",
        "right": "空"
      },
      "manipulator_mode": "dual_arm"
    },
    "after": {
      "robot_location": "room_floor_living_room_0",
      "robot_holding": "空",
      "robot_hands": {
        "left": "空",
        "right": "空"
      },
      "manipulator_mode": "dual_arm"
    }
  },
  "entities": [
    {
      "name": "candle_0",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_0",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "candle_1",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_1",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "candle_2",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_2",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "candle_3",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_3",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cheese_0",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_0",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cheese_1",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_1",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cheese_2",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_2",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cheese_3",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_3",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cookie_0",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_0",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cookie_1",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_1",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cookie_2",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_2",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "cookie_3",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "breakfast_table_13",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_3",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "breakfast_table_13"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "bow_0",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_0",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "bow_1",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_1",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "bow_2",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_2",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "bow_3",
      "changed": true,
      "before": {
        "type": null,
        "direct_parent": "coffee_table_12",
        "direct_relation": "ontop",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": null,
        "direct_parent": "basket_3",
        "direct_relation": "inside",
        "is_container": false,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "coffee_table_12"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "basket_0",
      "changed": false,
      "before": {
        "type": "receptacle",
        "direct_parent": "room_floor_living_room_0",
        "direct_relation": "onfloor",
        "is_container": true,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "room_floor_living_room_0"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": "receptacle",
        "direct_parent": "room_floor_living_room_0",
        "direct_relation": "onfloor",
        "is_container": true,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "room_floor_living_room_0"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "basket_1",
      "changed": false,
      "before": {
        "type": "receptacle",
        "direct_parent": "room_floor_living_room_0",
        "direct_relation": "onfloor",
        "is_container": true,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "room_floor_living_room_0"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": "receptacle",
        "direct_parent": "room_floor_living_room_0",
        "direct_relation": "onfloor",
        "is_container": true,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "room_floor_living_room_0"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "basket_2",
      "changed": false,
      "before": {
        "type": "receptacle",
        "direct_parent": "room_floor_living_room_0",
        "direct_relation": "onfloor",
        "is_container": true,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "room_floor_living_room_0"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": "receptacle",
        "direct_parent": "room_floor_living_room_0",
        "direct_relation": "onfloor",
        "is_container": true,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "room_floor_living_room_0"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "basket_3",
      "changed": false,
      "before": {
        "type": "receptacle",
        "direct_parent": "room_floor_living_room_0",
        "direct_relation": "onfloor",
        "is_container": true,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "room_floor_living_room_0"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": "receptacle",
        "direct_parent": "room_floor_living_room_0",
        "direct_relation": "onfloor",
        "is_container": true,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor",
          "room_floor_living_room_0"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "room_floor_living_room_0",
      "changed": false,
      "before": {
        "type": "receptacle",
        "direct_parent": "behavior_room_anchor",
        "direct_relation": "inside",
        "is_container": true,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": "receptacle",
        "direct_parent": "behavior_room_anchor",
        "direct_relation": "inside",
        "is_container": true,
        "full_path": [
          "behavior_room",
          "behavior_room_anchor"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "behavior_room_anchor",
      "changed": false,
      "before": {
        "type": "receptacle",
        "direct_parent": "behavior_room",
        "direct_relation": "inside",
        "is_container": true,
        "full_path": [
          "behavior_room"
        ],
        "states": {},
        "properties": []
      },
      "after": {
        "type": "receptacle",
        "direct_parent": "behavior_room",
        "direct_relation": "inside",
        "is_container": true,
        "full_path": [
          "behavior_room"
        ],
        "states": {},
        "properties": []
      }
    },
    {
      "name": "behavior_room",
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
  },
  "evaluation_context": {},
  "external_goal": {
    "has_external_goal": true,
    "external_goal_state": {},
    "external_goal_text": "",
    "structured_goal_state": {},
    "structured_final_state": {
      "basket_0": {
        "contains": [
          "candle_0",
          "cheese_0",
          "cookie_0",
          "bow_0"
        ]
      },
      "basket_1": {
        "contains": [
          "candle_1",
          "cheese_1",
          "cookie_1",
          "bow_1"
        ]
      },
      "basket_2": {
        "contains": [
          "candle_2",
          "cheese_2",
          "cookie_2",
          "bow_2"
        ]
      },
      "basket_3": {
        "contains": [
          "candle_3",
          "cheese_3",
          "cookie_3",
          "bow_3"
        ]
      }
    }
  },
  "benchmark_final_state_compare": {
    "benchmark": "EAI-BEHAVIOR",
    "status": "prepared_for_framework_llm_judge",
    "environment_format": "BEHAVIOR initial_env_cache 转成 benchmark 本地对象状态图，保留关系/状态目标命名",
    "action_format": "BEHAVIOR 官方 action sequencing 原生动作 JSON 对象：{action, object}",
    "official_evaluator": "EAI BEHAVIOR ActionSequenceEvaluator，使用 headless 符号图环境",
    "used_fields": {
      "task_context": [
        "dataset",
        "environment_source",
        "identifier",
        "initial_environment_cache_path",
        "initial_environment_source",
        "instruction",
        "name_category",
        "raw_goal_clauses",
        "raw_goal_condition",
        "raw_goal_condition_count",
        "raw_source"
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
        }
      },
      "evaluation_context": {},
      "goal_projection": {
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
        }
      },
      "external_goal": {
        "has_external_goal": true,
        "external_goal_state": {},
        "external_goal_text": "",
        "structured_goal_state": {},
        "structured_final_state": {
          "basket_0": {
            "contains": [
              "candle_0",
              "cheese_0",
              "cookie_0",
              "bow_0"
            ]
          },
          "basket_1": {
            "contains": [
              "candle_1",
              "cheese_1",
              "cookie_1",
              "bow_1"
            ]
          },
          "basket_2": {
            "contains": [
              "candle_2",
              "cheese_2",
              "cookie_2",
              "bow_2"
            ]
          },
          "basket_3": {
            "contains": [
              "candle_3",
              "cheese_3",
              "cookie_3",
              "bow_3"
            ]
          }
        }
      }
    },
    "understanding_final_state": {
      "basket_0": {
        "contains": [
          "candle_0",
          "cheese_0",
          "cookie_0",
          "bow_0"
        ]
      },
      "basket_1": {
        "contains": [
          "candle_1",
          "cheese_1",
          "cookie_1",
          "bow_1"
        ]
      },
      "basket_2": {
        "contains": [
          "candle_2",
          "cheese_2",
          "cookie_2",
          "bow_2"
        ]
      },
      "basket_3": {
        "contains": [
          "candle_3",
          "cheese_3",
          "cookie_3",
          "bow_3"
        ]
      }
    },
    "state_diff_summary": {
      "entity_count_compared": 25,
      "changed_entity_count": 16,
      "changed_entities": [
        "bow_0",
        "bow_1",
        "bow_2",
        "bow_3",
        "candle_0",
        "candle_1",
        "candle_2",
        "candle_3",
        "cheese_0",
        "cheese_1",
        "cheese_2",
        "cheese_3",
        "cookie_0",
        "cookie_1",
        "cookie_2",
        "cookie_3"
      ],
      "changed_entities_truncated": false,
      "robot_changed": false,
      "robot_change": {
        "changed": false
      }
    },
    "initial_environment_summary": {
      "available": true,
      "entity_count": 25,
      "type_counts": {
        "receptacle": 8,
        "room": 1,
        "unknown": 16
      },
      "states_sample": {},
      "relations_sample": {
        "basket_0": {
          "direct_relation": "onfloor",
          "direct_parent": "room_floor_living_room_0"
        },
        "behavior_room": {
          "direct_relation": "",
          "direct_parent": "未知环境"
        },
        "behavior_room_anchor": {
          "direct_relation": "inside",
          "direct_parent": "behavior_room"
        },
        "room_floor_living_room_0": {
          "direct_relation": "inside",
          "direct_parent": "behavior_room_anchor"
        },
        "basket_1": {
          "direct_relation": "onfloor",
          "direct_parent": "room_floor_living_room_0"
        },
        "basket_2": {
          "direct_relation": "onfloor",
          "direct_parent": "room_floor_living_room_0"
        },
        "basket_3": {
          "direct_relation": "onfloor",
          "direct_parent": "room_floor_living_room_0"
        },
        "candle_0": {
          "direct_relation": "ontop",
          "direct_parent": "breakfast_table_13"
        },
        "breakfast_table_13": {
          "direct_relation": "inside",
          "direct_parent": "behavior_room_anchor"
        },
        "candle_1": {
          "direct_relation": "ontop",
          "direct_parent": "breakfast_table_13"
        },
        "candle_2": {
          "direct_relation": "ontop",
          "direct_parent": "breakfast_table_13"
        },
        "candle_3": {
          "direct_relation": "ontop",
          "direct_parent": "breakfast_table_13"
        },
        "cheese_0": {
          "direct_relation": "ontop",
          "direct_parent": "coffee_table_12"
        },
        "coffee_table_12": {
          "direct_relation": "inside",
          "direct_parent": "behavior_room_anchor"
        },
        "cheese_1": {
          "direct_relation": "ontop",
          "direct_parent": "coffee_table_12"
        },
        "cheese_2": {
          "direct_relation": "ontop",
          "direct_parent": "coffee_table_12"
        },
        "cheese_3": {
          "direct_relation": "ontop",
          "direct_parent": "coffee_table_12"
        },
        "cookie_0": {
          "direct_relation": "ontop",
          "direct_parent": "breakfast_table_13"
        },
        "cookie_1": {
          "direct_relation": "ontop",
          "direct_parent": "breakfast_table_13"
        },
        "cookie_2": {
          "direct_relation": "ontop",
          "direct_parent": "breakfast_table_13"
        }
      }
    },
    "final_environment_summary": {
      "available": true,
      "entity_count": 25,
      "type_counts": {
        "receptacle": 8,
        "room": 1,
        "unknown": 16
      },
      "states_sample": {},
      "relations_sample": {
        "basket_0": {
          "direct_relation": "onfloor",
          "direct_parent": "room_floor_living_room_0"
        },
        "behavior_room": {
          "direct_relation": "",
          "direct_parent": "未知环境"
        },
        "behavior_room_anchor": {
          "direct_relation": "inside",
          "direct_parent": "behavior_room"
        },
        "room_floor_living_room_0": {
          "direct_relation": "inside",
          "direct_parent": "behavior_room_anchor"
        },
        "basket_1": {
          "direct_relation": "onfloor",
          "direct_parent": "room_floor_living_room_0"
        },
        "basket_2": {
          "direct_relation": "onfloor",
          "direct_parent": "room_floor_living_room_0"
        },
        "basket_3": {
          "direct_relation": "onfloor",
          "direct_parent": "room_floor_living_room_0"
        },
        "candle_0": {
          "direct_relation": "inside",
          "direct_parent": "basket_0"
        },
        "breakfast_table_13": {
          "direct_relation": "inside",
          "direct_parent": "behavior_room_anchor"
        },
        "candle_1": {
          "direct_relation": "inside",
          "direct_parent": "basket_1"
        },
        "candle_2": {
          "direct_relation": "inside",
          "direct_parent": "basket_2"
        },
        "candle_3": {
          "direct_relation": "inside",
          "direct_parent": "basket_3"
        },
        "cheese_0": {
          "direct_relation": "inside",
          "direct_parent": "basket_0"
        },
        "coffee_table_12": {
          "direct_relation": "inside",
          "direct_parent": "behavior_room_anchor"
        },
        "cheese_1": {
          "direct_relation": "inside",
          "direct_parent": "basket_1"
        },
        "cheese_2": {
          "direct_relation": "inside",
          "direct_parent": "basket_2"
        },
        "cheese_3": {
          "direct_relation": "inside",
          "direct_parent": "basket_3"
        },
        "cookie_0": {
          "direct_relation": "inside",
          "direct_parent": "basket_0"
        },
        "cookie_1": {
          "direct_relation": "inside",
          "direct_parent": "basket_1"
        },
        "cookie_2": {
          "direct_relation": "inside",
          "direct_parent": "basket_2"
        }
      }
    },
    "initial_robot": {
      "robot_location": "room_floor_living_room_0",
      "robot_holding": "空",
      "robot_hands": {
        "left": "空",
        "right": "空"
      },
      "manipulator_mode": "dual_arm"
    },
    "final_robot": {
      "robot_location": "room_floor_living_room_0",
      "robot_holding": "空",
      "robot_hands": {
        "left": "空",
        "right": "空"
      },
      "manipulator_mode": "dual_arm"
    },
    "fairness_notes": [
      "raw_goal_condition/name_category 是 BEHAVIOR case 输入中的公开目标条件；不使用人工动作序列答案。"
    ],
    "judge_contract": "公共 final-state audit 只能依据本 benchmark-local goal packet、understanding_final_state、sandbox 前后环境差异和任务原文判断完成度；不得转换到其他 benchmark 的动作或环境格式。",
    "enabled": true,
    "comparer_module": "benchmark.eai.behavior.framework.code.final_state"
  }
}

判定边界：
1. 优先读取 state_audit_context.benchmark_final_state_compare；其中包含 BEHAVIOR raw_goal_condition/name_category 目标投影和本地环境差异摘要。
2. 结合 understanding final_state、raw_goal_condition、sandbox final environment/final robot 和 state_diff 判断关键目标是否完成。
3. 不使用人工动作序列答案；保持 BEHAVIOR 原生动作和图状态语义。
4. 如果关键目标缺失，is_passed=false，并写出缺失的最终状态和后续 planning 应补的动作类型。
5. 如果当前最终态只需追加动作即可修复，repair_mode="continue_from_current"；如果已验证前缀本身错，repair_mode="reset_and_replan"。

输出 JSON：
{"is_passed": true, "issue": "", "fix_advice": "", "repair_mode": "continue_from_current", "accepted_diffs": [], "unexpected_diffs": []}
