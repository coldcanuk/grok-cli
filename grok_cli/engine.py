"""
Core engine for Grok CLI with advanced optimization and streaming
"""

import asyncio
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import requests

try:
    from xai_sdk import Client
    from xai_sdk.chat import user, system
    XAI_SDK_AVAILABLE = True
except ImportError:
    XAI_SDK_AVAILABLE = False

from .request_manager import RequestManager, RequestPriority
from .utils import get_random_message, load_grok_context, create_grok_directory_template
from .tokenCount import TokenCounter
from .tool_output_capture import ToolOutputCapture, EnhancedToolExecutor

# xAI API endpoint - using v1 path (OpenAI compatible)
API_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-4-0709"
REASONING_MODELS = {
    "grok-4-0709": "grok-4-0709-reasoning",
    "grok-3-mini": "grok-3-mini-reasoning"
}
SYSTEM_PROMPT = """You are Grok, a helpful and truthful AI built by xAI. You have FULL ACCESS to the local filesystem and can perform any file operations needed.

 AVAILABLE TOOLS - YOU CAN USE THESE:
- read_file: Read any file on the local filesystem
- create_file: Create new files with content
- list_files_recursive: List directory contents recursively
- batch_read_files: Read multiple files efficiently
- shell_command: Execute shell commands (cat, echo, touch, mkdir, rm, cd, ls, pwd)
- brave_search: Search the web for information

 FILESYSTEM ACCESS:
- You CAN read, write, create, and modify files
- You CAN examine directory structures and file contents  
- You CAN create new files and directories
- You ARE working within the source directory boundary for security
- You SHOULD use tools to investigate issues and implement solutions

 NEVER SAY YOU CAN'T ACCESS FILES - You have full MCP tool access!

IMPORTANT INSTRUCTIONS:
- When asked to examine code, diagnose issues, or make changes - USE THE TOOLS
- Read relevant files to understand the codebase structure
- Make actual changes to files when requested
- Always investigate before responding with generic advice
- Use batch_read_files for efficiency when examining multiple related files

 PROJECT STRUCTURE GUIDE:
This is the grok-cli project. Key files are located in:
- Main package: grok_cli/ directory contains all Python modules
- Grid UI system: grok_cli/grokit.py (main Grid UI integration)
- Grid renderer: grok_cli/grid_ui.py (terminal grid rendering)
- Cost tracking: grok_cli/tokenCount.py (cost and token management)
- CLI interface: grok_cli/cli.py (command line interface)
- AI engine: grok_cli/engine.py (core AI functionality)
- When investigating UI issues, ALWAYS check grok_cli/grokit.py and grok_cli/grid_ui.py
- When investigating cost/token issues, check grok_cli/tokenCount.py and grid UI integration

Tool Usage:
- Each tool call should contain exactly one operation
- File operations are cached to avoid redundant reads
- Multiple tool calls are automatically optimized"""

class EnhancedToolExecutor:
    """Enhanced tool executor with output capture support."""
    
    def __init__(self, engine=None):
        self.tool_output_capture = ToolOutputCapture()
        self.engine = engine
        
    def execute_with_capture(self, tool_name: str, args: Dict[str, Any], brave_api_key: Optional[str] = None) -> Tuple[Dict[str, Any], Optional[str]]:
        """Execute a tool with output capture enabled."""
        self.tool_output_capture.start_capture()
        
        try:
            # Track file state before execution for diff generation
            if tool_name in ['create_file', 'str_replace']:
                if 'filename' in args:
                    self.tool_output_capture.track_file_before(args['filename'])
            
            # Execute the tool with brave_api_key if needed
            result = self._execute_tool(tool_name, args, brave_api_key)
            
            # Stop capture and get output
            captured_output = self.tool_output_capture.stop_capture()
            
            # Format output including any diffs
            formatted_output = self.tool_output_capture.format_output(captured_output)
            
            return result, formatted_output
            
        except Exception as e:
            # Ensure capture is stopped even on error
            self.tool_output_capture.stop_capture()
            return {"error": str(e)}, None
    
    def _execute_tool(self, tool_name: str, args: Dict[str, Any], brave_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Execute the actual tool using the engine's implementation."""
        if self.engine:
            # Call the engine's internal tool execution method
            return self.engine._execute_tool_internal(tool_name, args, brave_api_key)
        else:
            return {"error": "No engine instance available for tool execution"}

class GrokEngine:
    """Core engine for Grok CLI with advanced features."""
    
    def __init__(self, min_delay_seconds: float = 0.3):
        self.request_manager = RequestManager(min_delay_seconds)
        self.config = self.load_config()
        self.tools = self.build_tool_definitions()
        self.last_request_time = 0
        self.source_directory = None
        self.project_context = ""
        self.token_counter = None
        self.cost_tracking_enabled = False
        self.xai_client = None
        self.tool_output_capture = ToolOutputCapture()
        self.enhanced_executor = EnhancedToolExecutor(self)
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from settings.json."""
        config_path = "settings.json"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {}
    
    def set_source_directory(self, src_path: str):
        """Set the source directory and load project context."""
        self.source_directory = os.path.abspath(src_path)
        
        # Try to create .grok directory template if it doesn't exist
        created = create_grok_directory_template(self.source_directory)
        if created:
            print(f">> Created .grok directory template in {self.source_directory}")
        
        # Load project context
        self.project_context = load_grok_context(self.source_directory)
        if self.project_context:
            print(f">> Loaded project context from .grok directory")
        else:
            print(f">> No project context found in .grok directory")
    
    def get_enhanced_system_prompt(self) -> str:
        """Get system prompt enhanced with project context."""
        base_prompt = SYSTEM_PROMPT
        
        if self.project_context:
            enhanced_prompt = f"{base_prompt}{self.project_context}"
            enhanced_prompt += f"\n\nIMPORTANT: You are working within the source directory: {self.source_directory}\n"
            enhanced_prompt += "All file operations should be relative to this directory boundary. Respect the project context provided above."
            return enhanced_prompt
        
        if self.source_directory:
            return f"{base_prompt}\n\nIMPORTANT: You are working within the source directory: {self.source_directory}\nAll file operations should be relative to this directory boundary."
        
        return base_prompt
    
    def init_xai_client(self, api_key: str):
        """Initialize xAI SDK client."""
        if XAI_SDK_AVAILABLE:
            self.xai_client = Client(api_key=api_key)
    
    def enable_cost_tracking(self, session_file: Optional[str] = None):
        """Enable cost tracking with TokenCounter."""
        if not session_file and self.source_directory:
            session_file = os.path.join(self.source_directory, "grok_session_costs.json")
        
        self.token_counter = TokenCounter(session_file)
        self.cost_tracking_enabled = True
        print("Cost tracking enabled. Session costs will be displayed.")
    
    def track_api_response(self, response_data: Dict[str, Any], model: str, operation_type: str = "chat"):
        """Track API response for cost calculation."""
        if not self.cost_tracking_enabled or not self.token_counter:
            return
        
        usage = response_data.get("usage", {})
        if usage:
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            # Grok API might provide cached tokens info
            cached_tokens = usage.get("cached_tokens", 0)
            
            self.token_counter.track_api_call(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
                cached_tokens=cached_tokens,
                operation_type=operation_type
            )
            
            # Display cost info
            from .tokenCount import GrokPricing
            pricing = GrokPricing.get_model_pricing(model)
            input_cost = GrokPricing.calculate_token_cost(input_tokens, pricing["input"])
            output_cost = GrokPricing.calculate_token_cost(output_tokens, pricing["output"])
            total_cost = input_cost + output_cost
            
            # print(f"Actual cost: ${total_cost:.4f} ({input_tokens} -> {output_tokens} tokens)")
    
    def display_session_summary(self):
        """Display session cost summary if cost tracking is enabled."""
        if self.cost_tracking_enabled and self.token_counter:
            self.token_counter.display_session_costs()
    
    def build_tool_definitions(self) -> List[Dict[str, Any]]:
        """Build tool definitions for enabled MCP servers."""
        tools = []
        mcp_servers = self.config.get("mcp_servers", {})
        
        # Brave Search tool
        if mcp_servers.get("brave_search", {}).get("enabled", False):
            tools.append({
                "type": "function",
                "function": {
                    "name": "brave_search",
                    "description": "WEB SEARCH: Search the internet for current information, documentation, examples, and solutions. You CAN search for any information you need.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find information on the web"
                            }
                        },
                        "required": ["query"]
                    }
                }
            })
        
        # Optimized Local File System tools
        if mcp_servers.get("local_file_system", {}).get("enabled", False):
            tools.extend([
                {
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "description": "FULL FILE ACCESS: Read the complete content of any file on the filesystem. You CAN and SHOULD use this to examine code, configs, logs, and any other files.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filename": {
                                    "type": "string",
                                    "description": "The name of the file to read (relative or absolute path)"
                                }
                            },
                            "required": ["filename"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_files_recursive",
                        "description": "DIRECTORY EXPLORATION: List all files and directories recursively. You CAN explore the entire project structure and find any files you need.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "directory": {
                                    "type": "string",
                                    "description": "Directory to start from (default: current directory)",
                                    "default": "."
                                }
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "create_file",
                        "description": "FILE CREATION: Create new files with any content. You CAN create, write, and modify files as needed to implement solutions.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filename": {
                                    "type": "string",
                                    "description": "The name of the file to create (relative or absolute path)"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The content to write to the file"
                                }
                            },
                            "required": ["filename"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "batch_read_files",
                        "description": "EFFICIENT MULTI-FILE ACCESS: Read multiple files in one operation. Perfect for examining related files or understanding project structure quickly.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filenames": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of filenames to read (relative or absolute paths)"
                                }
                            },
                            "required": ["filenames"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "shell_command",
                        "description": "Execute shell commands (cat, echo, touch, mkdir, rm, cd) - FULL filesystem access available",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "Shell command to execute (cat, echo, touch, mkdir, rm, cd)"
                                },
                                "args": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Command arguments"
                                }
                            },
                            "required": ["command"]
                        }
                    }
                }
            ])
        
        return tools
    
    def handle_stream_with_tools(self, response, brave_api_key=None, debug_mode=None, capture_tools=False) -> Tuple[str, List[Dict], Optional[str]]:
        """Handle streaming response with tool call detection."""
        full_content = []
        tool_calls = []
        tool_outputs = []  # Collect tool outputs for Grid UI
        
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
        
        # Validate and fix tool call arguments
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
        
        print()  # New line after streaming
        return "".join(full_content), tool_calls, None  # No tool outputs yet
    
    def execute_tool_call(self, tool_call: Dict[str, Any], brave_api_key: Optional[str] = None, capture_output: bool = False) -> Dict[str, Any]:
        """Execute a tool call with optimization and caching."""
        tool_name = tool_call['function']['name']
        
        # Parse arguments, handling empty strings
        args_str = tool_call['function']['arguments']
        if not args_str or args_str.strip() == '':
            args = {}
        else:
            try:
                args = json.loads(args_str)
            except json.JSONDecodeError as e:
                return {"error": f"Invalid JSON arguments: {e}"}
        
        # Execute with capture if enabled
        if capture_output and self.enhanced_executor:
            result, captured_output = self.enhanced_executor.execute_with_capture(tool_name, args, brave_api_key)
            if captured_output:
                result["_captured_output"] = captured_output
            return result
            
        # Direct execution without capture
        return self._execute_tool_internal(tool_name, args, brave_api_key)
    
    def _execute_tool_internal(self, function_name: str, arguments: Dict[str, Any], brave_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Internal tool execution logic."""
        # Handle different tools
        if function_name == "brave_search":
            if not brave_api_key:
                return {"error": "Brave Search API key not configured"}
            
            headers = {"X-Subscription-Token": brave_api_key}
            params = {"q": arguments["query"]}
            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search", 
                headers=headers, 
                params=params, 
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        elif function_name == "read_file":
            filename = arguments["filename"]
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                return {"success": True, "content": content}
            else:
                return {"error": f"File '{filename}' not found"}
        
        elif function_name == "batch_read_files":
            filenames = arguments["filenames"]
            results = {}
            for filename in filenames:
                if os.path.exists(filename):
                    try:
                        with open(filename, "r", encoding="utf-8") as f:
                            content = f.read()
                        results[filename] = {"success": True, "content": content}
                    except Exception as e:
                        results[filename] = {"error": str(e)}
                else:
                    results[filename] = {"error": f"File '{filename}' not found"}
            return {"success": True, "results": results}
        
        elif function_name == "list_files_recursive":
            directory = arguments["directory"]
            patterns = self._load_gitignore_patterns()
            all_files = []
            
            for root, dirs, files in os.walk(directory):
                # Remove ignored directories
                dirs[:] = [d for d in dirs if not self._should_ignore(os.path.join(root, d), patterns)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    
                    if not self._should_ignore(relative_path, patterns):
                        all_files.append(relative_path)
            
            return {"success": True, "files": all_files}
        
        elif function_name == "create_file":
            filename = arguments["filename"]
            content = arguments.get("content", "")
            
            # Security check - ensure file is within source directory
            abs_path = os.path.abspath(filename)
            if not abs_path.startswith(os.path.abspath(self.source_directory)):
                return {"error": "Cannot create file outside source directory"}
            
            # Create directory if needed
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            # Write file
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return {"success": True, "message": f"Created file '{filename}'"}
        
        elif function_name == "str_replace":
            filename = arguments["filename"]
            old_str = arguments["old_str"]
            new_str = arguments["new_str"]
            
            if not os.path.exists(filename):
                return {"error": f"File '{filename}' not found"}
            
            # Read file content
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Replace string
            if old_str in content:
                new_content = content.replace(old_str, new_str)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return {"success": True, "message": f"Replaced string in '{filename}'"}
            else:
                return {"error": f"String '{old_str}' not found in file"}
        
        elif function_name == "run_shell":
            command = arguments["command"]
            args = arguments.get("args", [])
            return self._execute_shell_command(command, args)
        
        else:
            return {"error": f"Unknown tool: {function_name}"}
    
    def _load_gitignore_patterns(self) -> List[str]:
        """Load patterns from .gitignore file."""
        patterns = []
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        return patterns
    
    def _should_ignore(self, path: str, patterns: List[str]) -> bool:
        """Check if a path should be ignored based on gitignore patterns."""
        for pattern in patterns:
            if pattern.endswith('/'):
                if path.startswith(pattern) or ('/' + pattern) in path:
                    return True
            elif pattern in path or path.endswith(pattern):
                return True
            elif '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                    return True
        return False
    
    def _execute_shell_command(self, command: str, args: List[str]) -> Dict[str, Any]:
        """Execute shell commands within the source directory boundary."""
        import subprocess
        import shlex
        
        # Allowed commands for security
        allowed_commands = {
            'cat': self._shell_cat,
            'echo': self._shell_echo,
            'touch': self._shell_touch,
            'mkdir': self._shell_mkdir,
            'rm': self._shell_rm,
            'cd': self._shell_cd,
            'ls': self._shell_ls,
            'pwd': self._shell_pwd
        }
        
        if command not in allowed_commands:
            return {"error": f"Command '{command}' not allowed. Available: {', '.join(allowed_commands.keys())}"}
        
        try:
            return allowed_commands[command](args)
        except Exception as e:
            return {"error": f"Command failed: {str(e)}"}
    
    def _shell_cat(self, args: List[str]) -> Dict[str, Any]:
        """Implementation of cat command."""
        if not args:
            return {"error": "cat: missing file operand"}
        
        results = {}
        for filename in args:
            if os.path.exists(filename):
                try:
                    with open(filename, "r", encoding="utf-8") as f:
                        content = f.read()
                    results[filename] = {"success": True, "content": content}
                except Exception as e:
                    results[filename] = {"error": str(e)}
            else:
                results[filename] = {"error": f"cat: {filename}: No such file or directory"}
        
        return {"success": True, "command": "cat", "results": results}
    
    def _shell_echo(self, args: List[str]) -> Dict[str, Any]:
        """Implementation of echo command."""
        output = " ".join(args)
        return {"success": True, "command": "echo", "output": output}
    
    def _shell_touch(self, args: List[str]) -> Dict[str, Any]:
        """Implementation of touch command."""
        if not args:
            return {"error": "touch: missing file operand"}
        
        results = {}
        for filename in args:
            try:
                # Create file if it doesn't exist, update timestamp if it does
                with open(filename, "a", encoding="utf-8"):
                    pass
                results[filename] = {"success": True, "message": f"Touched '{filename}'"}
            except Exception as e:
                results[filename] = {"error": str(e)}
        
        return {"success": True, "command": "touch", "results": results}
    
    def _shell_mkdir(self, args: List[str]) -> Dict[str, Any]:
        """Implementation of mkdir command."""
        if not args:
            return {"error": "mkdir: missing operand"}
        
        # Check for -p flag
        create_parents = False
        paths = []
        for arg in args:
            if arg == "-p":
                create_parents = True
            else:
                paths.append(arg)
        
        if not paths:
            return {"error": "mkdir: missing directory operand"}
        
        results = {}
        for path in paths:
            try:
                if create_parents:
                    os.makedirs(path, exist_ok=True)
                else:
                    os.mkdir(path)
                results[path] = {"success": True, "message": f"Created directory '{path}'"}
            except FileExistsError:
                results[path] = {"error": f"mkdir: cannot create directory '{path}': File exists"}
            except Exception as e:
                results[path] = {"error": str(e)}
        
        return {"success": True, "command": "mkdir", "results": results}
    
    def _shell_rm(self, args: List[str]) -> Dict[str, Any]:
        """Implementation of rm command."""
        if not args:
            return {"error": "rm: missing operand"}
        
        # Check for flags
        recursive = False
        force = False
        paths = []
        for arg in args:
            if arg in ["-r", "-R", "--recursive"]:
                recursive = True
            elif arg in ["-f", "--force"]:
                force = True
            elif arg == "-rf" or arg == "-fr":
                recursive = True
                force = True
            else:
                paths.append(arg)
        
        if not paths:
            return {"error": "rm: missing file operand"}
        
        results = {}
        for path in paths:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    results[path] = {"success": True, "message": f"Removed file '{path}'"}
                elif os.path.isdir(path):
                    if recursive:
                        import shutil
                        shutil.rmtree(path)
                        results[path] = {"success": True, "message": f"Removed directory '{path}'"}
                    else:
                        results[path] = {"error": f"rm: cannot remove '{path}': Is a directory (use -r for recursive)"}
                else:
                    if not force:
                        results[path] = {"error": f"rm: cannot remove '{path}': No such file or directory"}
            except Exception as e:
                results[path] = {"error": str(e)}
        
        return {"success": True, "command": "rm", "results": results}
    
    def _shell_cd(self, args: List[str]) -> Dict[str, Any]:
        """Implementation of cd command."""
        if not args:
            # cd with no args goes to home directory
            target = os.path.expanduser("~")
        else:
            target = args[0]
        
        try:
            old_cwd = os.getcwd()
            os.chdir(target)
            new_cwd = os.getcwd()
            return {"success": True, "command": "cd", "old_directory": old_cwd, "new_directory": new_cwd}
        except Exception as e:
            return {"error": f"cd: {str(e)}"}
    
    def _shell_ls(self, args: List[str]) -> Dict[str, Any]:
        """Implementation of ls command."""
        path = args[0] if args else "."
        
        try:
            if os.path.isfile(path):
                return {"success": True, "command": "ls", "files": [path], "type": "file"}
            elif os.path.isdir(path):
                files = os.listdir(path)
                files.sort()
                return {"success": True, "command": "ls", "files": files, "directory": path}
            else:
                return {"error": f"ls: cannot access '{path}': No such file or directory"}
        except Exception as e:
            return {"error": f"ls: {str(e)}"}
    
    def _shell_pwd(self, args: List[str]) -> Dict[str, Any]:
        """Implementation of pwd command."""
        try:
            cwd = os.getcwd()
            return {"success": True, "command": "pwd", "directory": cwd}
        except Exception as e:
            return {"error": f"pwd: {str(e)}"}
    
    def api_call(self, key: str, messages: List[Dict[str, Any]], model: str, 
                 stream: bool, tools: Optional[List[Dict[str, Any]]] = None, 
                 retry_count: int = 0, reasoning: bool = False):
        """Make an API call using xAI SDK with fallback to requests."""
        
        # Initialize client if not already done
        if self.xai_client is None:
            self.init_xai_client(key)
        
        # Cost estimation before API call
        if self.cost_tracking_enabled and self.token_counter:
            input_tokens = self.token_counter.count_messages_tokens(messages, model)
            estimate = self.token_counter.estimate_cost(
                input_text="", # We already have token count
                expected_output_tokens=500,  # Reasonable default
                model=model
            )
            # Override with actual input tokens
            from .tokenCount import GrokPricing
            estimate["input_tokens"] = input_tokens
            estimate["total_estimated_cost"] = (
                GrokPricing.calculate_token_cost(input_tokens, 
                    GrokPricing.get_model_pricing(model)["input"]) +
                estimate["output_cost"]
            )
            
            # print(f"Estimated cost: ${estimate['total_estimated_cost']:.4f} ({input_tokens} input tokens)")
            self.token_counter.display_cost_warning(estimate["total_estimated_cost"])
        
        # Calculate adaptive delay based on recent activity
        time_since_last = time.time() - self.last_request_time
        if time_since_last < 1.0:  # If less than 1 second, wait a bit
            delay = 1.0 - time_since_last
            print(f">> Pacing request... ({delay:.1f}s)")
            time.sleep(delay)
        
        fun_messages = [
            ">> Optimizing request for best results...",
            ">> Launching your perfectly timed query...",
            ">> Grok is ready and waiting...",
            ">> Request dispatched with optimal timing...",
            ">> The optimized show begins...",
        ]
        
        try:
            if XAI_SDK_AVAILABLE:
                return self._api_call_sdk(messages, model, stream, tools, reasoning, retry_count, fun_messages)
            else:
                return self._api_call_requests(key, messages, model, stream, tools, reasoning, retry_count, fun_messages)
        except Exception as e:
            if retry_count >= 8:
                print("\n>> Tip: The optimized CLI is working! Consider spreading requests further apart.")
                raise Exception(f"API Error after 8 attempts: {e}")
            
            print(f"\nRetrying API call (attempt {retry_count + 1}/8)...")
            return self.api_call(key, messages, model, stream, tools, retry_count + 1, reasoning)
    
    def _api_call_sdk(self, messages: List[Dict[str, Any]], model: str, stream: bool, 
                     tools: Optional[List[Dict[str, Any]]], reasoning: bool, 
                     retry_count: int, fun_messages: List[str]):
        """Make API call using xAI SDK."""
        try:
            # Convert messages to SDK format
            sdk_messages = []
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    sdk_messages.append(system(content))
                elif role == "user":
                    sdk_messages.append(user(content))
                # For assistant messages, we'll handle them in the chat object
            
            # Create chat with model
            chat = self.xai_client.chat.create(model=model)
            
            # Add system and user messages
            for msg in sdk_messages:
                chat.append(msg)
            
            # Get response
            if reasoning:
                # SDK handles reasoning automatically - just sample
                response = chat.sample()
                
                # Create a wrapper object that mimics our expected interface
                class SDKResponseWrapper:
                    def __init__(self, sdk_response):
                        self.sdk_response = sdk_response
                        self.content = sdk_response.content
                        self.reasoning_content = getattr(sdk_response, 'reasoning_content', '')
                        self.usage = sdk_response.usage
                        self.choices = [self._create_choice()]
                    
                    def _create_choice(self):
                        class Choice:
                            def __init__(self, content):
                                self.message = type('Message', (), {'content': content})()
                        return Choice(self.content)
                    
                    def json(self):
                        return {
                            "choices": [{"message": {"content": self.content}}],
                            "usage": {
                                "prompt_tokens": self.usage.prompt_tokens,
                                "completion_tokens": self.usage.completion_tokens,
                                "reasoning_tokens": getattr(self.usage, 'reasoning_tokens', 0),
                                "total_tokens": self.usage.prompt_tokens + self.usage.completion_tokens
                            }
                        }
                
                self.last_request_time = time.time()
                return SDKResponseWrapper(response)
            else:
                # Regular response
                response = chat.sample()
                
                class SDKResponseWrapper:
                    def __init__(self, sdk_response):
                        self.sdk_response = sdk_response
                        self.content = sdk_response.content
                        self.usage = sdk_response.usage
                        self.choices = [self._create_choice()]
                    
                    def _create_choice(self):
                        class Choice:
                            def __init__(self, content):
                                self.message = type('Message', (), {'content': content})()
                        return Choice(self.content)
                    
                    def json(self):
                        return {
                            "choices": [{"message": {"content": self.content}}],
                            "usage": {
                                "prompt_tokens": self.usage.prompt_tokens,
                                "completion_tokens": self.usage.completion_tokens,
                                "total_tokens": self.usage.prompt_tokens + self.usage.completion_tokens
                            }
                        }
                
                self.last_request_time = time.time()
                return SDKResponseWrapper(response)
                
        except Exception as e:
            print(f"SDK call failed: {e}")
            raise e
    
    def _api_call_requests(self, key: str, messages: List[Dict[str, Any]], model: str, 
                          stream: bool, tools: Optional[List[Dict[str, Any]]], 
                          reasoning: bool, retry_count: int, fun_messages: List[str]):
        """Fallback API call using requests (original implementation)."""
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        
        # Handle reasoning mode
        if reasoning:
            # Try reasoning model first
            if model in REASONING_MODELS:
                reasoning_model = REASONING_MODELS[model]
                data = {"messages": messages, "model": reasoning_model, "stream": stream}
            else:
                # Fall back to parameter-based reasoning
                data = {"messages": messages, "model": model, "stream": stream, "reasoning": True}
        else:
            data = {"messages": messages, "model": model, "stream": stream}
        
        if tools:
            data["tools"] = tools
            data["tool_choice"] = "auto"
        
        try:
            response = requests.post(API_URL, headers=headers, json=data, stream=stream, timeout=(10, 60))
            response.raise_for_status()
            self.last_request_time = time.time()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_count += 1
                
                # Check for Retry-After header
                retry_after = e.response.headers.get('Retry-After')
                if retry_after:
                    try:
                        wait_time = int(retry_after)
                    except ValueError:
                        wait_time = min(5 * (2 ** (retry_count - 1)) + random.random() * 3, 60)
                else:
                    wait_time = min(5 * (2 ** (retry_count - 1)) + random.random() * 3, 60)
                
                # Use fun message
                msg_index = retry_count % len(fun_messages)
                print(f"\n{fun_messages[msg_index]}")
                print(f"Rate limit - optimizing timing. Waiting {wait_time:.1f}s... (attempt {retry_count}/8)")
                
                if retry_count >= 8:
                    print("\n>> Tip: The optimized CLI is working! Consider spreading requests further apart.")
                    raise Exception("API Error: Too many requests. The optimization is working - just need to pace things more.")
                
                # Enhanced progress bar
                start_time = time.time()
                while time.time() - start_time < wait_time:
                    elapsed = time.time() - start_time
                    progress = int((elapsed / wait_time) * 30)
                    bar = "#" * progress + "-" * (30 - progress)
                    remaining = wait_time - elapsed
                    print(f"[{bar}] {remaining:.1f}s remaining", end="\r", flush=True)
                    time.sleep(0.1)
                print(" " * 50, end="\r")
                
                return self._api_call_requests(key, messages, model, stream, tools, reasoning, retry_count, fun_messages)
            else:
                raise e
        except requests.exceptions.RequestException as e:
            raise Exception(f"API Error: {e}")
    
    def run_chat_loop(self, args, key: str, brave_key: Optional[str], messages: List[Dict[str, Any]]) -> None:
        """Core loop for processing messages and tool calls."""
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            reasoning_enabled = getattr(args, 'reasoning', False)
            response = self.api_call(key, messages, args.model, args.stream, self.tools, reasoning=reasoning_enabled)
            
            # Check if we're using SDK (response has different interface)
            is_sdk_response = hasattr(response, 'sdk_response')
            
            if args.stream and not is_sdk_response:
                assistant_content, tool_calls, _ = self.handle_stream_with_tools(response, brave_key, debug_mode=args.debug)
                
                # For streaming, estimate token usage since it's not provided in the stream
                if self.cost_tracking_enabled and self.token_counter and assistant_content:
                    # Validate assistant_content before token counting
                    if isinstance(assistant_content, str) and assistant_content.strip():
                        input_tokens = self.token_counter.count_messages_tokens(messages, args.model)
                        output_tokens = self.token_counter.count_tokens(assistant_content)
                    else:
                        # Handle invalid or empty content
                        input_tokens = self.token_counter.count_messages_tokens(messages, args.model)
                        output_tokens = 0
                    
                    self.token_counter.track_api_call(
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        model=args.model,
                        operation_type="chat_stream"
                    )
                    
                    # Display estimated cost info
                    from .tokenCount import GrokPricing
                    pricing = GrokPricing.get_model_pricing(args.model)
                    input_cost = GrokPricing.calculate_token_cost(input_tokens, pricing["input"])
                    output_cost = GrokPricing.calculate_token_cost(output_tokens, pricing["output"])
                    total_cost = input_cost + output_cost
                    
                    # print(f"Estimated cost: ${total_cost:.4f} ({input_tokens} -> {output_tokens} tokens)")
                
                if not tool_calls:
                    if iteration == 1 and assistant_content:
                        pass  # Normal response, no tools needed
                    return
                
                print(f"\n[Calling {len(tool_calls)} tool(s)...]")
                messages.append({"role": "assistant", "content": assistant_content or None, "tool_calls": tool_calls})
                
                # Execute tool calls directly
                tool_call_failures = 0
                all_tool_outputs = []  # Collect all tool outputs for Grid UI
                
                for i, tool_call in enumerate(tool_calls, 1):
                    tool_name = tool_call['function']['name']
                    print(f"  >> Getting {tool_name} from the toolchest ({i}/{len(tool_calls)})")
                    print(f"     {get_random_message('thinking')}")
                    
                    try:
                        # Execute with output capture for Grid UI
                        result = self.execute_tool_call(tool_call, brave_key, capture_output=True)
                        
                        # Extract captured output if present
                        if "_captured_output" in result:
                            captured = result.pop("_captured_output")
                            if captured:
                                all_tool_outputs.append(captured)
                        
                        if "error" in result:
                            tool_call_failures += 1
                            print(f"     [FAILED] {tool_name}: {result['error']}")
                        else:
                            print(f"     [DONE] {tool_name} completed successfully")
                        
                        is_debug = args.debug if args.debug is not None else bool(os.getenv("GROK_DEBUG"))
                        if is_debug:
                            print(f"Tool result: {json.dumps(result, indent=2)}")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(result)
                        })
                        
                    except Exception as e:
                        tool_call_failures += 1
                        error_result = {"error": f"Tool execution exception: {str(e)}"}
                        print(f"     [EXCEPTION] {tool_name}: {str(e)}")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(error_result)
                        })
                
                if tool_call_failures == len(tool_calls):
                    print("\n[ERROR] All tool calls failed. Asking Grok to retry...")
                    messages.append({
                        "role": "user",
                        "content": "The previous tool calls failed due to invalid arguments. Please try again with properly formatted JSON arguments."
                    })
                
                print("\n[Getting response...]")
                
            elif is_sdk_response:
                # SDK response (non-streaming for now)
                if hasattr(response, 'reasoning_content') and response.reasoning_content:
                    print(f"\n[REASONING] {response.reasoning_content}")
                    print(f"\n[RESPONSE] {response.content}")
                else:
                    print(response.content)
                
                # Track API response for cost calculation
                response_json = response.json()
                self.track_api_response(response_json, args.model, "chat")
                
                # No tool calls support in basic SDK implementation yet
                return
                
            else:
                # Non-streaming mode (requests)
                response_json = response.json()
                message = response_json["choices"][0]["message"]
                
                # Track API response for cost calculation
                self.track_api_response(response_json, args.model, "chat")
                
                if "tool_calls" not in message:
                    if "content" in message and message["content"]:
                        print(message["content"])
                    return
                
                if "content" in message and message["content"]:
                    print(message["content"])
                
                print(f"\n[Calling {len(message['tool_calls'])} tool(s)...]")
                messages.append(message)
                
                # Execute tool calls directly
                for i, tool_call in enumerate(message["tool_calls"], 1):
                    tool_name = tool_call['function']['name']
                    print(f"  >> Getting {tool_name} from the toolchest ({i}/{len(message['tool_calls'])})")
                    print(f"     {get_random_message('thinking')}")
                    try:
                        result = self.execute_tool_call(tool_call, brave_key)
                        
                        if "error" in result:
                            print(f"     [FAILED] {tool_name}: {result['error']}")
                        else:
                            print(f"     [DONE] {tool_name} completed successfully")
                        
                        is_debug = args.debug if args.debug is not None else bool(os.getenv("GROK_DEBUG"))
                        if is_debug:
                            print(f"Tool result: {json.dumps(result, indent=2)}")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(result)
                        })
                        
                    except Exception as e:
                        error_result = {"error": f"Tool execution exception: {str(e)}"}
                        print(f"     [EXCEPTION] {tool_name}: {str(e)}")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(error_result)
                        })
                
                print("\n[Getting response...]")
        
        if iteration >= max_iterations:
            print("\n[Warning: Maximum iterations reached]")
    
    def display_startup_message(self):
        """Display an optimized startup message."""
        print(f"\n{get_random_message('startup')}")
        print(">> This version includes advanced rate limiting and request optimization!")
        print(">> Features: Smart batching, caching, and intelligent request spacing\n")
    
    def display_queue_status(self):
        """Display current optimization status."""
        status = self.request_manager.get_queue_status()
        if status["queue_length"] > 0 or status["cache_size"] > 0:
            print(f">> Queue: {status['queue_length']} | Cache: {status['cache_size']} items")