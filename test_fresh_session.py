#!/usr/bin/env python3
"""
Test that new interactive chat sessions start fresh
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_fresh_session():
    """Test that new sessions start with only the welcome message."""
    print("Testing Fresh Session Behavior...")
    print("=" * 60)
    
    try:
        from grok_cli.grokit import GroKitGridIntegration
        
        # Test 1: Create new session (no loaded_session parameter)
        print("1. Testing new interactive chat session:")
        grid = GroKitGridIntegration(".")
        
        # Check AI content - should only have the welcome message
        ai_messages = grid.renderer.ai_content
        print(f"   + Number of messages in new session: {len(ai_messages)}")
        
        if len(ai_messages) == 1:
            first_msg = ai_messages[0]
            if first_msg.get("role") == "system" and "Welcome to GroKit" in first_msg.get("content", ""):
                print("   + PASS: New session starts with only welcome message")
            else:
                print(f"   - FAIL: Unexpected first message: {first_msg}")
        elif len(ai_messages) == 0:
            print("   + PASS: New session starts completely fresh")
        else:
            print(f"   - FAIL: New session has {len(ai_messages)} messages (should be 0-1)")
            for i, msg in enumerate(ai_messages):
                print(f"     Message {i}: {msg.get('role')} - {msg.get('content', '')[:50]}...")
        
        # Test 2: Verify no old conversation history
        print("\n2. Testing that old history is not loaded:")
        old_history_found = False
        for msg in ai_messages:
            content = msg.get("content", "")
            if any(phrase in content.lower() for phrase in ["hello grok", "typing", "loud and clear"]):
                old_history_found = True
                print(f"   - FAIL: Found old conversation: {content[:100]}...")
                break
        
        if not old_history_found:
            print("   + PASS: No old conversation history in new session")
        
        print("\n" + "=" * 60)
        print("FRESH SESSION TEST RESULTS:")
        if len(ai_messages) <= 1 and not old_history_found:
            print("+ New sessions start fresh")
            print("+ No old conversation history loaded")
            print("+ Welcome message only (if any)")
            print("+ Ready for new conversation")
            result = True
        else:
            print("- New sessions are loading old history")
            print("- Fix needed in conversation loading")
            result = False
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fresh_session()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)