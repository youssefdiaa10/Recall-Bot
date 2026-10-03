# Recall Bot

Recall Bot is a Python chat assistant with a Streamlit web interface and a command-line interface. Both use a Groq-hosted model through LangChain and LangGraph, stream responses as they are generated, and save conversation history in SQLite.

## Features

- Stream assistant responses in the browser or terminal
- Use a calculator tool for arithmetic expressions (`+`, `-`, `*`, `/`, `%`, `**`, unary signs, and parentheses)
- Resume saved conversations by selecting or reusing their thread ID
- Share saved conversations between the Streamlit and command-line interfaces when they use the same thread ID

The current agent registers the calculator tool. The project also contains an older web search implementation in `tools.py`, but it is not currently registered with the agent.

## Requirements

- Python 3.10 or newer
- A Groq API key

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project directory:

```env
GROQ_API_KEY=your_groq_api_key
```

## Run the web app

```powershell
streamlit run app.py
```

Choose a saved conversation in the sidebar to resume it, or choose **+ New conversation** and provide a name. If the name is blank, the app generates a new ID. Enter messages in the chat box; replies stream into the page.

## Run the command-line app

```powershell
python chatbot.py
```

Enter a conversation name to resume it, or leave it blank to use `default`. Type a message at the `You:` prompt. Type `quit` or `exit` to leave.

## Conversation storage

The agent stores checkpoints in `chat_history.db` in the current working directory. Keep this file to retain saved conversations. Both interfaces use it by default.

## Project files

- `app.py` — Streamlit chat interface, conversation selector, history display, and streamed responses.
- `chatbot.py` — command-line chat interface.
- `agent.py` — Groq model setup, calculator tool registration, and SQLite-backed conversation checkpoints.
- `tools.py` — calculator and a web search tool; only the calculator is currently registered with the agent.
- `requirements.txt` — Python dependencies.
