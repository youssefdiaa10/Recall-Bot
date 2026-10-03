import asyncio
import uuid

import streamlit as st
from langchain.messages import AIMessageChunk

from langchain_core.runnables import RunnableConfig

from src.agent import build_agent, list_threads

NEW_CONVERSATION = "+ New conversation"


st.set_page_config(page_title="LangChain Chatbot", page_icon="💬")
st.title("💬 LangChain chatbot")


@st.cache_resource
def get_agent():
    #? Streamlit reruns this script after interactions. Cache the agent so its
    #? SQLite-backed checkpointer and model setup are reused across reruns.
    #? build_agent() is async, so run it to completion once here.
    return asyncio.run(build_agent())


agent = get_agent()

with st.sidebar:
    existing_threads = list_threads()
    options = existing_threads + [NEW_CONVERSATION]
    default_index = options.index("default") if "default" in options else 0
    choice = st.selectbox("Conversation", options, index=default_index)

    if choice == NEW_CONVERSATION:
        thread_id = st.text_input("Name this conversation", value="").strip()
        if not thread_id:
            #? Give a blank name a fresh ID instead of resuming "default".
            thread_id = f"chat-{uuid.uuid4().hex[:6]}"
    else:
        thread_id = choice

config: RunnableConfig = {"configurable": {"thread_id": thread_id}}


def render_history(config: RunnableConfig) -> None:
    """Redraw every past turn for this thread, read straight from the
    checkpointer -- the same database the CLI version reads and writes."""
    state = agent.get_state(config)
    messages = state.values.get("messages", []) if state.values else []

    i = 0
    while i < len(messages):
        msg = messages[i]

        if (
            msg.type == "human"
            and isinstance(msg.content, str)
            and msg.content.startswith("[Attached file:")
        ):
            name = msg.content.split("]", 1)[0].removeprefix("[Attached file: ")
            prompt_text = ""
            if i + 1 < len(messages) and messages[i + 1].type == "human":
                prompt_text = messages[i + 1].content
                i += 1  #? The next human message is the prompt shown with the attachment.
            with st.chat_message("user"):
                st.caption(f"📎 {name}")
                if prompt_text:
                    st.write(prompt_text)

        elif msg.type == "human" and msg.content:
            with st.chat_message("user"):
                st.write(msg.content)

        elif msg.type == "ai":
            text = "".join(
                block.get("text", "") for block in msg.content_blocks if block["type"] == "text"
            )
            if text:
                with st.chat_message("assistant"):
                    st.write(text)

        i += 1


def token_stream(messages: list[dict], config: RunnableConfig):
    """Yield plain-text chunks as the model generates them, for
    st.write_stream. Tool-call chunks are announced inline too."""
    for token, metadata in agent.stream(
        {"messages": messages},
        config,
        stream_mode="messages",
    ):
        if not isinstance(token, AIMessageChunk):
            continue
        for block in token.content_blocks:
            if block["type"] == "text":
                yield block["text"]
            elif block["type"] == "tool_call":
                yield f"\n\n*calling tool: {block.get('name')}*\n\n"


render_history(config)

if prompt := st.chat_input("Message the bot..."):
    turn_messages = []

    turn_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        st.write_stream(token_stream(turn_messages, config))

    #? The checkpointer saved the turn during agent.stream(). The rerun below
    #? redraws the conversation from that saved state.
    st.rerun()
