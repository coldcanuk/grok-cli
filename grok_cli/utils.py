"""Shared utility functions for Grok CLI."""

import json
import os
import sys
import base64
import fnmatch
import random
import re

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

def is_wsl_environment():
    """Check if running in WSL environment."""
    try:
        # Check multiple WSL indicators
        wsl_env = os.getenv('WSLENV')
        wsl_distro = os.getenv('WSL_DISTRO_NAME')
        
        if wsl_env or wsl_distro:
            return True
            
        # Check for WSL in proc/version (Linux subsystem)
        if os.path.exists('/proc/version'):
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                return 'microsoft' in version_info or 'wsl' in version_info
                
        # Check if we're in a Linux-like environment but on Windows paths
        if os.path.exists('/mnt/c') or 'microsoft' in os.uname().release.lower():
            return True
            
        return False
    except:
        return False

def should_strip_emojis():
    """Determine if emojis should be stripped based on environment."""
    # Check if terminal can handle Unicode emojis
    stdout_encoding = getattr(sys.stdout, 'encoding', None) or 'utf-8'
    can_display_unicode = stdout_encoding.lower() not in ('cp1252', 'ascii')
    
    # Check environment variable override
    grok_strip = os.getenv('GROK_STRIP_EMOJIS', '').lower()
    if grok_strip:
        # Explicit override - but only if terminal can handle it
        if grok_strip in ('0', 'false', 'no') and not can_display_unicode:
            # User wants emojis but terminal can't display them - warn and strip anyway
            return True
        return grok_strip in ('1', 'true', 'yes')
    
    # Auto-detect based on terminal capabilities
    if not can_display_unicode or is_wsl_environment() or sys.platform == 'win32':
        return True
    
    return False

def strip_emojis_from_message(message):
    """Strip emojis from message and replace with >> prefix."""
    if not message:
        return ">> Loading..."
    
    # More comprehensive emoji regex pattern
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "]+", 
        flags=re.UNICODE
    )
    
    # Remove emojis and clean up
    clean_message = emoji_pattern.sub('', message).strip()
    
    # If message starts with whitespace after emoji removal, clean it
    if clean_message and not clean_message.startswith('>>'):
        clean_message = ">> " + clean_message
    elif not clean_message:
        clean_message = ">> Processing..."
    
    return clean_message

def load_messages(message_type="startup"):
    """Load messages from JSON files with fallback to simple messages."""
    try:
        # Get the directory where this utils.py file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        if message_type == "startup":
            json_path = os.path.join(current_dir, "startup.json")
        elif message_type == "thinking":
            json_path = os.path.join(current_dir, "thinking.json")
        else:
            return [">> Loading..."]
        
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f)
            
            # Extract and process messages based on environment
            messages = []
            strip_emojis = should_strip_emojis()
            
            for item in messages_data:
                try:
                    message = item.get("message", "")
                    if message:
                        if strip_emojis:
                            clean_message = strip_emojis_from_message(message)
                        else:
                            clean_message = message
                        messages.append(clean_message)
                except (UnicodeEncodeError, UnicodeDecodeError):
                    # Fallback message if Unicode issues
                    messages.append(">> Processing...")
            
            return messages if messages else [">> Loading..."]
        
    except Exception as e:
        # Fallback messages if file loading fails
        pass
    
    # Fallback messages
    if message_type == "startup":
        return [
            ">> Launching optimized Grok CLI...",
            ">> Powering up the efficiency engine...",
            ">> Advanced request management active...",
            ">> Smart batching and caching enabled..."
        ]
    elif message_type == "thinking":
        return [
            ">> Grok is pondering your request...",
            ">> Computing the meaning of life... and your query...",
            ">> The mental circus is in full swing...",
            ">> Neurons are firing in chaotic patterns..."
        ]
    else:
        return [">> Processing..."]

def get_random_message(message_type="startup"):
    """Get a random message of the specified type."""
    messages = load_messages(message_type)
    message = random.choice(messages)
    
    # Handle display encoding issues
    try:
        # Try to encode the message to detect Unicode issues
        message.encode(sys.stdout.encoding or 'utf-8')
        return message
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fall back to stripped version if encoding fails
        return strip_emojis_from_message(message)

def load_grok_context(src_directory):
    """Load context from .grok directory in the source directory."""
    grok_dir = os.path.join(src_directory, '.grok')
    context_parts = []
    
    if not os.path.exists(grok_dir):
        return ""
    
    # Load README.md first if it exists
    readme_path = os.path.join(grok_dir, 'README.md')
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read().strip()
                if readme_content:
                    context_parts.append(f"# .grok Directory Context\n{readme_content}")
        except Exception as e:
            context_parts.append(f"# .grok Directory Context\nNote: Could not read README.md ({e})")
    
    # Load all .mdc files
    mdc_files = []
    try:
        for filename in os.listdir(grok_dir):
            if filename.endswith('.mdc'):
                mdc_files.append(filename)
    except Exception:
        pass
    
    if mdc_files:
        mdc_files.sort()  # Consistent ordering
        for filename in mdc_files:
            file_path = os.path.join(grok_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        context_parts.append(f"# Context from {filename}\n{content}")
            except Exception as e:
                context_parts.append(f"# Context from {filename}\nNote: Could not read file ({e})")
    
    if context_parts:
        full_context = "\n\n".join(context_parts)
        return f"\n\n# USER PROJECT CONTEXT\nThe following context has been loaded from the .grok directory in the source project:\n\n{full_context}\n\n"
    
    return ""

def create_grok_directory_template(src_directory):
    """Create .grok directory with README.md template if it doesn't exist."""
    grok_dir = os.path.join(src_directory, '.grok')
    readme_path = os.path.join(grok_dir, 'README.md')
    
    if not os.path.exists(grok_dir):
        os.makedirs(grok_dir, exist_ok=True)
    
    if not os.path.exists(readme_path):
        readme_template = """# .grok Directory

This directory contains context files for Grok CLI to understand your project better.

## Purpose
- **README.md** (this file): Describes your project context and goals
- **\*.mdc files**: Markdown context files with specific instructions, coding standards, or project knowledge

## How it works
When you run `grok-cli --src /path/to/your/project`, Grok CLI will:
1. Read this README.md for project overview
2. Load all .mdc files for additional context and instructions
3. Include this context in every conversation with Grok

## Example .mdc files you might create:
- `coding-standards.mdc` - Your coding style and conventions
- `architecture.mdc` - System architecture and design patterns
- `api-docs.mdc` - API documentation and usage examples
- `troubleshooting.mdc` - Common issues and solutions

## Tips
- Keep .mdc files focused on specific topics
- Use clear, descriptive filenames
- Include examples and specific instructions
- Update context as your project evolves

---
*This directory is inspired by Cursor's .cursorrules concept*
"""
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_template)
            return True
        except Exception:
            return False
    
    return False
