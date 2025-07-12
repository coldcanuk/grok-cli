# CLI File Analysis

## cli.py - The ACTUAL Entry Point

**Confirmed**: setup.py line 10 calls `grok_cli.cli:main`

### main() Function Flow:
1. Load config from settings.json
2. Create RequestManager instance  
3. Parse command line arguments
4. Get API keys (XAI + optional Brave)
5. Route to either:
   - `single_prompt()` if --prompt provided
   - `interactive_chat()` if --chat flag
   - `test_mode()` if --test flag

### Key Dependencies:
- utils: load_config, get_api_key, build_vision_content
- api_client: api_call, show_thinking_message, show_startup_message  
- file_tools: build_tool_definitions, execute_tool_call
- request_manager: RequestManager, RequestPriority
- streaming: handle_stream

### Core Logic:
- `run_chat_loop()`: Main processing with 10 iteration limit
- Handles both streaming and non-streaming responses
- Uses asyncio for tool execution via RequestManager
- Tool call failure handling and retry logic

## Key Questions:
1. Why does optimized_cli.py exist if cli.py is the entry point?
2. Are they meant to be alternatives or is one deprecated?
3. Should we consolidate or keep separate?