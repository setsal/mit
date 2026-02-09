"""Main entry point for the MIT framework."""

import asyncio
import uuid

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from mit.config import get_config
from mit.graph import get_graph
from mit.logging import setup_logging
from mit.state import AgentState


async def run_query(query: str, thread_id: str | None = None) -> str:
    """Run a query through the MIT framework.

    Args:
        query: User query
        thread_id: Optional thread ID for conversation continuity

    Returns:
        Agent response
    """
    from langchain_core.messages import HumanMessage
    
    graph = get_graph()
    config = get_config()

    if thread_id is None:
        thread_id = str(uuid.uuid4())

    # Only pass the new message - the checkpointer handles state persistence
    # The graph will merge this with existing state via the add_messages reducer
    input_state = {
        "messages": [HumanMessage(content=query)],
    }

    result = await graph.ainvoke(
        input_state,
        config={"configurable": {"thread_id": thread_id}},
    )

    return result.get("final_answer", "No answer generated.")


async def interactive_session():
    """Run an interactive session with the MIT framework."""
    print("=" * 60)
    print("MIT - Multi Intelligence Twin")
    print("=" * 60)
    print("Available modules: network, auth")
    print("Type 'quit' or 'exit' to end the session.")
    print("Type 'new' to start a new conversation thread.")
    print("=" * 60)

    thread_id = str(uuid.uuid4())
    print(f"\nThread ID: {thread_id}\n")

    while True:
        try:
            query = input("You: ").strip()

            if not query:
                continue

            if query.lower() in ("quit", "exit"):
                print("Goodbye!")
                break

            if query.lower() == "new":
                thread_id = str(uuid.uuid4())
                print(f"\nNew thread started: {thread_id}\n")
                continue

            print("\nProcessing...")
            response = await run_query(query, thread_id)
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


def main():
    """Main entry point."""
    # Initialize logging
    config = get_config()
    setup_logging(config.agent.log_level)

    asyncio.run(interactive_session())


if __name__ == "__main__":
    main()
