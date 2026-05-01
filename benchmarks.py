def detect_benchmark(text: str) -> str | None:
    lower = text.lower()
    route_kw = ("route", "mininet", "pingall", "machine")
    malt_kw = ("graph", "networkx", "process_graph", "data center")
    k8s_kw = ("kubernetes", "kubectl", "networkpolicy", "pod", "namespace")
    if any(k in lower for k in route_kw):
        return "route"
    if any(k in lower for k in malt_kw):
        return "malt"
    if any(k in lower for k in k8s_kw):
        return "k8s"
    return None
