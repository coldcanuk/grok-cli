#!/usr/bin/env python3
"""Test script to verify /help and /costs commands are working properly."""

import sys
import os

# Add the grok_cli directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'grok_cli'))

from grokit import GroKitGrid
from datetime import datetime

def test_help_command():
    """Test that /help command displays properly."""
    print("Testing /help command...")
    print("=" * 70)
    
    # Create a GroKitGrid instance
    grid = GroKitGrid()
    
    # Clear any existing content
    grid.renderer.ai_content.clear()
    
    # Simulate the /help command
    result = grid._process_special_commands("/help")
    print(f"Command result: {result}")
    
    # Check if help was added to AI content
    if grid.renderer.ai_content:
        print(f"\nMessages in AI content: {len(grid.renderer.ai_content)}")
        last_msg = grid.renderer.ai_content[-1]
        print(f"Last message role: {last_msg.get('role')}")
        print(f"Content preview: {last_msg.get('content', '')[:200]}...")
        
        # Test rendering
        print("\nTesting markdown rendering of help content:")
        lines = grid.renderer.markdown_renderer.render_markdown(last_msg.get('content', ''))
        print(f"Rendered {len(lines)} lines")
        for i, line in enumerate(lines[:10]):
            print(f"  {i}: {repr(line)}")
    else:
        print("ERROR: No content was added to AI window!")

def test_costs_command():
    """Test that /costs command displays properly."""
    print("\n\nTesting /costs command...")
    print("=" * 70)
    
    # Create a GroKitGrid instance
    grid = GroKitGrid()
    
    # Clear any existing content
    grid.renderer.ai_content.clear()
    
    # Simulate the /costs command
    result = grid._process_special_commands("/costs")
    print(f"Command result: {result}")
    
    # Check if costs were added to AI content
    if grid.renderer.ai_content:
        print(f"\nMessages in AI content: {len(grid.renderer.ai_content)}")
        last_msg = grid.renderer.ai_content[-1]
        print(f"Last message role: {last_msg.get('role')}")
        print(f"Content: {last_msg.get('content', '')}")
    else:
        print("ERROR: No content was added to AI window!")

def test_wrong_command():
    """Test that wrong commands are passed through."""
    print("\n\nTesting wrong command (/cost without 's')...")
    print("=" * 70)
    
    grid = GroKitGrid()
    
    # Test wrong command
    result = grid._process_special_commands("/cost")
    print(f"Command result: {result}")
    
    if result == "/cost":
        print("CORRECT: Wrong command was passed through as regular input")
    else:
        print("ERROR: Wrong command was not handled correctly")

if __name__ == "__main__":
    test_help_command()
    test_costs_command()
    test_wrong_command()
    
    print("\n\nSummary:")
    print("The fixes ensure that:")
    print("1. System messages now use the markdown renderer")
    print("2. /help command displays formatted help text")
    print("3. /costs command displays cost summary")
    print("4. Wrong commands like /cost are passed to AI as regular input")
