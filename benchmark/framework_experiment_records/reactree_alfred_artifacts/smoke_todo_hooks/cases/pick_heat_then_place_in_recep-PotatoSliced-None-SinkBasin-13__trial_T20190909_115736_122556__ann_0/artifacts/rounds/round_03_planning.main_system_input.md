# Round 3 planning.main_system Input

## Message 1: system

任务：生成 ALFRED 官方原生动作计划。
只输出 JSON；不要解释，不要输出 Markdown。

原始任务：


规划目标：
Place a cooked potato slice in the sink

机器人状态：
- 位置：kitchen_anchor
- 手持：空
- 完整状态：{"robot_location":"kitchen_anchor","robot_holding":"空","x_display":"71"}

当前环境 JSON：
{"Apple (1)":{"direct_parent":"SinkBasin (1)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","SinkBasin (1)"]},"kitchen":{"direct_parent":"未知环境","direct_relation":null,"type":null,"states":{},"properties":[],"is_container":true,"full_path":[]},"kitchen_anchor":{"direct_parent":"kitchen","direct_relation":"inside","type":"receptacle","states":{},"properties":[],"is_container":true,"full_path":["kitchen"]},"SinkBasin (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Apple (2)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"CounterTop (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Apple (3)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"Bowl (1)":{"direct_parent":"Fridge (1)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"Cold","isHot":false,"isCool":true,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","Fridge (1)"]},"Fridge (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Bowl (2)":{"direct_parent":"Cabinet (22)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","Cabinet (22)"]},"Cabinet (22)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Bowl (3)":{"direct_parent":"Cabinet (17)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","Cabinet (17)"]},"Cabinet (17)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Bread (1)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"CounterTop (3)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Bread (2)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"ButterKnife (1)":{"direct_parent":"CounterTop (2)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (2)"]},"CounterTop (2)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"ButterKnife (2)":{"direct_parent":"CounterTop (2)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (2)"]},"ButterKnife (3)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"Cabinet (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (10)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"WineBottle (1)":{"direct_parent":"Cabinet (10)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","Cabinet (10)"]},"Cabinet (11)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (12)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (13)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (14)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (15)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"PepperShaker (1)":{"direct_parent":"Cabinet (15)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","Cabinet (15)"]},"Cabinet (16)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"DishSponge (2)":{"direct_parent":"Cabinet (17)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","Cabinet (17)"]},"Cabinet (18)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (19)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (2)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (20)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (21)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (23)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (24)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (25)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (26)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (3)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (4)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (5)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (6)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (7)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (8)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Cabinet (9)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"CoffeeMachine (1)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":"receptacle","states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["toggleable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"Spoon (2)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"DishSponge (1)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"Fork (2)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"Spoon (1)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"Faucet (1)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":null,"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["toggleable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"Knife (1)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"Lettuce (3)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"Toaster (1)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":"receptacle","states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["toggleable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"Pan (2)":{"direct_parent":"CounterTop (1)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","CounterTop (1)"]},"Plate (1)":{"direct_parent":"CounterTop (2)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","CounterTop (2)"]},"Egg (1)":{"direct_parent":"CounterTop (2)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (2)"]},"SoapBottle (1)":{"direct_parent":"CounterTop (2)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (2)"]},"Spoon (3)":{"direct_parent":"CounterTop (2)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (2)"]},"Pencil (1)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"Fork (1)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"Plate (2)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"Spatula (1)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"PaperTowelRoll (1)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"Cup (2)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"SaltShaker (1)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"PepperShaker (2)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"Mug (1)":{"direct_parent":"CounterTop (3)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","CounterTop (3)"]},"Cup (1)":{"direct_parent":"Microwave (1)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","Microwave (1)"]},"Microwave (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isToggled":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","toggleable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Curtains (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":[],"is_container":false,"full_path":["kitchen","kitchen_anchor"]},"Drawer (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Drawer (10)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Drawer (11)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Fork (3)":{"direct_parent":"Drawer (11)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","Drawer (11)"]},"Drawer (12)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Pencil (2)":{"direct_parent":"Drawer (12)","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","Drawer (12)"]},"Drawer (2)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Drawer (3)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Drawer (4)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Drawer (5)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Drawer (6)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Drawer (7)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Drawer (8)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Drawer (9)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["openable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Tomato (1)":{"direct_parent":"Fridge (1)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"Cold","isHot":false,"isCool":true,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","Fridge (1)"]},"Potato (1)":{"direct_parent":"Fridge (1)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"Cold","isHot":false,"isCool":true,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","Fridge (1)"]},"Tomato (2)":{"direct_parent":"Fridge (1)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"Cold","isHot":false,"isCool":true,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","Fridge (1)"]},"GarbageCan (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Lettuce (1)":{"direct_parent":"GarbageCan (1)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","GarbageCan (1)"]},"Lettuce (2)":{"direct_parent":"SinkBasin (1)","direct_relation":"inside","type":null,"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","sliceable"],"is_container":false,"full_path":["kitchen","kitchen_anchor","SinkBasin (1)"]},"LightSwitch (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":null,"states":{"isToggled":true,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["toggleable"],"is_container":false,"full_path":["kitchen","kitchen_anchor"]},"Pan (1)":{"direct_parent":"StoveBurner (1)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","StoveBurner (1)"]},"StoveBurner (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Pot (1)":{"direct_parent":"StoveBurner (3)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","StoveBurner (3)"]},"StoveBurner (3)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Pot (2)":{"direct_parent":"StoveBurner (4)","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["pickupable","receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor","StoveBurner (4)"]},"StoveBurner (4)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"Sink (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":[],"is_container":false,"full_path":["kitchen","kitchen_anchor"]},"StoveBurner (2)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":"receptacle","states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["receptacle"],"is_container":true,"full_path":["kitchen","kitchen_anchor"]},"StoveKnob (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":null,"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["toggleable"],"is_container":false,"full_path":["kitchen","kitchen_anchor"]},"StoveKnob (2)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":null,"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["toggleable"],"is_container":false,"full_path":["kitchen","kitchen_anchor"]},"StoveKnob (3)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":null,"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["toggleable"],"is_container":false,"full_path":["kitchen","kitchen_anchor"]},"StoveKnob (4)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":null,"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":["toggleable"],"is_container":false,"full_path":["kitchen","kitchen_anchor"]},"Window (1)":{"direct_parent":"kitchen_anchor","direct_relation":"inside","type":null,"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"properties":[],"is_container":false,"full_path":["kitchen","kitchen_anchor"]}}

任务相关环境事实：
[{"name":"Apple (1)","direct_parent":"SinkBasin (1)","full_path":["kitchen","kitchen_anchor","SinkBasin (1)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Apple (2)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Apple (3)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Bowl (1)","direct_parent":"Fridge (1)","full_path":["kitchen","kitchen_anchor","Fridge (1)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"Cold","isHot":false,"isCool":true,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Bowl (2)","direct_parent":"Cabinet (22)","full_path":["kitchen","kitchen_anchor","Cabinet (22)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Bowl (3)","direct_parent":"Cabinet (17)","full_path":["kitchen","kitchen_anchor","Cabinet (17)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Bread (1)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Bread (2)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"ButterKnife (1)","direct_parent":"CounterTop (2)","full_path":["kitchen","kitchen_anchor","CounterTop (2)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"ButterKnife (2)","direct_parent":"CounterTop (2)","full_path":["kitchen","kitchen_anchor","CounterTop (2)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"ButterKnife (3)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Cabinet (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (10)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (11)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (12)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (13)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (14)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (15)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (16)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (17)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (18)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (19)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (2)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (20)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (21)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (22)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (23)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (24)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (25)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (26)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (3)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (4)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (5)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (6)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (7)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (8)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cabinet (9)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"CoffeeMachine (1)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"CounterTop (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"CounterTop (2)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"CounterTop (3)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cup (1)","direct_parent":"Microwave (1)","full_path":["kitchen","kitchen_anchor","Microwave (1)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Cup (2)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Curtains (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"DishSponge (1)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"DishSponge (2)","direct_parent":"Cabinet (17)","full_path":["kitchen","kitchen_anchor","Cabinet (17)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Drawer (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (10)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (11)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (12)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (2)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (3)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (4)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (5)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (6)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (7)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (8)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Drawer (9)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Egg (1)","direct_parent":"CounterTop (2)","full_path":["kitchen","kitchen_anchor","CounterTop (2)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Faucet (1)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Fork (1)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Fork (2)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Fork (3)","direct_parent":"Drawer (11)","full_path":["kitchen","kitchen_anchor","Drawer (11)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Fridge (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"GarbageCan (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Knife (1)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Lettuce (1)","direct_parent":"GarbageCan (1)","full_path":["kitchen","kitchen_anchor","GarbageCan (1)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Lettuce (2)","direct_parent":"SinkBasin (1)","full_path":["kitchen","kitchen_anchor","SinkBasin (1)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Lettuce (3)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"LightSwitch (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isToggled":true,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Microwave (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isOpen":false,"isToggled":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Mug (1)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Pan (1)","direct_parent":"StoveBurner (1)","full_path":["kitchen","kitchen_anchor","StoveBurner (1)"],"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Pan (2)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"PaperTowelRoll (1)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Pencil (1)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Pencil (2)","direct_parent":"Drawer (12)","full_path":["kitchen","kitchen_anchor","Drawer (12)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"PepperShaker (1)","direct_parent":"Cabinet (15)","full_path":["kitchen","kitchen_anchor","Cabinet (15)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"PepperShaker (2)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Plate (1)","direct_parent":"CounterTop (2)","full_path":["kitchen","kitchen_anchor","CounterTop (2)"],"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Plate (2)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Pot (1)","direct_parent":"StoveBurner (3)","full_path":["kitchen","kitchen_anchor","StoveBurner (3)"],"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Pot (2)","direct_parent":"StoveBurner (4)","full_path":["kitchen","kitchen_anchor","StoveBurner (4)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Potato (1)","direct_parent":"Fridge (1)","full_path":["kitchen","kitchen_anchor","Fridge (1)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"Cold","isHot":false,"isCool":true,"isCooked":false},"type":null,"is_container":false},{"name":"SaltShaker (1)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Sink (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"SinkBasin (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"SoapBottle (1)","direct_parent":"CounterTop (2)","full_path":["kitchen","kitchen_anchor","CounterTop (2)"],"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Spatula (1)","direct_parent":"CounterTop (3)","full_path":["kitchen","kitchen_anchor","CounterTop (3)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Spoon (1)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Spoon (2)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Spoon (3)","direct_parent":"CounterTop (2)","full_path":["kitchen","kitchen_anchor","CounterTop (2)"],"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"StoveBurner (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"StoveBurner (2)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"StoveBurner (3)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"StoveBurner (4)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"StoveKnob (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"StoveKnob (2)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"StoveKnob (3)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"StoveKnob (4)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":true,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"Toaster (1)","direct_parent":"CounterTop (1)","full_path":["kitchen","kitchen_anchor","CounterTop (1)"],"states":{"isToggled":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":"receptacle","is_container":true},{"name":"Tomato (1)","direct_parent":"Fridge (1)","full_path":["kitchen","kitchen_anchor","Fridge (1)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"Cold","isHot":false,"isCool":true,"isCooked":false},"type":null,"is_container":false},{"name":"Tomato (2)","direct_parent":"Fridge (1)","full_path":["kitchen","kitchen_anchor","Fridge (1)"],"states":{"isSliced":false,"isDirty":false,"isClean":true,"visible":false,"temperature":"Cold","isHot":false,"isCool":true,"isCooked":false},"type":null,"is_container":false},{"name":"Window (1)","direct_parent":"kitchen_anchor","full_path":["kitchen","kitchen_anchor"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"WineBottle (1)","direct_parent":"Cabinet (10)","full_path":["kitchen","kitchen_anchor","Cabinet (10)"],"states":{"isDirty":false,"isClean":true,"visible":false,"temperature":"RoomTemp","isHot":false,"isCool":false,"isCooked":false},"type":null,"is_container":false},{"name":"kitchen","direct_parent":"未知环境","full_path":[],"states":{},"type":null,"is_container":true},{"name":"kitchen_anchor","direct_parent":"kitchen","full_path":["kitchen"],"states":{},"type":"receptacle","is_container":true}]

任务上下文：
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

理解层实体选择：
{
  "targets": {
    "primary": [
      "Potato (1)"
    ],
    "alternatives": []
  },
  "tools": {
    "primary": [
      "Pan (1)"
    ],
    "alternatives": []
  },
  "receptacles": {
    "primary": [
      "SinkBasin (1)"
    ],
    "alternatives": []
  }
}

可用动作与 skill 契约：
<available_skills>
---
name: go to
description: Official ReAcTree ALFRED navigation action.
---

## 参数
planning、handler 和官方导出均使用 ALFRED 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `go to`。 |
| target | string | 当前 ALFRED 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 ALFRED 原生动作名 `go to` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 只有在目标位置或交互锚点当前不可直接到达时，才应导航。
- 如果机器人已经处于同一个可交互位置簇，不要重复导航。
- 其他动作的交互距离和父节点要求由对应 handler.validate(...) 校验。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，模拟机器人位置应更新到目标位置或可交互锚点。

## 输出格式
- planning 最终输出必须是 ALFRED 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "go to", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。
- ALFRED 的 `done` 不属于单步 skill；官方导出阶段会在计划末尾补齐终止标记。

---
name: pick up
description: Official ReAcTree ALFRED pickup action.
---

## 参数
planning、handler 和官方导出均使用 ALFRED 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `pick up`。 |
| target | string | 当前 ALFRED 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 ALFRED 原生动作名 `pick up` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标必须由 ALFRED metadata 标记为 `pickupable`，或属于 ReAcTree ALFRED 官方可拿取对象类别；容器、灯、台面等不可拿取实体不能作为 `pick up` 目标。
- 目标物体必须可达；当前 `robot_location`、目标父节点和手持状态必须满足 handler 校验。
- 如果目标位于关闭的 openable 容器内，handler 必须拒绝该步。
- ALFRED 动作模型使用单手持有状态：`holding` / `robot_holding`。不要输出 left/right hand 变体，也不要假设可以同时持有两个物体；当前手必须为空才能 `pick up`。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标物体会进入单手 `holding` / `robot_holding`。

## 输出格式
- planning 最终输出必须是 ALFRED 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "pick up", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。
- ALFRED 的 `done` 不属于单步 skill；官方导出阶段会在计划末尾补齐终止标记。

---
name: put down
description: Official ReAcTree ALFRED put-down action.
---

## 参数
planning、handler 和官方导出均使用 ALFRED 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `put down`。 |
| target | string | 当前 ALFRED 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 ALFRED 原生动作名 `put down` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 机器人当前必须已经持有或携带待放置物体，`target` 必须等于当前手持物体。
- 当前 `robot_location` 必须是有效 ALFRED receptacle/surface 实例；如果目标位置不满足放置条件，handler 必须拒绝。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，物体的父节点关系会移动到当前机器人所在实例，并释放手持状态。

## 输出格式
- planning 最终输出必须是 ALFRED 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "put down", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。
- ALFRED 的 `done` 不属于单步 skill；官方导出阶段会在计划末尾补齐终止标记。

---
name: open
description: Official ReAcTree ALFRED open action.
---

## 参数
planning、handler 和官方导出均使用 ALFRED 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `open`。 |
| target | string | 当前 ALFRED 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 ALFRED 原生动作名 `open` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须由 ALFRED metadata 标记为 `openable`，或属于 ReAcTree ALFRED 官方可打开对象类别，且当前不是已打开状态。
- 当前 `robot_location` 必须满足 handler 的交互距离/父节点校验。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 ALFRED 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "open", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。
- ALFRED 的 `done` 不属于单步 skill；官方导出阶段会在计划末尾补齐终止标记。

---
name: close
description: Official ReAcTree ALFRED close action.
---

## 参数
planning、handler 和官方导出均使用 ALFRED 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `close`。 |
| target | string | 当前 ALFRED 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 ALFRED 原生动作名 `close` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须由 ALFRED metadata 标记为 `openable`，或属于 ReAcTree ALFRED 官方可关闭对象类别，且当前不是已关闭状态。
- 当前 `robot_location` 必须满足 handler 的交互距离/父节点校验。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的 `isOpen` 状态会变为 false；其他连带效果只以 handler.apply(...) 和官方 evaluator 为准。

## 输出格式
- planning 最终输出必须是 ALFRED 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "close", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。
- ALFRED 的 `done` 不属于单步 skill；官方导出阶段会在计划末尾补齐终止标记。

---
name: turn on
description: Official ReAcTree ALFRED turn-on action.
---

## 参数
planning、handler 和官方导出均使用 ALFRED 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `turn on`。 |
| target | string | 当前 ALFRED 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 ALFRED 原生动作名 `turn on` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须由 ALFRED metadata 标记为 `toggleable`，或属于 ReAcTree ALFRED 官方可开关对象类别，且当前不是已开启状态。
- 成功后目标的 `isToggled` 状态会变为 true；其他设备连带效果只以 handler.apply(...) 和官方 evaluator 为准。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 ALFRED 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "turn on", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。
- ALFRED 的 `done` 不属于单步 skill；官方导出阶段会在计划末尾补齐终止标记。

---
name: turn off
description: Official ReAcTree ALFRED turn-off action.
---

## 参数
planning、handler 和官方导出均使用 ALFRED 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `turn off`。 |
| target | string | 当前 ALFRED 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 ALFRED 原生动作名 `turn off` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 目标对象必须由 ALFRED metadata 标记为 `toggleable`，或属于 ReAcTree ALFRED 官方可开关对象类别，且当前不是已关闭状态。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，目标对象的状态标志会更新，例如 open/closed 或 toggled on/off。

## 输出格式
- planning 最终输出必须是 ALFRED 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "turn off", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。
- ALFRED 的 `done` 不属于单步 skill；官方导出阶段会在计划末尾补齐终止标记。

---
name: slice
description: Official ReAcTree ALFRED slice action.
---

## 参数
planning、handler 和官方导出均使用 ALFRED 原生动作对象。

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| action | string | 固定为 `slice`。 |
| target | string | 当前 ALFRED 场景中的精确目标实体名。 |
## 前提条件
- 必须使用官方 ALFRED 原生动作名 `slice` 和字段 schema。
- 当前场景图、机器人状态以及该技能的 `handler.validate(...)` 逻辑，是唯一有效的前提条件来源。
- 引用的对象必须已经存在于当前 benchmark 场景中；不要假设隐藏对象或隐藏状态变化。
- 切片动作按 ReAcTree ALFRED 源码的 `slice <object>` schema 校验；该 handler 不接收额外工具参数。
- 目标必须由 ALFRED metadata 标记为 `sliceable`，或属于 ReAcTree ALFRED 官方可切片对象类别，且当前还没有 `isSliced=true`。
- 目标物体应在可交互位置上；不要在手持目标物体时切它。
- 成功切开某个 `Base (n)` 后，ReAcTree 官方环境会生成同一 base class 的新编号切片；后续 pick/place 应使用这些生成后的 base-class slice 实例，不要使用改名成 `BaseSliced` 的不存在名字。

## 执行效果
- 如果校验通过，机器人状态和场景状态如何更新，以该技能的 `handler.apply(...)` 为准。
- 如果校验失败，sandbox 必须拒绝该步，并返回 handler 给出的 issue/fix。
- 成功执行后，会更新切片状态，并可能生成新的 part 对象或改变后续可用的目标对象名。

## 输出格式
- planning 最终输出必须是 ALFRED 原生动作 JSON 数组；本技能的一步写成：
```json
{"action": "slice", "target": "<target>"}
```
- 除 `action`、`target` 外不要输出其他字段；不要输出解释或 Markdown。
- ALFRED 的 `done` 不属于单步 skill；官方导出阶段会在计划末尾补齐终止标记。
</available_skills>

历史失败反馈：
暂无相关拦截记录

规划边界：
1. 只使用 <available_skills> 中列出的动作。
2. 动作参数、前置条件、状态依赖和效果只以对应 skill 契约为准。
3. 只引用当前环境、任务上下文、任务相关环境事实或理解层结果中出现的实体/房间/对象名。
4. 如果已有修复反馈或修复状态，只生成尚未验证的后续动作。

输出格式：
直接输出 ALFRED 原生动作 JSON 数组。
每个元素只能包含 action 和 target；不要输出 done，官方导出阶段会补齐终止标记。
如果任务已经完成，返回 []。

## Message 2: human

开始规划。
