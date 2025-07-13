#!/usr/bin/env python3
"""
Test the new streaming UI without requiring API keys
"""

import os
import sys
import time
from pathlib import Path

# Add the grok_cli package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_streaming_renderer():
    """Test the streaming renderer with mock data."""
    print("Testing Streaming UI Components...")
    print("=" * 50)
    
    try:
        from grok_cli.streaming_ui import StreamingRenderer
        
        # Create renderer
        renderer = StreamingRenderer()
        
        print("1. Testing session start...")
        renderer.start_session("GroKit Streaming Test")
        
        print("\n2. Testing user message...")
        renderer.show_user_message("Hello! Can you write a Python function to reverse a string?")
        
        print("\n3. Testing AI response streaming...")
        renderer.start_ai_response()
        
        # Simulate streaming response
        response_chunks = [
            "Here's a Python function to reverse a string:\n\n",
            "```python\n",
            "def reverse_string(s):\n",
            "    \"\"\"Reverse a string using slicing.\"\"\"\n",
            "    return s[::-1]\n\n",
            "# Example usage\n",
            "text = \"Hello, World!\"\n",
            "reversed_text = reverse_string(text)\n",
            "print(reversed_text)  # Output: !dlroW ,olleH\n",
            "```\n\n",
            "This function uses Python's slicing notation `[::-1]` which:\n",
            "- Starts at the end of the string\n",
            "- Moves backwards with step -1\n",
            "- Returns a new reversed string\n\n",
            "The slicing method is very efficient for string reversal!"
        ]
        
        full_response = ""
        for chunk in response_chunks:
            full_response += chunk
            renderer.stream_content(chunk)
            time.sleep(0.1)  # Simulate streaming delay
        
        # Finish with cost info
        cost_info = {"cost": "$0.0023", "tokens": "156"}
        renderer.finish_ai_response(full_response, cost_info)
        
        print("\n4. Testing system messages...")
        renderer.show_system_message("This is an info message", "info")
        renderer.show_system_message("This is a success message", "success")
        renderer.show_system_message("This is a warning message", "warning")
        renderer.show_system_message("This is an error message", "error")
        
        print("\n5. Testing help display...")
        renderer.show_help()
        
        print("\n6. Testing cost summary...")
        cost_data = {
            "total_cost_usd": 0.012345,
            "total_tokens": 1234,
            "operations_count": 5,
            "session_duration": "5m 23s"
        }
        renderer.show_cost_summary(cost_data)
        
        print("\n[OK] All streaming UI tests completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_basic_functionality():
    """Test basic functionality without Rich if needed."""
    print("\nTesting Basic Functionality...")
    print("=" * 50)
    
    # Test without Rich
    os.environ['FORCE_NO_RICH'] = '1'
    
    try:
        from grok_cli.streaming_ui import StreamingRenderer
        
        renderer = StreamingRenderer()
        renderer.start_session("Basic Test")
        renderer.show_user_message("Test message")
        renderer.start_ai_response()
        renderer.stream_content("This is a test response")
        renderer.finish_ai_response()
        
        print("[OK] Basic functionality test passed!")
        
    except Exception as e:
        print(f"[ERROR] Basic test failed: {e}")
    
    finally:
        # Clean up
        if 'FORCE_NO_RICH' in os.environ:
            del os.environ['FORCE_NO_RICH']

def test_grokit_integration():
    """Test GroKit integration."""
    print("\nTesting GroKit Integration...")
    print("=" * 50)
    
    try:
        from grok_cli.grokit import GroKitUI
        
        # Test that streaming chat can be imported
        ui = GroKitUI(".")
        
        # Test the method exists
        if hasattr(ui, 'launch_streaming_chat'):
            print("[OK] Streaming chat method exists in GroKit")
        else:
            print("[ERROR] Streaming chat method missing from GroKit")
        
        # Test the streaming UI can be imported
        from grok_cli.streaming_ui import StreamingAIChat
        
        # Create instance (but don't run it)
        streaming_chat = StreamingAIChat(".")
        print("[OK] StreamingAIChat can be instantiated")
        
        print("[OK] GroKit integration test passed!")
        
    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("GroKit Streaming UI Test Suite")
    print("=" * 60)
    
    test_streaming_renderer()
    test_basic_functionality()
    test_grokit_integration()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("\nTo test with real AI:")
    print("1. Set your XAI_API_KEY environment variable")
    print("2. Run: grokit (or python -m grok_cli.grokit)")
    print("3. Select option 1: Streaming Chat (New!)")
    print("\nExpected experience:")
    print("- Smooth real-time streaming (no flicker)")
    print("- Beautiful code syntax highlighting")
    print("- Classic terminal feel")
    print("- Live cost tracking")

if __name__ == "__main__":
    main()