from src.agents.project_chat.graph import compiled_graph as project_chat_graph

AGENT_REGISTRY = {
    "project_chat": project_chat_graph,
}


def get_graph(agent_name: str) -> object:
    graph = AGENT_REGISTRY.get(agent_name)
    if graph is None:
        msg = f"Unknown agent: {agent_name}. Available: {list(AGENT_REGISTRY.keys())}"
        raise KeyError(msg)
    return graph
