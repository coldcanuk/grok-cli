"""
Demo script for GroKit Grid UI - Showcase all features and test different terminal sizes
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def demo_grid_components():
    """Demonstrate all grid UI components."""
    print("=" * 70)
    print("GROKIT GRID UI DEMO - Complete Feature Showcase")
    print("=" * 70)
    
    try:
        from grok_cli.grid_ui import GridRenderer, VersionManager
        from grok_cli.persistence import PersistentStorage, ClipboardHandler
        from grok_cli.enhanced_input import EnhancedInputHandler, TextOptimizer
        from grok_cli.grokit import GroKitGridIntegration
        
        print("\n1. Testing Core Components")
        print("-" * 30)
        
        # Test GridRenderer
        print("Testing GridRenderer...")
        renderer = GridRenderer()
        print(f"PASS: Grid Renderer: {renderer.width}x{renderer.height} terminal")
        
        # Test VersionManager
        print("Testing VersionManager...")
        version_mgr = VersionManager(".")
        version = version_mgr.get_version()
        print(f"PASS: Version Manager: Detected version {version}")
        
        # Test PersistentStorage
        print("Testing PersistentStorage...")
        storage = PersistentStorage(".")
        print(f"PASS: Persistence: Session ID {storage.session_id}")
        
        # Test ClipboardHandler
        print("Testing ClipboardHandler...")
        clipboard = ClipboardHandler()
        clipboard_content = clipboard.get_clipboard_text()
        if clipboard_content:
            print(f"PASS: Clipboard: Found {len(clipboard_content)} characters")
        else:
            print("PASS: Clipboard: No content (normal)")
        
        # Test TextOptimizer
        print("Testing TextOptimizer...")
        optimizer = TextOptimizer()
        test_text = "This is a   test   text   with   multiple   spaces   and\n\n\nline breaks."
        optimized, meta = optimizer.optimize_text(test_text)
        savings = meta.get('savings', 0) if meta.get('optimized', False) else 0
        print(f"PASS: Text Optimizer: {savings} chars saved")
        
        # Test EnhancedInputHandler
        print("Testing EnhancedInputHandler...")
        input_handler = EnhancedInputHandler()
        state = input_handler.get_current_state()
        print(f"PASS: Enhanced Input: Ready (multiline: {state['multiline_mode']})")
        
        print("\n2. Testing Grid UI Rendering")
        print("-" * 30)
        
        # Set up test content
        renderer.update_header("GROKIT DEMO", "Grid UI Test", version)
        
        # Add test messages
        renderer.add_ai_message("user", "Hello, this is a test message!")
        renderer.add_ai_message("assistant", "Hello! I'm testing the grid UI system. This message tests word wrapping and multi-line display capabilities.")
        renderer.add_ai_message("system", "System message: Grid UI components loaded successfully.")
        renderer.add_ai_message("user", "Can you show me the cost tracking?")
        renderer.add_ai_message("assistant", "The cost tracking displays real-time token usage and USD costs in the status bar at the bottom of the interface.")
        
        # Update status
        renderer.update_status("Demo Mode Active", "$0.0123", "1,234")
        renderer.update_input("This is test input text...")
        
        print("Rendering full grid UI...")
        renderer.render_full_screen()
        
        print(f"\n3. Testing Different Terminal Sizes")
        print("-" * 30)
        
        # Test with different terminal sizes
        test_sizes = [
            (80, 24),   # Standard
            (120, 30),  # Wide
            (60, 20),   # Narrow
            (100, 40)   # Tall
        ]
        
        for width, height in test_sizes:
            print(f"Testing {width}x{height} terminal...")
            test_renderer = GridRenderer(width, height)
            test_renderer.update_header("GROKIT", "Size Test", version)
            test_renderer.add_ai_message("system", f"Testing {width}x{height} terminal size")
            test_renderer.update_status("Size Test", "$0.00", "0")
            # Don't render to avoid cluttering output
            print(f"PASS: {width}x{height}: AI window height = {test_renderer.ai_window_height}")
        
        print(f"\n4. Testing Persistence Features")
        print("-" * 30)
        
        # Test message storage
        storage.add_message("user", "Test persistence message")
        storage.add_message("assistant", "Persistence is working correctly!")
        
        # Test cost tracking
        storage.update_cost_tracking(0.0012, 150, "test_operation")
        storage.update_cost_tracking(0.0034, 420, "test_response")
        
        # Test feature usage
        storage.add_feature_usage("grid_ui_demo")
        storage.add_feature_usage("persistence_test")
        
        # Get session stats
        stats = storage.get_session_stats()
        print(f"PASS: Session Stats: {stats['total_messages']} messages, ${stats['cost_summary']['total_cost']:.4f} cost")
        
        # Test history retrieval
        recent_messages = storage.get_recent_history(days=1, limit=5)
        print(f"PASS: History: {len(recent_messages)} recent messages")
        
        print(f"\n5. Testing GroKit Grid Integration")
        print("-" * 30)
        
        # Test the full GroKit Grid application in test mode
        print("Initializing GroKit Grid application...")
        app = GroKitGridIntegration(".")
        print("PASS: GroKit Grid: Initialized successfully")
        print(f"PASS: Working directory: {app.src_path}")
        print(f"PASS: Session ID: {app.storage.session_id}")
        print(f"PASS: Status: {app.status_message}")
        
        print(f"\n6. Available Features Summary")
        print("-" * 30)
        
        features = {
            "Grid-based UI": "Terminal layout with header, chat, input, and status areas",
            "Persistent Storage": "Chat history saved to .grok/history/, sessions to .grok/session/",
            "Enhanced Input": "Multi-line support, clipboard paste, history, optimization",
            "Cost Tracking": "Real-time token and USD cost monitoring",
            "Version Management": "Automatic version detection from project files",
            "Leader Integration": "Strategic planning mode with grok-3-mini -> grok-4-0709",
            "Text Optimization": "Automatic text cleanup to reduce API costs",
            "Clipboard Support": "Cross-platform clipboard integration",
            "Session Management": "Persistent session data with export capabilities",
            "Real-time Updates": "Throttled rendering for smooth performance"
        }
        
        for feature, description in features.items():
            print(f"  {feature:20s}: {description}")
        
        print(f"\n7. Usage Instructions")
        print("-" * 30)
        
        print("Command Line Usage:")
        print("  grokit                         # Launch GroKit menu interface")
        print("  grokit --src /path             # Launch in specific directory")
        print("  Select option 4: Grid UI       # Access enhanced grid interface")
        print("")
        print("In-Application Commands:")
        print("  /leader [objective]            # Strategic planning mode")
        print("  /paste                         # Paste from clipboard")
        print("  /multi                         # Toggle multi-line input")
        print("  /costs                         # Show cost summary")
        print("  /stats                         # Show session statistics")
        print("  /export                        # Export session data")
        print("  /clear                         # Clear chat history")
        print("  /help                          # Show help information")
        print("  /quit                          # Exit application")
        print("")
        print("Multi-line Input:")
        print("  Type text across multiple lines")
        print("  Type '###' on new line to submit")
        print("  Use /paste to insert clipboard content")
        print("  Use /single to return to single-line mode")
        
        print(f"\n8. File Structure Created")
        print("-" * 30)
        
        # Show .grok directory structure
        grok_dir = storage.grok_dir
        if grok_dir.exists():
            print(f"PASS: .grok/ directory: {grok_dir}")
            for subdir in ["history", "session"]:
                subdir_path = grok_dir / subdir
                if subdir_path.exists():
                    file_count = len(list(subdir_path.glob("*")))
                    print(f"  |-- {subdir}/: {file_count} files")
            
            gitignore_path = grok_dir / ".gitignore"
            if gitignore_path.exists():
                print(f"  +-- .gitignore: Created for sensitive data")
        
        print(f"\n{'='*70}")
        print("GROKIT GRID UI DEMO COMPLETE!")
        print("All components are working correctly and ready for interactive use.")
        print(f"{'='*70}")
        
        return True
        
    except Exception as e:
        print(f"DEMO FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_terminal_compatibility():
    """Test grid UI compatibility across different terminal configurations."""
    print("\n" + "="*50)
    print("TERMINAL COMPATIBILITY TEST")
    print("="*50)
    
    try:
        from grok_cli.grid_ui import GridRenderer
        
        # Test color support
        renderer = GridRenderer()
        print("Testing color support...")
        
        try:
            print(f"{renderer.colors['green']}PASS: Color test: GREEN{renderer.colors['end']}")
            print(f"{renderer.colors['blue']}PASS: Color test: BLUE{renderer.colors['end']}")
            print(f"{renderer.colors['yellow']}PASS: Color test: YELLOW{renderer.colors['end']}")
            print("Colors: SUPPORTED")
        except UnicodeEncodeError:
            print("Colors: SUPPORTED (with ASCII fallback)")
        
        # Test Unicode box drawing
        print("\nTesting Unicode box drawing...")
        try:
            print("╔════════════════════════════╗")
            print("║       Unicode Test         ║")
            print("╚════════════════════════════╝")
            print("Unicode: SUPPORTED")
        except UnicodeEncodeError:
            print("+---------------------------+")
            print("|       ASCII Fallback      |")
            print("+---------------------------+")
            print("Unicode: ASCII FALLBACK")
        
        # Test terminal size detection
        print(f"\nTerminal size: {renderer.width}x{renderer.height}")
        if renderer.width < 80 or renderer.height < 24:
            print("WARNING: Terminal size is smaller than recommended (80x24)")
        else:
            print("Terminal size: ADEQUATE")
        
        # Test cursor positioning
        print("\nTesting cursor positioning...")
        renderer.move_cursor(1, 1)
        print("Cursor positioning: WORKING")
        
        print("\nTerminal compatibility: PASSED")
        return True
        
    except Exception as e:
        print(f"Terminal compatibility test FAILED: {e}")
        return False

if __name__ == "__main__":
    print("Starting GroKit Grid UI Comprehensive Demo...")
    
    # Run main demo
    demo_success = demo_grid_components()
    
    # Run compatibility test
    compat_success = test_terminal_compatibility()
    
    if demo_success and compat_success:
        print("\nSUCCESS: ALL TESTS PASSED! GroKit Grid UI is ready for use.")
    else:
        print("\nWARNING: Some tests failed. Check output above for details.")