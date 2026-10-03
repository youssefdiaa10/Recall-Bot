"""Agent setup: persistent memory and the agent itself.

The Streamlit interface in app.py and the command-line interface in chatbot.py
both use this agent setup and its SQLite checkpoint database, so they can
resume the same conversation when given the same thread ID.
"""

import os
import sqlite3

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver

from src.tools import calculator

load_dotenv()  #? Load API credentials from the project .env file.


async def build_agent(db_path: str = "chat_history.db"):
    """Create the agent, backed by a persistent SQLite checkpointer.

    The coroutine initializes the SQLite checkpointer and constructs the
    model-backed agent. Call it once per process and reuse the returned agent.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    checkpointer.setup()  #? Create the checkpoint tables if they do not exist.

    LLM = ChatGroq(model="openai/gpt-oss-120b")

    return create_agent(
        model=LLM,
        system_prompt="You are a friendly, concise assistant.",
        #? The current agent exposes the calculator tool from tools.py.
        tools=[calculator],
        checkpointer=checkpointer,
    )


def list_threads(db_path: str = "chat_history.db") -> list[str]:
    """Return every thread_id that has at least one saved checkpoint.

    SqliteSaver stores every checkpoint as a row in a 'checkpoints' table
    keyed by (thread_id, checkpoint_ns, checkpoint_id). There's no built-in
    "list all conversations" call on the checkpointer itself, so this reads
    the table directly -- a distinct thread_id is a distinct conversation.
    """
    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id"
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []  #? No conversations have been saved yet.
    finally:
        conn.close()

    return [row[0] for row in rows]
