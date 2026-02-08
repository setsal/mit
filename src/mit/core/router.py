"""Module router - entry point for routing to module owners."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph

from mit.config import get_config
from mit.core.coordinator import BaseCoordinator
from mit.logging import get_logger
from mit.state import AgentState

logger = get_logger("router")


class ModuleRouter:
    """Routes user queries to the appropriate module owner (agent)."""

    def __init__(self, agents: dict[str, BaseCoordinator]) -> None:
        """Initialize the router with available agents.

        Args:
            agents: Dictionary mapping module names to coordinator instances
        """
        self.agents = agents
        config = get_config()
        self.llm = AzureChatOpenAI(
            azure_endpoint=config.azure_openai.endpoint,
            api_key=config.azure_openai.api_key,
            api_version=config.azure_openai.api_version,
            azure_deployment=config.azure_openai.deployment,
            temperature=0.0,
        )
        self._router_prompt = self._build_router_prompt()

    def _build_router_prompt(self) -> ChatPromptTemplate:
        """Build prompt for module routing."""
        module_descriptions = "\n".join(
            f"- {name}: {agent.name}"
            for name, agent in self.agents.items()
        )
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are a query router. Determine which module should handle the user's query.

Available modules:
{module_descriptions}

Respond with ONLY the module name, nothing else.""",
                ),
                ("human", "{query}"),
            ]
        )

    async def route_query(self, query: str) -> str:
        """Route the query to the appropriate module."""
        logger.debug(f"Routing query: {query[:100]}...")
        chain = self._router_prompt | self.llm
        response = await chain.ainvoke({"query": query})
        module_name = response.content.strip().lower()

        if module_name in self.agents:
            logger.info(f"Routed to module: {module_name}")
            return module_name

        # Default to first module if routing fails
        default_module = next(iter(self.agents.keys()))
        logger.warning(f"Unknown module '{module_name}', defaulting to: {default_module}")
        return default_module

    async def router_node(self, state: AgentState) -> AgentState:
        """Node that routes to the appropriate module."""
        messages = state.get("messages", [])
        query = ""
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                query = msg.content
                break
            elif isinstance(msg, tuple) and msg[0] == "human":
                query = msg[1]
                break

        module_name = await self.route_query(query)

        return {
            **state,
            "current_module": module_name,
            "hop_count": 0,  # Reset hop count for new module
            "visited_agents": [],
        }

    def route_to_module(self, state: AgentState) -> str:
        """Determine which module to route to."""
        return state.get("current_module", next(iter(self.agents.keys())))

    def build_graph(self) -> StateGraph:
        """Build the main routing graph."""
        builder = StateGraph(AgentState)

        # Add router node
        builder.add_node("route", self.router_node)

        # Add each module's graph as a node
        for name, agent in self.agents.items():
            module_graph = agent.get_graph().compile()
            builder.add_node(name, module_graph)

        # Define edges
        builder.add_edge(START, "route")
        builder.add_conditional_edges(
            "route",
            self.route_to_module,
            {name: name for name in self.agents.keys()},
        )

        # All modules end at END
        for name in self.agents.keys():
            builder.add_edge(name, END)

        return builder
