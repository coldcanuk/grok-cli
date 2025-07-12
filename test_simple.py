#!/usr/bin/env python3
"""Simple test to verify grok-cli tool usage"""

import subprocess
import os

# Simple test prompt that should trigger file creation
prompt = "Create a file called test_output.txt with the content 'Hello from Grok CLI'"

print("Testing grok-cli with simple file creation...")
result = subprocess.run(
    ["python", "-m", "grok_cli.cli", "--prompt", prompt],
    capture_output=True,
    text=True
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)

# Check if file was created
if os.path.exists("test_output.txt"):
    print("\nSUCCESS: File was created")
    with open("test_output.txt", "r") as f:
        print(f"Content: {f.read()}")
    os.remove("test_output.txt")  # Clean up
else:
    print("\nFAILED: File was not created")
