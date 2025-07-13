#!/usr/bin/env python3
"""
Test script for /clear command functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the grok_cli package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from grok_cli.persistence import PersistentStorage
from grok_cli.grid_ui import GridRenderer
from grok_cli.grokit import GroKitGridIntegration

def test_persistence_clear():
    """Test PersistentStorage clear_session_history method."""
    print("=== Testing PersistentStorage.clear_session_history() ===")
    
    # Create a test storage instance
    storage = PersistentStorage(".")
    
    # Add some test messages
    print("1. Adding test messages...")
    storage.add_message("user", "Test message 1", {"test": True})
    storage.add_message("assistant", "Test response 1")
    storage.add_message("user", "Test message 2", {"test": True})
    
    # Check messages were added
    messages_before = storage.get_session_messages()
    print(f"   Messages before clear: {len(messages_before)}")
    
    # Test clear functionality
    print("2. Testing clear_session_history()...")
    storage.clear_session_history()
    
    # Check messages were cleared
    messages_after = storage.get_session_messages()
    print(f"   Messages after clear: {len(messages_after)}")
    
    if len(messages_after) == 0:
        print("   [OK] Session history cleared successfully")
    else:
        print(f"   [ERROR] Session still has {len(messages_after)} messages")
    
    print()

def test_grid_renderer_clear():
    """Test GridRenderer clear_ai_history method."""
    print("=== Testing GridRenderer.clear_ai_history() ===")
    
    # Create a test renderer
    renderer = GridRenderer()
    
    # Add some test content
    print("1. Adding test AI messages...")
    renderer.add_ai_message("user", "Test user message")
    renderer.add_ai_message("assistant", "Test AI response")
    renderer.add_ai_message("user", "Another test message")
    
    print(f"   AI content before clear: {len(renderer.ai_content)} messages")
    
    # Test clear functionality
    print("2. Testing clear_ai_history()...")
    renderer.clear_ai_history()
    
    print(f"   AI content after clear: {len(renderer.ai_content)} messages")
    
    if len(renderer.ai_content) == 0:
        print("   [OK] AI history cleared successfully")
    else:
        print(f"   [ERROR] AI content still has {len(renderer.ai_content)} messages")
    
    print()

def test_integrated_clear():
    """Test the integrated /clear command processing (without running UI)."""
    print("=== Testing Integrated /clear Command Processing ===")
    
    try:
        # Create a mock grid integration instance
        print("1. Creating GroKitGridIntegration instance...")
        grid_integration = GroKitGridIntegration(".")
        
        # Add some messages through storage
        print("2. Adding test messages through storage...")
        grid_integration.storage.add_message("user", "Test message before clear")
        grid_integration.storage.add_message("assistant", "Test response before clear")
        
        # Add messages to renderer
        grid_integration.renderer.add_ai_message("user", "Test message before clear")
        grid_integration.renderer.add_ai_message("assistant", "Test response before clear")
        
        print(f"   Storage messages before: {len(grid_integration.storage.get_session_messages())}")
        print(f"   Renderer content before: {len(grid_integration.renderer.ai_content)}")
        
        # Test the /clear command processing
        print("3. Testing /clear command processing...")
        result = grid_integration._process_special_commands("/clear")
        
        print(f"   Storage messages after: {len(grid_integration.storage.get_session_messages())}")
        print(f"   Renderer content after: {len(grid_integration.renderer.ai_content)}")
        print(f"   Command processing result: {result}")
        
        # Check if both were cleared
        storage_cleared = len(grid_integration.storage.get_session_messages()) == 0
        renderer_cleared = len(grid_integration.renderer.ai_content) == 0
        
        if storage_cleared and renderer_cleared:
            print("   [OK] /clear command works correctly - both storage and display cleared")
        else:
            print(f"   [ERROR] /clear command incomplete:")
            print(f"     Storage cleared: {storage_cleared}")
            print(f"     Renderer cleared: {renderer_cleared}")
        
    except Exception as e:
        print(f"   [ERROR] Exception during integration test: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def main():
    """Run all clear command tests."""
    print("Testing /clear Command Functionality")
    print("=" * 50)
    
    try:
        test_persistence_clear()
        test_grid_renderer_clear()
        test_integrated_clear()
        
        print("=" * 50)
        print("[OK] All /clear command tests completed!")
        
    except Exception as e:
        print(f"[ERROR] Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()