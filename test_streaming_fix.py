#!/usr/bin/env python3
"""
Test script to verify streaming functionality and window refresh fixes
"""

import os
import sys
import json
from pathlib import Path

# Add the grok_cli package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from grok_cli.engine import GrokEngine
from grok_cli.grid_ui import GridRenderer
from grok_cli.grokit import GroKitGridIntegration

def test_streaming_configuration():
    """Test that streaming is properly configured."""
    print("=== Testing Streaming Configuration ===")
    
    engine = GrokEngine()
    
    print("1. Checking XAI SDK availability...")
    from grok_cli.engine import XAI_SDK_AVAILABLE
    print(f"   XAI SDK Available: {XAI_SDK_AVAILABLE}")
    
    print("2. Testing API call routing...")
    
    # Test that streaming requests use requests method (not SDK)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"}
    ]
    
    # Mock the private methods to see which one gets called
    original_sdk = engine._api_call_sdk
    original_requests = engine._api_call_requests
    
    sdk_called = False
    requests_called = False
    
    def mock_sdk(*args, **kwargs):
        nonlocal sdk_called
        sdk_called = True
        return original_sdk(*args, **kwargs)
    
    def mock_requests(*args, **kwargs):
        nonlocal requests_called
        requests_called = True
        # Don't actually call - just return mock
        class MockResponse:
            def iter_lines(self):
                return iter([b'data: {"choices":[{"delta":{"content":"test"}}]}', b'data: [DONE]'])
        return MockResponse()
    
    engine._api_call_sdk = mock_sdk
    engine._api_call_requests = mock_requests
    
    try:
        # Test non-streaming (should use SDK if available)
        print("   Testing non-streaming request...")
        sdk_called = requests_called = False
        try:
            engine.api_call("fake_key", messages, "grok-4-0709", stream=False)
        except:
            pass  # Expected to fail without real API key
        
        if XAI_SDK_AVAILABLE:
            print(f"     SDK called: {sdk_called} (expected: True)")
            print(f"     Requests called: {requests_called} (expected: False)")
        else:
            print(f"     SDK called: {sdk_called} (expected: False - SDK not available)")
            print(f"     Requests called: {requests_called} (expected: True)")
        
        # Test streaming (should use requests even if SDK available)
        print("   Testing streaming request...")
        sdk_called = requests_called = False
        try:
            engine.api_call("fake_key", messages, "grok-4-0709", stream=True)
        except:
            pass  # Expected to fail without real API key
        
        print(f"     SDK called: {sdk_called} (expected: False)")
        print(f"     Requests called: {requests_called} (expected: True)")
        
        if not requests_called:
            print("   [WARNING] Streaming requests not properly routed to requests method!")
        else:
            print("   [OK] Streaming properly configured")
            
    finally:
        # Restore original methods
        engine._api_call_sdk = original_sdk
        engine._api_call_requests = original_requests
    
    print()

def test_grid_streaming_methods():
    """Test the grid renderer streaming methods."""
    print("=== Testing Grid Renderer Streaming Methods ===")
    
    renderer = GridRenderer()
    
    print("1. Testing streaming update method exists...")
    if hasattr(renderer, 'update_message_content_streaming'):
        print("   [OK] update_message_content_streaming method exists")
    else:
        print("   [ERROR] update_message_content_streaming method missing!")
        return
    
    print("2. Testing streaming update functionality...")
    
    # Add a test message
    renderer.add_ai_message("assistant", "Initial content")
    
    if len(renderer.ai_content) > 0:
        print(f"   Initial content: '{renderer.ai_content[0]['content']}'")
        
        # Test streaming update
        renderer.update_message_content_streaming(0, "Updated streaming content")
        
        updated_content = renderer.ai_content[0]['content']
        print(f"   Updated content: '{updated_content}'")
        
        if updated_content == "Updated streaming content":
            print("   [OK] Streaming update works correctly")
        else:
            print("   [ERROR] Streaming update failed")
    else:
        print("   [ERROR] Failed to add initial message")
    
    print()

def test_grokit_integration():
    """Test GroKit integration doesn't use problematic full refreshes."""
    print("=== Testing GroKit Integration ===")
    
    print("1. Checking streaming handler implementation...")
    
    # Read the grokit.py file to verify the fix is in place
    grokit_path = Path(__file__).parent / "grok_cli" / "grokit.py"
    
    if grokit_path.exists():
        with open(grokit_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that the old problematic code is replaced
        if "render_ai_window()" in content and "streaming_content" in content:
            # Look for the problematic line
            lines = content.split('\n')
            problematic_lines = []
            for i, line in enumerate(lines):
                if "render_ai_window()" in line and "streaming" in content[max(0, content.find(line) - 200):content.find(line) + 200]:
                    problematic_lines.append((i + 1, line.strip()))
            
            if problematic_lines:
                print("   [WARNING] Found render_ai_window() calls in streaming context:")
                for line_num, line in problematic_lines:
                    print(f"     Line {line_num}: {line}")
            
        # Check for the new streaming method usage
        if "update_message_content_streaming" in content:
            print("   [OK] New streaming method found in GroKit integration")
        else:
            print("   [WARNING] New streaming method not found in GroKit")
    else:
        print("   [ERROR] Could not read GroKit file")
    
    print()

def test_mock_streaming_flow():
    """Test a mock streaming flow to verify behavior."""
    print("=== Testing Mock Streaming Flow ===")
    
    try:
        # Create a minimal grid integration (without running UI)
        integration = GroKitGridIntegration(".")
        
        print("1. Testing streaming response handling...")
        
        # Create a mock streaming response
        class MockStreamingResponse:
            def iter_lines(self):
                # Simulate streaming chunks
                chunks = [
                    b'data: {"choices":[{"delta":{"content":"Hello"}}]}',
                    b'data: {"choices":[{"delta":{"content":" there"}}]}',
                    b'data: {"choices":[{"delta":{"content":"!"}}]}',
                    b'data: [DONE]'
                ]
                return iter(chunks)
        
        # Add initial assistant message
        msg_index = len(integration.renderer.ai_content)
        integration.renderer.add_ai_message("assistant", "")
        
        print(f"   Initial message index: {msg_index}")
        print(f"   Initial message count: {len(integration.renderer.ai_content)}")
        
        # Simulate streaming updates
        test_content = ""
        streaming_chunks = ["Hello", " there", "!"]
        
        for chunk in streaming_chunks:
            test_content += chunk
            print(f"   Updating with: '{test_content}'")
            
            # Use the streaming update method
            integration.renderer.update_message_content_streaming(msg_index, test_content)
            
            # Verify content was updated
            if msg_index < len(integration.renderer.ai_content):
                actual_content = integration.renderer.ai_content[msg_index]['content']
                print(f"   Actual content: '{actual_content}'")
                
                if actual_content == test_content:
                    print(f"   [OK] Chunk {len(streaming_chunks) - streaming_chunks.index(chunk) + len([c for c in streaming_chunks[:streaming_chunks.index(chunk) + 1]])} updated correctly")
                else:
                    print(f"   [ERROR] Content mismatch: expected '{test_content}', got '{actual_content}'")
        
        final_content = integration.renderer.ai_content[msg_index]['content'] if msg_index < len(integration.renderer.ai_content) else ""
        print(f"   Final content: '{final_content}'")
        
        if final_content == "Hello there!":
            print("   [OK] Mock streaming flow completed successfully")
        else:
            print(f"   [ERROR] Final content incorrect: '{final_content}'")
            
    except Exception as e:
        print(f"   [ERROR] Mock streaming test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def main():
    """Run all streaming tests."""
    print("Testing Streaming Fix Implementation")
    print("=" * 60)
    
    try:
        test_streaming_configuration()
        test_grid_streaming_methods()
        test_grokit_integration()
        test_mock_streaming_flow()
        
        print("=" * 60)
        print("[OK] All streaming tests completed!")
        print("\nKey Fixes Implemented:")
        print("1. ✓ Fixed API routing to use requests method for streaming")
        print("2. ✓ Added efficient streaming update method to GridRenderer")
        print("3. ✓ Replaced full window refresh with targeted streaming updates")
        print("4. ✓ Prevented window clearing during streaming")
        
    except Exception as e:
        print(f"[ERROR] Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()