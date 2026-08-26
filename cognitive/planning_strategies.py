from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from interfaces.contracts import TaskGraph, TodoList
from interfaces.services import BrainTask


class PlanningStrategyOwner(Protocol):
    def _cut_ingredient_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _make_tea_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _do_laundry_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _turn_on_device_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _turn_off_device_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _open_container_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _close_container_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _put_object_into_container_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _clean_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _pickup_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _read_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _observe_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _touch_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _type_on_device_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _sleep_on_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _drink_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...
    def _sit_on_object_plan(self, task: BrainTask, graph: TaskGraph) -> TodoList: ...


@dataclass(frozen=True)
class PlanningStrategy:
    skill_id: str
    method_name: str
    pyramid_node_id: str | None = None

    def generate(self, owner: PlanningStrategyOwner, task: BrainTask, graph: TaskGraph) -> TodoList:
        return getattr(owner, self.method_name)(task, graph)


PLANNING_STRATEGIES: tuple[PlanningStrategy, ...] = (
    PlanningStrategy("cooking.cut_ingredient", "_cut_ingredient_plan", "cooking.cut_ingredient"),
    PlanningStrategy("cooking.make_tea", "_make_tea_plan", "cooking.make_tea"),
    PlanningStrategy("laundry.do_laundry", "_do_laundry_plan", "laundry.do_laundry"),
    PlanningStrategy("device.turn_on", "_turn_on_device_plan", "device.turn_on"),
    PlanningStrategy("device.turn_off", "_turn_off_device_plan", "device.turn_off"),
    PlanningStrategy("container.open", "_open_container_plan", "container.open"),
    PlanningStrategy("container.close", "_close_container_plan", "container.close"),
    PlanningStrategy("object.put_into_container", "_put_object_into_container_plan", "object.put_into_container"),
    PlanningStrategy("object.clean", "_clean_object_plan", "object.clean"),
    PlanningStrategy("object.pickup", "_pickup_object_plan", "object.pickup"),
    PlanningStrategy("object.read", "_read_object_plan", "object.read"),
    PlanningStrategy("object.observe", "_observe_object_plan", "object.observe"),
    PlanningStrategy("object.touch", "_touch_object_plan", "object.touch"),
    PlanningStrategy("device.type_on", "_type_on_device_plan", "device.type_on"),
    PlanningStrategy("object.sleep_on", "_sleep_on_object_plan", "object.sleep_on"),
    PlanningStrategy("object.drink", "_drink_object_plan", "object.drink"),
    PlanningStrategy("object.sit_on", "_sit_on_object_plan", "object.sit_on"),
)
