"""Chainlit Chat UI for the MIT framework.

Provides a web-based chat interface with real-time step visualization
showing the multi-agent graph execution flow.

Run with:
    chainlit run chainlit_app.py --port 8080
"""

import uuid

from dotenv import load_dotenv

load_dotenv()

import chainlit as cl

from mit.config import get_config
from mit.logging import setup_logging
from mit.server.streaming import stream_query

# Initialize logging
config = get_config()
setup_logging(config.agent.log_level)


@cl.on_chat_start
async def on_chat_start():
    """Initialize a new chat session with a unique thread ID."""
    thread_id = str(uuid.uuid4())
    cl.user_session.set("thread_id", thread_id)

    await cl.Message(
        content=(
            "👋 歡迎使用 **MIT - Multi Intelligence Twin**！\n\n"
            "我可以協助你回答關於各模組的專業問題。\n"
            "直接輸入你的問題即可開始。"
        ),
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming user messages with streaming step visualization.

    Uses a single updating message to show live processing status,
    then replaces it with a collapsible step summary + final answer.
    This avoids cl.Step which always renders below message content.
    """
    thread_id = cl.user_session.get("thread_id")

    # Single response message — updated in real-time during processing
    response_msg = cl.Message(content="⏳ 處理中...")
    await response_msg.send()

    # Track step state for live status display
    active_steps: dict[str, str] = {}  # node -> label
    completed_steps: list[str] = []
    final_answer = None

    def _build_live_status() -> str:
        """Build a live status string showing completed and active steps."""
        lines = []
        for label in completed_steps:
            lines.append(f"✅ ~~{label}~~")
        for label in active_steps.values():
            lines.append(f"⏳ {label}")
        return "\n".join(lines) if lines else "⏳ 處理中..."

    async for event in stream_query(message.content, thread_id):
        if event.event == "step_start" and event.node and event.content:
            active_steps[event.node] = event.content
            response_msg.content = _build_live_status()
            await response_msg.update()

        elif event.event == "step_end" and event.node:
            label = active_steps.pop(event.node, None)
            if label:
                completed_steps.append(label)
            response_msg.content = _build_live_status()
            await response_msg.update()

        elif event.event == "final_answer":
            final_answer = event.content

        elif event.event == "done":
            if event.content:
                cl.user_session.set("thread_id", event.content)

        elif event.event == "error":
            response_msg.content = f"❌ 錯誤：{event.content}"
            await response_msg.update()
            return

    # Build the final message: collapsible step summary on top, answer below
    step_lines = "\n".join(f"- ✅ {label}" for label in completed_steps)
    steps_section = (
        f"<details>\n<summary>🔍 處理步驟 ({len(completed_steps)} 步)</summary>\n\n"
        f"{step_lines}\n\n</details>\n\n"
        if completed_steps
        else ""
    )

    answer = final_answer or "⚠️ 無法產生回答。"
    response_msg.content = f"{steps_section}{answer}"
    await response_msg.update()
