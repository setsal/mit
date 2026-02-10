"""Auth Errors sub-agent for troubleshooting authentication issues."""

from mit.core.base_agent import BaseSubAgent


class AuthErrorsSubAgent(BaseSubAgent):
    """Handles authentication error troubleshooting.

    Specializes in:
    - 401 Unauthorized errors
    - 403 Forbidden errors
    - Token expiration issues
    - Invalid credentials
    """

    collection_name = "auth_errors"
    description = "Authentication error troubleshooting: 401/403 errors, token expiration, and invalid credentials."
    system_prompt = """You are an authentication troubleshooting expert for the Auth module.
Your role is to help diagnose and fix authentication-related issues:
- 401 Unauthorized errors (invalid/missing credentials)
- 403 Forbidden errors (insufficient permissions)
- Token expiration and refresh issues
- Invalid or malformed tokens
- Scope and permission problems

When answering:
- Start by identifying the likely root cause
- Provide step-by-step debugging instructions
- If the issue requires understanding OAuth specs, refer to the OAuth agent
- Include common fixes and workarounds

Always base your answers on the provided context."""

    can_refer_to = ["oauth"]

    @property
    def name(self) -> str:
        """Return the agent name."""
        return "errors"
