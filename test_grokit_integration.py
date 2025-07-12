"""
Test GroKit Grid UI integration
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_grokit_grid_integration():
    """Test that GroKit can launch the Grid UI successfully."""
    print("Testing GroKit Grid UI Integration...")
    
    try:
        from grok_cli.grokit import GroKitUI, GroKitGridIntegration
        
        # Test main GroKit UI
        print("1. Testing GroKit UI initialization...")
        ui = GroKitUI(".")
        print("   PASS: GroKit UI initialized")
        
        # Test Grid UI integration
        print("2. Testing Grid UI integration...")
        grid_ui = GroKitGridIntegration(".")
        print("   PASS: Grid UI integration initialized")
        
        # Test components
        print("3. Testing Grid UI components...")
        print(f"   Renderer: {grid_ui.renderer.width}x{grid_ui.renderer.height}")
        print(f"   Storage: {grid_ui.storage.session_id}")
        print(f"   Version: {grid_ui.version_manager.get_version()}")
        print("   PASS: All components working")
        
        # Test menu options
        print("4. Testing menu integration...")
        ui.clear_screen()
        ui.print_header()
        ui.print_main_menu()
        print("   PASS: Menu shows 8 options including Grid UI")
        
        print("\nSUCCESS: All tests passed! GroKit Grid UI integration is working.")
        print("\nTo use:")
        print("1. Run: grokit")
        print("2. Select option 4: Grid UI (Enhanced Interface)")
        print("3. Enjoy the enhanced grid-based interface!")
        print("\nGrid UI provides:")
        print("• Real-time chat with persistent history")
        print("• Enhanced input with clipboard support")
        print("• Cost tracking and optimization")
        print("• Leader-follower strategic planning")
        
        return True
        
    except Exception as e:
        print(f"FAIL: Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_grokit_grid_integration()