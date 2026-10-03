import asyncio

from langchain.messages import AIMessageChunk

from agent import build_agent


async def stream_reply(agent, user_input: str, config: dict) -> None:
    """Print the model's reply token by token as it is generated."""
    print("Bot: ", end="", flush=True)

    async for token, metadata in agent.astream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="messages",  #? Yields message chunks with metadata as they arrive.
    ):
        if not isinstance(token, AIMessageChunk):
            continue  #? Skip tool results and other non-model messages.
        for block in token.content_blocks:
            if block["type"] == "text":
                print(block["text"], end="", flush=True)
            elif block["type"] == "tool_call":
                print(f"\n[calling tool: {block.get('name')}]", end="", flush=True)

    print("\n")


async def main() -> None:
    print("Setting up the chat agent...")
    agent = await build_agent()

    print("Chatbot ready. Type 'quit' to exit.")
    thread_id = input("Conversation name (blank for 'default'): ").strip() or "default"
    config = {"configurable": {"thread_id": thread_id}}
    print(f"Resuming conversation '{thread_id}'.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            break

        await stream_reply(agent, user_input, config)


if __name__ == "__main__":
    asyncio.run(main())
