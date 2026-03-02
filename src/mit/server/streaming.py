"""Graph streaming event processor.

Translates LangGraph's raw astream_events into structured StreamEvents
that frontends (FastAPI SSE, Chainlit) can consume to show real-time
step-by-step progress of the multi-agent graph execution.
"""

import uuid
from collections.abc import AsyncGenerator

from langchain_core.messages import HumanMessage

from mit.graph import get_graph
from mit.server.schemas import StreamEvent

# Human-readable labels for graph nodes
NODE_LABELS: dict[str, str] = {
    "route": "🔀 Router 分析查詢中...",
    "direct": "💬 直接回覆中...",
    "classify": "🏷️ 分類查詢類型中...",
    "handle_referral": "🔄 轉介處理中...",
    "synthesize": "💡 彙整回答中...",
}

# Patterns for module/agent nodes that are dynamically named
MODULE_LABEL = "📦 {name} Agent 處理中..."
SUB_AGENT_LABEL = "🔍 {name} 檢索知識庫中..."

# Nodes to skip in streaming output (internal/noisy)
SKIP_NODES = {"__start__", "__end__", ""}


def _get_node_label(node_name: str) -> str | None:
    """Map a graph node name to a human-readable label.

    Returns None if the node should be skipped.
    """
    if node_name in SKIP_NODES:
        return None

    # Check static mapping first
    if node_name in NODE_LABELS:
        return NODE_LABELS[node_name]

    # Capitalize as a fallback for dynamic module/agent names
    return MODULE_LABEL.format(name=node_name.replace("_", " ").title())


async def stream_query(
    query: str,
    thread_id: str | None = None,
) -> AsyncGenerator[StreamEvent, None]:
    """Stream graph execution events for a user query.

    This is the core interface that both FastAPI and Chainlit consume.
    It runs the MIT graph with astream_events and yields structured
    StreamEvent objects representing each meaningful step.

    Args:
        query: User query string
        thread_id: Optional thread ID for conversation continuity

    Yields:
        StreamEvent objects representing graph execution steps
    """
    graph = get_graph()

    if thread_id is None:
        thread_id = str(uuid.uuid4())

    input_state = {
        "messages": [HumanMessage(content=query)],
    }
    config = {"configurable": {"thread_id": thread_id}}

    # Track which nodes we've already emitted step_start for
    active_nodes: set[str] = set()
    final_answer: str | None = None

    try:
        async for event in graph.astream_events(
            input_state, config=config, version="v2"
        ):
            kind = event.get("event", "")
            name = event.get("name", "")
            tags = event.get("tags", [])

            # --- Node lifecycle events ---
            if kind == "on_chain_start" and name not in active_nodes:
                label = _get_node_label(name)
                if label:
                    active_nodes.add(name)
                    yield StreamEvent(
                        event="step_start",
                        node=name,
                        content=label,
                    )

            elif kind == "on_chain_end" and name in active_nodes:
                active_nodes.discard(name)

                # Capture final_answer from the last state output
                output = event.get("data", {}).get("output", {})
                if isinstance(output, dict) and output.get("final_answer"):
                    final_answer = output["final_answer"]

                yield StreamEvent(
                    event="step_end",
                    node=name,
                    content=None,
                )

            # --- LLM token streaming ---
            elif kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    content = chunk.content
                    # Handle Gemini list format
                    if isinstance(content, list):
                        parts = []
                        for block in content:
                            if isinstance(block, dict) and "text" in block:
                                parts.append(block["text"])
                            elif isinstance(block, str):
                                parts.append(block)
                        content = "".join(parts)

                    if content:
                        yield StreamEvent(
                            event="token",
                            node=None,
                            content=content,
                        )

    except Exception as e:
        yield StreamEvent(
            event="error",
            node=None,
            content=str(e),
        )
        return

    # Emit the final answer
    yield StreamEvent(
        event="final_answer",
        node=None,
        content=final_answer or "No answer generated.",
    )

    # Signal completion with thread_id so client can continue conversation
    yield StreamEvent(
        event="done",
        node=None,
        content=thread_id,
    )
