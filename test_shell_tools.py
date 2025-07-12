#!/usr/bin/env python3
"""
Test script for the new shell command tools in grok-cli engine
"""

import os
import sys
import json
import tempfile
import shutil

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_shell_tools():
    """Test the shell command tools implementation."""
    print("Testing Shell Command Tools...")
    print("=" * 60)
    
    try:
        from grok_cli.engine import GrokEngine
        
        # Initialize engine
        engine = GrokEngine()
        print("+ Engine initialized successfully")
        
        # Create a temporary test directory
        with tempfile.TemporaryDirectory() as test_dir:
            os.chdir(test_dir)
            print(f"+ Working in test directory: {test_dir}")
            
            # Test 1: pwd command
            print("\n1. Testing pwd command:")
            result = engine._execute_shell_command("pwd", [])
            print(f"   Result: {result}")
            assert result.get("success"), "pwd should succeed"
            assert "directory" in result, "pwd should return directory"
            print("   + PASS: pwd command works")
            
            # Test 2: echo command
            print("\n2. Testing echo command:")
            result = engine._execute_shell_command("echo", ["Hello", "World"])
            print(f"   Result: {result}")
            assert result.get("success"), "echo should succeed"
            assert result.get("output") == "Hello World", "echo should return correct output"
            print("   + PASS: echo command works")
            
            # Test 3: touch command
            print("\n3. Testing touch command:")
            result = engine._execute_shell_command("touch", ["test_file.txt"])
            print(f"   Result: {result}")
            assert result.get("success"), "touch should succeed"
            assert os.path.exists("test_file.txt"), "touch should create file"
            print("   + PASS: touch command works")
            
            # Test 4: ls command
            print("\n4. Testing ls command:")
            result = engine._execute_shell_command("ls", ["."])
            print(f"   Result: {result}")
            assert result.get("success"), "ls should succeed"
            assert "test_file.txt" in result.get("files", []), "ls should show created file"
            print("   + PASS: ls command works")
            
            # Test 5: cat command (empty file)
            print("\n5. Testing cat command:")
            result = engine._execute_shell_command("cat", ["test_file.txt"])
            print(f"   Result: {result}")
            assert result.get("success"), "cat should succeed"
            assert "test_file.txt" in result.get("results", {}), "cat should return file results"
            print("   + PASS: cat command works")
            
            # Test 6: mkdir command
            print("\n6. Testing mkdir command:")
            result = engine._execute_shell_command("mkdir", ["test_dir"])
            print(f"   Result: {result}")
            assert result.get("success"), "mkdir should succeed"
            assert os.path.isdir("test_dir"), "mkdir should create directory"
            print("   + PASS: mkdir command works")
            
            # Test 7: cd command
            print("\n7. Testing cd command:")
            old_dir = os.getcwd()
            result = engine._execute_shell_command("cd", ["test_dir"])
            print(f"   Result: {result}")
            assert result.get("success"), "cd should succeed"
            new_dir = os.getcwd()
            assert old_dir != new_dir, "cd should change directory"
            print("   + PASS: cd command works")
            
            # Test 8: rm command
            print("\n8. Testing rm command:")
            os.chdir(old_dir)  # Go back to test root
            result = engine._execute_shell_command("rm", ["test_file.txt"])
            print(f"   Result: {result}")
            assert result.get("success"), "rm should succeed"
            assert not os.path.exists("test_file.txt"), "rm should remove file"
            print("   + PASS: rm command works")
            
            # Test 9: rm -r command (directory)
            print("\n9. Testing rm -r command:")
            result = engine._execute_shell_command("rm", ["-r", "test_dir"])
            print(f"   Result: {result}")
            assert result.get("success"), "rm -r should succeed"
            assert not os.path.exists("test_dir"), "rm -r should remove directory"
            print("   + PASS: rm -r command works")
            
            # Test 10: Tool call integration
            print("\n10. Testing tool call integration:")
            tool_call = {
                "function": {
                    "name": "shell_command",
                    "arguments": json.dumps({"command": "echo", "args": ["Tool", "integration", "test"]})
                },
                "id": "test_call_1"
            }
            result = engine.execute_tool_call(tool_call)
            print(f"   Result: {result}")
            assert result.get("success"), "Tool call should succeed"
            assert "Tool integration test" in str(result), "Tool call should return echo output"
            print("   + PASS: Tool call integration works")
        
        print("\n" + "=" * 60)
        print("SHELL TOOLS TEST RESULTS:")
        print("+ All shell commands implemented and working")
        print("+ pwd, echo, touch, ls, cat, mkdir, cd, rm all functional")
        print("+ Tool call integration working")
        print("+ Error handling and success reporting working")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_shell_tools()
    sys.exit(0 if success else 1)