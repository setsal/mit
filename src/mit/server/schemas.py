"""Request/Response schemas for the MIT server API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request payload."""

    query: str = Field(..., description="User query to send to the MIT framework")
    thread_id: str | None = Field(
        None, description="Thread ID for conversation continuity. Auto-generated if not provided."
    )


class ChatResponse(BaseModel):
    """Chat response payload."""

    answer: str = Field(..., description="Final answer from the MIT framework")
    thread_id: str = Field(..., description="Thread ID for this conversation")


class StreamEvent(BaseModel):
    """A single streaming event from graph execution.

    Events are emitted during graph processing to communicate
    the current step to the frontend.
    """

    event: str = Field(
        ...,
        description="Event type: step_start, step_end, token, final_answer, error",
    )
    node: str | None = Field(None, description="Graph node name that emitted this event")
    content: str | None = Field(None, description="Event content: step label, token text, or answer")
