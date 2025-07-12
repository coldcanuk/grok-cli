#!/usr/bin/env python3
"""Test the --debug flag functionality"""

import subprocess
import os
import sys

def test_debug_flag():
    print("🧪 Testing --debug flag functionality")
    print("=" * 50)
    
    # Clean up any existing environment variable
    if "GROK_DEBUG" in os.environ:
        del os.environ["GROK_DEBUG"]
    
    # Test 1: Debug off (--debug 0)
    print("\n1. Testing --debug 0 (should be quiet)")
    result = subprocess.run(
        ["python", "-m", "grok_cli.cli", "--debug", "0", "--prompt", "Hello, this is a test"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    debug_indicators = ["[DEBUG]", "[INFO]", "[WARNING]"]
    has_debug = any(indicator in result.stdout for indicator in debug_indicators)
    
    if not has_debug:
        print("✅ SUCCESS: No debug output with --debug 0")
    else:
        print("❌ FAILED: Found debug output with --debug 0")
        print("Output:", result.stdout[:200])
    
    # Test 2: Debug on (--debug 1)
    print("\n2. Testing --debug 1 (should be verbose)")
    result = subprocess.run(
        ["python", "-m", "grok_cli.cli", "--debug", "1", "--prompt", "Hello, this is a test"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    has_debug = any(indicator in result.stdout for indicator in debug_indicators)
    
    if has_debug:
        print("✅ SUCCESS: Found debug output with --debug 1")
    else:
        print("❌ FAILED: No debug output with --debug 1")
        print("Output:", result.stdout[:200])
    
    # Test 3: Environment variable override
    print("\n3. Testing environment variable override")
    os.environ["GROK_DEBUG"] = "1"
    result = subprocess.run(
        ["python", "-m", "grok_cli.cli", "--debug", "0", "--prompt", "Hello, this is a test"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    has_debug = any(indicator in result.stdout for indicator in debug_indicators)
    
    if not has_debug:
        print("✅ SUCCESS: --debug 0 overrides GROK_DEBUG=1")
    else:
        print("❌ FAILED: --debug 0 did not override GROK_DEBUG=1")
        print("Output:", result.stdout[:200])
    
    # Clean up
    if "GROK_DEBUG" in os.environ:
        del os.environ["GROK_DEBUG"]
    
    print("\n" + "=" * 50)
    print("🎉 Debug flag testing complete!")
    print("\n📋 Usage examples:")
    print("   grok-cli --debug 1 --prompt 'your prompt'  # Debug ON")
    print("   grok-cli --debug 0 --prompt 'your prompt'  # Debug OFF")
    print("   grok-cli --prompt 'your prompt'             # Default (OFF)")

if __name__ == "__main__":
    test_debug_flag()
