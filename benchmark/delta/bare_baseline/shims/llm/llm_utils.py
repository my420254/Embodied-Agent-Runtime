from copy import deepcopy
import ast
import json
import re


def _strip_think_blocks(text: str):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()


def _extract_first_json_object(text: str):
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escape = False
    for idx in range(start, len(text)):
        ch = text[idx]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start: idx + 1]
    return None


def _parse_plan_payload(response: str):
    cleaned = _strip_think_blocks(response)
    block = _extract_first_json_object(cleaned)
    if not block:
        return None
    for parser in (json.loads, ast.literal_eval):
        try:
            value = parser(block)
        except Exception:
            continue
        if isinstance(value, dict):
            return value
    return None


def _extract_plan_lines_from_text(text: str):
    normalized = str(text).replace("\\\\n", "\n").replace("\\n", "\n")
    lines = []
    for raw_line in normalized.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "(" in line and ")" in line:
            line = line[line.find("("): line.rfind(")") + 1]
            if line.startswith("(") and line.endswith(")"):
                lines.append(line)
    if lines:
        return lines
    return re.findall(r"\([^()\n]+\)", normalized)


def export_result(response: str, file_name: str):
    response = _strip_think_blocks(response)
    if "```" in response:
        response = response.split("```")[1]
    start_idx = response.find("(define")
    if start_idx > 0 and response[0: start_idx] != "\n":
        response = response.replace(response[0: start_idx], "")
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(response)


def export_obj_list(response: str):
    assert "[" in response and "]" in response, "No list found in response!"
    start_idx = response.find("[")
    end_idx = response.rfind("]")
    obj_list_str = response[start_idx + 1:end_idx]
    return ast.literal_eval(f"[{obj_list_str}]")


def export_subgoal_list(response: str):
    subgoal_list = []
    for g in response.split("```"):
        cg = deepcopy(g)
        cg = cg.replace(" ", "")
        if "(:goal" in cg and cg.endswith(")\n"):
            subgoal_list.append(g[g.find("(:goal"):g.rfind(")\n")+len(")\n")])
    return subgoal_list


def export_sayplan_search_cmd(response: str):
    output = _parse_plan_payload(response)
    if output is None:
        raise ValueError("No valid dict payload found in response")
    return output["mode"], output["chain_of_thought"], output["reasoning"], output["command"]


def export_sayplan_plan(response: str, file_name: str):
    payload = _parse_plan_payload(response)
    if payload and "plan" in payload:
        plan_source = payload["plan"]
    else:
        plan_source = _strip_think_blocks(response)

    if isinstance(plan_source, list):
        plan_list = [str(x).strip() for x in plan_source if str(x).strip()]
    else:
        plan_list = _extract_plan_lines_from_text(plan_source)
    if not plan_list:
        raise ValueError("No action lines found in response")
    plan_length = len(plan_list)
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("\n".join(plan_list))
    return plan_list, plan_length


def export_python_code(response: str):
    start_idx = response.find("```python")
    end_idx = response.rfind("```")
    return response[start_idx + len("```python"): end_idx]
