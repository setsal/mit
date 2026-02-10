"""Network Library agent - coordinator for network-related queries."""

from langgraph.graph import StateGraph

from mit.core.coordinator import BaseCoordinator
from mit.agents.network.api_ref import ApiRefSubAgent
from mit.agents.network.issues import IssuesSubAgent


class NetworkAgent(BaseCoordinator):
    """Network Library module owner.

    Coordinates between API reference and issue troubleshooting sub-agents.
    """

    name = "network"
    description = "Handles network library questions: API endpoints, parameters, error codes, and troubleshooting network issues."

    def __init__(self) -> None:
        """Initialize the Network agent with sub-agents."""
        self.sub_agents = {
            "api_ref": ApiRefSubAgent(),
            "issues": IssuesSubAgent(),
        }
        super().__init__()

    def build_graph(self) -> StateGraph:
        """Build the workflow graph for Network module.

        Uses the default graph structure with classification and referral handling.
        """
        return self.build_default_graph()
