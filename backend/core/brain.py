import json
import anthropic
from typing import AsyncGenerator
from backend.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, SYSTEM_PROMPT
from backend.tools import get_anthropic_tools, execute_tool
from backend.core.memory import save_message, get_conversation_messages

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


async def think(
    user_text: str,
    on_tool_call=None,
    on_tool_result=None,
) -> str:
    """
    Sends user_text to Claude, executes any tool calls, returns final response text.
    on_tool_call(tool_name, args) and on_tool_result(tool_name, result) are optional callbacks.
    """
    save_message("user", user_text)

    messages = get_conversation_messages(limit=20)
    tools = get_anthropic_tools()

    while True:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        # Collect text and tool use blocks
        text_parts = []
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(block)

        if response.stop_reason == "end_turn" or not tool_calls:
            final_text = " ".join(text_parts).strip()
            save_message("assistant", final_text)
            return final_text

        # Execute tool calls
        assistant_msg = {"role": "assistant", "content": response.content}
        messages.append(assistant_msg)

        tool_results = []
        for tc in tool_calls:
            args = tc.input if isinstance(tc.input, dict) else json.loads(tc.input)
            if on_tool_call:
                await on_tool_call(tc.name, args)
            result = execute_tool(tc.name, args)
            if on_tool_result:
                await on_tool_result(tc.name, result)
            save_message("tool", result, tool_name=tc.name)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})
