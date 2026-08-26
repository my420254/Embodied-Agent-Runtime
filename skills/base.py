from typing import Protocol


ValidationResult = tuple[bool, str, str]


class SkillHandler(Protocol):
    name: str

    def validate(self, sim_env: dict, sim_robot: dict, params: dict) -> ValidationResult:
        ...

    def apply(self, sim_env: dict, sim_robot: dict, params: dict) -> None:
        ...

