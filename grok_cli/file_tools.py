"""File operations and tool handling for Grok CLI."""

import json
import os
import requests
from typing import Dict, Any, List, Optional
from .utils import load_config, should_ignore, load_gitignore_patterns

# Cache for file contents to avoid redundant reads
file_cache = {}

def build_tool_definitions():
    """Build tool definitions for enabled MCP servers."""
    config = load_config()
    tools = []
    mcp_servers = config.get("mcp_servers", {})
    
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
    
    # Local File System tools
    if mcp_servers.get("local_file_system", {}).get("enabled", False):
        tools.extend([
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
                    "name": "read_file",
                    "description": "Read the content of a file",
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
                    "name": "append_to_file",
                    "description": "Append content to an existing file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "The name of the file to append to"
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to append"
                            }
                        },
                        "required": ["filename", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Delete a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "The name of the file to delete"
                            }
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List files in the current directory",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files_recursive",
                    "description": "List all files recursively in the project, respecting .gitignore patterns",
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
                    "name": "create_project_overview",
                    "description": "Create a comprehensive table of contents/overview of the entire project structure with file descriptions. This is perfect for documenting projects and understanding codebases.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "output_filename": {
                                "type": "string",
                                "description": "Name of the output file (default: tableofcontents.md)",
                                "default": "tableofcontents.md"
                            },
                            "include_summary": {
                                "type": "boolean",
                                "description": "Include file count summary (default: true)",
                                "default": True
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "smart_codebase_read",
                    "description": "Intelligently read a codebase by prioritizing important files and batching reads for efficiency. Returns a comprehensive overview.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to analyze (default: current directory)",
                                "default": "."
                            },
                            "max_files": {
                                "type": "integer",
                                "description": "Maximum number of files to read (default: 50)",
                                "default": 50
                            }
                        }
                    }
                }
            }
        ])
    
    return tools

def list_files_recursive_impl(directory=".", gitignore_patterns=None):
    """Recursively list all files in directory respecting .gitignore."""
    if gitignore_patterns is None:
        gitignore_patterns = load_gitignore_patterns()
    
    all_files = []
    for root, dirs, files in os.walk(directory):
        # Remove directories that should be ignored
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), gitignore_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            
            if not should_ignore(relative_path, gitignore_patterns):
                all_files.append(relative_path)
    
    return all_files

def prioritize_files(files: List[str]) -> List[str]:
    """Prioritize files for reading based on importance."""
    priority_patterns = {
        1: ['readme.md', 'readme.rst', 'readme.txt', 'readme'],
        2: ['setup.py', 'setup.cfg', 'pyproject.toml', 'package.json'],
        3: ['requirements.txt', 'requirements.in', 'poetry.lock', 'package-lock.json'],
        4: ['__init__.py', 'main.py', 'app.py', 'index.py', 'cli.py'],
        5: ['config.py', 'settings.py', 'configuration.py', '.env', '.env.example'],
        6: ['.gitignore', 'Dockerfile', 'docker-compose.yml', 'Makefile'],
    }
    
    prioritized = []
    remaining = files.copy()
    
    # Add files by priority
    for priority_level in sorted(priority_patterns.keys()):
        patterns = priority_patterns[priority_level]
        for pattern in patterns:
            for file in remaining[:]:
                if file.lower().endswith(pattern.lower()) or os.path.basename(file).lower() == pattern.lower():
                    prioritized.append(file)
                    remaining.remove(file)
    
    # Add remaining Python files
    python_files = [f for f in remaining if f.endswith('.py')]
    prioritized.extend(sorted(python_files))
    remaining = [f for f in remaining if not f.endswith('.py')]
    
    # Add remaining source files
    source_extensions = ['.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.go', '.rs']
    source_files = [f for f in remaining if any(f.endswith(ext) for ext in source_extensions)]
    prioritized.extend(sorted(source_files))
    remaining = [f for f in remaining if f not in source_files]
    
    # Add remaining files (but skip common non-source files)
    skip_extensions = ['.pyc', '.pyo', '.log', '.db', '.sqlite', '.cache', '.tmp', '.bak']
    remaining = [f for f in remaining if not any(f.endswith(ext) for ext in skip_extensions)]
    prioritized.extend(sorted(remaining))
    
    return prioritized

def batch_read_files(filenames: List[str]) -> Dict[str, Any]:
    """Read multiple files efficiently, using cache when available."""
    results = {}
    
    for filename in filenames:
        # Check cache first
        if filename in file_cache:
            results[filename] = file_cache[filename]
            continue
            
        # Read file
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                result = {"success": True, "content": content}
                file_cache[filename] = result  # Cache the result
                results[filename] = result
            except Exception as e:
                results[filename] = {"error": str(e)}
        else:
            results[filename] = {"error": f"File '{filename}' not found"}
    
    return results

def smart_codebase_read(directory=".", max_files=50):
    """Intelligently read a codebase by prioritizing important files."""
    # Get all files
    all_files = list_files_recursive_impl(directory)
    
    # Prioritize files
    prioritized_files = prioritize_files(all_files)
    
    # Take only the most important files up to max_files
    files_to_read = prioritized_files[:max_files]
    
    # Batch read the files
    file_contents = batch_read_files(files_to_read)
    
    # Create a summary
    summary = {
        "total_files": len(all_files),
        "files_read": len(files_to_read),
        "file_structure": all_files,
        "prioritized_files": files_to_read,
        "file_contents": file_contents,
        "cache_hits": sum(1 for f in files_to_read if f in file_cache)
    }
    
    return summary

def execute_tool_call(tool_call, brave_api_key=None, debug_mode=None):
    """Execute a tool call and return the result."""
    function_name = tool_call["function"]["name"]
    
    # Check debug mode (command line arg overrides environment variable)
    is_debug = debug_mode if debug_mode is not None else bool(os.getenv("GROK_DEBUG"))
    
    # Debug logging
    if is_debug:
        print(f"[DEBUG] Raw tool call: {json.dumps(tool_call, indent=2)}")
    
    try:
        arguments = json.loads(tool_call["function"]["arguments"])
    except json.JSONDecodeError as e:
        # Special handling for concatenated JSON objects (common with read_file)
        raw_args = tool_call["function"]["arguments"]
        if function_name == "read_file" and "}{" in raw_args:
            print(f"\n[INFO] Detected multiple file read request, will batch process")
            # Extract all filenames from concatenated JSON
            filenames = []
            parts = raw_args.split("}{")
            for i, part in enumerate(parts):
                if i == 0:
                    part = part + "}"
                elif i == len(parts) - 1:
                    part = "{" + part
                else:
                    part = "{" + part + "}"
                try:
                    obj = json.loads(part)
                    if "filename" in obj:
                        filenames.append(obj["filename"])
                except:
                    pass
            
            if filenames:
                # Batch process all files
                print(f"[INFO] Batch reading {len(filenames)} files...")
                results = batch_read_files(filenames)
                return {"success": True, "batch_results": results, "files_read": len(filenames)}
            else:
                return {"error": f"Could not extract filenames from batched request"}
        else:
            print(f"\n[ERROR] Failed to parse tool arguments for {function_name}")
            print(f"Raw arguments: {repr(tool_call['function']['arguments'])}")
            print(f"Error: {e}")
            return {"error": f"Invalid JSON in tool arguments: {str(e)}"}
    
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
        
        elif function_name == "create_file":
            filename = arguments["filename"]
            content = arguments.get("content", "")
            with open(filename, "w") as f:
                f.write(content)
            return {"success": True, "message": f"File '{filename}' created successfully"}
        
        elif function_name == "read_file":
            filename = arguments["filename"]
            # Use cache if available
            if filename in file_cache:
                return file_cache[filename]
            
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    content = f.read()
                result = {"success": True, "content": content}
                file_cache[filename] = result  # Cache the result
                return result
            else:
                return {"error": f"File '{filename}' not found"}
        
        elif function_name == "append_to_file":
            filename = arguments["filename"]
            content = arguments["content"]
            if os.path.exists(filename):
                with open(filename, "a") as f:
                    f.write(content)
                # Invalidate cache
                if filename in file_cache:
                    del file_cache[filename]
                return {"success": True, "message": f"Content appended to '{filename}'"}
            else:
                return {"error": f"File '{filename}' not found"}
        
        elif function_name == "delete_file":
            filename = arguments["filename"]
            if os.path.exists(filename):
                os.remove(filename)
                # Invalidate cache
                if filename in file_cache:
                    del file_cache[filename]
                return {"success": True, "message": f"File '{filename}' deleted successfully"}
            else:
                return {"error": f"File '{filename}' not found"}
        
        elif function_name == "list_files":
            files = [f for f in os.listdir(".") if os.path.isfile(f)]
            return {"success": True, "files": files}
        
        elif function_name == "list_files_recursive":
            directory = arguments.get("directory", ".")
            files = list_files_recursive_impl(directory)
            return {"success": True, "files": files, "count": len(files)}
        
        elif function_name == "smart_codebase_read":
            directory = arguments.get("directory", ".")
            max_files = arguments.get("max_files", 50)
            result = smart_codebase_read(directory, max_files)
            return {"success": True, **result}
        
        elif function_name == "create_project_overview":
            output_filename = arguments.get("output_filename", "tableofcontents.md")
            include_summary = arguments.get("include_summary", True)
            
            # Use smart codebase read to get comprehensive info
            codebase_info = smart_codebase_read(".", max_files=100)
            all_files = codebase_info["file_structure"]
            
            def describe_file(filepath):
                """Generate a description for a file based on its name and extension."""
                name = os.path.basename(filepath)
                ext = os.path.splitext(filepath)[1].lower()
                
                # Special files
                if name.lower() == 'readme.md':
                    return "Main project documentation and overview"
                elif name.lower() == 'setup.py':
                    return "Python package setup and installation configuration"
                elif name.lower() == 'requirements.txt':
                    return "Python package dependencies list"
                elif name.lower() == '.gitignore':
                    return "Git ignore patterns for version control"
                elif name.lower() == 'license':
                    return "Project license terms and conditions"
                elif name.lower() == 'dockerfile':
                    return "Docker container build instructions"
                
                # Python files
                elif ext == '.py':
                    if 'test' in name.lower():
                        return f"Test file - {name.replace('.py', '').replace('test_', '').replace('_', ' ')}"
                    elif name == '__init__.py':
                        return "Python package initialization file"
                    elif name == 'cli.py':
                        return "Command-line interface implementation"
                    elif name == 'main.py':
                        return "Main application entry point"
                    else:
                        return f"Python module - {name.replace('.py', '').replace('_', ' ')}"
                
                # Configuration files
                elif ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
                    return f"Configuration file - {name.replace(ext, '').replace('_', ' ')}"
                
                # Documentation
                elif ext in ['.md', '.rst', '.txt']:
                    if 'readme' in name.lower():
                        return "Documentation file"
                    else:
                        return f"Documentation - {name.replace(ext, '').replace('_', ' ')}"
                
                # Web files
                elif ext in ['.html', '.css', '.js']:
                    return f"Web asset - {ext[1:].upper()} file"
                
                # Data files
                elif ext in ['.csv', '.json', '.xml', '.sql']:
                    return f"Data file - {ext[1:].upper()} format"
                
                # Default
                else:
                    return f"File - {name}"
            
            # Create table of contents content
            content = []
            content.append("# Project Table of Contents")
            content.append("")
            content.append("This is an automated table of contents generated by Grok CLI.")
            content.append("")
            content.append("## Project Structure")
            content.append("")
            
            # Group files by directory
            dirs = {}
            for file in sorted(all_files):
                dir_name = os.path.dirname(file) if os.path.dirname(file) else "."
                if dir_name not in dirs:
                    dirs[dir_name] = []
                dirs[dir_name].append(file)
            
            # Generate content
            for dir_name in sorted(dirs.keys()):
                if dir_name == ".":
                    content.append("### Root Directory")
                else:
                    content.append(f"### {dir_name}/")
                content.append("")
                
                for file in sorted(dirs[dir_name]):
                    description = describe_file(file)
                    content.append(f"- **{os.path.basename(file)}** - {description}")
                content.append("")
            
            # Add summary if requested
            if include_summary:
                content.append("## Summary")
                content.append("")
                content.append(f"Total files: {len(all_files)}")
                
                # Count by type
                py_files = [f for f in all_files if f.endswith('.py')]
                test_files = [f for f in py_files if 'test' in f.lower()]
                config_files = [f for f in all_files if any(f.endswith(ext) for ext in ['.json', '.yaml', '.yml', '.toml', '.ini'])]
                
                content.append(f"Python files: {len(py_files)}")
                content.append(f"Test files: {len(test_files)}")
                content.append(f"Configuration files: {len(config_files)}")
                content.append("")
                content.append("Generated automatically by Grok CLI.")
                content.append(f"Files cached during generation: {len(file_cache)}")
            
            # Write to file
            with open(output_filename, "w") as f:
                f.write("\n".join(content))
            
            return {
                "success": True, 
                "message": f"Project overview created in '{output_filename}'",
                "files_processed": len(all_files),
                "output_file": output_filename,
                "cache_size": len(file_cache)
            }
        
        else:
            return {"error": f"Unknown function: {function_name}"}
            
    except Exception as e:
        return {"error": str(e)}

def clear_file_cache():
    """Clear the file cache."""
    global file_cache
    file_cache.clear()
