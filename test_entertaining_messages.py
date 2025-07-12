#!/usr/bin/env python3
"""Test the entertaining messages during waiting periods"""

import subprocess
import os
import sys

def test_startup_messages():
    """Test that startup messages appear immediately"""
    print("=== Testing Startup Messages ===")
    
    # Test a simple prompt to see startup message
    result = subprocess.run(
        ["python", "-m", "grok_cli.cli", "--prompt", "Hello, just testing startup messages"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    # Check for emoji and fun messages
    startup_indicators = ["🥔", "🔔", "🎯", "🚀", "📡", "🎪", "🌟", "🎲", "🧙", "📞"]
    found_startup = any(indicator in result.stdout for indicator in startup_indicators)
    
    if found_startup:
        print("✅ SUCCESS: Found startup message with emoji!")
    else:
        print("❌ FAILED: No startup message found")
        
    return found_startup

def test_thinking_messages():
    """Test thinking messages during file operations"""
    print("\n=== Testing Thinking Messages ===")
    
    # Create a test file first
    with open("test_file.txt", "w") as f:
        f.write("This is a test file for reading")
    
    # Test a command that should trigger thinking messages
    result = subprocess.run(
        ["python", "-m", "grok_cli.cli", "--prompt", "Read the file test_file.txt and tell me what's in it"],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    
    # Check for thinking messages
    thinking_indicators = ["🤔", "💭", "🎪", "🧠", "🎯", "🍕", "🎲", "🎭", "🌟", "🦆"]
    found_thinking = any(indicator in result.stdout for indicator in thinking_indicators)
    
    if found_thinking:
        print("✅ SUCCESS: Found thinking message with emoji!")
    else:
        print("❌ FAILED: No thinking message found")
    
    # Clean up
    try:
        os.remove("test_file.txt")
    except:
        pass
        
    return found_thinking

def main():
    print("🎭 Testing Grok CLI Entertainment Features")
    print("=" * 50)
    
    startup_ok = test_startup_messages()
    thinking_ok = test_thinking_messages()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"Startup Messages: {'✅ PASS' if startup_ok else '❌ FAIL'}")
    print(f"Thinking Messages: {'✅ PASS' if thinking_ok else '❌ FAIL'}")
    
    if startup_ok and thinking_ok:
        print("\n🎉 All entertainment features working perfectly!")
        print("The CLI now provides fun, engaging feedback during all waiting periods!")
    else:
        print("\n⚠️  Some features may need attention")
        
    return startup_ok and thinking_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
