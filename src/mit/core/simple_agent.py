"""Base simple LLM agent class without RAG capabilities.

Use this for sub-agents that only need an LLM with a system prompt,
without any vector store / retrieval. Plug-compatible with BaseSubAgent
so coordinators can use either type interchangeably.
"""

from abc import ABC, abstractmethod

from langchain_core.prompts import ChatPromptTemplate

from mit.config import get_config
from mit.llm import extract_text, get_chat_llm
from mit.logging import get_logger
from mit.state import AgentResponse, AgentState


class SimpleLLMAgent(ABC):
    """Sub-agent that uses only LLM, no RAG retrieval.

    Each simple agent must define:
    - system_prompt: Agent personality and instructions
    - description: Brief description of what this agent handles
    - can_refer_to: List of sub-agents this agent can refer to

    Unlike BaseSubAgent, this class does NOT require a ChromaDB
    collection or Retriever. It answers purely from its system prompt
    and the conversation context.
    """

    system_prompt: str
    description: str
    can_refer_to: list[str] = []

    def __init__(self) -> None:
        """Initialize the simple agent with LLM only (no RAG)."""
        config = get_config()
        self.llm = get_chat_llm(temperature=config.agent.temperature)
        self._sibling_descriptions: dict[str, str] = {}
        self._prompt_template = None  # Built lazily after siblings are set
        self._logger = get_logger(f"agent.{self.name}")

    def set_siblings(self, siblings: dict[str, str]) -> None:
        """Set sibling agent descriptions for referral awareness.

        Args:
            siblings: Dict mapping sibling agent names to their descriptions
        """
        self._sibling_descriptions = {k: v for k, v in siblings.items() if k != self.name}
        self._prompt_template = self._build_prompt_template()

    def _build_prompt_template(self) -> ChatPromptTemplate:
        """Build the prompt template for this agent."""
        # Build sibling awareness section
        sibling_section = ""
        if self._sibling_descriptions:
            sibling_lines = "\n".join(
                f"- {name}: {desc}"
                for name, desc in self._sibling_descriptions.items()
            )
            sibling_section = f"""\n\nYou are part of a team of specialized agents. Here are your sibling agents:
{sibling_lines}

If the user's question relates to a sibling agent's expertise, include a referral suggestion in your response.
Use phrases like "refer to [agent_name]" or "consult [agent_name] agent" to trigger a referral."""

        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt + sibling_section),
                (
                    "system",
                    """Use the conversation context to answer the user's question.
If you cannot answer, say so clearly.
If the question would be better answered by another agent, indicate this in your response.

Conversation context:
{context}""",
                ),
                ("human", "{query}"),
            ]
        )

    async def generate(self, query: str, messages_context: str) -> AgentResponse:
        """Generate a response using the LLM.

        Args:
            query: User query
            messages_context: Formatted conversation history

        Returns:
            AgentResponse with answer, empty sources, optional referral
        """
        self._logger.debug("Generating response (LLM-only)...")

        chain = self._prompt_template | self.llm
        response = await chain.ainvoke({
            "context": messages_context or "No previous conversation.",
            "query": query,
        })
        response_text = extract_text(response.content)

        # Parse response for referrals
        referral = self._detect_referral(response_text)
        if referral:
            self._logger.info(f"Detected referral -> {referral}")

        self._logger.info("Response generated")
        return AgentResponse(
            answer=response_text,
            sources=[],
            referral=referral,
            confidence=1.0,
        )

    def _detect_referral(self, response: str) -> str | None:
        """Detect if the response suggests consulting another agent."""
        response_lower = response.lower()
        for agent_name in self.can_refer_to:
            if agent_name.lower() in response_lower:
                referral_phrases = [
                    f"consult {agent_name}",
                    f"check with {agent_name}",
                    f"refer to {agent_name}",
                    f"{agent_name} agent",
                ]
                if any(phrase in response_lower for phrase in referral_phrases):
                    return agent_name
        return None

    async def invoke(self, state: AgentState) -> AgentState:
        """Main entry point - generate response using LLM only.

        Compatible interface with BaseSubAgent.invoke().
        """
        # Get the latest user message
        messages = state.get("messages", [])
        query = ""
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                query = msg.content
                break
            elif isinstance(msg, tuple) and msg[0] == "human":
                query = msg[1]
                break

        if not query:
            return {
                **state,
                "final_answer": "No query provided.",
                "referral": None,
            }

        # Build conversation context from message history
        messages_context = ""
        if len(messages) > 1:
            history_lines = []
            for msg in messages[:-1]:
                if hasattr(msg, "type"):
                    role = "User" if msg.type == "human" else "Assistant"
                    history_lines.append(f"{role}: {msg.content}")
                elif isinstance(msg, tuple):
                    role = "User" if msg[0] == "human" else "Assistant"
                    history_lines.append(f"{role}: {msg[1]}")
            if history_lines:
                messages_context = "\n".join(history_lines[-10:])

        # Generate response (no retrieval step)
        response = await self.generate(query, messages_context)

        return {
            **state,
            "context": [],  # No RAG context
            "final_answer": response["answer"],
            "referral": response["referral"],
        }

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of this sub-agent."""
        ...
