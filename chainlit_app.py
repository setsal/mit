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
    """Handle incoming user messages with streaming step visualization."""
    thread_id = cl.user_session.get("thread_id")

    # Track active steps so we can close them properly
    active_steps: dict[str, cl.Step] = {}
    final_answer = None

    async for event in stream_query(message.content, thread_id):
        if event.event == "step_start" and event.node and event.content:
            # Create a new Chainlit Step to show this node's activity
            step = cl.Step(name=event.content, type="tool")
            await step.send()
            active_steps[event.node] = step

        elif event.event == "step_end" and event.node:
            # Close the step when the node finishes
            step = active_steps.pop(event.node, None)
            if step:
                step.output = "✅ 完成"
                await step.update()

        elif event.event == "final_answer":
            final_answer = event.content

        elif event.event == "done":
            # Update thread_id in case it was auto-generated
            if event.content:
                cl.user_session.set("thread_id", event.content)

        elif event.event == "error":
            await cl.Message(
                content=f"❌ 錯誤：{event.content}",
            ).send()
            return

    # Close any remaining active steps
    for step in active_steps.values():
        step.output = "✅ 完成"
        await step.update()

    # Send the final answer
    if final_answer:
        await cl.Message(content=final_answer).send()
    else:
        await cl.Message(content="⚠️ 無法產生回答。").send()
