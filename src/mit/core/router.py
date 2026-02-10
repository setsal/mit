"""Module router - entry point for routing to module owners."""

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph

from mit.core.coordinator import BaseCoordinator
from mit.llm import extract_text, get_chat_llm
from mit.logging import get_logger
from mit.state import AgentState

logger = get_logger("router")


class ModuleRouter:
    """Routes user queries to the appropriate module owner (agent).

    The router can either:
    1. Route to a specialized module agent
    2. Respond directly for general/conversational queries
    """

    def __init__(self, agents: dict[str, BaseCoordinator]) -> None:
        """Initialize the router with available agents.

        Args:
            agents: Dictionary mapping module names to coordinator instances
        """
        self.agents = agents
        self.llm = get_chat_llm(temperature=0.0)
        self._router_prompt = self._build_router_prompt()
        self._direct_prompt = self._build_direct_prompt()

    def _build_router_prompt(self) -> ChatPromptTemplate:
        """Build prompt for module routing."""
        module_descriptions = "\n".join(
            f"- {name}: {agent.description}"
            for name, agent in self.agents.items()
        )
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are a query router. Determine which module should handle the user's query based on the module descriptions below.

Available modules:
{module_descriptions}

Rules:
- If the query clearly matches a module's expertise, respond with ONLY the module name.
- If the query is general conversation (greetings, follow-ups, asking about previous questions, etc.), respond with ONLY the word "direct".
- If the query does not match any module, respond with ONLY the word "direct".

Respond with ONLY one word: a module name or "direct".""",
                ),
                ("human", "{query}"),
            ]
        )

    def _build_direct_prompt(self) -> ChatPromptTemplate:
        """Build prompt for direct responses (non-module queries)."""
        module_descriptions = "\n".join(
            f"- {name}: {agent.description}"
            for name, agent in self.agents.items()
        )
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are the MIT (Multi Intelligence Twin) assistant. You coordinate specialized module agents.

Available modules:
{module_descriptions}

When answering:
- For general questions or greetings, respond naturally.
- For conversation history questions (e.g., "what was my previous question"), use the conversation messages to answer.
- If the user asks something that could be handled by a module, suggest which module could help.
- Keep responses concise and helpful.""",
                ),
                ("human", "{messages_context}\n\nCurrent question: {query}"),
            ]
        )

    async def route_query(self, query: str) -> str:
        """Route the query to a module or decide to respond directly."""
        logger.debug(f"Routing query: {query[:100]}...")
        chain = self._router_prompt | self.llm
        response = await chain.ainvoke({"query": query})
        decision = extract_text(response.content).strip().lower()

        if decision in self.agents:
            logger.info(f"Routed to module: {decision}")
            return decision

        if decision == "direct":
            logger.info("Handling directly (no module needed)")
            return "direct"

        # Default: try direct response for unknown decisions
        logger.warning(f"Unknown routing '{decision}', handling directly")
        return "direct"

    async def direct_response_node(self, state: AgentState) -> AgentState:
        """Handle queries directly without routing to a module."""
        logger.debug("Generating direct response...")

        messages = state.get("messages", [])
        query = ""
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                query = msg.content
                break
            elif isinstance(msg, tuple) and msg[0] == "human":
                query = msg[1]
                break

        # Build conversation context from message history
        messages_context = ""
        if len(messages) > 1:
            history_lines = []
            for msg in messages[:-1]:  # Exclude current message
                if hasattr(msg, "type"):
                    role = "User" if msg.type == "human" else "Assistant"
                    history_lines.append(f"{role}: {msg.content}")
                elif isinstance(msg, tuple):
                    role = "User" if msg[0] == "human" else "Assistant"
                    history_lines.append(f"{role}: {msg[1]}")
            if history_lines:
                messages_context = "Previous conversation:\n" + "\n".join(history_lines[-10:])  # Last 10 messages

        chain = self._direct_prompt | self.llm
        response = await chain.ainvoke({
            "messages_context": messages_context or "No previous conversation.",
            "query": query,
        })

        response_text = extract_text(response.content)

        # Add AI response to messages for memory
        new_messages = list(messages) + [AIMessage(content=response_text)]

        return {
            **state,
            "messages": new_messages,
            "final_answer": response_text,
        }

    async def router_node(self, state: AgentState) -> AgentState:
        """Node that routes to the appropriate module or handles directly."""
        from mit.config import get_config
        config = get_config()

        messages = state.get("messages", [])
        query = ""
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                query = msg.content
                break
            elif isinstance(msg, tuple) and msg[0] == "human":
                query = msg[1]
                break

        module_name = await self.route_query(query)

        # Initialize all state fields
        return {
            **state,
            "current_module": module_name,
            "current_sub_agent": state.get("current_sub_agent", ""),
            "hop_count": 0,
            "max_hops": state.get("max_hops", config.agent.max_hops),
            "visited_agents": [],
            "context": state.get("context", []),
            "final_answer": None,
            "referral": None,
            "thread_id": state.get("thread_id", ""),
        }

    def route_to_module(self, state: AgentState) -> str:
        """Determine which module to route to, or 'direct'."""
        return state.get("current_module", "direct")

    def build_graph(self) -> StateGraph:
        """Build the main routing graph."""
        builder = StateGraph(AgentState)

        # Add router node
        builder.add_node("route", self.router_node)

        # Add direct response node
        builder.add_node("direct", self.direct_response_node)

        # Add each module's graph as a node
        for name, agent in self.agents.items():
            module_graph = agent.get_graph().compile()
            builder.add_node(name, module_graph)

        # Define edges
        builder.add_edge(START, "route")

        # Route to module or direct
        route_map = {name: name for name in self.agents.keys()}
        route_map["direct"] = "direct"
        builder.add_conditional_edges("route", self.route_to_module, route_map)

        # All paths end at END
        builder.add_edge("direct", END)
        for name in self.agents.keys():
            builder.add_edge(name, END)

        return builder
