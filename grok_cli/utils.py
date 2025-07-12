"""Shared utility functions for Grok CLI."""

import json
import os
import sys
import base64
import fnmatch

def load_config():
    config_path = "settings.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}

def get_api_key(args):
    key = args.api_key or os.getenv("XAI_API_KEY")
    if not key:
        sys.exit("Error: No API key provided. Set XAI_API_KEY env var or use --api-key.")
    if args.api_key:
        print("Warning: For security, prefer env var over --api-key to avoid exposure in history.")
    
    brave_api_key = None
    config = load_config()
    mcp_servers = config.get("mcp_servers", {})
    
    if mcp_servers.get("brave_search", {}).get("enabled", False):
        brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not brave_api_key:
            print("Warning: Brave Search is enabled but BRAVE_SEARCH_API_KEY not found.")

    return key, brave_api_key

def build_vision_content(prompt, image):
    content = [{"type": "text", "text": prompt}]
    if image:
        if os.path.isfile(image):
            with open(image, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
            url = f"data:image/{os.path.splitext(image)[1][1:]};base64,{img_data}"
        else:
            url = image  # Assume URL
        content.append({"type": "image_url", "image_url": {"url": url}})
    return content

def load_gitignore_patterns():
    """Load patterns from .gitignore file."""
    patterns = []
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def should_ignore(path, patterns):
    """Check if a path should be ignored based on gitignore patterns."""
    # Basic implementation - matches exact strings and simple wildcards
    for pattern in patterns:
        # Handle directory patterns
        if pattern.endswith('/'):
            if path.startswith(pattern) or ('/' + pattern) in path:
                return True
        # Handle file patterns
        elif pattern in path or path.endswith(pattern):
            return True
        # Handle wildcard patterns (simplified)
        elif '*' in pattern:
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
    return False
