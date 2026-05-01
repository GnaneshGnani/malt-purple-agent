from __future__ import annotations


SYSTEM_PROMPTS: dict[str, str] = {
    "route": (
        "You are an expert network engineer debugging a Mininet virtual network.\n"
        "The network has packet loss due to a misconfiguration on the router.\n"
        "You must diagnose the problem and fix it using shell commands.\n"
        "Rules:\n"
        "- Output ONLY a JSON object with exactly two keys: 'machine' (the node name "
        "to run the command on) and 'command' (a single shell command).\n"
        "- Do NOT include sudo. Do NOT use vtysh. Do NOT use ping commands.\n"
        "- Node and interface names have a prefix (e.g. 'p29_r0', 'p29_r0-eth1').\n"
        "- Run one diagnostic command first to identify the root cause, then fix it.\n"
        "- Do not break connections that are currently working.\n"
        'Output format (strict): {"machine": "<node>", "command": "<cmd>"}'
    ),
    "malt": (
        "You are a Python expert working with NetworkX graphs representing data center topologies.\n"
        "You will receive a question asking you to mutate or query a graph.\n"
        "Rules:\n"
        "- Output ONLY a Python function named process_graph(graph_data) inside a ```python code block.\n"
        "- Do not include import statements. The names copy, nx, json, and math are available.\n"
        "- Use normal NetworkX graph operations and small local helper functions inside process_graph.\n"
        "- Use only the listed global names plus variables/functions you define inside process_graph.\n"
        "- Always work on graph_copy = copy.deepcopy(graph_data); never mutate graph_data directly.\n"
        "- Always return exactly one dict with keys 'type', 'data', and 'updated_graph'.\n"
        "- The 'type' value must be one of 'text', 'list', 'table', or 'graph'. For counts, return "
        "'type': 'text' and make 'data' a string. For list/rank queries, return 'type': 'list'.\n"
        "- For graph outputs, set both 'data' and 'updated_graph' to the updated NetworkX graph object "
        "or to nx.readwrite.json_graph.node_link_data(graph_copy).\n"
        "- For text/list/table outputs without mutation, compute from graph_copy and return graph_copy as "
        "'updated_graph'. For add/remove/update-then-text/list/table outputs, compute the requested answer "
        "from working_graph, but return safety_graph = copy.deepcopy(graph_data) as 'updated_graph' unless "
        "the user explicitly asks you to return a graph.\n"
        "- MALT hierarchy uses directed edges whose edge attribute type contains 'RK_CONTAINS'; parent nodes "
        "point to child nodes.\n"
        "- Node attributes include 'name' and 'type'. A node's type may be a string or a list, so check both.\n"
        "- Use node attributes for lookup: attrs.get('name') == target. Do not infer by prefixes or rely on "
        "node.startswith.\n"
        "- To count descendants, do BFS/DFS over outgoing RK_CONTAINS edges from the parent.\n"
        "- To list direct children, only return the 'name' attributes of immediate RK_CONTAINS successors.\n"
        "- To rank direct children by physical_capacity_bps, sum capacity from EK_PORT nodes in each child's "
        "contained subtree and sort by capacity descending.\n"
        "- New EK_PORT nodes must have physical_capacity_bps=1000.\n"
        "- New EK_PACKET_SWITCH nodes must have at least one EK_PORT child with nonzero capacity; "
        "create a child port and connect it with an RK_CONTAINS edge.\n"
        "- Valid node types are EK_SUPERBLOCK, EK_CHASSIS, EK_RACK, EK_AGG_BLOCK, EK_JUPITER, EK_PORT, "
        "EK_SPINEBLOCK, EK_PACKET_SWITCH, EK_CONTROL_POINT, EK_CONTROL_DOMAIN. Do not output typos "
        "like EK_PACKET SWITCH.\n"
        "- For graph-return remove tasks, match the requested removal exactly and return the updated graph. "
        "For remove/add/update-then-list/count/rank/text requests, apply the mutation on working_graph only "
        "to compute 'data', then use copy.deepcopy(graph_data) as 'updated_graph' for safety.\n"
        "- Do not print or log anything. Only return the result dict."
    ),
    "k8s": (
        "You are a Kubernetes network policy expert. A microservice deployment has "
        "connectivity mismatches due to incorrect NetworkPolicy resources.\n"
        "Rules:\n"
        "- Diagnose using kubectl get/describe commands first.\n"
        "- Fix using kubectl patch or by providing corrected YAML.\n"
        "- Output one command at a time as plain text.\n"
        "- Do not break currently working connections."
    ),
}

ROUTE_FEW_SHOT_TURNS: list[dict[str, str]] = [
    {
        "user": """
    p29_h1 -> p29_h2 X X p29_r0
    p29_h2 -> p29_h1 X X p29_r0
    p29_h3 -> X X p29_h4 p29_r0
    p29_h4 -> X X p29_h3 p29_r0
    p29_r0 -> p29_h1 p29_h2 p29_h3 p29_h4
    *** Results: 40% dropped (12/20 received)
        """.strip(),
        "assistant": '{"machine": "p29_r0", "command": "sysctl net.ipv4.ip_forward"}',
    },
    {
        "user": """
    p29_h1 -> p29_h2 X X X
    p29_h2 -> p29_h1 X X X
    p29_h3 -> X X p29_h4 p29_r0
    p29_h4 -> X X p29_h3 p29_r0
    p29_r0 -> X X p29_h3 p29_h4
    *** Results: 60% dropped (8/20 received)
""".strip(),
        "assistant": '{"machine": "p29_r0", "command": "ip link show"}',
    },
    {
        "user": """
    p29_h1 -> p29_h2 X X p29_r0
    p29_h2 -> h1 X X p29_r0
    p29_h3 -> X X p29_h4 X
    p29_h4 -> X X p29_h3 X
    p29_r0 -> p29_h1 p29_h2 X X
    *** Results: 60% dropped (8/20 received)
        """.strip(),
        "assistant": '{"machine": "p29_r0", "command": "iptables -L -v --line-numbers"}',
    },
    {
        "user": """
    p29_h1 -> p29_h2 X X X X X
    p29_h2 -> p29_h1 X X X X X
    p29_h3 -> X X p29_h4 p29_h5 p29_h6 p29_r0
    p29_h4 -> X X p29_h3 p29_h5 p29_h6 p29_r0
    p29_h5 -> X X p29_h3 p29_h4 p29_h6 p29_r0
    p29_h6 -> X X p29_h3 p29_h4 p29_h5 p29_r0
    p29_r0 -> X X p29_h3 p29_h4 p29_h5 p29_h6
    *** Results: 47% dropped (22/42 received)
""".strip(),
        "assistant": '{"machine": "p29_r0", "command": "ip route"}',
    },
    {
        "user": """
    p29_h1 -> p29_h2 p29_h3 p29_h4 X X X X p29_r0
    p29_h2 -> p29_h1 p29_h3 p29_h4 X X X X p29_r0
    p29_h3 -> p29_h1 p29_h2 p29_h4 X X X X p29_r0
    p29_h4 -> p29_h1 p29_h2 p29_h3 X X X X p29_r0
    p29_h5 -> X X X X p29_h6 p29_h7 p29_h8 X
    p29_h6 -> X X X X p29_h5 p29_h7 p29_h8 X
    p29_h7 -> X X X X p29_h5 p29_h6 p29_h8 X
    p29_h8 -> X X X X p29_h5 p29_h6 p29_h7 X
    p29_r0 -> p29_h1 p29_h2 p29_h3 p29_h4 X X X X
    *** Results: 55% dropped (32/72 received)
""".strip(),
        "assistant": '{"machine": "p29_r0", "command": "ip addr show dev p29_r0-eth2"}',
    },
]

MALT_FEW_SHOT_TURNS: list[dict[str, str]] = [
    {
        "user": "Add new node with name new_EK_PORT_99 type EK_PORT, to ju1.a3.m2.s2c1. Return a graph.",
        "assistant": (
            "```python\n"
            "def process_graph(graph_data):\n"
            "    graph_copy = copy.deepcopy(graph_data)\n"
            "    parent = None\n"
            "    for node, attrs in graph_copy.nodes(data=True):\n"
            "        if attrs.get('name') == 'ju1.a3.m2.s2c1':\n"
            "            parent = node\n"
            "            break\n"
            "    graph_copy.add_node(\n"
            "        'new_EK_PORT_99',\n"
            "        name='new_EK_PORT_99',\n"
            "        type='EK_PORT',\n"
            "        physical_capacity_bps=1000,\n"
            "    )\n"
            "    if parent is not None:\n"
            "        graph_copy.add_edge(parent, 'new_EK_PORT_99', type='RK_CONTAINS')\n"
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
            "    parent = None\n"
            "    for node, attrs in graph_copy.nodes(data=True):\n"
            "        if attrs.get('name') == 'ju1.a2.m3':\n"
            "            parent = node\n"
            "            break\n"
            "    switch_id = 'new_EK_PACKET_SWITCH_95'\n"
            "    port_id = 'new_EK_PACKET_SWITCH_95.p1'\n"
            "    graph_copy.add_node(switch_id, name=switch_id, type='EK_PACKET_SWITCH')\n"
            "    graph_copy.add_node(port_id, name=port_id, type='EK_PORT', physical_capacity_bps=1000)\n"
            "    if parent is not None:\n"
            "        graph_copy.add_edge(parent, switch_id, type='RK_CONTAINS')\n"
            "    graph_copy.add_edge(switch_id, port_id, type='RK_CONTAINS')\n"
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
            "    def node_by_name(graph, name):\n"
            "        for node, attrs in graph.nodes(data=True):\n"
            "            if attrs.get('name') == name:\n"
            "                return node\n"
            "        return None\n"
            "    def has_type(attrs, expected_type):\n"
            "        types = attrs.get('type', [])\n"
            "        if isinstance(types, str):\n"
            "            return types == expected_type\n"
            "        return expected_type in types\n"
            "    def is_contains(edge_attrs):\n"
            "        edge_type = edge_attrs.get('type', [])\n"
            "        if isinstance(edge_type, str):\n"
            "            return edge_type == 'RK_CONTAINS'\n"
            "        return 'RK_CONTAINS' in edge_type\n"
            "    target = node_by_name(working_graph, 'ju1.a2.m2.s2c2')\n"
            "    if target is not None:\n"
            "        working_graph.remove_node(target)\n"
            "    parent = node_by_name(working_graph, 'ju1.a2.m2')\n"
            "    count = 0\n"
            "    if parent is not None:\n"
            "        queue = [parent]\n"
            "        visited = set()\n"
            "        while queue:\n"
            "            current = queue.pop(0)\n"
            "            if current in visited:\n"
            "                continue\n"
            "            visited.add(current)\n"
            "            for _, child, edge_attrs in working_graph.out_edges(current, data=True):\n"
            "                if is_contains(edge_attrs):\n"
            "                    if has_type(working_graph.nodes[child], 'EK_PACKET_SWITCH'):\n"
            "                        count += 1\n"
            "                    queue.append(child)\n"
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
            "    def node_by_name(graph, name):\n"
            "        for node, attrs in graph.nodes(data=True):\n"
            "            if attrs.get('name') == name:\n"
            "                return node\n"
            "        return None\n"
            "    def is_contains(edge_attrs):\n"
            "        edge_type = edge_attrs.get('type', [])\n"
            "        if isinstance(edge_type, str):\n"
            "            return edge_type == 'RK_CONTAINS'\n"
            "        return 'RK_CONTAINS' in edge_type\n"
            "    parent = node_by_name(working_graph, 'ju1.s4.dom')\n"
            "    switch_id = 'new_EK_PACKET_SWITCH_14'\n"
            "    port_id = 'new_EK_PACKET_SWITCH_14.p1'\n"
            "    working_graph.add_node(switch_id, name=switch_id, type='EK_PACKET_SWITCH')\n"
            "    working_graph.add_node(port_id, name=port_id, type='EK_PORT', physical_capacity_bps=1000)\n"
            "    if parent is not None:\n"
            "        working_graph.add_edge(parent, switch_id, type='RK_CONTAINS')\n"
            "    working_graph.add_edge(switch_id, port_id, type='RK_CONTAINS')\n"
            "    child_nodes = []\n"
            "    if parent is not None:\n"
            "        for _, child, edge_attrs in working_graph.out_edges(parent, data=True):\n"
            "            if is_contains(edge_attrs):\n"
            "                child_nodes.append(working_graph.nodes[child].get('name', child))\n"
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
            "    def node_by_name(graph, name):\n"
            "        for node, attrs in graph.nodes(data=True):\n"
            "            if attrs.get('name') == name:\n"
            "                return node\n"
            "        return None\n"
            "    def is_contains(edge_attrs):\n"
            "        edge_type = edge_attrs.get('type', [])\n"
            "        if isinstance(edge_type, str):\n"
            "            return edge_type == 'RK_CONTAINS'\n"
            "        return 'RK_CONTAINS' in edge_type\n"
            "    parent = node_by_name(working_graph, 'ju1.a3.m3')\n"
            "    working_graph.add_node(\n"
            "        'new_EK_PORT_15',\n"
            "        name='new_EK_PORT_15',\n"
            "        type='EK_PORT',\n"
            "        physical_capacity_bps=1000,\n"
            "    )\n"
            "    if parent is not None:\n"
            "        working_graph.add_edge(parent, 'new_EK_PORT_15', type='RK_CONTAINS')\n"
            "    child_nodes = []\n"
            "    if parent is not None:\n"
            "        for _, child, edge_attrs in working_graph.out_edges(parent, data=True):\n"
            "            if is_contains(edge_attrs):\n"
            "                child_nodes.append(working_graph.nodes[child].get('name', child))\n"
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
            "    def node_by_name(graph, name):\n"
            "        for node, attrs in graph.nodes(data=True):\n"
            "            if attrs.get('name') == name:\n"
            "                return node\n"
            "        return None\n"
            "    def has_type(attrs, expected_type):\n"
            "        types = attrs.get('type', [])\n"
            "        if isinstance(types, str):\n"
            "            return types == expected_type\n"
            "        return expected_type in types\n"
            "    def is_contains(edge_attrs):\n"
            "        edge_type = edge_attrs.get('type', [])\n"
            "        if isinstance(edge_type, str):\n"
            "            return edge_type == 'RK_CONTAINS'\n"
            "        return 'RK_CONTAINS' in edge_type\n"
            "    def total_capacity(start_node):\n"
            "        total = 0\n"
            "        queue = [start_node]\n"
            "        visited = set()\n"
            "        while queue:\n"
            "            current = queue.pop(0)\n"
            "            if current in visited:\n"
            "                continue\n"
            "            visited.add(current)\n"
            "            attrs = graph_copy.nodes[current]\n"
            "            if has_type(attrs, 'EK_PORT'):\n"
            "                total += attrs.get('physical_capacity_bps', 0)\n"
            "            for _, child, edge_attrs in graph_copy.out_edges(current, data=True):\n"
            "                if is_contains(edge_attrs):\n"
            "                    queue.append(child)\n"
            "        return total\n"
            "    parent = node_by_name(graph_copy, 'ju1.a3.dom')\n"
            "    ranked = []\n"
            "    if parent is not None:\n"
            "        for _, child, edge_attrs in graph_copy.out_edges(parent, data=True):\n"
            "            if is_contains(edge_attrs):\n"
            "                ranked.append((graph_copy.nodes[child].get('name', child), total_capacity(child)))\n"
            "    ranked.sort(key=lambda item: item[1], reverse=True)\n"
            "    return {'type': 'list', 'data': ranked, 'updated_graph': graph_copy}\n"
            "```"
        ),
    },
]

ROUTE_RETRY_PROMPT = (
    "Your previous output was not valid JSON with 'machine' and 'command' keys. "
    'Output ONLY the JSON object, nothing else: {"machine": "...", "command": "..."}'
)

MALT_RETRY_PROMPT = (
    "Your previous output was not valid MALT code. Output ONLY one ```python code block with "
    "`def process_graph(graph_data)`, no imports, no print/log calls, valid Python syntax, and a return dict "
    "containing 'type', 'data', and 'updated_graph'. Use ordinary NetworkX/copy code and only the listed "
    "global names."
)
