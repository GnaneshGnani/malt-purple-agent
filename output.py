from __future__ import annotations

import ast
import json
import re


def extract_first_json_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def validate_route_output(text: str) -> tuple[bool, str | None]:
    raw = extract_first_json_object(text)
    if not raw:
        return False, None
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return False, None
    if not isinstance(obj, dict):
        return False, None
    m, cmd = obj.get("machine"), obj.get("command")
    if not isinstance(m, str) or not isinstance(cmd, str) or not m.strip() or not cmd.strip():
        return False, None
    return True, json.dumps({"machine": m.strip(), "command": cmd.strip()})


def extract_python_fence(text: str) -> str | None:
    m = re.search(r"```python\s*([\s\S]*?)```", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def validate_malt_output(text: str) -> bool:
    inner = extract_python_fence(text)
    if not inner:
        return False
    if "updated_graph" not in inner:
        return False
    try:
        tree = ast.parse(inner)
    except SyntaxError:
        return False

    process_graph = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "process_graph":
            process_graph = node
            break
    if process_graph is None or len(process_graph.args.args) != 1:
        return False
    if process_graph.args.args[0].arg != "graph_data":
        return False

    blocked_names = {
        "globals",
        "locals",
        "eval",
        "exec",
        "getattr",
        "setattr",
        "__import__",
        "collections",
    }
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return False
        if isinstance(node, ast.Name) and node.id.startswith("solid_step_"):
            return False
        if isinstance(node, ast.Name) and node.id in blocked_names:
            return False
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and "solid_step_" in node.value:
            return False
        if isinstance(node, ast.Attribute) and node.attr.startswith("solid_step_"):
            return False
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            return False
    return True
