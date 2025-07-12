# File Dependency Analysis

## Current Architecture Problems

### Entry Point Chain (ACTIVE):
```
setup.py → grok_cli.cli:main
  ↓
cli.py imports:
  - utils.py (load_config, get_api_key, build_vision_content)
  - api_client.py (api_call, show_thinking_message, show_startup_message)
  - file_tools.py (build_tool_definitions, execute_tool_call)
  - request_manager.py (RequestManager, RequestPriority)
  - streaming.py (handle_stream)
```

### Disconnected Implementation (UNUSED):
```
optimized_cli.py (Class-based, self-contained)
  - Has own tool definitions (better ones!)
  - Has own API client logic (with rate limiting!)
  - Has own file operations (with caching!)
  - Uses RequestManager but otherwise independent
```

## File Relationships:

### utils.py - Shared Utilities
- Used by: cli.py
- NOT used by: optimized_cli.py (has own methods)
- Functions: load_config, get_api_key, build_vision_content, gitignore handling

### api_client.py - API Communication  
- Used by: cli.py
- NOT used by: optimized_cli.py (has own api_call_optimized)
- Functions: api_call, rate limiting messages, startup messages

### file_tools.py - Tool Definitions & Execution
- Used by: cli.py, request_manager.py
- NOT used by: optimized_cli.py (has own tool definitions)
- Functions: build_tool_definitions, execute_tool_call, file operations

### request_manager.py - Async Request Handling
- Used by: cli.py, optimized_cli.py, file_tools.py
- Functions: BatchedRequest, RequestManager, priority handling

### streaming.py - Stream Response Handling
- Used by: cli.py  
- NOT used by: optimized_cli.py (probably should be!)
- Functions: handle_stream, tool call detection

## Major Issues Identified:

1. **Duplicate Functionality**: Two complete CLI implementations
2. **Better Code Unused**: optimized_cli.py has superior features but no entry point
3. **Scattered Logic**: Tool definitions in both file_tools.py AND optimized_cli.py
4. **Missing Integration**: streaming.py not used by optimized version
5. **Code Duplication**: API calling logic in both api_client.py and optimized_cli.py