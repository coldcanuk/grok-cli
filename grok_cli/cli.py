"""
Clean CLI entry point for Grok CLI
"""

import argparse
import json
import os
import random
import sys

from .engine import GrokEngine, DEFAULT_MODEL, SYSTEM_PROMPT
from .utils import get_api_key, build_vision_content

def single_prompt(args, engine: GrokEngine):
    """Handle single prompt mode."""
    engine.display_startup_message()
    
    key, brave_key = get_api_key(args)
    content = build_vision_content(args.prompt, args.image)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": content}
    ]
    
    engine.run_chat_loop(args, key, brave_key, messages)

def interactive_chat(args, engine: GrokEngine):
    """Handle interactive chat mode."""
    startup_messages = [
        "🥔 Throwing a potato down the hall to get Grok's attention...",
        "🔔 Ringing the consciousness bell...",
        "🎯 Aiming your query at the cosmic bullseye...",
    ]
    
    print(f"\n{random.choice(startup_messages)}\n")
    
    key, brave_key = get_api_key(args)
    
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Interactive chat started. Type /quit to exit, /clear to reset history, /save <file> to save.")
    print(f"Available tools: {[tool['function']['name'] for tool in engine.tools]}")
    
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
            filename = user_input.split(" ", 1)[1]
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(history, f, indent=2)
                print(f"History saved to {filename}.")
            except Exception as e:
                print(f"Error saving history: {e}")
            continue
        
        content = build_vision_content(user_input, args.image) if args.image else user_input
        history.append({"role": "user", "content": content})
        
        engine.run_chat_loop(args, key, brave_key, history)

def test_mode():
    """Run simple self-tests."""
    print("Testing Grok CLI...")
    
    # Test vision content building
    assert build_vision_content("test", None) == [{"type": "text", "text": "test"}]
    
    # Test engine initialization
    engine = GrokEngine()
    assert engine.config is not None
    assert engine.tools is not None
    
    print("All tests passed!")

def main():
    """Main entry point for the CLI."""
    engine = GrokEngine()
    
    parser = argparse.ArgumentParser(
        description="Grok CLI: Interact with xAI Grok API. Get key at https://x.ai/api."
    )
    parser.add_argument("--prompt", help="Single prompt to send.")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat.")
    parser.add_argument("--model", default=engine.config.get("model", DEFAULT_MODEL), help="Model to use.")
    parser.add_argument("--stream", action="store_true", default=engine.config.get("stream", False), help="Stream response.")
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

    if args.prompt:
        single_prompt(args, engine)
    elif args.chat:
        interactive_chat(args, engine)

if __name__ == "__main__":
    main()