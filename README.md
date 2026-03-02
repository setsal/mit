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

# Run the application (CLI)
uv run python -m mit.main
```

## Demo Interface (Chainlit + FastAPI)

```bash
# Install server dependencies
uv sync --extra server

# Option 1: Chainlit Chat UI (port 8080)
uv run chainlit run chainlit_app.py --port 8080

# Option 2: FastAPI REST API (port 8000)
uv run uvicorn mit.server.app:app --reload --port 8000
```

- **Chainlit**: Open `http://localhost:8080` for a Chat UI with real-time multi-agent step visualization
- **FastAPI**: Open `http://localhost:8000/docs` for Swagger UI
  - `POST /chat` — Standard Q&A
  - `POST /chat/stream` — SSE streaming (with step events)
  - `GET /graph` — Get graph structure (Mermaid format)

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

