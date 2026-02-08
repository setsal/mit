# MIT Framework - System Overview

## Presentation for Manager

---

## What is MIT?

**Multi Intelligence Twin** - A framework for building AI-powered knowledge assistants.

Each **Agent** (module owner) has specialized **Sub-agents** that answer domain-specific questions using RAG.

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Query                          │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   Module Router                         │
│            "Which module handles this?"                 │
└─────────────────────────────────────────────────────────┘
                           ↓
         ┌─────────────────┴─────────────────┐
         ↓                                   ↓
┌─────────────────┐                ┌─────────────────┐
│ Network Agent   │                │   Auth Agent    │
│  (Coordinator)  │                │  (Coordinator)  │
└─────────────────┘                └─────────────────┘
    ↓         ↓                        ↓         ↓
┌───────┐ ┌───────┐                ┌───────┐ ┌───────┐
│API_Ref│ │Issues │                │ OAuth │ │Errors │
│  RAG  │ │  RAG  │                │  RAG  │ │  RAG  │
└───────┘ └───────┘                └───────┘ └───────┘
```

---

## Key Features (Current)

| Feature | Description |
|---------|-------------|
| **Multi-Agent** | Multiple domain experts with specialized knowledge |
| **RAG-Powered** | Answers from internal documents (MD/TXT files) |
| **Cross-Referral** | Sub-agents can refer to each other |
| **Cycle Protection** | Prevents infinite loops (max 10 hops) |
| **Stateful** | Multi-turn conversations with memory |
| **Async** | Built on asyncio for performance |

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Orchestration** | LangGraph (state machine) |
| **LLM** | Azure OpenAI (gpt-4) |
| **Embeddings** | Azure OpenAI (text-embedding-ada-002) |
| **Vector Store** | ChromaDB (local) |
| **Language** | Python 3.10+ |

---

## Current Phase: Core Framework ✅

- ✅ Base classes for agents and coordinators
- ✅ RAG pipeline (ingest → embed → store → retrieve)
- ✅ Query routing and classification
- ✅ Cross-agent referral mechanism
- ✅ CLI interface for testing

---

## Future Roadmap

### Phase 2: API Interfaces

| Interface | Description |
|-----------|-------------|
| **HTTP/REST** | Query agents via REST API endpoints |
| **MCP** | Model Context Protocol for IDE integration |
| **WebSocket** | Real-time streaming responses |

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│   HTTP   │  │   MCP    │  │WebSocket │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     └─────────────┼─────────────┘
                   ↓
          ┌───────────────┐
          │ MIT Framework │
          └───────────────┘
```

### Phase 3: Scale & Production

- Production vector store (Pinecone/Weaviate)
- Authentication & authorization
- Monitoring & observability
- Multi-tenant support

---

## Business Value

1. **Knowledge Centralization** - Experts' knowledge accessible 24/7
2. **Reduced Onboarding** - New team members get instant answers
3. **Scalable Expertise** - One agent serves many users
4. **Extensible** - Easy to add new knowledge domains

---

## Demo

```bash
# Example query
You: How do I fix a 504 error in the Network Library?

# System routes to: Network Agent → Issues Sub-agent
# Issues agent retrieves from RAG: common_errors.md
# Returns: Step-by-step troubleshooting guide
```

---

## Summary

| Aspect | Status |
|--------|--------|
| Core Framework | ✅ Complete |
| PoC Agents | ✅ Network, Auth |
| Next Step | HTTP/MCP Interface |

**Ready for Phase 2 development.**
