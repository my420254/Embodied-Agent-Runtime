from adapters.mcp_skill_adapter import build_mcp_skill_manifest, skill_contract_to_mcp_tool
from skills.contracts import SkillContract


def test_skill_contract_to_mcp_tool_exports_json_schema():
    contract = SkillContract(
        skill_id="Pickup",
        description="抓取目标物品",
        parameters={"target_item": "string"},
        handler="skills.Pickup.handler:PickupSkill",
        execution_domain="机械臂控制",
    )

    tool = skill_contract_to_mcp_tool(contract).to_dict()

    assert tool["name"] == "Pickup"
    assert tool["inputSchema"]["properties"]["target_item"]["type"] == "string"
    assert tool["inputSchema"]["required"] == ["target_item"]
    assert tool["metadata"]["execution_domain"] == "机械臂控制"


def test_build_mcp_skill_manifest_reads_enabled_skills():
    manifest = build_mcp_skill_manifest()
    names = {tool["name"] for tool in manifest["tools"]}

    assert manifest["tool_count"] >= 1
    assert "Pickup" in names
    assert "Slice" in names
