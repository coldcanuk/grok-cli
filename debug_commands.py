#!/usr/bin/env python3
"""Debug script to test command handling in GroKit."""

import sys
import os

# Add the grok_cli directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'grok_cli'))

from grokit import GroKitGrid

def test_command_processing():
    """Test that commands are being processed correctly."""
    print("Testing Command Processing")
    print("=" * 70)
    
    # Create a GroKitGrid instance
    grid = GroKitGrid()
    
    # Test processing various commands
    test_inputs = [
        "/help",
        "/costs", 
        "/cost",  # Wrong command
        "regular input"
    ]
    
    for test_input in test_inputs:
        print(f"\nTesting input: '{test_input}'")
        result = grid._process_special_commands(test_input)
        print(f"Result: {result}")
        
        if result is None:
            print("Command was processed (returned None)")
            # Check if content was added to AI window
            if grid.renderer.ai_content:
                last_msg = grid.renderer.ai_content[-1]
                print(f"Last message role: {last_msg.get('role')}")
                print(f"Content preview: {last_msg.get('content', '')[:100]}...")
        else:
            print(f"Input passed through: '{result}'")

def test_help_rendering():
    """Test that help content is being rendered properly."""
    print("\n\n" + "=" * 70)
    print("Testing Help Rendering")
    print("=" * 70)
    
    grid = GroKitGrid()
    
    # Clear any existing content
    grid.renderer.ai_content.clear()
    
    # Call _show_help directly
    print("Calling _show_help()...")
    grid._show_help()
    
    # Check what was added
    print(f"\nNumber of messages in AI content: {len(grid.renderer.ai_content)}")
    
    if grid.renderer.ai_content:
        for i, msg in enumerate(grid.renderer.ai_content):
            print(f"\nMessage {i}:")
            print(f"  Role: {msg.get('role')}")
            print(f"  Timestamp: {msg.get('timestamp')}")
            print(f"  Content length: {len(msg.get('content', ''))}")
            
            # Check if markdown was rendered
            content = msg.get('content', '')
            if content:
                # Try to render it manually
                print("\n  Attempting manual render:")
                lines = grid.renderer.markdown_renderer.render_markdown(content)
                print(f"  Rendered {len(lines)} lines")
                for j, line in enumerate(lines[:5]):
                    print(f"    Line {j}: {repr(line)}")
                if len(lines) > 5:
                    print(f"    ... and {len(lines) - 5} more lines")

def test_cost_summary():
    """Test that cost summary is working."""
    print("\n\n" + "=" * 70)
    print("Testing Cost Summary")
    print("=" * 70)
    
    grid = GroKitGrid()
    
    # Clear any existing content
    grid.renderer.ai_content.clear()
    
    # Call _show_cost_summary directly
    print("Calling _show_cost_summary()...")
    grid._show_cost_summary()
    
    # Check what was added
    print(f"\nNumber of messages in AI content: {len(grid.renderer.ai_content)}")
    
    if grid.renderer.ai_content:
        last_msg = grid.renderer.ai_content[-1]
        print(f"Last message role: {last_msg.get('role')}")
        print(f"Content: {last_msg.get('content', '')}")

if __name__ == "__main__":
    test_command_processing()
    test_help_rendering()
    test_cost_summary()
