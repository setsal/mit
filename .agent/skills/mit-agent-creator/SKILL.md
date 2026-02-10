---
name: mit-agent-creator
description: Create a new MIT agent from prepared materials. Use when the user wants to add a new agent module to the MIT framework, given a materials folder with knowledge documents organized by sub-agent.
---

# MIT Agent Creator

Generate a complete agent module for the MIT (Multi Intelligence Twin) framework from a prepared `materials/` folder.

## When to Use This Skill

- User wants to add a new agent/module to the MIT framework
- User has prepared knowledge documents in `materials/<agent_name>/<sub_agent_name>/`
- User wants to scaffold agent code from an existing materials folder structure

## Prerequisites

The user must have documents organized in:
```
materials/<agent_name>/
├── <sub_agent_a>/
│   └── *.md / *.txt
└── <sub_agent_b>/
    └── *.md / *.txt
```

## Step-by-Step Process

### Step 1: Scan Materials Folder

Read the `materials/` directory to discover the agent name and sub-agent names:

```
materials/<AGENT_NAME>/
├── <SUB_AGENT_1>/    → becomes a sub-agent
└── <SUB_AGENT_2>/    → becomes another sub-agent
```

The folder names become the module name and sub-agent names. Briefly read the documents inside each sub-folder to understand what each sub-agent should specialize in.

### Step 2: Create Sub-Agent Files

For each sub-folder, create a sub-agent file at:
`src/mit/agents/<agent_name>/<sub_agent_name>.py`

Use this template:

```python
"""<Description> sub-agent for <Agent> module."""

from mit.core.base_agent import BaseSubAgent


class <SubAgentClass>(BaseSubAgent):
    """<What this sub-agent handles>.

    Specializes in:
    - <topic 1 from reading the documents>
    - <topic 2>
    - <topic 3>
    """

    collection_name = "<agent_name>_<sub_agent_name>"  # Convention: agent_subagent
    description = "<One line describing what this sub-agent handles>"
    system_prompt = """You are a <role> expert for the <Agent> module.
Your role is to answer questions about:
- <topic 1>
- <topic 2>
- <topic 3>

When answering:
- <guidance based on the domain>
- If the question would be better answered by another agent, suggest consulting them

Always base your answers on the provided context."""

    can_refer_to = ["<other_sub_agent_name>"]  # List sibling names if cross-referral makes sense

    @property
    def name(self) -> str:
        """Return the agent name."""
        return "<sub_agent_name>"
```

**Key rules:**
- `collection_name` = `<agent_name>_<sub_agent_name>` (underscore joined)
- `description` = concise one-liner (used for sibling awareness and routing)
- `system_prompt` = detailed role instructions derived from reading the actual documents
- `can_refer_to` = list sibling sub-agent names where cross-referral makes sense
- `name` property = matches the sub-agent folder name

### Step 3: Create Agent Coordinator

Create the coordinator at `src/mit/agents/<agent_name>/agent.py`:

```python
"""<Agent> agent - coordinator for <domain>-related queries."""

from langgraph.graph import StateGraph

from mit.core.coordinator import BaseCoordinator
from mit.agents.<agent_name>.<sub_agent_1> import <SubAgent1Class>
from mit.agents.<agent_name>.<sub_agent_2> import <SubAgent2Class>


class <AgentClass>(BaseCoordinator):
    """<Agent> module owner.

    Coordinates between <sub_agent_1> and <sub_agent_2> sub-agents.
    """

    name = "<agent_name>"
    description = "<One line describing what this module handles overall>"

    def __init__(self) -> None:
        """Initialize the <Agent> agent with sub-agents."""
        self.sub_agents = {
            "<sub_agent_1>": <SubAgent1Class>(),
            "<sub_agent_2>": <SubAgent2Class>(),
        }
        super().__init__()

    def build_graph(self) -> StateGraph:
        """Build the workflow graph for <Agent> module."""
        return self.build_default_graph()
```

**Key rules:**
- `name` = matches the materials folder name
- `description` = required, used by the router for query routing decisions
- `sub_agents` dict keys = match the sub-folder names
- Always call `super().__init__()` AFTER setting `self.sub_agents`

### Step 4: Create `__init__.py`

Create `src/mit/agents/<agent_name>/__init__.py`:

```python
from mit.agents.<agent_name>.agent import <AgentClass>
from mit.agents.<agent_name>.<sub_agent_1> import <SubAgent1Class>
from mit.agents.<agent_name>.<sub_agent_2> import <SubAgent2Class>

__all__ = ["<AgentClass>", "<SubAgent1Class>", "<SubAgent2Class>"]
```

### Step 5: Register Agent in Graph

Edit `src/mit/graph.py`:

1. Add import: `from mit.agents.<agent_name> import <AgentClass>`
2. Add to agents dict: `"<agent_name>": <AgentClass>()`

### Step 6: Update Ingestion Script

Edit `scripts/ingest.py`, add entries to `COLLECTION_MAPPING`:

```python
COLLECTION_MAPPING = {
    # ... existing entries ...
    "<agent_name>/<sub_agent_1>": "<agent_name>_<sub_agent_1>",
    "<agent_name>/<sub_agent_2>": "<agent_name>_<sub_agent_2>",
}
```

The mapping key = folder path under `materials/`, the value = `collection_name` used in the sub-agent.

### Step 7: Run Ingestion

```bash
uv run python scripts/ingest.py
```

### Step 8: Test the Agent

```bash
uv run python scripts/test_agent.py <agent_name> "test query about the domain"
```

Or run the full system:
```bash
uv run python -m mit.main
```

## Naming Conventions Summary

| Item | Convention | Example |
|------|-----------|---------|
| Materials folder | `materials/<agent>/` | `materials/database/` |
| Sub-agent folder | `materials/<agent>/<sub>/` | `materials/database/queries/` |
| Agent module | `src/mit/agents/<agent>/` | `src/mit/agents/database/` |
| Sub-agent file | `<sub>.py` | `queries.py` |
| Collection name | `<agent>_<sub>` | `database_queries` |
| Coordinator class | `<Agent>Agent` | `DatabaseAgent` |
| Sub-agent class | `<Sub>SubAgent` | `QueriesSubAgent` |
| Ingestion mapping | `<agent>/<sub>` → `<agent>_<sub>` | `database/queries` → `database_queries` |

## Reference: Existing Agent Examples

- **Network Agent**: `src/mit/agents/network/` with sub-agents `api_ref` and `issues`
- **Auth Agent**: `src/mit/agents/auth/` with sub-agents `oauth` and `errors`

## Important Notes

- The `description` field on both coordinators and sub-agents is **required**
- Sub-agent descriptions enable **sibling awareness** — each sub-agent knows what its siblings handle
- Coordinator descriptions enable **smart routing** — the router uses them to decide which module handles a query
- Read the actual documents in materials to write accurate `system_prompt` and `description` values
- The router can also handle queries directly if they don't match any agent
