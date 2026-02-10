"""Issues sub-agent for Network Library troubleshooting."""

from mit.core.base_agent import BaseSubAgent


class IssuesSubAgent(BaseSubAgent):
    """Handles common error codes and troubleshooting.

    Specializes in:
    - Error code diagnosis (504, 401, 403, etc.)
    - Common issues and solutions
    - Debugging strategies
    - Performance problems
    """

    collection_name = "network_issues"
    description = "HTTP error codes, connection problems, timeouts, and performance troubleshooting."
    system_prompt = """You are a troubleshooting expert for the Network Library.
Your role is to help diagnose and fix common issues:
- HTTP error codes (504 Gateway Timeout, 401 Unauthorized, 403 Forbidden, etc.)
- Connection problems and timeouts
- Authentication failures
- Performance issues

When answering:
- Start by identifying the likely root cause
- Provide step-by-step troubleshooting instructions
- If the fix requires specific API parameters or configuration, refer to the API_Ref agent
- Include workarounds when available

Always base your answers on the provided context."""

    can_refer_to = ["api_ref"]

    @property
    def name(self) -> str:
        """Return the agent name."""
        return "issues"
