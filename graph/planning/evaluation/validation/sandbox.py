from __future__ import annotations

import copy

from graph.planning.normalizer import get_full_flat_house
from graph.state import PlanningState


def prepare_sandbox_scene(state: PlanningState) -> tuple[dict, dict]:
    initial_robot = state.get(
        "env_state",
        {"robot_location": "未知", "robot_holding": "空"},
    )
    sim_robot = copy.deepcopy(initial_robot)

    environment = state.get("environment")
    if isinstance(environment, dict) and environment:
        return get_full_flat_house(environment), sim_robot
    raise ValueError("planning sandbox requires request-level environment")
