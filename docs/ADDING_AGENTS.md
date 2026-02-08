# Adding a New Agent to MIT Framework

## Quick Start

To add a new agent, create 3 files in a new folder under `src/mit/agents/`.

---

## Step 1: Create Agent Folder

```
src/mit/agents/
└── your_agent/           # e.g., "database", "payment"
    ├── __init__.py
    ├── agent.py          # Coordinator
    ├── sub_agent_a.py    # First sub-agent
    └── sub_agent_b.py    # Second sub-agent
```

---

## Step 2: Create Sub-Agents

Each sub-agent extends `BaseSubAgent`:

```python
# src/mit/agents/your_agent/queries.py
from mit.core.base_agent import BaseSubAgent

class QueriesSubAgent(BaseSubAgent):
    collection_name = "database_queries"  # ChromaDB collection
    system_prompt = """You are a database query expert.
    Answer questions about SQL queries and optimization."""
    can_refer_to = ["schema"]  # Optional: agents this can refer to
    
    @property
    def name(self) -> str:
        return "queries"
```

---

## Step 3: Create Agent Coordinator

The coordinator manages sub-agents:

```python
# src/mit/agents/your_agent/agent.py
from langgraph.graph import StateGraph
from mit.core.coordinator import BaseCoordinator
from mit.agents.your_agent.queries import QueriesSubAgent
from mit.agents.your_agent.schema import SchemaSubAgent

class DatabaseAgent(BaseCoordinator):
    name = "database"
    
    def __init__(self):
        self.sub_agents = {
            "queries": QueriesSubAgent(),
            "schema": SchemaSubAgent(),
        }
        super().__init__()
    
    def build_graph(self) -> StateGraph:
        return self.build_default_graph()  # Use default routing
```

---

## Step 4: Create `__init__.py`

```python
# src/mit/agents/your_agent/__init__.py
from mit.agents.your_agent.agent import DatabaseAgent
from mit.agents.your_agent.queries import QueriesSubAgent
from mit.agents.your_agent.schema import SchemaSubAgent

__all__ = ["DatabaseAgent", "QueriesSubAgent", "SchemaSubAgent"]
```

---

## Step 5: Register in Main Graph

Edit `src/mit/graph.py`:

```python
from mit.agents.your_agent import DatabaseAgent

def create_graph(...):
    agents = {
        "network": NetworkAgent(),
        "auth": AuthAgent(),
        "database": DatabaseAgent(),  # Add here
    }
```

---

## Step 6: Add Knowledge Data

1. Create data folder:
   ```
   data/your_agent/
   ├── queries/     # For QueriesSubAgent
   │   └── *.md
   └── schema/      # For SchemaSubAgent
       └── *.md
   ```

2. Update `scripts/ingest.py`:
   ```python
   COLLECTION_MAPPING = {
       # existing...
       "your_agent/queries": "database_queries",
       "your_agent/schema": "database_schema",
   }
   ```

3. Run ingestion:
   ```bash
   uv run python scripts/ingest.py
   ```

---

## Summary Checklist

- [ ] Create folder `src/mit/agents/your_agent/`
- [ ] Create sub-agent classes extending `BaseSubAgent`
- [ ] Create coordinator class extending `BaseCoordinator`
- [ ] Create `__init__.py` with exports
- [ ] Register agent in `graph.py`
- [ ] Add knowledge files to `data/your_agent/`
- [ ] Update `scripts/ingest.py` collection mapping
- [ ] Run `uv run python scripts/ingest.py`
