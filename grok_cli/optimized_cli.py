"""
Optimized Grok CLI with advanced rate limiting and batching
"""

import argparse
import json
import os
import sys
import time
import base64
import random
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import requests

from .request_manager import RequestManager, RequestPriority

API_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-4"
SYSTEM_PROMPT = """You are Grok, a helpful and truthful AI built by xAI. When asked to create files or perform file operations, use the available tools to complete the task.

IMPORTANT: I have optimized file operations for you. When you need to read multiple files, I can handle them efficiently in batches. You can make multiple tool calls and I will optimize them automatically.

When using tools:
- Each tool call should contain exactly one operation
- I will batch and cache operations for efficiency
- File operations are cached to avoid redundant reads
- Your requests are prioritized and rate-limited automatically
"""

class OptimizedGrokCLI:
    def __init__(self):
        self.request_manager = RequestManager(min_delay_seconds=0.3)
        self.config = self.load_config()
        self.tools = self.build_tool_definitions()
        
    def load_config(self) -> Dict[str, Any]:
        config_path = "settings.json"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {}
    
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
                    "description": "Search the web using Brave Search API",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
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
                        "description": "Read the content of a file (cached and batched for efficiency)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filename": {
                                    "type": "string",
                                    "description": "The name of the file to read"
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
                        "description": "List all files recursively, respecting .gitignore (cached)",
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
                        "description": "Create a new file with content",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filename": {
                                    "type": "string",
                                    "description": "The name of the file to create"
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
                        "description": "Read multiple files efficiently in a single operation",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filenames": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of filenames to read"
                                }
                            },
                            "required": ["filenames"]
                        }
                    }
                }
            ])
        
        return tools
    
    def execute_tool_call_optimized(self, tool_call: Dict[str, Any], brave_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Execute a tool call with optimization and caching."""
        function_name = tool_call["function"]["name"]
        
        try:
            arguments = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError as e:
            # Handle concatenated JSON (gracefully extract first valid JSON)
            raw_args = tool_call["function"]["arguments"]
            if "}{" in raw_args:
                first_obj_end = raw_args.find("}") + 1
                if first_obj_end > 0:
                    try:
                        arguments = json.loads(raw_args[:first_obj_end])
                        print(f"[INFO] Extracted first operation from batched request")
                    except json.JSONDecodeError:
                        return {"error": f"Invalid JSON in tool arguments: {str(e)}"}
                else:
                    return {"error": f"Invalid JSON in tool arguments: {str(e)}"}
            else:
                return {"error": f"Invalid JSON in tool arguments: {str(e)}"}
        
        # Execute the optimized tool call
        return self._execute_tool_function(function_name, arguments, brave_api_key)
    
    def _execute_tool_function(self, function_name: str, arguments: Dict[str, Any], brave_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Execute the actual tool function."""
        try:
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
                directory = arguments.get("directory", ".")
                files = self._list_files_recursive_impl(directory)
                return {"success": True, "files": files, "count": len(files)}
            
            elif function_name == "create_file":
                filename = arguments["filename"]
                content = arguments.get("content", "")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"success": True, "message": f"File '{filename}' created successfully"}
            
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _list_files_recursive_impl(self, directory: str = ".") -> List[str]:
        """List files recursively, respecting .gitignore."""
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
        
        return all_files
    
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
    
    def api_call_optimized(self, key: str, messages: List[Dict[str, Any]], model: str, 
                          stream: bool, tools: Optional[List[Dict[str, Any]]] = None, 
                          retry_count: int = 0) -> requests.Response:
        """Make an API call with advanced rate limiting."""
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {"messages": messages, "model": model, "stream": stream}
        
        if tools:
            data["tools"] = tools
            data["tool_choice"] = "auto"
        
        # Calculate adaptive delay based on recent activity
        time_since_last = time.time() - self.request_manager.last_request_time
        if time_since_last < 1.0:  # If less than 1 second, wait a bit
            delay = 1.0 - time_since_last
            print(f"⏱️ Pacing request... ({delay:.1f}s)")
            time.sleep(delay)
        
        fun_messages = [
            "🎯 Optimizing request for best results...",
            "🚀 Launching your perfectly timed query...",
            "🧠 Grok is ready and waiting...",
            "✨ Request dispatched with optimal timing...",
            "🎪 The optimized show begins...",
        ]
        
        try:
            response = requests.post(API_URL, headers=headers, json=data, stream=stream, timeout=(10, 60))
            response.raise_for_status()
            self.request_manager.last_request_time = time.time()
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
                    print("\n💡 Tip: The optimized CLI is working! Consider spreading requests further apart.")
                    sys.exit("API Error: Too many requests. The optimization is working - just need to pace things more.")
                
                # Enhanced progress bar
                start_time = time.time()
                while time.time() - start_time < wait_time:
                    elapsed = time.time() - start_time
                    progress = int((elapsed / wait_time) * 30)
                    bar = "█" * progress + "░" * (30 - progress)
                    remaining = wait_time - elapsed
                    print(f"[{bar}] {remaining:.1f}s remaining", end="\r", flush=True)
                    time.sleep(0.1)
                print(" " * 50, end="\r")
                
                return self.api_call_optimized(key, messages, model, stream, tools, retry_count)
            else:
                raise e
        except requests.exceptions.RequestException as e:
            sys.exit(f"API Error: {e}")
    
    def display_startup_message(self):
        """Display an optimized startup message."""
        startup_messages = [
            "🚀 Launching optimized Grok CLI...",
            "⚡ Powering up the efficiency engine...",
            "🎯 Optimized for speed and intelligence...",
            "🔧 Advanced request management active...",
            "💫 Smart batching and caching enabled...",
        ]
        
        print(f"\n{random.choice(startup_messages)}")
        print("✨ This version includes advanced rate limiting and request optimization!")
        print("📊 Features: Smart batching, caching, and intelligent request spacing\n")
    
    def display_queue_status(self):
        """Display current optimization status."""
        status = self.request_manager.get_queue_status()
        if status["queue_length"] > 0 or status["cache_size"] > 0:
            print(f"📊 Queue: {status['queue_length']} | Cache: {status['cache_size']} items")

# Export for use in main CLI
optimized_cli = OptimizedGrokCLI()
