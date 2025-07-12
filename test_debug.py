#!/usr/bin/env python3
"""Debug test for the tableofcontents.md creation"""

import subprocess
import os

# Enable debug mode
os.environ["GROK_DEBUG"] = "1"

# The prompt that was failing
prompt = 'Read our codebase and create a tableofcontents.md file. List each file in the format: /path/to/file;{description of what the file does}'

print("Running grok-cli with DEBUG enabled...")
print(f"Prompt: {prompt}")
print("-" * 80)

# Run the command
result = subprocess.run(
    ["python", "-m", "grok_cli.cli", "--stream", "--prompt", prompt],
    capture_output=False,  # Let output stream to console
    text=True
)

print("\n" + "-" * 80)
print(f"Return code: {result.returncode}")

# Check if tableofcontents.md was created
if os.path.exists("tableofcontents.md"):
    print("\nSUCCESS: tableofcontents.md was created!")
    print("\nContent preview:")
    with open("tableofcontents.md", "r") as f:
        content = f.read()
        # Show first 500 chars
        print(content[:500] + "..." if len(content) > 500 else content)
else:
    print("\nWARNING: tableofcontents.md was not created")
