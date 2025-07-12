"""
Grok CLI - A high-performance command-line interface for xAI's Grok API.

Features:
- Advanced rate limiting with intelligent request pacing
- Interactive chat with conversation history
- Vision support for image processing
- MCP server integration for function calling
- Optimized performance with request batching and caching
"""

__version__ = "1.0.0"
__author__ = "Grok CLI Team"
__email__ = "noreply@example.com"
__license__ = "MIT"

from .cli import main
from .engine import GrokEngine

__all__ = ["main", "GrokEngine", "__version__"]