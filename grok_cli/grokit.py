"""
GroKit - Interactive menu-driven interface for Grok CLI
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from .tokenCount import TokenCounter, create_token_counter
from .engine import GrokEngine
from .leader import LeaderFollowerOrchestrator
from .input_handler import MultiLineInputHandler, GroKitInterface
from .grid_ui import GridRenderer, VersionManager
from .persistence import PersistentStorage
from .enhanced_input import EnhancedInputHandler


class GroKitUI(GroKitInterface):
    """Main UI class for GroKit interface."""
    
    def __init__(self, src_path: str = "."):
        super().__init__()  # Initialize GroKitInterface
        
        self.src_path = os.path.abspath(src_path)
        self.token_counter = create_token_counter(
            os.path.join(self.src_path, "grokit_session_costs.json")
        )
        self.engine = GrokEngine()
        self.engine.set_source_directory(self.src_path)
        self.engine.enable_cost_tracking(
            os.path.join(self.src_path, "grokit_session_costs.json")
        )
        
        self.current_session = {
            "start_time": datetime.now().isoformat(),
            "commands_executed": 0,
            "active_mode": "menu"
        }
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the GroKit header."""
        try:
            self.print_box("🚀 GROKIT 🚀", "Interactive Grok Interface")
        except UnicodeEncodeError:
            self.print_box("GROKIT", "Interactive Grok Interface")
    
    def print_cost_summary(self, compact: bool = True):
        """Print current session cost summary."""
        if not self.token_counter:
            return
        
        summary = self.token_counter.get_session_summary()
        
        if compact:
            try:
                self.print_styled(f"💰 Session Cost: ${summary['total_cost_usd']:.4f} USD", "cyan")
            except UnicodeEncodeError:
                self.print_styled(f"Session Cost: ${summary['total_cost_usd']:.4f} USD", "cyan")
        else:
            try:
                self.print_styled(f"\n📊 Cost Summary:", "cyan")
            except UnicodeEncodeError:
                self.print_styled(f"\nCost Summary:", "cyan")
            self.print_styled(f"Total: ${summary['total_cost_usd']:.4f} USD", "yellow")
            self.print_styled(f"Operations: {summary['operations_count']}", "yellow")
            self.print_styled(f"Duration: {summary['session_duration']}", "yellow")
    
    def print_main_menu(self):
        """Print the main menu options."""
        self.print_styled("\nSelect an option:", "blue")
        try:
            self.print_styled("1. 💬 Interactive Chat (Grid UI)", "green")
            self.print_styled("2. 🔄 Resume Previous Session", "green")
            self.print_styled("3. 🎯 Leader Mode (Strategic Planning)", "green")
            self.print_styled("4. 📋 Single Prompt", "green")
            self.print_styled("5. ⚙️  Settings", "green")
            self.print_styled("6. 📊 Cost Analysis", "green")
            self.print_styled("7. ❓ Help", "green")
            self.print_styled("8. 🚪 Exit", "green")
        except UnicodeEncodeError:
            self.print_styled("1. Interactive Chat (Grid UI)", "green")
            self.print_styled("2. Resume Previous Session", "green")
            self.print_styled("3. Leader Mode (Strategic Planning)", "green")
            self.print_styled("4. Single Prompt", "green")
            self.print_styled("5. Settings", "green")
            self.print_styled("6. Cost Analysis", "green")
            self.print_styled("7. Help", "green")
            self.print_styled("8. Exit", "green")
        
        self.print_cost_summary(compact=True)
        self.print_styled(f"\nWorking Directory: {self.src_path}", "yellow")
    
    def get_menu_choice(self) -> str:
        """Get user menu selection."""
        while True:
            try:
                choice = input(f"\n{self.colors['bold']}Enter choice (1-8): {self.colors['end']}").strip()
                if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                    return choice
                else:
                    print(f"{self.colors['red']}Invalid choice. Please enter 1-8.{self.colors['end']}")
            except KeyboardInterrupt:
                return '8'  # Exit on Ctrl+C
    
    def run_grok_cli_command(self, args: List[str]) -> Tuple[bool, str]:
        """Execute grok-cli command and return success status and output."""
        try:
            # Build the complete command
            cmd = ["python", "-m", "grok_cli.cli"] + args + ["--src", self.src_path, "--cost"]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(__file__))
            )
            
            self.current_session["commands_executed"] += 1
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr or result.stdout
                
        except Exception as e:
            return False, f"Error executing command: {e}"
    
    # Legacy interactive_chat method removed - now using Grid UI for all interactive chat
    
    def execute_leader_mode(self, objective: str):
        """Execute leader mode for strategic planning."""
        self.print_styled("\n🎯 Leader Mode Activated", "header")
        self.print_styled(f"Objective: {objective}", "yellow")
        
        success, output = self.run_grok_cli_command(["--lead", "--prompt", objective])
        
        if success:
            self.print_styled("\nLeader Planning Complete:", "green")
            print(output)
        else:
            self.print_styled(f"\nLeader Mode Error: {output}", "red")
    
    def single_prompt_mode(self):
        """Handle single prompt input."""
        self.clear_screen()
        self.print_header()
        print(f"{self.colors['cyan']}📝 Single Prompt Mode{self.colors['end']}")
        
        prompt = input("\nEnter your prompt: ").strip()
        if not prompt:
            print("No prompt entered.")
            return
        
        print(f"\n{self.colors['yellow']}Processing...{self.colors['end']}")
        
        success, output = self.run_grok_cli_command(["--prompt", prompt])
        
        if success:
            print(f"\n{self.colors['green']}Response:{self.colors['end']}")
            print(output)
        else:
            print(f"\n{self.colors['red']}Error:{self.colors['end']} {output}")
        
        self.wait_for_key()
    
    def show_settings(self):
        """Display and manage settings."""
        self.clear_screen()
        self.print_header()
        print(f"{self.colors['cyan']}⚙️ Settings{self.colors['end']}")
        
        print(f"\nWorking Directory: {self.src_path}")
        print(f"Session Commands: {self.current_session['commands_executed']}")
        print(f"Cost Tracking: Enabled")
        
        # Show current grok-cli settings if available
        settings_file = os.path.join(os.path.dirname(__file__), "..", "settings.json")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                print(f"Current Model: {settings.get('model', 'grok-4')}")
                print(f"Streaming: {settings.get('stream', False)}")
            except Exception as e:
                print(f"Error reading settings: {e}")
        
        self.wait_for_key()
    
    def show_cost_analysis(self):
        """Show detailed cost analysis."""
        self.clear_screen()
        self.print_header()
        print(f"{self.colors['cyan']}📊 Cost Analysis{self.colors['end']}")
        
        if self.token_counter:
            self.token_counter.display_session_costs()
        else:
            print("Cost tracking not available.")
        
        self.wait_for_key()
    
    def show_help(self):
        """Display help information."""
        self.clear_screen()
        self.print_header()
        print(f"{self.colors['cyan']}❓ GroKit Help{self.colors['end']}")
        
        print(f"\n{self.colors['green']}Main Features:{self.colors['end']}")
        print("• Interactive Chat - Full conversation with Grok in enhanced Grid UI")
        print("• Leader Mode - Strategic planning with grok-3-mini -> grok-4-0709")
        print("• Single Prompt - Quick questions and responses")
        print("• Cost Tracking - Real-time USD cost monitoring with streaming")
        print("• Persistent Storage - Chat history and session management")
        
        print(f"\n{self.colors['green']}Chat Commands:{self.colors['end']}")
        print("• /leader [objective] - Activate leader mode in chat")
        print("• /reasoning [prompt] - Activate reasoning mode for deeper analysis")
        print("• /multiline - Enable multi-line input mode")
        print("• /costs - Show current session costs")
        print("• /help - Show help information")
        print("• /quit - Exit chat mode")
        
        print(f"\n{self.colors['green']}Keyboard Shortcuts:{self.colors['end']}")
        print("• SHIFT+ENTER - New line (in multiline mode)")
        print("• Ctrl+C - Exit current mode")
        print("• ESC - Exit multiline mode")
        
        self.wait_for_key()
    
    def show_chat_help(self):
        """Show help within chat mode."""
        self.print_styled("\nChat Commands:", "cyan")
        print("• /leader [objective] - Strategic planning mode")
        print("• /multi - Toggle multi-line input mode")
        print("• /costs - Show session costs")
        print("• /help - Show this help")
        print("• /quit - Exit chat")
    
    def launch_grid_ui(self):
        """Launch the enhanced grid UI interface."""
        self.clear_screen()
        self.print_styled("🖥️  Launching Grid UI...", "cyan")
        print("\nInitializing enhanced interface with:")
        print("• Grid-based layout with header, chat, input, and status areas")
        print("• Persistent chat history in .grok/history/")
        print("• Enhanced input with clipboard support and multi-line mode")
        print("• Real-time cost tracking and session management")
        print("• Leader-follower integration")
        
        try:
            # Import and initialize the grid UI components directly here
            grid_ui = GroKitGridIntegration(self.src_path)
            grid_ui.run()
        except Exception as e:
            self.print_styled(f"\nError launching Grid UI: {e}", "red")
            self.print_styled("Falling back to standard interface...", "yellow")
            self.wait_for_key()
    
    def resume_previous_session(self):
        """Display session browser and allow user to select a previous session."""
        self.clear_screen()
        self.print_header()
        print(f"{self.colors['cyan']}🔄 Resume Previous Session{self.colors['end']}")
        
        # Get available sessions
        from .persistence import PersistentStorage
        sessions = PersistentStorage.get_available_sessions(self.src_path)
        
        if not sessions:
            print(f"\n{self.colors['yellow']}No previous sessions found.{self.colors['end']}")
            print("Start a new interactive chat session to create your first session.")
            self.wait_for_key()
            return
        
        # Display sessions
        print(f"\n{self.colors['green']}Available Sessions:{self.colors['end']}")
        print("=" * 70)
        
        for i, session in enumerate(sessions, 1):
            # Parse start time for display
            start_time = session.get("start_time", "")
            if start_time:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    display_time = start_time
            else:
                display_time = "Unknown"
            
            # Display session info
            print(f"\n{self.colors['bold']}{i}. Session: {session.get('session_id', 'unknown')}{self.colors['end']}")
            print(f"   Started: {display_time}")
            print(f"   Messages: {session.get('message_count', 0)}")
            print(f"   Cost: ${session.get('total_cost', 0.0):.4f} | Tokens: {session.get('total_tokens', 0):,}")
            print(f"   Preview: {session.get('preview', 'No preview available')}")
        
        print("=" * 70)
        print(f"{self.colors['blue']}0. Return to main menu{self.colors['end']}")
        
        # Get user choice
        while True:
            try:
                choice = input(f"\n{self.colors['bold']}Select session (0-{len(sessions)}): {self.colors['end']}").strip()
                
                if choice == '0':
                    return
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(sessions):
                    selected_session = sessions[choice_num - 1]
                    self._launch_grid_ui_with_session(selected_session)
                    return
                else:
                    print(f"{self.colors['red']}Invalid choice. Please enter 0-{len(sessions)}.{self.colors['end']}")
                    
            except ValueError:
                print(f"{self.colors['red']}Invalid input. Please enter a number.{self.colors['end']}")
            except KeyboardInterrupt:
                return
    
    def _launch_grid_ui_with_session(self, session_info: Dict):
        """Launch Grid UI with a pre-loaded session."""
        self.clear_screen()
        self.print_styled("🖥️  Loading session into Grid UI...", "cyan")
        print(f"\nLoading session: {session_info.get('session_id', 'unknown')}")
        print(f"Messages: {session_info.get('message_count', 0)}")
        print(f"Original start time: {session_info.get('start_time', 'unknown')}")
        
        try:
            # Load the full session data
            session_data = PersistentStorage.load_session_data(session_info["file_path"])
            
            # Launch grid UI with pre-loaded session
            grid_ui = GroKitGridIntegration(self.src_path, loaded_session=session_data)
            grid_ui.run()
        except Exception as e:
            self.print_styled(f"\nError loading session: {e}", "red")
            print("Falling back to standard interface...")
            self.wait_for_key()
    
    def run(self):
        """Main run loop for GroKit."""
        try:
            while True:
                self.clear_screen()
                self.print_header()
                self.print_main_menu()
                
                choice = self.get_menu_choice()
                
                if choice == '1':
                    self.launch_grid_ui()  # Use grid UI for interactive chat
                elif choice == '2':
                    self.resume_previous_session()  # New session browser
                elif choice == '3':
                    objective = input("\nEnter objective for leader mode: ").strip()
                    if objective:
                        self.execute_leader_mode(objective)
                        self.wait_for_key()
                elif choice == '4':
                    self.single_prompt_mode()
                elif choice == '5':
                    self.show_settings()
                elif choice == '6':
                    self.show_cost_analysis()
                elif choice == '7':
                    self.show_help()
                elif choice == '8':
                    break
        
        except KeyboardInterrupt:
            pass
        
        # Final cost summary
        print(f"\n{self.colors['cyan']}Thank you for using GroKit!{self.colors['end']}")
        self.print_cost_summary(compact=False)


class GroKitGridIntegration:
    """Integration class for the grid UI within GroKit."""
    
    def __init__(self, src_path: str = ".", loaded_session: Dict = None):
        """Initialize the Grid UI integration."""
        self.src_path = src_path
        self.running = True
        self.loaded_session = loaded_session
        
        # Initialize components
        self.renderer = GridRenderer()
        self.storage = PersistentStorage(self.src_path)
        
        # Initialize enhanced input with callback for real-time updates
        self.enhanced_input = EnhancedInputHandler(
            on_char_update=self._on_input_update
        )
        
        # Initialize AI engine
        self.engine = GrokEngine()
        self.engine.set_source_directory(self.src_path)
        self.token_counter = None
        
        # Version manager
        self.version_mgr = VersionManager(os.path.dirname(os.path.dirname(__file__)))
        self.renderer.update_header(version=self.version_mgr.get_version())
        
        # UI state
        self.status_message = "Ready"
        self.cost_display = "$0.0000"
        self.tokens_display = "0"
        
        # Setup UI
        self._setup_ui()
        self._enable_cost_tracking()
        
        # Load conversation history (either from loaded session or recent history)
        if self.loaded_session:
            self._load_session_into_grid()
        else:
            self._load_conversation_history()
    
    def _setup_ui(self):
        """Initialize the UI with header and initial content."""
        version = self.version_mgr.get_version()
        self.renderer.update_header(
            title="GROKIT",
            subtitle="Enhanced Grid Interface",
            version=version
        )
        
        # Add welcome message
        welcome_msg = (
            "Welcome to GroKit Grid UI! Enhanced interface features:\n"
            "• Real-time chat with persistent history\n"
            "• Clipboard paste support (/paste)\n"
            "• Multi-line input mode (/multi)\n"
            "• Cost tracking and optimization\n"
            "• Leader-follower strategic planning\n\n"
            "Type /help for commands or start chatting!"
        )
        
        self.renderer.add_ai_message("system", welcome_msg)
        self._update_status("GroKit Grid initialized")
    
    def _load_conversation_history(self):
        """Load conversation history for new sessions (should start fresh)."""
        # For new interactive chat sessions, we don't load old history
        # Only the welcome message should be shown
        # History loading only happens when resuming a specific session
        pass
    
    def _load_session_into_grid(self):
        """Load a previous session's data into the grid UI."""
        try:
            if not self.loaded_session:
                return
            
            # Update storage to use the loaded session
            session_id = self.loaded_session.get("session_id", "unknown")
            messages = self.loaded_session.get("messages", [])
            cost_tracking = self.loaded_session.get("cost_tracking", {})
            
            # Replace welcome message with session info
            self.renderer.clear_ai_history()
            
            try:
                session_info_msg = (
                    f"📂 Resumed Session: {session_id}\n"
                    f"Original start: {self.loaded_session.get('start_time', 'unknown')}\n"
                    f"Messages loaded: {len(messages)}\n"
                    f"Session cost: ${cost_tracking.get('total_cost', 0.0):.4f}\n\n"
                    f"Continuing conversation..."
                )
            except UnicodeEncodeError:
                # ASCII fallback for Windows
                session_info_msg = (
                    f"[RESUMED] Session: {session_id}\n"
                    f"Original start: {self.loaded_session.get('start_time', 'unknown')}\n"
                    f"Messages loaded: {len(messages)}\n"
                    f"Session cost: ${cost_tracking.get('total_cost', 0.0):.4f}\n\n"
                    f"Continuing conversation..."
                )
            
            self.renderer.add_ai_message("system", session_info_msg)
            
            # Load all messages from the session
            for message in messages:
                role = message.get("role", "unknown")
                content = message.get("content", "")
                timestamp = message.get("timestamp", "")
                
                # Extract just the time part for display
                if timestamp:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        display_time = dt.strftime("%H:%M:%S")
                    except:
                        display_time = timestamp
                else:
                    display_time = ""
                
                self.renderer.add_ai_message(role, content, display_time)
            
            # Update cost display with session totals
            self.cost_display = f"${cost_tracking.get('total_cost', 0.0):.4f}"
            self.tokens_display = f"{cost_tracking.get('total_tokens', 0):,}"
            
            self._update_status(f"Session resumed - {len(messages)} messages loaded")
            
            # Update storage session ID to continue this session
            self.storage.session_id = session_id
            
        except Exception as e:
            print(f"Warning: Could not load session into grid: {e}")
            # Fall back to regular conversation history loading
            self._load_conversation_history()
    
    def _enable_cost_tracking(self):
        """Enable cost tracking for the session with unified tracking."""
        try:
            from .tokenCount import create_token_counter
            cost_file = os.path.join(self.src_path, "grokit_grid_costs.json")
            
            # Create a shared token counter instance
            self.token_counter = create_token_counter(cost_file)
            
            # Use the same token counter for the engine
            self.engine.token_counter = self.token_counter
            self.engine.cost_tracking_enabled = True
            
            # Initialize display
            self._update_cost_display()
        except Exception as e:
            print(f"Warning: Could not enable cost tracking: {e}")
    
    def _update_status(self, message: str):
        """Update status message."""
        self.status_message = message
        self.renderer.update_status(message=message)
    
    def _update_cost_display(self):
        """Update cost and token display with real-time data."""
        if self.token_counter:
            try:
                summary = self.token_counter.get_session_summary()
                self.cost_display = f"${summary.get('total_cost_usd', 0.0):.4f}"
                self.tokens_display = f"{summary.get('total_tokens', 0):,}"
                self.renderer.update_status(cost=self.cost_display, tokens=self.tokens_display)
                
                # Also update the engine's token counter if they're different
                if self.engine.token_counter and self.engine.token_counter != self.token_counter:
                    engine_summary = self.engine.token_counter.get_session_summary()
                    if engine_summary.get('total_cost_usd', 0) > summary.get('total_cost_usd', 0):
                        self.cost_display = f"${engine_summary.get('total_cost_usd', 0.0):.4f}"
                        self.tokens_display = f"{engine_summary.get('total_tokens', 0):,}"
                        self.renderer.update_status(
                            cost=self.cost_display,
                            tokens=self.tokens_display
                        )
            except Exception as e:
                print(f"Warning: Could not update cost display: {e}")
    
    def _extract_cost_info(self, response: str) -> Optional[Dict[str, str]]:
        """Extract cost information from response if present."""
        # Look for cost patterns in the response
        import re
        cost_pattern = r'Estimated cost: \$([0-9.]+) \(([0-9,]+) input tokens\)'
        match = re.search(cost_pattern, response)
        if match:
            return {
                'cost': f"${match.group(1)}",
                'tokens': match.group(2).replace(',', '')
            }
        return None
    
    def _process_special_commands(self, user_input: str) -> Optional[str]:
        """Process special GroKit commands."""
        command = user_input.strip().lower()
        
        if command == "/quit" or command == "/exit":
            self.running = False
            return None
        
        elif command == "/clear":
            self.renderer.clear_ai_history()
            self._update_status("Chat history cleared")
            return None
        
        elif command.startswith("/leader"):
            objective = command[7:].strip()
            if not objective:
                self._update_status("Enter objective for leader mode:")
                self.renderer.render_full_screen()
                objective_input, _ = self.enhanced_input.get_input("Objective: ")
                objective = objective_input.strip()
            
            if objective and objective != "/quit":
                self._execute_leader_mode(objective)
            return None
        
        elif command.startswith("/reasoning"):
            prompt = command[10:].strip()
            if not prompt:
                self._update_status("Enter prompt for reasoning mode:")
                self.renderer.render_full_screen()
                reasoning_input, _ = self.enhanced_input.get_input("Reasoning prompt: ")
                prompt = reasoning_input.strip()
            
            if prompt and prompt != "/quit":
                self._execute_reasoning_mode(prompt)
            return None
        
        elif command == "/costs":
            self._show_cost_summary()
            return None
        
        elif command == "/help":
            self._show_help()
            return None
        
        return user_input
    
    def _execute_leader_mode(self, objective: str):
        """Execute leader-follower mode."""
        self._update_status("Initializing leader mode...")
        self.renderer.add_ai_message("system", f"Leader Mode: {objective}")
        self.renderer.render_full_screen()
        
        try:
            # Simple placeholder - would integrate with actual leader orchestrator
            self.renderer.add_ai_message("leader", f"Strategic plan for: {objective}")
            self.renderer.add_ai_message("system", "Leader mode completed")
            self._update_status("Leader mode completed")
        except Exception as e:
            self.renderer.add_ai_message("error", f"Leader mode error: {e}")
            self._update_status("Leader mode failed")
        
        self.renderer.render_full_screen()
    
    def _execute_reasoning_mode(self, prompt: str):
        """Execute reasoning mode with enhanced AI processing."""
        self._update_status("Activating reasoning mode...")
        self.renderer.add_ai_message("system", f"Reasoning Mode: {prompt}")
        self.renderer.render_full_screen()
        
        try:
            # Get AI response with reasoning enabled
            self._update_status("AI is reasoning deeply...")
            self.renderer.render_full_screen()
            
            ai_response = self._get_ai_response(prompt, reasoning=True)
            if ai_response:
                self.renderer.add_ai_message("assistant", f"[REASONING] {ai_response}")
                self.storage.add_message("assistant", ai_response, {"reasoning": True})
            
            self._update_cost_display()
            self._update_status("Reasoning completed")
        except Exception as e:
            self.renderer.add_ai_message("error", f"Reasoning mode error: {e}")
            self._update_status("Reasoning mode failed")
        
        self.renderer.render_full_screen()
    
    def _show_cost_summary(self):
        """Show cost summary."""
        if self.token_counter:
            summary = self.token_counter.get_session_summary()
            breakdown = summary.get('cost_breakdown', {})
            
            cost_msg = (
                f"Session Cost Summary:\n"
                f"Session Duration: {summary.get('session_duration', 'N/A')}\n"
                f"Total Cost: ${summary.get('total_cost_usd', 0.0):.4f} USD\n\n"
                f"Cost Breakdown:\n"
            )
            
            # Add input tokens info
            input_info = breakdown.get('input_tokens', {})
            if input_info.get('count', 0) > 0:
                cost_msg += f"  Input Tokens: {input_info.get('count', 0):,} -> ${input_info.get('cost', 0.0):.4f}\n"
            
            # Add output tokens info
            output_info = breakdown.get('output_tokens', {})
            if output_info.get('count', 0) > 0:
                cost_msg += f"  Output Tokens: {output_info.get('count', 0):,} -> ${output_info.get('cost', 0.0):.4f}\n"
            
            # Add cached tokens info
            cached_info = breakdown.get('cached_tokens', {})
            if cached_info.get('count', 0) > 0:
                cost_msg += f"  Cached Tokens: {cached_info.get('count', 0):,} -> ${cached_info.get('cost', 0.0):.4f}\n"
            
            # Add live searches info
            search_info = breakdown.get('live_searches', {})
            if search_info.get('count', 0) > 0:
                cost_msg += f"  Live Searches: {search_info.get('count', 0)} -> ${search_info.get('cost', 0.0):.4f}\n"
            
            cost_msg += f"\nOperations: {summary.get('operations_count', 0)}"
        else:
            cost_msg = "Cost tracking not available."
        
        # Clear the input area first
        self.renderer.update_input("", 0)
        
        # Add cost summary as system message
        self.renderer.add_ai_message("system", f"Here is the output of \"/costs\":\n\n{cost_msg}")
        
        # Only update the AI window and input area, not full screen
        self.renderer.render_ai_window()
        self.renderer.render_input_area()
    
    def _show_help(self):
        """Show help information."""
        help_msg = (
            "GroKit Grid Commands:\n"
            "/leader [objective] - Strategic planning\n"
            "/reasoning [prompt] - Deep reasoning mode\n"
            "/paste - Paste from clipboard\n"
            "/multi - Toggle multi-line input\n"
            "/costs - Show cost summary\n"
            "/clear - Clear chat history\n"
            "/help - Show this help\n"
            "/quit - Exit to main menu"
        )
        
        # Clear the input area first
        self.renderer.update_input("", 0)
        
        # Add help as system message with proper header
        self.renderer.add_ai_message("system", f"Here is the output of \"/help\":\n\n{help_msg}")
        
        # Only update the AI window and input area, not full screen
        self.renderer.render_ai_window()
        self.renderer.render_input_area()
    
    def _get_ai_response(self, user_input: str, reasoning: bool = False) -> str:
        """Get real AI response using GrokEngine with streaming."""
        try:
            import os
            
            # Check for API key
            api_key = os.getenv('XAI_API_KEY')
            if not api_key:
                return "Error: No XAI_API_KEY found. Please set your API key in environment variables."
            
            # Create messages for the conversation with enhanced system prompt
            system_prompt = self.engine.get_enhanced_system_prompt()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # Use engine to get response with streaming enabled
            try:
                # Create a simple namespace object for args
                class Args:
                    model = "grok-4-0709"
                    stream = True
                    debug = 0
                
                args = Args()
                brave_key = os.getenv('BRAVE_SEARCH_API_KEY', '')
                
                # Get response with reasoning support using SDK
                response = self.engine.api_call(api_key, messages, args.model, args.stream, self.engine.tools, retry_count=0, reasoning=reasoning)
                
                # Check if we're using SDK response
                if hasattr(response, 'sdk_response'):
                    # SDK response format - update costs immediately
                    self._update_cost_display()
                    
                    if reasoning and hasattr(response, 'reasoning_content') and response.reasoning_content:
                        return f"[REASONING]\n{response.reasoning_content}\n\n[RESPONSE]\n{response.content}"
                    else:
                        return response.content if response.content else "I apologize, but I couldn't generate a response."
                elif args.stream:
                    # Handle streaming response (requests) with real-time cost updates
                    assistant_content, tool_calls, tool_outputs = self.engine.handle_stream_with_tools(
                        response, brave_key, debug_mode=args.debug, capture_tools=True
                    )
                    
                    # Update cost display after streaming completes
                    self._update_cost_display()
                    
                    # If we have tool outputs (including diffs), append them to the response
                    if tool_outputs:
                        if assistant_content:
                            return f"{assistant_content}\n\n{tool_outputs}"
                        else:
                            return tool_outputs
                    
                    return assistant_content if assistant_content else "I apologize, but I couldn't generate a response."
                else:
                    # Handle non-streaming response (requests) with cost update
                    self._update_cost_display()
                    
                    if hasattr(response, 'choices') and response.choices:
                        return response.choices[0].message.content
                    else:
                        return "I apologize, but I couldn't generate a response."
                        
            except Exception as e:
                return f"Error communicating with AI: {str(e)}"
                
        except Exception as e:
            return f"Error in AI response system: {str(e)}"
    
    def _on_input_update(self, text: str, cursor_pos: int):
        """Callback for real-time input updates."""
        self.renderer.update_input(text, cursor_pos)
        # Critical: render the input area to show the updated text
        self.renderer.render_input_area()
        sys.stdout.flush()
    
    def run(self):
        """Main run loop for Grid UI."""
        try:
            # Initial render
            self.renderer.render_full_screen()
            
            while self.running:
                try:
                    # Get user input
                    user_input, input_metadata = self.enhanced_input.get_input("You: ")
                    
                    if not user_input.strip():
                        continue
                    
                    # Process special commands
                    processed_input = self._process_special_commands(user_input)
                    if processed_input is None:
                        continue
                    
                    # Add user message and process
                    self.renderer.add_ai_message("user", processed_input)
                    self.storage.add_message("user", processed_input, input_metadata)
                    
                    # Update only the AI window and status, not full screen
                    self._update_status("AI is thinking...")
                    self.renderer.render_ai_window()
                    self.renderer.render_status_bar()
                    
                    ai_response = self._get_ai_response(processed_input)
                    if ai_response:
                        # Extract cost info if present in response
                        cost_info = self._extract_cost_info(ai_response)
                        if cost_info:
                            self.renderer.add_ai_message("assistant", ai_response, 
                                                        timestamp=datetime.now().strftime("%H:%M:%S"),
                                                        cost=cost_info['cost'],
                                                        tokens=cost_info['tokens'])
                        else:
                            self.renderer.add_ai_message("assistant", ai_response)
                        self.storage.add_message("assistant", ai_response)
                    
                    # Update cost display in status bar
                    self._update_cost_display()
                    self._update_status("Response received")
                    
                    # Only update AI window and status bar, not full screen
                    self.renderer.render_ai_window()
                    self.renderer.render_status_bar()
                    
                    # Clear input area for next input
                    self.renderer.update_input("", 0)
                    
                except KeyboardInterrupt:
                    self.running = False
                except Exception as e:
                    error_msg = f"Error: {e}"
                    self.renderer.add_ai_message("error", error_msg)
                    self._update_status("Error occurred")
                    self.renderer.render_full_screen()
        
        finally:
            # Return to menu
            print(f"\nReturning to GroKit main menu...")
            time.sleep(1)


def main():
    """Main entry point for GroKit."""
    import argparse
    
    parser = argparse.ArgumentParser(description="GroKit - Interactive Grok Interface")
    parser.add_argument("--src", default=".", help="Source directory (default: current directory)")
    args = parser.parse_args()
    
    # Verify grok-cli is available
    try:
        result = subprocess.run(
            ["python", "-m", "grok_cli.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        if result.returncode != 0:
            print("Error: grok-cli not available. Please ensure it's properly installed.")
            sys.exit(1)
    except Exception as e:
        print(f"Error: Cannot access grok-cli: {e}")
        sys.exit(1)
    
    # Launch GroKit
    ui = GroKitUI(args.src)
    ui.run()


if __name__ == "__main__":
    main()