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
            self.print_styled("2. 🎯 Leader Mode (Strategic Planning)", "green")
            self.print_styled("3. 📋 Single Prompt", "green")
            self.print_styled("4. ⚙️  Settings", "green")
            self.print_styled("5. 📊 Cost Analysis", "green")
            self.print_styled("6. ❓ Help", "green")
            self.print_styled("7. 🚪 Exit", "green")
        except UnicodeEncodeError:
            self.print_styled("1. Interactive Chat (Grid UI)", "green")
            self.print_styled("2. Leader Mode (Strategic Planning)", "green")
            self.print_styled("3. Single Prompt", "green")
            self.print_styled("4. Settings", "green")
            self.print_styled("5. Cost Analysis", "green")
            self.print_styled("6. Help", "green")
            self.print_styled("7. Exit", "green")
        
        self.print_cost_summary(compact=True)
        self.print_styled(f"\nWorking Directory: {self.src_path}", "yellow")
    
    def get_menu_choice(self) -> str:
        """Get user menu selection."""
        while True:
            try:
                choice = input(f"\n{self.colors['bold']}Enter choice (1-7): {self.colors['end']}").strip()
                if choice in ['1', '2', '3', '4', '5', '6', '7']:
                    return choice
                else:
                    print(f"{self.colors['red']}Invalid choice. Please enter 1-7.{self.colors['end']}")
            except KeyboardInterrupt:
                return '7'  # Exit on Ctrl+C
    
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
                    objective = input("\nEnter objective for leader mode: ").strip()
                    if objective:
                        self.execute_leader_mode(objective)
                        self.wait_for_key()
                elif choice == '3':
                    self.single_prompt_mode()
                elif choice == '4':
                    self.show_settings()
                elif choice == '5':
                    self.show_cost_analysis()
                elif choice == '6':
                    self.show_help()
                elif choice == '7':
                    break
        
        except KeyboardInterrupt:
            pass
        
        # Final cost summary
        print(f"\n{self.colors['cyan']}Thank you for using GroKit!{self.colors['end']}")
        self.print_cost_summary(compact=False)


class GroKitGridIntegration:
    """Integration class for the grid UI within GroKit."""
    
    def __init__(self, src_path: str):
        self.src_path = src_path
        
        # Initialize grid UI components
        self.renderer = GridRenderer()
        self.version_manager = VersionManager(self.src_path)
        self.storage = PersistentStorage(self.src_path)
        self.enhanced_input = EnhancedInputHandler(on_status_update=self._update_status)
        
        # Initialize AI engine and tools
        self.engine = GrokEngine()
        self.engine.set_source_directory(self.src_path)
        self.token_counter = None
        
        # UI state
        self.running = True
        self.status_message = "Ready"
        self.cost_display = "$0.0000"
        self.tokens_display = "0"
        
        # Setup UI
        self._setup_ui()
        self._enable_cost_tracking()
    
    def _setup_ui(self):
        """Initialize the UI with header and initial content."""
        version = self.version_manager.get_version()
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
        self.renderer.render_full_screen()
    
    def _update_cost_display(self):
        """Update cost and token display with real-time data."""
        if self.token_counter:
            try:
                summary = self.token_counter.get_session_summary()
                self.cost_display = f"${summary.get('total_cost_usd', 0.0):.4f}"
                self.tokens_display = f"{summary.get('total_tokens', 0):,}"
                
                self.renderer.update_status(
                    cost=self.cost_display,
                    tokens=self.tokens_display
                )
                
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
        """Display cost summary."""
        if self.token_counter:
            summary = self.token_counter.get_session_summary()
            cost_msg = (
                f"Session Cost Summary:\n"
                f"Total: ${summary.get('total_cost_usd', 0.0):.4f} USD\n"
                f"Tokens: {summary.get('total_tokens', 0):,}\n"
                f"Operations: {summary.get('operations_count', 0)}"
            )
        else:
            cost_msg = "Cost tracking not available."
        
        self.renderer.add_ai_message("system", cost_msg)
        self.renderer.render_full_screen()
    
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
        
        self.renderer.add_ai_message("system", help_msg)
        self.renderer.render_full_screen()
    
    def _get_ai_response(self, user_input: str, reasoning: bool = False) -> str:
        """Get real AI response using GrokEngine with streaming."""
        try:
            import os
            
            # Check for API key
            api_key = os.getenv('XAI_API_KEY')
            if not api_key:
                return "Error: No XAI_API_KEY found. Please set your API key in environment variables."
            
            # Create messages for the conversation
            messages = [
                {"role": "system", "content": "You are Grok, a helpful AI assistant built by xAI. Be concise but thorough in your responses."},
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
                    assistant_content, tool_calls = self.engine.handle_stream_with_tools(response, brave_key, debug_mode=args.debug)
                    
                    # Update cost display after streaming completes
                    self._update_cost_display()
                    
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
                    
                    # Get real AI response with streaming
                    self._update_status("AI is thinking...")
                    self.renderer.render_full_screen()
                    
                    ai_response = self._get_ai_response(processed_input)
                    if ai_response:
                        self.renderer.add_ai_message("assistant", ai_response)
                        self.storage.add_message("assistant", ai_response)
                    
                    # Force cost display update after response
                    self._update_cost_display()
                    self._update_status("Response received")
                    self.renderer.render_full_screen()
                    
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