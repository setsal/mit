"""Auth agent - coordinator for authentication-related queries."""

from langgraph.graph import StateGraph

from mit.core.coordinator import BaseCoordinator
from mit.agents.auth.oauth import OAuthSubAgent
from mit.agents.auth.errors import AuthErrorsSubAgent


class AuthAgent(BaseCoordinator):
    """Auth module owner.

    Coordinates between OAuth specifications and auth error troubleshooting.
    """

    name = "auth"

    def __init__(self) -> None:
        """Initialize the Auth agent with sub-agents."""
        self.sub_agents = {
            "oauth": OAuthSubAgent(),
            "errors": AuthErrorsSubAgent(),
        }
        super().__init__()

    def build_graph(self) -> StateGraph:
        """Build the workflow graph for Auth module.

        Uses the default graph structure with classification and referral handling.
        """
        return self.build_default_graph()
