#!/usr/bin/env python3
"""
Script to connect to x.ai API and list all available models.
Returns the results in JSON format.
"""

import requests
import json
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

# Try to import python-dotenv for .env file support
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

def load_environment():
    """
    Load environment variables from .env file if available.
    """
    if DOTENV_AVAILABLE:
        # Look for .env file in the project root (parent directory of scripts)
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            print(f"📁 Loaded environment from {env_path}", file=sys.stderr)
        else:
            print("⚠️  .env file not found, using system environment variables", file=sys.stderr)
    else:
        print("⚠️  python-dotenv not installed, using system environment variables", file=sys.stderr)
        print("   Install with: pip install python-dotenv", file=sys.stderr)

def get_xai_models(api_key: str, base_url: str = "https://api.x.ai/v1") -> Optional[Dict]:
    """
    Connect to x.ai API and fetch all available models.
    
    Args:
        api_key: The x.ai API key
        base_url: The base URL for the x.ai API
        
    Returns:
        Dictionary containing the API response with model data, or None if error
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Make request to the models endpoint
        response = requests.get(f"{base_url}/models", headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request to x.ai API: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        return None

def format_models_output(models_data: Dict) -> str:
    """
    Format the models data for pretty JSON output.
    
    Args:
        models_data: The raw API response containing model data
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(models_data, indent=2, ensure_ascii=False)

def main():
    """
    Main function to execute the script.
    """
    # Load environment variables from .env file
    load_environment()
    
    # Get API key from environment variable
    # Check both XAI_API_KEY and X_API_KEY for compatibility
    api_key = os.getenv("XAI_API_KEY") or os.getenv("X_API_KEY")
    
    if not api_key:
        print("Error: API key not found. Please set XAI_API_KEY or X_API_KEY in your .env file", file=sys.stderr)
        print("Example in .env: X_API_KEY=your-api-key-here", file=sys.stderr)
        sys.exit(1)
    
    # Optional: Allow custom base URL via environment variable
    base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
    
    print(f"🔗 Connecting to x.ai API at {base_url}", file=sys.stderr)
    print(f"🔑 Using API key: {api_key[:8]}...", file=sys.stderr)
    
    # Fetch models from x.ai API
    models_data = get_xai_models(api_key, base_url)
    
    if models_data is None:
        print("Failed to fetch models from x.ai API", file=sys.stderr)
        sys.exit(1)
    
    # Output the JSON data
    print(format_models_output(models_data))
    
    # Optional: Show summary to stderr
    if "data" in models_data:
        model_count = len(models_data["data"])
        print(f"✅ Successfully fetched {model_count} models from x.ai", file=sys.stderr)
    else:
        print("⚠️  Unexpected response format from x.ai API", file=sys.stderr)

if __name__ == "__main__":
    main()