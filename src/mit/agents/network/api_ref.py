"""API Reference sub-agent for Network Library."""

from mit.core.base_agent import BaseSubAgent


class ApiRefSubAgent(BaseSubAgent):
    """Handles API endpoint definitions and parameter types.

    Specializes in:
    - Endpoint documentation
    - Request/response formats
    - Parameter specifications
    - Authentication requirements
    """

    collection_name = "network_api_ref"
    system_prompt = """You are an API reference expert for the Network Library.
Your role is to answer questions about:
- Endpoint definitions and URLs
- Request parameters and their types
- Response formats and status codes
- Authentication and authorization requirements

When answering:
- Be precise about parameter names, types, and requirements
- Include example request/response formats when helpful
- If the question involves error handling or troubleshooting, suggest consulting the Issues agent

Always base your answers on the provided context."""

    can_refer_to = []  # API ref is typically the source, not a referrer

    @property
    def name(self) -> str:
        """Return the agent name."""
        return "api_ref"
