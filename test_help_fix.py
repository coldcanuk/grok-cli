#!/usr/bin/env python3
"""Test script to verify the /help command works with the enhanced markdown renderer."""

import sys
import os

# Add the grok_cli directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'grok_cli'))

from grokit import GroKitGrid
from markdown_renderer import RICH_AVAILABLE

def test_help_command():
    """Test that the /help command displays properly."""
    print("Testing /help Command Display")
    print("=" * 70)
    print(f"Rich library available: {RICH_AVAILABLE}")
    print("=" * 70)
    
    # Create a GroKitGrid instance
    grid = GroKitGrid()
    
    # Simulate the help command
    print("\nSimulating /help command...")
    grid._show_help()
    
    # Check that help was added to the AI content
    if grid.renderer.ai_content:
        last_message = grid.renderer.ai_content[-1]
        print(f"\nLast message role: {last_message.get('role')}")
        print(f"Message timestamp: {last_message.get('timestamp')}")
        print("\nHelp content preview:")
        print("-" * 70)
        
        # Show the raw content
        content = last_message.get('content', '')
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 70)
        
        # Show the rendered lines if available
        if 'rendered_lines' in last_message:
            print("\nRendered output:")
            print("-" * 70)
            for line in last_message['rendered_lines'][:20]:
                print(line)
            if len(last_message['rendered_lines']) > 20:
                print(f"... and {len(last_message['rendered_lines']) - 20} more lines")
        else:
            print("\nNo rendered lines found - checking markdown renderer...")
            # Manually render the content to see what happens
            lines = grid.renderer.markdown_renderer.render_markdown(content)
            print(f"Manually rendered {len(lines)} lines:")
            for line in lines[:20]:
                print(line)
    else:
        print("ERROR: No messages found in AI content!")
    
    print("\n" + "=" * 70)
    print("Test completed!")

if __name__ == "__main__":
    test_help_command()
