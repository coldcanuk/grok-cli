#!/usr/bin/env python3
"""Debug why /help command is not displaying."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'grok_cli'))

from grokit import GroKitGridIntegration
from datetime import datetime

def test_help_command():
    """Test the help command execution path."""
    print("Testing /help command execution...")
    print("=" * 60)
    
    # Create instance
    grid = GroKitGridIntegration()
    
    # Test 1: Check if command is recognized
    print("\n1. Testing command recognition:")
    result = grid._process_special_commands("/help")
    print(f"   Command result: {result}")
    print(f"   Should be None: {result is None}")
    
    # Test 2: Check AI content after command
    print("\n2. Checking AI content after command:")
    print(f"   Number of messages: {len(grid.renderer.ai_content)}")
    if grid.renderer.ai_content:
        for i, msg in enumerate(grid.renderer.ai_content):
            print(f"   Message {i}: role={msg.get('role')}, timestamp={msg.get('timestamp')}")
            content = msg.get('content', '')
            print(f"   Content length: {len(content)}")
            print(f"   Content preview: {content[:100]}...")
    
    # Test 3: Try calling _show_help directly
    print("\n3. Testing _show_help() directly:")
    initial_count = len(grid.renderer.ai_content)
    grid._show_help()
    final_count = len(grid.renderer.ai_content)
    print(f"   Messages before: {initial_count}")
    print(f"   Messages after: {final_count}")
    print(f"   New messages added: {final_count - initial_count}")
    
    # Test 4: Check the help message content
    print("\n4. Checking help message content:")
    if final_count > initial_count:
        last_msg = grid.renderer.ai_content[-1]
        content = last_msg.get('content', '')
        print(f"   Content starts with: {repr(content[:50])}")
        print(f"   Contains 'GroKit': {'GroKit' in content}")
        print(f"   Contains '/help': {'/help' in content}")
    
    # Test 5: Check if markdown rendering might be the issue
    print("\n5. Testing markdown rendering:")
    help_msg = """# GroKit Grid Commands

## Available Commands:

- `/leader [objective]` - Strategic planning mode"""
    
    try:
        lines = grid.renderer.markdown_renderer.render_markdown(help_msg)
        print(f"   Rendered {len(lines)} lines successfully")
        for i, line in enumerate(lines[:5]):
            print(f"   Line {i}: {repr(line)}")
    except Exception as e:
        print(f"   ERROR rendering markdown: {e}")
    
    print("\n" + "=" * 60)
    print("Debug complete!")

if __name__ == "__main__":
    test_help_command()
