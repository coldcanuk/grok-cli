# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation & Setup
```bash
# Install in development mode
pip install -e .

# Install with virtual environment (recommended)
python -m venv grok-env
# Windows:
grok-env\Scripts\Activate.ps1
# Linux/WSL:
source grok-env/bin/activate
pip install -e .
```

### Testing & Validation
```bash
# Run built-in self-tests
grok-cli --test

# Test basic functionality (requires API key)
grok-cli --src . --prompt "Hello, test prompt"
```

### Running the CLI
```bash
# All commands require --src flag (source directory)
grok-cli --src /path/to/project --prompt "Your question"
grok-cli --src . --chat  # Interactive mode
grok-cli --src . --cost --prompt "Your question"  # Cost tracking
grokit --src .  # GroKit menu interface
grok-cli --src . --help  # Show all options
```

## Architecture Overview

### Core Components
- **cli.py**: Clean entry point with argument parsing and mode routing
- **engine.py**: Core functionality with streaming, tool execution, and rate limiting
- **utils.py**: Shared utilities for config, vision, project context, and gitignore handling
- **request_manager.py**: Advanced batching, caching, and request optimization (currently integrated into engine)

### Key Design Patterns

**Source Directory Boundary**: All operations require `--src` flag to establish working directory boundary. This enables:
- Portable operation from any location
- Automatic `.grok/` context loading for project-specific instructions
- Security boundary for file operations

**Project Context System**: 
- `.grok/README.md`: Project overview loaded into system prompt
- `.grok/*.mdc`: Additional context files (coding standards, architecture docs)
- Auto-creates template if directory doesn't exist

**Tool Integration**: MCP-style tools for file operations and web search:
- `read_file`, `batch_read_files`, `list_files_recursive`, `create_file`
- `brave_search` (requires BRAVE_SEARCH_API_KEY)
- Intelligent caching and batching for efficiency

**Rate Limiting & Optimization**:
- Adaptive delays with exponential backoff for 429 errors
- Progress bars during rate limit waits
- Request batching and caching to minimize API calls
- Smart pacing between requests

### Configuration
- **settings.json**: Main configuration (model, streaming, MCP server settings)
- **Environment variables**: XAI_API_KEY (required), BRAVE_SEARCH_API_KEY (optional), GROK_DEBUG
- **startup.json/thinking.json**: Fun messages for user experience

### GroKit Interface System
**Interactive Menu Interface**: User-friendly alternative to command-line usage
- Clean menu-driven navigation with numbered options
- Advanced multi-line input with `###` submission syntax
- In-chat leader mode integration via `/leader` command
- Real-time cost tracking and session management
- Cross-platform compatibility with Unicode/ASCII fallback

**Key Components**:
- **grokit.py**: Main interface with menu system and grok-cli integration
- **input_handler.py**: Enhanced input handling with multi-line support
- Intelligent command routing through grok-cli subprocess calls
- Persistent session cost tracking and display

### File Operations Caching
The engine includes sophisticated caching for file operations to avoid redundant reads during tool calls. File operations are automatically batched when possible.

### Error Recovery
- Robust JSON parsing for malformed tool call arguments
- Graceful handling of concatenated JSON in streaming responses
- Retry logic with user-friendly progress indicators
- Tool call failure recovery with helpful error messages

## Common Development Workflows

### Adding New Tools
1. Define tool schema in `engine.py:build_tool_definitions()`
2. Implement execution logic in `engine.py:_execute_tool_function()`
3. Add caching logic if applicable in `request_manager.py`

### Modifying Project Context System
- Context loading: `utils.py:load_grok_context()`
- Template creation: `utils.py:create_grok_directory_template()`
- System prompt integration: `engine.py:get_enhanced_system_prompt()`

### Debugging
- Use `--debug 1` flag or `GROK_DEBUG=1` environment variable
- Debug output shows tool execution details and JSON parsing issues
- Rate limiting includes detailed timing and retry information

## Important Notes

### Security Considerations
- API keys should use environment variables, not command line flags
- File operations are bounded to the specified source directory
- .gitignore patterns are respected for file listing operations

### Platform Compatibility
- Windows PowerShell, WSL, and Linux support
- Unicode/emoji handling with fallbacks for terminal compatibility
- Path handling works across different OS conventions

### Performance Features
- Request batching reduces API calls
- File operation caching prevents redundant reads
- Intelligent rate limiting with adaptive delays
- Progress indicators for better user experience during waits