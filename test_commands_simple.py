#!/usr/bin/env python3
"""Simple test to verify commands work without debug flooding."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'grok_cli'))

from grokit import GroKitGrid

def test_commands():
    """Test that commands work without debug output flooding."""
    print("Testing GroKit commands...")
    print("=" * 50)
    
    # Create instance
    grid = GroKitGrid()
    
    # Test /help command
    print("\n1. Testing /help command:")
    result = grid._process_special_commands("/help")
    if result is None:
        print("   ✓ /help command processed successfully")
        if grid.renderer.ai_content:
            last_msg = grid.renderer.ai_content[-1]
            print(f"   ✓ Content added to AI window (role: {last_msg.get('role')})")
            print(f"   ✓ Content starts with: {last_msg.get('content', '')[:50]}...")
        else:
            print("   ✗ ERROR: No content added to AI window!")
    else:
        print(f"   ✗ ERROR: Command returned: {result}")
    
    # Clear content
    grid.renderer.ai_content.clear()
    
    # Test /costs command
    print("\n2. Testing /costs command:")
    result = grid._process_special_commands("/costs")
    if result is None:
        print("   ✓ /costs command processed successfully")
        if grid.renderer.ai_content:
            last_msg = grid.renderer.ai_content[-1]
            print(f"   ✓ Content added to AI window (role: {last_msg.get('role')})")
            print(f"   ✓ Content starts with: {last_msg.get('content', '')[:50]}...")
        else:
            print("   ✗ ERROR: No content added to AI window!")
    else:
        print(f"   ✗ ERROR: Command returned: {result}")
    
    # Test wrong command (should pass through)
    print("\n3. Testing /cost (wrong command):")
    result = grid._process_special_commands("/cost")
    if result == "/cost":
        print("   ✓ Wrong command passed through correctly")
    else:
        print(f"   ✗ ERROR: Expected '/cost', got: {result}")
    
    print("\n" + "=" * 50)
    print("Test complete! No debug flooding should have occurred.")

if __name__ == "__main__":
    test_commands()
