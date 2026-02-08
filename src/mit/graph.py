"""Main LangGraph orchestration for the MIT framework."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from mit.agents.network import NetworkAgent
from mit.agents.auth import AuthAgent
from mit.core.router import ModuleRouter
from mit.state import AgentState


def create_graph(checkpointer: MemorySaver | None = None) -> StateGraph:
    """Create the main MIT graph with all agents.

    Args:
        checkpointer: Optional checkpointer for conversation persistence

    Returns:
        Compiled LangGraph
    """
    # Initialize agents
    agents = {
        "network": NetworkAgent(),
        "auth": AuthAgent(),
    }

    # Create router
    router = ModuleRouter(agents)

    # Build the main graph
    graph_builder = router.build_graph()

    # Compile with optional checkpointer
    if checkpointer:
        return graph_builder.compile(checkpointer=checkpointer)
    return graph_builder.compile()


def get_default_graph():
    """Get the default graph with in-memory checkpointer."""
    checkpointer = MemorySaver()
    return create_graph(checkpointer=checkpointer)


# Default graph instance
_default_graph = None


def get_graph():
    """Get or create the default graph instance."""
    global _default_graph
    if _default_graph is None:
        _default_graph = get_default_graph()
    return _default_graph
