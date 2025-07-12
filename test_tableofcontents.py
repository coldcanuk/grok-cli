#!/usr/bin/env python3
"""Test script to verify grok-cli can create tableofcontents.md"""

import subprocess
import os
import sys

def test_grok_cli():
    # Check if API key is set
    if not os.getenv("XAI_API_KEY"):
        print("Error: XAI_API_KEY environment variable not set")
        sys.exit(1)
    
    # The prompt to test
    prompt = 'read our codebase and learn it. respecting our .gitignore please generate a `tableofcontents.md` in this format: /path/to/filename;{30 word description of the file and what it does}'
    
    # Run the command
    print("Running grok-cli with the test prompt...")
    result = subprocess.run(
        ["python", "-m", "grok_cli.cli", "--stream", "--prompt", prompt],
        capture_output=True,
        text=True
    )
    
    print("\n=== STDOUT ===")
    print(result.stdout)
    
    print("\n=== STDERR ===")
    print(result.stderr)
    
    print("\n=== Return Code ===")
    print(result.returncode)
    
    # Check if tableofcontents.md was created
    if os.path.exists("tableofcontents.md"):
        print("\n=== SUCCESS: tableofcontents.md was created ===")
        with open("tableofcontents.md", "r") as f:
            print(f.read())
    else:
        print("\n=== WARNING: tableofcontents.md was not created ===")

if __name__ == "__main__":
    test_grok_cli()
