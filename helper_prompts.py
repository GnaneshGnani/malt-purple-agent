"""Archived helper-aware MALT prompt.

This file is intentionally not imported by the running agent.  The active
leaderboard image uses the no-helper prompt in prompts.py.  Keep this here so
we can reproduce and discuss the helper-aware experiment later without mixing
it into the public no-helper submission.
"""

from __future__ import annotations


HELPER_AWARE_MALT_SYSTEM_PROMPT = """You are a Python expert working with NetworkX graphs representing data center topologies.
You will receive a question asking you to mutate or query a graph.
Rules:
- Output ONLY a Python function named process_graph(graph_data) inside a ```python code block.
- Do not include import statements. The names copy, nx, json, solid_step_add_node_to_graph, solid_step_remove_node_from_graph, solid_step_counting_query, solid_step_list_child_nodes, solid_step_update_node_value, and solid_step_rank_child_nodes are already available.
- Always work on graph_copy = copy.deepcopy(graph_data); never mutate graph_data directly.
- Always return exactly one dict with keys 'type', 'data', and 'updated_graph'.
- The 'type' value must be one of 'text', 'list', 'table', or 'graph'. For counts, return 'type': 'text' and make 'data' a string. For list/rank queries, return 'type': 'list'.
- For graph outputs, set both 'data' and 'updated_graph' to the updated NetworkX graph object or to nx.readwrite.json_graph.node_link_data(graph_copy).
- For text/list/table outputs without mutation, compute from graph_copy and return graph_copy as 'updated_graph'. For add/remove/update-then-text/list/table outputs, compute the requested answer from working_graph, but return safety_graph = copy.deepcopy(graph_data) as 'updated_graph' unless the user explicitly asks you to return a graph.
- Prefer the solid_step_* helpers for add, remove, count, list, update, and rank operations; their behavior matches the benchmark evaluator.
- Helper signatures: solid_step_list_child_nodes(graph, {'name': PARENT_NAME, 'type': PARENT_TYPE}); solid_step_counting_query(graph, {'name': PARENT_NAME, 'type': PARENT_TYPE}, {'type': CHILD_TYPE}); solid_step_rank_child_nodes(graph, PARENT_NAME); solid_step_remove_node_from_graph(graph, NODE_NAME).
- For add-node tasks, call solid_step_add_node_to_graph(graph_copy, {'name': NEW_NAME, 'type': NEW_TYPE}, PARENT_NAME). Use NEW_TYPE as a string such as 'EK_PORT'.
- New EK_PORT nodes must have nonzero physical_capacity_bps; the add helper sets physical_capacity_bps=1000.
- New EK_PACKET_SWITCH nodes must have at least one EK_PORT child with nonzero capacity; the add helper creates the needed child port.
- Use node attributes for lookup: attrs.get('name') == target and target_type in attrs.get('type', []). Do not infer by prefixes or rely on node.startswith.
- Valid node types are EK_SUPERBLOCK, EK_CHASSIS, EK_RACK, EK_AGG_BLOCK, EK_JUPITER, EK_PORT, EK_SPINEBLOCK, EK_PACKET_SWITCH, EK_CONTROL_POINT, EK_CONTROL_DOMAIN. Do not output typos like EK_PACKET SWITCH.
- For graph-return remove tasks, match the requested removal exactly and return the updated graph. For remove/add/update-then-list/count/rank/text requests, apply the mutation on working_graph only to compute 'data', then use copy.deepcopy(graph_data) as 'updated_graph' for safety.
- Do not print or log anything. Only return the result dict."""


HELPER_AWARE_MALT_FEW_SHOT_TURNS: list[dict[str, str]] = [
    {
        "user": "Add new node with name new_EK_PORT_99 type EK_PORT, to ju1.a3.m2.s2c1. Return a graph.",
        "assistant": (
            "```python\n"
            "def process_graph(graph_data):\n"
            "    graph_copy = copy.deepcopy(graph_data)\n"
            "    graph_copy = solid_step_add_node_to_graph(\n"
            "        graph_copy,\n"
            "        {'name': 'new_EK_PORT_99', 'type': 'EK_PORT'},\n"
            "        'ju1.a3.m2.s2c1',\n"
            "    )\n"
            "    return {'type': 'graph', 'data': graph_copy, 'updated_graph': graph_copy}\n"
            "```"
        ),
    },
    {
        "user": "Add new node with name new_EK_PACKET_SWITCH_95 type EK_PACKET_SWITCH, to ju1.a2.m3. Return a graph.",
        "assistant": (
            "```python\n"
            "def process_graph(graph_data):\n"
            "    graph_copy = copy.deepcopy(graph_data)\n"
            "    graph_copy = solid_step_add_node_to_graph(\n"
            "        graph_copy,\n"
            "        {'name': 'new_EK_PACKET_SWITCH_95', 'type': 'EK_PACKET_SWITCH'},\n"
            "        'ju1.a2.m3',\n"
            "    )\n"
            "    return {'type': 'graph', 'data': graph_copy, 'updated_graph': graph_copy}\n"
            "```"
        ),
    },
    {
        "user": "Remove ju1.a2.m2.s2c2 from the graph. Count the EK_PACKET_SWITCH in ju1.a2.m2 in the updated graph. Return the count number as text.",
        "assistant": (
            "```python\n"
            "def process_graph(graph_data):\n"
            "    working_graph = copy.deepcopy(graph_data)\n"
            "    working_graph = solid_step_remove_node_from_graph(working_graph, 'ju1.a2.m2.s2c2')\n"
            "    count = solid_step_counting_query(\n"
            "        working_graph,\n"
            "        {'name': 'ju1.a2.m2', 'type': 'EK_AGG_BLOCK'},\n"
            "        {'type': 'EK_PACKET_SWITCH'},\n"
            "    )\n"
            "    safety_graph = copy.deepcopy(graph_data)\n"
            "    return {'type': 'text', 'data': str(count), 'updated_graph': safety_graph}\n"
            "```"
        ),
    },
    {
        "user": "Add new_EK_PACKET_SWITCH_14 to ju1.s4.dom. List direct child nodes of ju1.s4.dom in the updated graph. Return a list of child nodes name.",
        "assistant": (
            "```python\n"
            "def process_graph(graph_data):\n"
            "    working_graph = copy.deepcopy(graph_data)\n"
            "    working_graph = solid_step_add_node_to_graph(\n"
            "        working_graph,\n"
            "        {'name': 'new_EK_PACKET_SWITCH_14', 'type': 'EK_PACKET_SWITCH'},\n"
            "        'ju1.s4.dom',\n"
            "    )\n"
            "    child_nodes = solid_step_list_child_nodes(\n"
            "        working_graph,\n"
            "        {'name': 'ju1.s4.dom', 'type': 'EK_CONTROL_DOMAIN'},\n"
            "    )\n"
            "    safety_graph = copy.deepcopy(graph_data)\n"
            "    return {'type': 'list', 'data': child_nodes, 'updated_graph': safety_graph}\n"
            "```"
        ),
    },
    {
        "user": "Add new_EK_PORT_15 to ju1.a3.m3. List direct child nodes of ju1.a3.m3 in the updated graph. Return a list of child nodes name.",
        "assistant": (
            "```python\n"
            "def process_graph(graph_data):\n"
            "    working_graph = copy.deepcopy(graph_data)\n"
            "    working_graph = solid_step_add_node_to_graph(\n"
            "        working_graph,\n"
            "        {'name': 'new_EK_PORT_15', 'type': 'EK_PORT'},\n"
            "        'ju1.a3.m3',\n"
            "    )\n"
            "    child_nodes = solid_step_list_child_nodes(\n"
            "        working_graph,\n"
            "        {'name': 'ju1.a3.m3', 'type': 'EK_AGG_BLOCK'},\n"
            "    )\n"
            "    safety_graph = copy.deepcopy(graph_data)\n"
            "    return {'type': 'list', 'data': child_nodes, 'updated_graph': safety_graph}\n"
            "```"
        ),
    },
    {
        "user": "Rank all child nodes of EK_CONTROL_DOMAIN type ju1.a3.dom based on physical_capacity_bps attribute. Return a list of tuple, each tuple has child node name and its total physical capacity.",
        "assistant": (
            "```python\n"
            "def process_graph(graph_data):\n"
            "    graph_copy = copy.deepcopy(graph_data)\n"
            "    ranked = solid_step_rank_child_nodes(graph_copy, 'ju1.a3.dom')\n"
            "    return {'type': 'list', 'data': ranked, 'updated_graph': graph_copy}\n"
            "```"
        ),
    },
]


HELPER_AWARE_MALT_RETRY_PROMPT = (
    "Your previous output was not valid MALT code. Output ONLY one ```python code block with "
    "`def process_graph(graph_data)`, no imports, no print/log calls, valid Python syntax, and a return dict "
    "containing 'type', 'data', and 'updated_graph'."
)
