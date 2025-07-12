"""Handles streaming responses from the Grok API."""

import json
import os

def handle_stream(response, brave_api_key=None, debug_mode=None):
    """Handle streaming response with potential tool calls."""
    full_content = []
    tool_calls = []
    
    is_debug = debug_mode if debug_mode is not None else bool(os.getenv("GROK_DEBUG"))
    
    for chunk in response.iter_lines():
        if chunk:
            chunk = chunk.decode("utf-8").lstrip("data: ")
            if chunk != "[DONE]":
                try:
                    data = json.loads(chunk)
                    choice = data["choices"][0]
                    
                    if "delta" in choice and "content" in choice["delta"]:
                        delta = choice["delta"]["content"]
                        print(delta, end="", flush=True)
                        full_content.append(delta)
                    
                    if "delta" in choice and "tool_calls" in choice["delta"]:
                        for tool_call_delta in choice["delta"]["tool_calls"]:
                            if "index" in tool_call_delta:
                                idx = tool_call_delta["index"]
                                while len(tool_calls) <= idx:
                                    tool_calls.append({
                                        "id": "",
                                        "type": "function",
                                        "function": {"name": "", "arguments": ""}
                                    })
                                
                                if "id" in tool_call_delta:
                                    tool_calls[idx]["id"] = tool_call_delta["id"]
                                if "function" in tool_call_delta:
                                    if "name" in tool_call_delta["function"]:
                                        tool_calls[idx]["function"]["name"] = tool_call_delta["function"]["name"]
                                    if "arguments" in tool_call_delta["function"]:
                                        tool_calls[idx]["function"]["arguments"] += tool_call_delta["function"]["arguments"]
                    
                except (KeyError, json.JSONDecodeError) as e:
                    if is_debug:
                        print(f"\n[DEBUG] Error parsing chunk: {e}")
                        print(f"[DEBUG] Raw chunk: {repr(chunk)}")
    
    for i, tool_call in enumerate(tool_calls):
        if tool_call["function"]["arguments"]:
            try:
                json.loads(tool_call["function"]["arguments"])
            except json.JSONDecodeError as e:
                print(f"\n[WARNING] Tool call {i} has invalid JSON arguments")
                if os.getenv("GROK_DEBUG"):
                    print(f"[DEBUG] Raw arguments: {repr(tool_call['function']['arguments'])}")
                args = tool_call["function"]["arguments"]
                if args.count('{') > args.count('}'):
                    depth = 0
                    last_complete = -1
                    for j, char in enumerate(args):
                        if char == '{':
                            depth += 1
                        elif char == '}':
                            depth -= 1
                            if depth == 0:
                                last_complete = j
                    if last_complete > 0:
                        tool_call["function"]["arguments"] = args[:last_complete + 1]
                        if os.getenv("GROK_DEBUG"):
                            print(f"[DEBUG] Fixed arguments: {tool_call['function']['arguments']}")
    
    print()
    return "".join(full_content), tool_calls
