"""Greeting agent - coordinator for product introduction and general queries."""

from langgraph.graph import StateGraph

from mit.core.coordinator import BaseCoordinator
from mit.agents.greeting.knowledge import GreetingKnowledgeSubAgent


class GreetingAgent(BaseCoordinator):
    """Greeting module owner.

    Single sub-agent coordinator that handles product introductions,
    greetings, and general information queries.

    Uses build_single_agent_graph() since there is only one sub-agent,
    skipping unnecessary classification and referral handling.
    """

    name = "greeting"
    description = "Handles greetings, product introductions, module overview, and general information about the MIT system."

    def __init__(self) -> None:
        """Initialize the Greeting agent with a single sub-agent."""
        self.sub_agents = {
            "knowledge": GreetingKnowledgeSubAgent(),
        }
        super().__init__()

    def build_graph(self) -> StateGraph:
        """Build the workflow graph for Greeting module.

        Uses single-agent graph since there is only one sub-agent.
        """
        return self.build_single_agent_graph()
