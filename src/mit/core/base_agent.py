"""Base sub-agent class with RAG capabilities."""

from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from mit.config import get_config
from mit.llm import get_chat_llm
from mit.logging import get_logger
from mit.rag.retriever import Retriever
from mit.state import AgentResponse, AgentState


class BaseSubAgent(ABC):
    """Base class for all RAG-powered sub-agents.

    Each sub-agent must define:
    - collection_name: ChromaDB collection to query
    - system_prompt: Agent personality and instructions
    - can_refer_to: List of sub-agents this agent can refer to
    """

    collection_name: str
    system_prompt: str
    can_refer_to: list[str] = []

    def __init__(self) -> None:
        """Initialize the sub-agent with LLM and retriever."""
        config = get_config()
        self.llm = get_chat_llm(temperature=config.agent.temperature)
        self.retriever = Retriever(collection_name=self.collection_name)
        self._prompt_template = self._build_prompt_template()
        self._logger = get_logger(f"agent.{self.name}")

    def _build_prompt_template(self) -> ChatPromptTemplate:
        """Build the prompt template for this agent."""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                (
                    "system",
                    """Use the following context to answer the user's question.
If you cannot answer based on the context, say so clearly.
If the question would be better answered by another agent, indicate this in your response.

Context:
{context}""",
                ),
                ("human", "{query}"),
            ]
        )

    async def retrieve(self, query: str, top_k: int | None = None) -> list[Document]:
        """Retrieve relevant documents for the query."""
        config = get_config()
        k = top_k or config.agent.default_top_k
        self._logger.debug(f"Retrieving from RAG (k={k}): {query[:80]}...")
        docs = await self.retriever.aretrieve(query, k=k)
        self._logger.info(f"Retrieved {len(docs)} documents")
        return docs

    async def generate(
        self, query: str, context: list[Document]
    ) -> AgentResponse:
        """Generate a response using retrieved context."""
        self._logger.debug("Generating response...")
        context_text = "\n\n".join(
            f"[{doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
            for doc in context
        )

        chain = self._prompt_template | self.llm
        response = await chain.ainvoke({"context": context_text, "query": query})

        # Parse response for referrals
        referral = self._detect_referral(response.content)
        if referral:
            self._logger.info(f"Detected referral -> {referral}")

        self._logger.info("Response generated")
        return AgentResponse(
            answer=response.content,
            sources=[doc.metadata.get("source", "unknown") for doc in context],
            referral=referral,
            confidence=1.0 if context else 0.5,
        )

    def _detect_referral(self, response: str) -> str | None:
        """Detect if the response suggests consulting another agent."""
        response_lower = response.lower()
        for agent_name in self.can_refer_to:
            if agent_name.lower() in response_lower:
                # Check for referral patterns
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
        """Main entry point - retrieve context and generate response."""
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

        # Retrieve and generate
        context = await self.retrieve(query)
        response = await self.generate(query, context)

        return {
            **state,
            "context": context,
            "final_answer": response["answer"],
            "referral": response["referral"],
        }

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of this sub-agent."""
        ...
