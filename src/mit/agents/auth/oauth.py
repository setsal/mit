"""OAuth sub-agent for Auth module."""

from mit.core.base_agent import BaseSubAgent


class OAuthSubAgent(BaseSubAgent):
    """Handles OAuth 2.0 specifications and implementation.

    Specializes in:
    - OAuth 2.0 grant types
    - Token formats and claims
    - Scope definitions
    - Authorization flows
    """

    collection_name = "auth_oauth"
    system_prompt = """You are an OAuth 2.0 expert for the Auth module.
Your role is to answer questions about:
- OAuth 2.0 grant types (authorization code, client credentials, etc.)
- Token formats (JWT, opaque tokens)
- Token claims and validation
- Scope definitions and permissions
- Authorization and authentication flows

When answering:
- Be precise about OAuth specifications
- Include flow diagrams conceptually when helpful
- Reference RFC specifications when applicable
- If the question involves authentication errors, suggest consulting the Errors agent

Always base your answers on the provided context."""

    can_refer_to = []

    @property
    def name(self) -> str:
        """Return the agent name."""
        return "oauth"
