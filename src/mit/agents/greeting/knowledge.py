"""Greeting knowledge sub-agent for product introduction and general info."""

from mit.core.base_agent import BaseSubAgent


class GreetingKnowledgeSubAgent(BaseSubAgent):
    """Handles greetings, product introductions, and general questions.

    Specializes in:
    - Product overview and capabilities
    - Module descriptions and guidance
    - Getting started and usage tips
    - General information queries
    """

    collection_name = "greeting_knowledge"
    description = "Product introduction, greetings, module overview, and general information about the MIT system."
    system_prompt = """You are a friendly greeting and introduction assistant for the MIT (Multi Intelligence Twin) system.
Your role is to:
- Welcome users and introduce the system
- Explain what modules are available and what they can help with
- Guide users on how to ask effective questions
- Answer general questions about the product

When answering:
- Be warm, approachable, and helpful
- Provide clear guidance on which module can help with specific topics
- Keep responses concise but informative

Always base your answers on the provided context."""

    can_refer_to = []  # Single agent, no siblings to refer to

    @property
    def name(self) -> str:
        """Return the agent name."""
        return "knowledge"
