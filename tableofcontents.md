# Table of Contents

This is an automatically generated table of contents for the Grok CLI project, respecting .gitignore. Each entry follows the format: `/path/to/filename: {Brief 30-word description outlining the file's purpose and functionality}.`

Generated for easy navigation, human-readable formatting, and parsable by code/LLMs.

```text
./.gitignore: Git ignore file specifying files and directories to exclude from version control, including build artifacts, environments, and temporary files.
./create_tableofcontents.py: Script that lists project files respecting .gitignore, generates descriptions based on file types, and creates a structured tableofcontents.md file.
./LICENSE: GNU General Public License v3 for the project, allowing free redistribution and modification with conditions.
./README.md: Project documentation including features, installation guides for various platforms, usage instructions, configuration, and troubleshooting for Grok CLI.
./requirements.txt: Python dependencies list including certifi, charset-normalizer, idna, requests, urllib3, and tiktoken for the project.
./settings.json: Configuration file specifying default model, streaming preference, and enabled MCP servers for tools like search and file operations.
./setup.py: Python package setup script defining name, version, dependencies, and entry points for the Grok CLI tool.
./.claude/settings.local.json: Claude settings file defining allowed and denied bash commands for some integration or automation.
./.github/issue_template.md: GitHub issue template with types, description, checklist, reproduction steps, and environment info.
./.github/pull_request_template.md: GitHub pull request template including description, type of change, testing info, checklist, and notes.
./.grok/architecture.mdc: Describes core components, design principles, and file structure of Grok CLI.
./.grok/coding-standards.mdc: Outlines Python code style, documentation, error handling, testing, and project philosophy for Grok CLI.
./.grok/README.md: Documentation for .grok directory purpose, how it works, examples, and tips for project context.
./grok_cli/cli.py: Main CLI entry point handling arguments, single prompts, interactive chat, and testing for Grok API interactions.
./grok_cli/engine.py: Core engine managing API calls, tool executions, rate limiting, streaming, and project context for Grok CLI.
./grok_cli/enhanced_input.py: Advanced input handler with real-time character updates, multi-line support, command handling, and cross-platform compatibility for Windows/Linux/WSL.
./grok_cli/grid_ui.py: Grid-based terminal UI renderer with panels for AI responses, user input, and system messages with cursor management.
./grok_cli/grokit.py: Main GroKit UI class providing interactive chat grid interface, session management, and integration with enhanced input system.
./grok_cli/input_handler.py: Basic input handler for terminal interactions, command processing, and multi-line input support with history management.
./grok_cli/leader.py: Leadership and team management module with role definitions, task delegation, and collaboration features for multi-agent workflows.
./grok_cli/markdown_renderer.py: Markdown-to-terminal renderer supporting headers, lists, code blocks, tables, and rich text formatting for console output.
./grok_cli/persistence.py: Session and conversation persistence manager handling save/load operations, history tracking, and file-based storage for chat continuity.
./grok_cli/request_manager.py: Manages request batching, caching, prioritization, and rate limiting for efficient tool operations in Grok CLI.
./grok_cli/startup.json: JSON file containing fun startup messages with emojis for display during Grok CLI initialization.
./grok_cli/terminal_input.py: Low-level terminal input handler with platform-specific implementations for real-time character capture on Windows/Linux/WSL.
./grok_cli/thinking.json: JSON file with humorous thinking messages and emojis for display during processing waits.
./grok_cli/tokenCount.py: Token counting utilities for API request management, cost estimation, and context window tracking.
./grok_cli/tool_output_capture.py: Captures and processes tool execution outputs, handling streaming responses and error management for tool calls.
./grok_cli/utils.py: Shared utilities for configuration, API keys, vision content, gitignore handling, emoji stripping, and context loading.
./grok_cli/__init__.py: Package initialization file for grok_cli module, enabling it as a Python package.
./grok_cli.egg-info/dependency_links.txt: Egg info file listing dependency links (empty) for the grok-cli package.
./grok_cli.egg-info/entry_points.txt: Specifies console entry point for grok-cli command.
./grok_cli.egg-info/PKG-INFO: Package metadata including version, summary, author, and description for grok-cli.
./grok_cli.egg-info/requires.txt: Lists required dependencies (requests) for the grok-cli package.
./grok_cli.egg-info/SOURCES.txt: Lists all files included in the grok-cli package distribution.
./grok_cli.egg-info/top_level.txt: Specifies top-level package name for the egg-info.
```

## Summary

- Total files documented: 36
- Generated on: 2025-07-12

## Recent Updates

- Enhanced cross-platform compatibility for Debian/Ubuntu, WSL, and Windows 11
- Improved terminal input handling with real-time character updates
- Added platform detection for WSL environments
- Fixed input field clearing and cursor display issues
- Updated enhanced_input.py, terminal_input.py, and grid_ui.py for better cross-platform support
