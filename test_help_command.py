#!/usr/bin/env python3
"""
Test the /help command behavior to identify UI smudging
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_help_command():
    """Test that /help command displays properly in the AI conversation window."""
    print("Testing /help Command Behavior...")
    print("=" * 60)
    
    try:
        from grok_cli.grokit import GroKitGridIntegration
        from datetime import datetime
        
        # Test 1: Check help command processing
        print("1. Testing help command processing:")
        grid = GroKitGridIntegration(".")
        
        # Simulate typing /help
        help_input = "/help"
        print(f"   + Simulating user input: '{help_input}'")
        
        # Process the special command
        result = grid._process_special_commands(help_input)
        print(f"   + Command processing result: {result}")
        
        # Check if help message was added to AI content
        help_messages = [msg for msg in grid.renderer.ai_content if msg['role'] == 'system' and 'Commands' in msg.get('content', '')]
        print(f"   + Help messages in AI content: {len(help_messages)}")
        
        if help_messages:
            last_help = help_messages[-1]
            print(f"   + Last help message timestamp: {last_help.get('timestamp', 'none')}")
            print(f"   + Help content preview: {last_help.get('content', '')[:100]}...")
        
        # Test 2: Check message formatting
        print("\n2. Testing message formatting:")
        
        # Check that the message has proper system role and timestamp
        if help_messages:
            msg = help_messages[-1]
            assert msg['role'] == 'system', f"Expected 'system' role, got '{msg['role']}'"
            assert msg.get('timestamp'), "Help message should have timestamp"
            assert 'GroKit Grid Commands:' in msg['content'], "Help message should contain command list"
            print("   + Message has correct role, timestamp, and content [OK]")
        else:
            print("   - No help messages found in AI content")
        
        # Test 3: Check that no content is printed outside the grid
        print("\n3. Testing clean output (no stdout pollution):")
        
        # Capture any print statements by testing the method directly
        import io
        import contextlib
        
        old_stdout = sys.stdout
        captured_output = io.StringIO()
        
        with contextlib.redirect_stdout(captured_output):
            grid._show_help()
        
        stdout_content = captured_output.getvalue()
        
        if stdout_content.strip():
            # Clean the content for display
            clean_content = stdout_content.replace('\x1b', '').replace('\r', '').replace('\n', ' ')[:100]
            print(f"   - WARNING: Help command printed to stdout: {clean_content}...")
        else:
            print("   + Help command produces no stdout output [OK]")
        
        print("\n" + "=" * 60)
        print("HELP COMMAND TEST RESULTS:")
        
        if help_messages and not stdout_content.strip():
            print("+ Help command displays in AI conversation window [OK]")
            print("+ Help message has proper system role and timestamp [OK]")
            print("+ No stdout pollution (clean UI) [OK]")
            print("\n/help command working correctly!")
        else:
            print("- Issues found with /help command:")
            if not help_messages:
                print("  * Help message not appearing in AI conversation window")
            if stdout_content.strip():
                print("  * Help command printing to stdout (causes UI smudging)")
        
        print("=" * 60)
        
        return len(help_messages) > 0 and not stdout_content.strip()
        
    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_help_command()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)