"""Base coordinator class for module owners."""

from abc import ABC, abstractmethod
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph

from mit.config import get_config
from mit.core.base_agent import BaseSubAgent
from mit.llm import extract_text, get_chat_llm
from mit.logging import get_logger
from mit.state import AgentState


class BaseCoordinator(ABC):
    """Base coordinator that routes queries to sub-agents.

    Each module owner extends this class and defines:
    - name: Module identifier
    - sub_agents: Dictionary of sub-agent instances
    - build_graph(): Custom workflow state machine
    """

    name: str
    description: str  # Brief description of what this module handles
    sub_agents: dict[str, BaseSubAgent]

    def __init__(self) -> None:
        """Initialize the coordinator with LLM for classification."""
        self.llm = get_chat_llm(temperature=0.0)
        self._classifier_prompt = self._build_classifier_prompt()
        self._synthesize_prompt = self._build_synthesize_prompt()
        self._graph = None
        self._logger = get_logger(f"coordinator.{self.name}")

    def _build_classifier_prompt(self) -> ChatPromptTemplate:
        """Build prompt for query classification."""
        agent_descriptions = "\n".join(
            f"- {name}: {agent.system_prompt[:100]}..."
            for name, agent in self.sub_agents.items()
        )
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are a query classifier for the {self.name} module.
Based on the user's query, determine which sub-agent should handle it.

Available sub-agents:
{agent_descriptions}

Respond with ONLY the sub-agent name, nothing else.""",
                ),
                ("human", "{query}"),
            ]
        )

    def _build_synthesize_prompt(self) -> ChatPromptTemplate:
        """Build prompt for response synthesis."""
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are the {self.name} module coordinator.
Your role is to synthesize the information gathered from sub-agents and provide a final, coherent response to the user.

Review the sub-agent's response and:
1. Ensure the answer is complete and addresses the user's question
2. Add any necessary context or clarification
3. Format the response clearly for the user

If the sub-agent couldn't fully answer, acknowledge what was found and what remains unknown.""",
                ),
                ("human", "User question: {query}\n\nSub-agent response:\n{sub_agent_response}\n\nPlease provide a synthesized final answer:"),
            ]
        )

    async def classify_query(self, query: str) -> str:
        """Classify the query to determine which sub-agent should handle it."""
        self._logger.debug(f"Classifying query: {query[:100]}...")
        chain = self._classifier_prompt | self.llm
        response = await chain.ainvoke({"query": query})
        agent_name = extract_text(response.content).strip().lower()

        # Validate agent name
        if agent_name in self.sub_agents:
            self._logger.info(f"Classified -> {agent_name}")
            return agent_name

        # Default to first agent if classification fails
        default_agent = next(iter(self.sub_agents.keys()))
        self._logger.warning(f"Unknown agent '{agent_name}', defaulting to: {default_agent}")
        return default_agent

    async def classify_node(self, state: AgentState) -> AgentState:
        """Node that classifies and routes to appropriate sub-agent."""
        messages = state.get("messages", [])
        query = ""
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                query = msg.content
                break
            elif isinstance(msg, tuple) and msg[0] == "human":
                query = msg[1]
                break

        sub_agent_name = await self.classify_query(query)

        return {
            **state,
            "current_sub_agent": sub_agent_name,
            "hop_count": state.get("hop_count", 0) + 1,
            "visited_agents": state.get("visited_agents", []) + [sub_agent_name],
        }

    def route_to_sub_agent(self, state: AgentState) -> str:
        """Route to the appropriate sub-agent based on classification."""
        return state.get("current_sub_agent", next(iter(self.sub_agents.keys())))

    async def handle_referral(self, state: AgentState) -> AgentState:
        """Handle referral to another sub-agent."""
        referral = state.get("referral")
        if referral and referral in self.sub_agents:
            self._logger.info(f"Handling referral -> {referral}")
            return {
                **state,
                "current_sub_agent": referral,
                "hop_count": state.get("hop_count", 0) + 1,
                "visited_agents": state.get("visited_agents", []) + [referral],
                "referral": None,  # Clear referral
            }
        return state

    def should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """Determine if we should continue processing or end."""
        # Check hop limit
        hop_count = state.get("hop_count", 0)
        max_hops = state.get("max_hops", 10)
        if hop_count >= max_hops:
            self._logger.warning(f"Hop limit reached ({hop_count}/{max_hops}), ending")
            return "end"

        # Check for referral
        referral = state.get("referral")
        if referral and referral in self.sub_agents:
            # Check if we've already visited this agent (cycle detection)
            if referral in state.get("visited_agents", []):
                self._logger.warning(f"Cycle detected: {referral} already visited, ending")
                return "end"
            return "continue"

        return "end"

    async def synthesize_node(self, state: AgentState) -> AgentState:
        """Synthesize sub-agent responses into a final answer."""
        self._logger.debug("Synthesizing final response...")
        
        # Get the original query
        messages = state.get("messages", [])
        query = ""
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                query = msg.content
                break
            elif isinstance(msg, tuple) and msg[0] == "human":
                query = msg[1]
                break
        
        # Get sub-agent response
        sub_agent_response = state.get("final_answer", "")
        
        if not sub_agent_response:
            return state
        
        # Synthesize the response
        chain = self._synthesize_prompt | self.llm
        response = await chain.ainvoke({
            "query": query,
            "sub_agent_response": sub_agent_response,
        })
        
        text = extract_text(response.content)
        
        self._logger.info("Response synthesized")
        
        # Add the AI response to messages for memory
        from langchain_core.messages import AIMessage
        new_messages = list(state.get("messages", [])) + [AIMessage(content=text)]
        
        return {
            **state,
            "messages": new_messages,
            "final_answer": text,
        }

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Build the custom workflow graph for this module.

        Override this method to define custom routing logic.
        """
        ...

    def get_graph(self) -> StateGraph:
        """Get or build the compiled graph."""
        if self._graph is None:
            self._graph = self.build_graph()
        return self._graph

    def build_default_graph(self) -> StateGraph:
        """Build a default graph with standard routing.

        Subclasses can use this as a starting point.
        """
        builder = StateGraph(AgentState)

        # Add classifier node
        builder.add_node("classify", self.classify_node)

        # Add sub-agent nodes
        for name, agent in self.sub_agents.items():
            builder.add_node(name, agent.invoke)

        # Add referral handler
        builder.add_node("handle_referral", self.handle_referral)
        
        # Add synthesize node - coordinator summarizes before returning
        builder.add_node("synthesize", self.synthesize_node)

        # Define edges
        builder.add_edge(START, "classify")
        builder.add_conditional_edges(
            "classify",
            self.route_to_sub_agent,
            {name: name for name in self.sub_agents.keys()},
        )

        # Each sub-agent can either continue via referral or go to synthesize
        for name in self.sub_agents.keys():
            builder.add_conditional_edges(
                name,
                self.should_continue,
                {"continue": "handle_referral", "end": "synthesize"},
            )

        # Referral handler routes back to sub-agent
        builder.add_conditional_edges(
            "handle_referral",
            self.route_to_sub_agent,
            {name: name for name in self.sub_agents.keys()},
        )
        
        # Synthesize node ends the graph
        builder.add_edge("synthesize", END)

        return builder
