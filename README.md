# MIT - Multi Intelligence Twin

A multi-agent framework for expertise where users interact with Module Owner AI-Twins. Each AI-Twin coordinates internal Sub-Agents specialized in different knowledge categories.

## Features

- **Module-Centric Architecture**: Users target specific Module Owners, each with specialized Sub-Agents
- **RAG-Powered Sub-Agents**: Answers derived from vector database built from Text/Markdown files
- **Asynchronous & Stateful**: Full asyncio support with multi-turn conversations
- **Cycle Protection**: Hop limits and agent visit tracking prevent infinite loops

## Quick Start

```bash
# Install dependencies
uv sync

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Ingest knowledge data
uv run python scripts/ingest.py

# Run the application
uv run python -m mit.main
```

## Project Structure

```
src/mit/
├── core/           # Base classes (BaseSubAgent, BaseCoordinator)
├── rag/            # RAG components (embeddings, vectorstore, retriever)
├── agents/         # Agent definitions (one folder per agent)
│   ├── network/    # Network Library agent
│   └── auth/       # Auth agent
└── graph.py        # Main LangGraph orchestration
```

## Configuration

Set the following environment variables in `.env`:

| Variable | Description |
|----------|-------------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | LLM deployment name (gpt-4) |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding deployment name |
| `CHROMADB_PERSIST_DIR` | ChromaDB persistence directory |

