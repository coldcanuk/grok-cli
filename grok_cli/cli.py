"""Grok CLI - Main entry point."""

import argparse
import json
import sys
import os
import asyncio

# Import from our new modules
from .utils import load_config, get_api_key, build_vision_content
from .api_client import api_call, show_thinking_message, show_startup_message
from .file_tools import build_tool_definitions, execute_tool_call
from .request_manager import RequestManager, RequestPriority
from .streaming import handle_stream

DEFAULT_MODEL = "grok-4"
SYSTEM_PROMPT = """You are Grok, a helpful and truthful AI built by xAI. When asked to create files or perform file operations, use the available tools to complete the task. Always use the appropriate tools when they are available rather than just describing what you would do.

Important: When using the read_file tool, you must make a separate tool call for each file you want to read. Do not try to read multiple files in a single tool call. Each tool call should have exactly one JSON object with one filename."""

def run_chat_loop(args, key, brave_key, request_manager, messages, tools):
    """Core loop for processing messages and tool calls."""
    max_iterations = 10
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        response = api_call(key, messages, args.model, args.stream, tools)
        
        if args.stream:
            assistant_content, tool_calls = handle_stream(response, brave_key, debug_mode=args.debug)
            
            if not tool_calls:
                if iteration == 1 and assistant_content:
                    pass
                return
            
            print("\n[Queueing tool calls...]")
            messages.append({"role": "assistant", "content": assistant_content or None, "tool_calls": tool_calls})
            
            for tool_call in tool_calls:
                request_manager.add_request(
                    tool_call['function']['name'],
                    json.loads(tool_call['function']['arguments']),
                    priority=RequestPriority.MEDIUM
                )
            
            results = asyncio.run(request_manager.process_queue())
            
            tool_call_failures = 0
            for tool_call in tool_calls:
                result_key = next((k for k in results if tool_call['function']['name'] in k), None)
                result = results.get(result_key, {"error": "Tool execution result not found"})

                if "error" in result:
                    tool_call_failures += 1
                    print(f"[WARNING] Tool call failed: {result['error']}")
                
                is_debug = args.debug if args.debug is not None else bool(os.getenv("GROK_DEBUG"))
                if is_debug:
                    print(f"Tool result: {json.dumps(result, indent=2)}")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                })
            
            if tool_call_failures == len(tool_calls):
                print("\n[ERROR] All tool calls failed. Asking Grok to retry...")
                messages.append({
                    "role": "user",
                    "content": "The previous tool calls failed due to invalid arguments. Please try again with properly formatted JSON arguments."
                })
            
            show_thinking_message()
            
        else:
            response_json = response.json()
            message = response_json["choices"][0]["message"]
            
            if "tool_calls" not in message:
                if "content" in message and message["content"]:
                    print(message["content"])
                return
            
            if "content" in message and message["content"]:
                print(message["content"])
            
            print("\n[Queueing tool calls...]")
            messages.append(message)
            
            for tool_call in message["tool_calls"]:
                request_manager.add_request(
                    tool_call['function']['name'],
                    json.loads(tool_call['function']['arguments']),
                    priority=RequestPriority.MEDIUM
                )

            results = asyncio.run(request_manager.process_queue())

            for tool_call in message["tool_calls"]:
                result_key = next((k for k in results if tool_call['function']['name'] in k), None)
                result = results.get(result_key, {"error": "Tool execution result not found"})

                is_debug = args.debug if args.debug is not None else bool(os.getenv("GROK_DEBUG"))
                if is_debug:
                    print(f"Tool result: {json.dumps(result, indent=2)}")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                })
            
            print("\n[Getting response...]")
    
    if iteration >= max_iterations:
        print("\n[Warning: Maximum iterations reached]")

def single_prompt(args, key, brave_key, request_manager):
    """Handle single prompt mode."""
    show_startup_message()
    tools = build_tool_definitions()
    content = build_vision_content(args.prompt, args.image)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": content}]
    run_chat_loop(args, key, brave_key, request_manager, messages, tools)

def interactive_chat(args, key, brave_key, request_manager):
    """Handle interactive chat mode."""
    import random
    
    startup_messages = [
        "🥔 Throwing a potato down the hall to get Grok's attention...",
        "🔔 Ringing the consciousness bell...",
        "🎯 Aiming your query at the cosmic bullseye...",
    ]
    
    print(f"\n{random.choice(startup_messages)}\n")
    
    tools = build_tool_definitions()
    
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Interactive chat started. Type /quit to exit, /clear to reset history, /save <file> to save.")
    print(f"Available tools: {[tool['function']['name'] for tool in tools]}")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except EOFError:
            break
        if user_input == "/quit":
            break
        elif user_input == "/clear":
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("History cleared.")
            continue
        elif user_input.startswith("/save "):
            file = user_input.split(" ", 1)[1]
            with open(file, "w", encoding="utf-8") as f:
                json.dump(history, f)
            print(f"History saved to {file}.")
            continue
        
        content = build_vision_content(user_input, args.image) if args.image else user_input
        history.append({"role": "user", "content": content})
        
        run_chat_loop(args, key, brave_key, request_manager, history, tools)

def test_mode():
    """Run simple self-tests."""
    # Test imports
    assert build_vision_content("test", None) == [{"type": "text", "text": "test"}]
    print("Tests passed.")

def main():
    """Main entry point for the CLI."""
    config = load_config()
    request_manager = RequestManager()
    
    parser = argparse.ArgumentParser(description="Grok CLI: Interact with xAI Grok API. Get key at https://x.ai/api.")
    parser.add_argument("--prompt", help="Single prompt to send.")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat.")
    parser.add_argument("--model", default=config.get("model", DEFAULT_MODEL), help="Model to use.")
    parser.add_argument("--stream", action="store_true", default=config.get("stream", False), help="Stream response.")
    parser.add_argument("--api-key", help="API key (prefer env var XAI_API_KEY for security).")
    parser.add_argument("--image", help="Image URL or local path for vision.")
    parser.add_argument("--debug", type=int, choices=[0, 1], help="Debug mode: 1=on, 0=off (overrides GROK_DEBUG env var).")
    parser.add_argument("--test", action="store_true", help="Run self-tests.")
    
    args = parser.parse_args()

    if args.test:
        test_mode()
        return

    if not args.prompt and not args.chat:
        parser.print_help()
        sys.exit(1)

    key, brave_key = get_api_key(args)

    if args.prompt:
        single_prompt(args, key, brave_key, request_manager)
    elif args.chat:
        interactive_chat(args, key, brave_key, request_manager)

if __name__ == "__main__":
    main()
