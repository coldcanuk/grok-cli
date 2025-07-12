#!/usr/bin/env python3
"""Final test of the fixed implementation"""

import subprocess
import os
import sys

# Clean up any existing tableofcontents.md
if os.path.exists("tableofcontents.md"):
    os.remove("tableofcontents.md")
    print("Removed existing tableofcontents.md")

# Test 1: Simple file creation to verify tools work
print("\n=== Test 1: Simple file creation ===")
result = subprocess.run(
    ["python", "-m", "grok_cli.cli", "--prompt", "Create a file called test_simple.txt with the content 'This is a test'"],
    capture_output=True,
    text=True
)

if os.path.exists("test_simple.txt"):
    print("SUCCESS: test_simple.txt created")
    os.remove("test_simple.txt")
else:
    print("FAILED: test_simple.txt not created")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

# Test 2: Simplified table of contents request
print("\n=== Test 2: Simplified table of contents ===")
simplified_prompt = """First, list all files in the project using list_files_recursive. 
Then read ONLY the following key files one at a time: README.md, setup.py, and grok_cli/cli.py.
Finally, create a file called tableofcontents.md that lists the project structure."""

result = subprocess.run(
    ["python", "-m", "grok_cli.cli", "--prompt", simplified_prompt],
    capture_output=True,
    text=True
)

print("Return code:", result.returncode)

if os.path.exists("tableofcontents.md"):
    print("\nSUCCESS: tableofcontents.md created!")
    with open("tableofcontents.md", "r") as f:
        content = f.read()
    print("\nContent preview:")
    print("-" * 40)
    print(content[:500] + "..." if len(content) > 500 else content)
else:
    print("\nFAILED: tableofcontents.md not created")
    print("\nSTDOUT:")
    print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
