#!/usr/bin/env python3
"""Test the new create_project_overview tool directly"""

import sys
import os
sys.path.insert(0, '.')

from grok_cli.cli import execute_tool_call

def test_project_overview_tool():
    print("🧪 Testing create_project_overview tool directly")
    print("=" * 60)
    
    # Create a mock tool call
    tool_call = {
        "function": {
            "name": "create_project_overview",
            "arguments": '{"output_filename": "test_overview.md", "include_summary": true}'
        }
    }
    
    print("Executing create_project_overview tool...")
    result = execute_tool_call(tool_call)
    
    print(f"Result: {result}")
    
    # Check if file was created
    if os.path.exists("test_overview.md"):
        print("\n✅ SUCCESS: test_overview.md was created!")
        
        with open("test_overview.md", "r") as f:
            content = f.read()
        
        print("\nContent preview:")
        print("-" * 40)
        lines = content.split('\n')
        for i, line in enumerate(lines[:15]):  # Show first 15 lines
            print(line)
        if len(lines) > 15:
            print("...")
            print(f"(Total lines: {len(lines)})")
        print("-" * 40)
        
        # Clean up
        os.remove("test_overview.md")
        print("\nCleaned up test file")
        
        return True
    else:
        print("\n❌ FAILED: test_overview.md was not created")
        return False

def test_simple_tools():
    print("\n🔧 Testing basic file tools...")
    
    # Test list_files_recursive
    tool_call = {
        "function": {
            "name": "list_files_recursive",
            "arguments": '{}'
        }
    }
    
    result = execute_tool_call(tool_call)
    if result.get("success"):
        file_count = result.get("count", 0)
        print(f"✅ list_files_recursive: Found {file_count} files")
    else:
        print(f"❌ list_files_recursive failed: {result}")
    
    # Test create_file
    tool_call = {
        "function": {
            "name": "create_file",
            "arguments": '{"filename": "test_temp.txt", "content": "This is a test"}'
        }
    }
    
    result = execute_tool_call(tool_call)
    if result.get("success"):
        print("✅ create_file: File created successfully")
        # Clean up
        if os.path.exists("test_temp.txt"):
            os.remove("test_temp.txt")
    else:
        print(f"❌ create_file failed: {result}")

if __name__ == "__main__":
    print("🚀 Testing Project Overview Tool Integration")
    print("This test bypasses the API to test tool functionality directly\n")
    
    # Test the new project overview tool
    overview_success = test_project_overview_tool()
    
    # Test other basic tools
    test_simple_tools()
    
    print("\n" + "=" * 60)
    if overview_success:
        print("🎉 Project overview tool is working perfectly!")
        print("✨ Now Grok can create comprehensive project documentation in a single API call!")
    else:
        print("⚠️ Project overview tool needs attention")
    
    print("\n💡 To use with Grok CLI:")
    print('   grok-cli --prompt "Create a project overview"')
    print('   grok-cli --prompt "Document this codebase with a table of contents"')
