"""Base coordinator class for module owners."""

from abc import ABC, abstractmethod
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph

from mit.config import get_config
from mit.core.base_agent import BaseSubAgent
from mit.logging import get_logger
from mit.state import AgentState


class BaseCoordinator(ABC):
    """Base coordinator that routes queries to sub-agents.

    Each module owner extends this class and defines:
    - name: Module identifier
    - sub_agents: Dictionary of sub-agent instances
    - build_graph(): Custom workflow state machine
    """

    name: str
    sub_agents: dict[str, BaseSubAgent]

    def __init__(self) -> None:
        """Initialize the coordinator with LLM for classification."""
        config = get_config()
        self.llm = AzureChatOpenAI(
            azure_endpoint=config.azure_openai.endpoint,
            api_key=config.azure_openai.api_key,
            api_version=config.azure_openai.api_version,
            azure_deployment=config.azure_openai.deployment,
            temperature=0.0,
        )
        self._classifier_prompt = self._build_classifier_prompt()
        self._graph = None
        self._logger = get_logger(f"coordinator.{self.name}")

    def _build_classifier_prompt(self) -> ChatPromptTemplate:
        """Build prompt for query classification."""
        agent_descriptions = "\n".join(
            f"- {name}: {agent.system_prompt[:100]}..."
            for name, agent in self.sub_agents.items()
        )
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are a query classifier for the {self.name} module.
Based on the user's query, determine which sub-agent should handle it.

Available sub-agents:
{agent_descriptions}

Respond with ONLY the sub-agent name, nothing else.""",
                ),
                ("human", "{query}"),
            ]
        )

    async def classify_query(self, query: str) -> str:
        """Classify the query to determine which sub-agent should handle it."""
        self._logger.debug(f"Classifying query: {query[:100]}...")
        chain = self._classifier_prompt | self.llm
        response = await chain.ainvoke({"query": query})
        agent_name = response.content.strip().lower()

        # Validate agent name
        if agent_name in self.sub_agents:
            self._logger.info(f"Classified -> {agent_name}")
            return agent_name

        # Default to first agent if classification fails
        default_agent = next(iter(self.sub_agents.keys()))
        self._logger.warning(f"Unknown agent '{agent_name}', defaulting to: {default_agent}")
        return default_agent

    async def classify_node(self, state: AgentState) -> AgentState:
        """Node that classifies and routes to appropriate sub-agent."""
        messages = state.get("messages", [])
        query = ""
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                query = msg.content
                break
            elif isinstance(msg, tuple) and msg[0] == "human":
                query = msg[1]
                break

        sub_agent_name = await self.classify_query(query)

        return {
            **state,
            "current_sub_agent": sub_agent_name,
            "hop_count": state.get("hop_count", 0) + 1,
            "visited_agents": state.get("visited_agents", []) + [sub_agent_name],
        }

    def route_to_sub_agent(self, state: AgentState) -> str:
        """Route to the appropriate sub-agent based on classification."""
        return state.get("current_sub_agent", next(iter(self.sub_agents.keys())))

    async def handle_referral(self, state: AgentState) -> AgentState:
        """Handle referral to another sub-agent."""
        referral = state.get("referral")
        if referral and referral in self.sub_agents:
            self._logger.info(f"Handling referral -> {referral}")
            return {
                **state,
                "current_sub_agent": referral,
                "hop_count": state.get("hop_count", 0) + 1,
                "visited_agents": state.get("visited_agents", []) + [referral],
                "referral": None,  # Clear referral
            }
        return state

    def should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """Determine if we should continue processing or end."""
        # Check hop limit
        hop_count = state.get("hop_count", 0)
        max_hops = state.get("max_hops", 10)
        if hop_count >= max_hops:
            self._logger.warning(f"Hop limit reached ({hop_count}/{max_hops}), ending")
            return "end"

        # Check for referral
        referral = state.get("referral")
        if referral and referral in self.sub_agents:
            # Check if we've already visited this agent (cycle detection)
            if referral in state.get("visited_agents", []):
                self._logger.warning(f"Cycle detected: {referral} already visited, ending")
                return "end"
            return "continue"

        return "end"

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Build the custom workflow graph for this module.

        Override this method to define custom routing logic.
        """
        ...

    def get_graph(self) -> StateGraph:
        """Get or build the compiled graph."""
        if self._graph is None:
            self._graph = self.build_graph()
        return self._graph

    def build_default_graph(self) -> StateGraph:
        """Build a default graph with standard routing.

        Subclasses can use this as a starting point.
        """
        builder = StateGraph(AgentState)

        # Add classifier node
        builder.add_node("classify", self.classify_node)

        # Add sub-agent nodes
        for name, agent in self.sub_agents.items():
            builder.add_node(name, agent.invoke)

        # Add referral handler
        builder.add_node("handle_referral", self.handle_referral)

        # Define edges
        builder.add_edge(START, "classify")
        builder.add_conditional_edges(
            "classify",
            self.route_to_sub_agent,
            {name: name for name in self.sub_agents.keys()},
        )

        # Each sub-agent can either end or continue via referral
        for name in self.sub_agents.keys():
            builder.add_conditional_edges(
                name,
                self.should_continue,
                {"continue": "handle_referral", "end": END},
            )

        # Referral handler routes back to sub-agent
        builder.add_conditional_edges(
            "handle_referral",
            self.route_to_sub_agent,
            {name: name for name in self.sub_agents.keys()},
        )

        return builder
