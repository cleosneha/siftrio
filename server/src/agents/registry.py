from src.agents.project_chat.graph import get_compiled_graph


def get_graph(agent_name: str) -> object:
    if agent_name == "project_chat":
        return get_compiled_graph()
    msg = f"Unknown agent: {agent_name}. Available: ['project_chat']"
    raise KeyError(msg)
