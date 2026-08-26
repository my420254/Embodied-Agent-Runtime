from __future__ import annotations

from typing import Any

from interfaces.contracts import SceneQuery, SceneQueryResult


class RuntimeSceneGraphService:
    """Minimal scene graph query facade over normalized object instances.

    Expected scene shape:
        {"objects": [{"id": "牛肉_1", "type": "beef", "states": {...}}, ...]}

    This service deliberately owns only runtime instances and state. It does
    not answer semantic affordance or skill questions; those belong to KG.
    """

    def __init__(self, scene: dict[str, Any]) -> None:
        objects = scene.get("objects", [])
        self.objects = tuple(obj for obj in objects if isinstance(obj, dict))

    def query(self, query: SceneQuery) -> SceneQueryResult:
        query_type = query.query_type
        if query_type == "find_instance":
            semantic_type = query.payload.get("type")
            name_hint = str(query.payload.get("name_hint") or "")
            matches = tuple(
                obj
                for obj in self.objects
                if obj.get("type") == semantic_type and (not name_hint or name_hint in str(obj.get("id", "")))
            )
            if not matches and name_hint:
                matches = tuple(obj for obj in self.objects if obj.get("type") == semantic_type)
            unknowns = () if matches else (f"no instance with type={semantic_type!r}",)
            return SceneQueryResult(query_type=query_type, instances=matches, unknowns=unknowns)

        if query_type == "resolve_instance":
            semantic_type = query.payload.get("type")
            name_hint = str(query.payload.get("name_hint") or "")
            if semantic_type:
                matches = tuple(
                    obj
                    for obj in self.objects
                    if obj.get("type") == semantic_type and (not name_hint or name_hint in str(obj.get("id", "")))
                )
                if not matches:
                    matches = tuple(obj for obj in self.objects if obj.get("type") == semantic_type)
            else:
                matches = tuple(obj for obj in self.objects if name_hint and name_hint in str(obj.get("id", "")))
            unknowns = () if matches else (f"cannot resolve instance type={semantic_type!r}",)
            return SceneQueryResult(query_type=query_type, instances=matches[:1], unknowns=unknowns)

        if query_type == "check_state":
            instance_id = query.payload.get("id")
            states = tuple(query.payload.get("states", ()))
            target = next((obj for obj in self.objects if obj.get("id") == instance_id), None)
            if target is None:
                return SceneQueryResult(query_type=query_type, unknowns=(f"unknown instance id={instance_id!r}",))
            current = target.get("states", {}) if isinstance(target.get("states"), dict) else {}
            return SceneQueryResult(
                query_type=query_type,
                instances=(target,),
                states={state: current.get(state) for state in states},
            )

        return SceneQueryResult(query_type=query_type, unknowns=(f"unsupported query_type={query_type}",))
