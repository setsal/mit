"""State definitions for the MIT framework."""

from typing import Annotated, TypedDict

from langchain_core.documents import Document
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State shared across all agents in the graph."""

    # Conversation messages (accumulates via reducer)
    messages: Annotated[list, add_messages]

    # Thread ID for multi-turn conversation isolation
    thread_id: str

    # Current module being queried (e.g., "network", "auth")
    current_module: str

    # Current sub-agent being invoked
    current_sub_agent: str

    # Hop tracking for cycle prevention
    hop_count: int
    max_hops: int

    # Track visited agents to detect cycles
    visited_agents: list[str]

    # Retrieved context documents
    context: list[Document]

    # Final answer to return to user
    final_answer: str | None

    # Referral to another sub-agent (if any)
    referral: str | None


class AgentResponse(TypedDict):
    """Response from a sub-agent."""

    answer: str
    sources: list[str]
    referral: str | None  # Suggested next agent to consult
    confidence: float
