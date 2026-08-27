from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from skills.contracts import SkillContract, load_all_skill_contracts, load_skill_contracts


_TYPE_ALIASES = {
    "str": "string",
    "string": "string",
    "text": "string",
    "int": "integer",
    "integer": "integer",
    "float": "number",
    "number": "number",
    "bool": "boolean",
    "boolean": "boolean",
    "dict": "object",
    "object": "object",
    "list": "array",
    "array": "array",
}


@dataclass(frozen=True)
class McpSkillTool:
    name: str
    description: str
    input_schema: dict[str, Any]
    annotations: dict[str, Any]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "annotations": self.annotations,
            "metadata": self.metadata,
        }


def _json_schema_type(type_text: str) -> str:
    normalized = str(type_text or "string").strip().lower()
    return _TYPE_ALIASES.get(normalized, "string")


def skill_contract_to_mcp_tool(contract: SkillContract) -> McpSkillTool:
    properties = {
        name: {
            "type": _json_schema_type(type_text),
            "description": f"{name} 参数，原始技能说明类型为 {type_text or 'string'}。",
        }
        for name, type_text in contract.parameters.items()
    }
    required = sorted(contract.parameters)
    high_risk = bool(contract.failure_policy)
    annotations = {
        "title": contract.skill_id,
        "readOnlyHint": False,
        "destructiveHint": high_risk,
        "idempotentHint": False,
        "openWorldHint": False,
    }
    return McpSkillTool(
        name=contract.skill_id,
        description=contract.description,
        input_schema={
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
        annotations=annotations,
        metadata={
            "handler": contract.handler,
            "execution_domain": contract.execution_domain,
            "planning_contract": contract.planning_contract,
            "failure_policy": contract.failure_policy,
            "status": contract.status,
            "version": contract.version,
        },
    )


def build_mcp_skill_manifest(
    *,
    profile: str | None = None,
    include_all: bool = False,
) -> dict[str, Any]:
    contracts = load_all_skill_contracts() if include_all else load_skill_contracts(profile)
    tools = [skill_contract_to_mcp_tool(contract).to_dict() for contract in contracts.values()]
    tools.sort(key=lambda tool: str(tool["name"]).lower())
    return {
        "schema_version": "ouragent-mcp-skill-manifest/v1",
        "description": "OurAgent embodied robot skills exported as MCP-compatible tool descriptors.",
        "profile": profile or ("all" if include_all else "default"),
        "tool_count": len(tools),
        "tools": tools,
    }


def export_mcp_skill_manifest(
    output_path: str | Path,
    *,
    profile: str | None = None,
    include_all: bool = False,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_mcp_skill_manifest(profile=profile, include_all=include_all)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


__all__ = [
    "McpSkillTool",
    "build_mcp_skill_manifest",
    "export_mcp_skill_manifest",
    "skill_contract_to_mcp_tool",
]
