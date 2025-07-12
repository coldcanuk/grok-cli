"""
Test GroKit functionality
"""

import sys
import os

# Add the parent directory to the path so we can import grok_cli
sys.path.insert(0, os.path.dirname(__file__))

def test_grokit_import():
    """Test that GroKit can be imported and initialized."""
    try:
        from grok_cli.grokit import GroKitUI
        from grok_cli.input_handler import MultiLineInputHandler
        
        # Test input handler
        handler = MultiLineInputHandler()
        print("PASS: MultiLineInputHandler imported successfully")
        
        # Test GroKit UI
        ui = GroKitUI(".")
        print("PASS: GroKitUI imported and initialized successfully")
        
        # Test header printing (without user interaction)
        print("\nTesting header display:")
        ui.print_header()
        
        print("\nTesting menu display:")
        ui.print_main_menu()
        
        print("\nPASS: All GroKit components working!")
        return True
        
    except Exception as e:
        print(f"FAIL: Error testing GroKit: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_grokit_import()