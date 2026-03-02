"""FastAPI application for the MIT framework.

Provides REST API and SSE streaming endpoints for interacting
with the MIT multi-agent system.
"""

import uuid

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from mit.config import get_config
from mit.graph import get_graph
from mit.logging import setup_logging
from mit.main import run_query
from mit.server.schemas import ChatRequest, ChatResponse, StreamEvent
from mit.server.streaming import stream_query

# Initialize logging
config = get_config()
setup_logging(config.agent.log_level)

app = FastAPI(
    title="MIT - Multi Intelligence Twin",
    description="Multi-agent framework API for expertise-based Q&A",
    version="0.1.0",
)

# CORS — allow all origins for demo purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a query and receive the final answer.

    Non-streaming endpoint. Waits for the full graph execution
    to complete before returning the response.
    """
    thread_id = request.thread_id or str(uuid.uuid4())
    answer = await run_query(request.query, thread_id)
    return ChatResponse(answer=answer, thread_id=thread_id)


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Send a query and receive Server-Sent Events (SSE) for each step.

    Streams real-time graph execution events including:
    - step_start/step_end: when a graph node begins/finishes
    - token: LLM streaming tokens
    - final_answer: the complete answer
    - done: completion signal with thread_id
    """
    thread_id = request.thread_id or str(uuid.uuid4())

    async def event_generator():
        async for event in stream_query(request.query, thread_id):
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/graph")
async def get_graph_visualization():
    """Get the Mermaid diagram of the current graph structure.

    Returns the graph topology as a Mermaid diagram string,
    which can be rendered in any Mermaid-compatible viewer.
    """
    graph = get_graph()
    mermaid = graph.get_graph().draw_mermaid()
    return {"mermaid": mermaid}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "MIT"}
