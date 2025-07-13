#!/usr/bin/env python3
"""
Test script for memory tool functionality in GroKit
"""

import os
import sys
import json
from pathlib import Path

# Add the grok_cli package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from grok_cli.memory_manager import MemoryManager
from grok_cli.engine import GrokEngine

def test_memory_manager():
    """Test MemoryManager directly."""
    print("=== Testing MemoryManager directly ===")
    
    # Initialize with current directory
    memory_manager = MemoryManager(".")
    
    # Test basic functionality
    print("1. Testing memory stats...")
    stats = memory_manager.get_memory_stats()
    print(f"   Memory stats: {json.dumps(stats, indent=2)}")
    
    # Test search functionality
    print("2. Testing search functionality...")
    
    # Search for common terms that might be in chat history
    test_queries = [
        "hello",
        "test",
        "script",
        "python"
    ]
    
    for query in test_queries:
        print(f"   Searching for '{query}':")
        
        # Test different search types
        for search_type in ["current_session", "recent_history", "all_history"]:
            result = memory_manager.search_memory(
                query=query,
                search_type=search_type,
                max_results=3
            )
            
            if result.get("success"):
                results_count = len(result.get("results", []))
                print(f"     {search_type}: {results_count} results")
            else:
                print(f"     {search_type}: Error - {result.get('error', 'Unknown')}")
    
    print()

def test_engine_integration():
    """Test memory tool through engine integration."""
    print("=== Testing Engine Integration ===")
    
    # Initialize engine
    engine = GrokEngine()
    engine.set_source_directory(".")
    
    # Test tool definitions
    print("1. Checking tool definitions...")
    tools = engine.build_tool_definitions()
    memory_tool = None
    
    for tool in tools:
        if tool.get("function", {}).get("name") == "memory_lookup":
            memory_tool = tool
            break
    
    if memory_tool:
        print("   [OK] memory_lookup tool found in definitions")
        print(f"   Description: {memory_tool['function']['description'][:100]}...")
    else:
        print("   [ERROR] memory_lookup tool NOT found in definitions")
        return
    
    # Test tool execution
    print("2. Testing tool execution...")
    
    # Test basic memory lookup
    test_args = {
        "query": "hello",
        "search_type": "recent_history",
        "max_results": 3
    }
    
    try:
        result = engine._execute_tool_internal("memory_lookup", test_args)
        
        if result.get("success"):
            results_count = len(result.get("results", []))
            print(f"   [OK] Tool execution successful: {results_count} results found")
            
            # Show sample results
            if result.get("results"):
                sample = result["results"][0]
                print(f"   Sample result: {sample.get('type', 'unknown')} - {sample.get('content', '')[:50]}...")
        else:
            print(f"   [WARNING] Tool execution returned error: {result.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"   [ERROR] Tool execution failed: {str(e)}")
    
    print()

def test_parameter_validation():
    """Test parameter validation and edge cases."""
    print("=== Testing Parameter Validation ===")
    
    engine = GrokEngine()
    engine.set_source_directory(".")
    
    test_cases = [
        # Valid cases
        {"query": "test", "search_type": "current_session", "max_results": 5},
        {"query": "hello", "search_type": "recent_history"},
        {"query": "script", "search_type": "all_history", "max_results": 1},
        
        # Edge cases
        {"query": "test", "search_type": "invalid_type", "max_results": 5},  # Invalid search type
        {"query": "test", "search_type": "recent_history", "max_results": 0},  # Invalid max_results
        {"query": "test", "search_type": "recent_history", "max_results": 25},  # Too high max_results
        {"query": "", "search_type": "recent_history"},  # Empty query
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. Testing: {test_case}")
        
        try:
            result = engine._execute_tool_internal("memory_lookup", test_case)
            
            if result.get("success"):
                results_count = len(result.get("results", []))
                print(f"   [OK] Success: {results_count} results")
            else:
                print(f"   [WARNING] Error: {result.get('error', 'Unknown')}")
                
        except Exception as e:
            print(f"   [ERROR] Exception: {str(e)}")
    
    print()

def main():
    """Run all tests."""
    print("Starting Memory Tool Tests")
    print("=" * 50)
    
    try:
        test_memory_manager()
        test_engine_integration()
        test_parameter_validation()
        
        print("=" * 50)
        print("[OK] All tests completed!")
        
    except Exception as e:
        print(f"[ERROR] Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()