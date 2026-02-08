#!/usr/bin/env python
"""Simple test script to query specific agents.

Usage:
    # Query the network agent
    uv run python scripts/test_agent.py network "How do I fix a 504 error?"

    # Query the auth agent
    uv run python scripts/test_agent.py auth "What is OAuth 2.0?"

    # Enable debug logging
    MIT_LOG_LEVEL=DEBUG uv run python scripts/test_agent.py network "test query"
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

load_dotenv()

from mit.config import get_config
from mit.logging import setup_logging, get_logger
from mit.state import AgentState

logger = get_logger("test")


async def test_agent(agent_name: str, query: str) -> None:
    """Test a specific agent with a query.

    Args:
        agent_name: Agent to test (network, auth)
        query: Query to send
    """
    # Import agents dynamically to avoid issues before env is loaded
    from mit.agents.network import NetworkAgent
    from mit.agents.auth import AuthAgent

    agents = {
        "network": NetworkAgent,
        "auth": AuthAgent,
    }

    if agent_name not in agents:
        print(f"Unknown agent: {agent_name}")
        print(f"Available agents: {', '.join(agents.keys())}")
        sys.exit(1)

    # Create agent
    agent_class = agents[agent_name]
    agent = agent_class()

    print(f"\n{'='*60}")
    print(f"Testing Agent: {agent_name}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")

    # Build initial state
    config = get_config()
    initial_state: AgentState = {
        "messages": [("human", query)],
        "thread_id": "test-thread",
        "current_module": agent_name,
        "current_sub_agent": "",
        "hop_count": 0,
        "max_hops": config.agent.max_hops,
        "visited_agents": [],
        "context": [],
        "final_answer": None,
        "referral": None,
    }

    # Compile and run the agent's graph
    graph = agent.get_graph().compile()
    result = await graph.ainvoke(initial_state)

    # Print results
    print(f"\n{'='*60}")
    print("RESULT")
    print(f"{'='*60}")
    print(f"\nSub-agent used: {result.get('current_sub_agent', 'unknown')}")
    print(f"Hop count: {result.get('hop_count', 0)}")
    print(f"Visited: {result.get('visited_agents', [])}")

    if result.get("context"):
        print(f"\nSources ({len(result['context'])} documents):")
        for doc in result["context"]:
            source = doc.metadata.get("source", "unknown")
            print(f"  - {source}")

    print(f"\n--- Answer ---\n")
    print(result.get("final_answer", "No answer"))

    if result.get("referral"):
        print(f"\n[Referral suggested: {result['referral']}]")


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    agent_name = sys.argv[1].lower()
    query = " ".join(sys.argv[2:])

    # Setup logging
    config = get_config()
    setup_logging(config.agent.log_level)

    # Run test
    asyncio.run(test_agent(agent_name, query))


if __name__ == "__main__":
    main()
