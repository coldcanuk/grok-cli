"""
StreamingUI - Classic terminal interface with modern Rich formatting
No screen clearing, no cursor jumping, just smooth streaming goodness!
"""

import os
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any, Generator
from io import StringIO

# Rich imports for beautiful formatting
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class StreamingRenderer:
    """Classic terminal renderer with Rich formatting - streams like a dream!"""
    
    def __init__(self):
        self.console = None
        self.colors = self._init_colors()
        self.session_started = False
        
        if RICH_AVAILABLE:
            self.console = Console(
                force_terminal=True,
                highlight=True,
                legacy_windows=False,
                color_system="truecolor",
                width=None  # Auto-detect terminal width
            )
    
    def _init_colors(self) -> Dict[str, str]:
        """ANSI color codes for fallback when Rich isn't available."""
        return {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'cyan': '\033[96m',
            'red': '\033[91m',
            'magenta': '\033[95m'
        }
    
    def start_session(self, title: str = "GroKit Enhanced Chat"):
        """Start a new chat session with a beautiful header."""
        if self.session_started:
            return
            
        self.session_started = True
        
        if RICH_AVAILABLE:
            # Rich header with style
            header_text = Text()
            header_text.append("🚀 ", style="bold blue")
            header_text.append(title, style="bold cyan")
            header_text.append(" 🚀", style="bold blue")
            
            panel = Panel(
                header_text,
                border_style="cyan",
                padding=(0, 1)
            )
            self.console.print(panel)
            self.console.print()
            
            # Show features in columns
            features = [
                "💬 Real-time AI streaming",
                "🎨 Rich markdown formatting", 
                "💰 Live cost tracking",
                "📝 Code syntax highlighting"
            ]
            
            feature_text = Text()
            for feature in features:
                feature_text.append(f"  {feature}\n", style="dim")
            
            self.console.print(feature_text)
            self.console.print("=" * 60, style="dim")
            self.console.print()
            
        else:
            # Fallback for terminals without Rich (ASCII-safe)
            try:
                print(f"\n{self.colors['cyan']}{self.colors['bold']}🚀 {title} 🚀{self.colors['reset']}")
            except UnicodeEncodeError:
                print(f"\n{self.colors['cyan']}{self.colors['bold']}** {title} **{self.colors['reset']}")
            print("=" * 50)
            print(f"{self.colors['dim']}Real-time AI chat with enhanced formatting{self.colors['reset']}")
            print("=" * 50)
            print()
    
    def show_user_message(self, message: str, timestamp: Optional[str] = None):
        """Display user message with clean formatting."""
        if not timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        if RICH_AVAILABLE:
            # Rich user message
            user_text = Text()
            user_text.append(f"[{timestamp}] ", style="dim")
            user_text.append("You: ", style="bold green")
            user_text.append(message, style="default")
            self.console.print(user_text)
            
        else:
            # Fallback
            print(f"{self.colors['dim']}[{timestamp}]{self.colors['reset']} {self.colors['green']}{self.colors['bold']}You:{self.colors['reset']} {message}")
    
    def start_ai_response(self, timestamp: Optional[str] = None):
        """Start an AI response section."""
        if not timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        if RICH_AVAILABLE:
            ai_header = Text()
            ai_header.append(f"[{timestamp}] ", style="dim")
            ai_header.append("🤖 AI: ", style="bold blue")
            self.console.print(ai_header, end="")
            
        else:
            try:
                print(f"{self.colors['dim']}[{timestamp}]{self.colors['reset']} {self.colors['blue']}{self.colors['bold']}🤖 AI:{self.colors['reset']} ", end='', flush=True)
            except UnicodeEncodeError:
                print(f"{self.colors['dim']}[{timestamp}]{self.colors['reset']} {self.colors['blue']}{self.colors['bold']}AI:{self.colors['reset']} ", end='', flush=True)
    
    def stream_content(self, content_chunk: str, is_complete: bool = False):
        """Stream content chunk with formatting - the magic happens here!"""
        if RICH_AVAILABLE:
            # Always stream as plain text for real-time effect
            # Don't try to detect or render markdown during streaming
            self.console.print(content_chunk, end="", highlight=False)
        else:
            # Fallback streaming
            print(content_chunk, end='', flush=True)
    
    def finish_ai_response(self, final_content: str = "", cost_info: Optional[Dict] = None):
        """Finish the AI response with optional cost info."""
        if RICH_AVAILABLE:
            # Just show cost info - don't re-render content (it was already streamed)
            if cost_info:
                cost_text = Text()
                cost_text.append("    💰 ", style="dim")
                cost_text.append(f"Cost: {cost_info.get('cost', '$0.0000')}", style="dim cyan")
                cost_text.append(" | ", style="dim")
                cost_text.append(f"Tokens: {cost_info.get('tokens', '0')}", style="dim cyan")
                self.console.print(cost_text)
            
            self.console.print()  # Extra line for spacing
            
        else:
            print()  # New line
            if cost_info:
                try:
                    print(f"    {self.colors['dim']}💰 Cost: {cost_info.get('cost', '$0.0000')} | Tokens: {cost_info.get('tokens', '0')}{self.colors['reset']}")
                except UnicodeEncodeError:
                    print(f"    {self.colors['dim']}Cost: {cost_info.get('cost', '$0.0000')} | Tokens: {cost_info.get('tokens', '0')}{self.colors['reset']}")
            print()
    
    def show_system_message(self, message: str, style: str = "info"):
        """Show system messages (commands, errors, etc.)."""
        if RICH_AVAILABLE:
            if style == "error":
                self.console.print(f"❌ {message}", style="red")
            elif style == "success":
                self.console.print(f"✅ {message}", style="green")
            elif style == "warning":
                self.console.print(f"⚠️  {message}", style="yellow")
            else:
                self.console.print(f"ℹ️  {message}", style="blue")
                
        else:
            color = self.colors.get('red' if style == 'error' else 'green' if style == 'success' else 'yellow' if style == 'warning' else 'blue', '')
            print(f"{color}{message}{self.colors['reset']}")
    
    def show_help(self):
        """Display help information."""
        if RICH_AVAILABLE:
            help_text = """
# GroKit Commands

**Chat Commands:**
- `/clear` - Clear chat history 
- `/costs` - Show session cost summary
- `/leader [objective]` - Strategic planning mode
- `/reasoning [prompt]` - Deep reasoning mode
- `/help` - Show this help
- `/quit` - Exit chat

**Tips:**
- Just type normally to chat with AI
- For multiline input: end your first line with `###`, then type more lines, then `###` on a new line to submit
- Code blocks get syntax highlighting automatically
- Responses stream in real-time
- Ctrl+C to exit anytime
"""
            md = Markdown(help_text, code_theme="monokai")
            self.console.print(Panel(md, border_style="blue", title="Help"))
            
        else:
            try:
                print(f"\n{self.colors['blue']}📖 GroKit Commands{self.colors['reset']}")
            except UnicodeEncodeError:
                print(f"\n{self.colors['blue']}GroKit Commands{self.colors['reset']}")
            print("-" * 30)
            print(f"{self.colors['green']}/clear{self.colors['reset']} - Clear chat history")
            print(f"{self.colors['green']}/costs{self.colors['reset']} - Show costs")
            print(f"{self.colors['green']}/help{self.colors['reset']} - Show help")
            print(f"{self.colors['green']}/quit{self.colors['reset']} - Exit")
            print()
    
    def show_cost_summary(self, cost_data: Dict):
        """Show beautiful cost summary."""
        if RICH_AVAILABLE:
            cost_text = f"""
# 💰 Session Cost Summary

**Total Cost:** ${cost_data.get('total_cost_usd', 0.0):.6f} USD
**Total Tokens:** {cost_data.get('total_tokens', 0):,}
**Operations:** {cost_data.get('operations_count', 0)}
**Duration:** {cost_data.get('session_duration', 'N/A')}

*Costs are tracked in real-time for transparency*
"""
            md = Markdown(cost_text)
            self.console.print(Panel(md, border_style="cyan", title="Cost Tracking"))
            
        else:
            try:
                print(f"\n{self.colors['cyan']}💰 Cost Summary{self.colors['reset']}")
            except UnicodeEncodeError:
                print(f"\n{self.colors['cyan']}Cost Summary{self.colors['reset']}")
            print("-" * 20)
            print(f"Total: ${cost_data.get('total_cost_usd', 0.0):.6f} USD")
            print(f"Tokens: {cost_data.get('total_tokens', 0):,}")
            print(f"Operations: {cost_data.get('operations_count', 0)}")
            print()

    def get_input(self, prompt: str = "You") -> str:
        """Get user input with multiline support."""
        if RICH_AVAILABLE:
            # Use rich prompt with timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            prompt_text = Text()
            prompt_text.append(f"[{timestamp}] ", style="dim")
            prompt_text.append(f"{prompt}: ", style="bold green")
            
            self.console.print(prompt_text, end="")
            
            # Check if user wants multiline (they'll type ###)
            first_line = input()
            
            # Check for multiline mode (if user types ### at the end)
            if first_line.endswith("###"):
                # Remove the ### and enter multiline mode
                lines = [first_line[:-3]]
                self.console.print("\n(Multi-line mode: Type '###' on new line to submit)", style="dim")
                
                while True:
                    try:
                        line = input("... ")
                        if line.strip() == "###":
                            break
                        lines.append(line)
                    except KeyboardInterrupt:
                        break
                
                user_input = "\n".join(lines).strip()
            else:
                user_input = first_line
            
            # Clear the input area and show the complete user message properly formatted
            user_display = Text()
            user_display.append(f"[{timestamp}] ", style="dim")
            user_display.append("You: ", style="bold green")
            
            # Show multiline content with proper formatting
            if "\n" in user_input:
                # For multiline, show a truncated version inline
                first_line_display = user_input.split('\n')[0]
                if len(first_line_display) > 60:
                    first_line_display = first_line_display[:60] + "..."
                user_display.append(f"{first_line_display} [multiline]", style="default")
            else:
                user_display.append(user_input, style="default")
            
            # Move cursor up and clear, then print formatted message
            print("\033[A\033[K", end="")  # ANSI: move up one line and clear
            self.console.print(user_display)
            
            return user_input
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            user_input = input(f"{self.colors['dim']}[{timestamp}]{self.colors['reset']} {self.colors['green']}{prompt}:{self.colors['reset']} ")
            # For fallback, basic single line input
            return user_input

class StreamingAIChat:
    """Classic terminal chat interface with streaming AI responses."""
    
    def __init__(self, src_path: str = "."):
        self.src_path = src_path
        self.renderer = StreamingRenderer()
        self.running = True
        
        # Import GroKit components we still need
        from .engine import GrokEngine
        from .persistence import PersistentStorage
        from .tokenCount import create_token_counter
        
        # Initialize backend components
        self.engine = GrokEngine()
        self.engine.set_source_directory(self.src_path)
        self.storage = PersistentStorage(self.src_path)
        
        # Cost tracking
        cost_file = os.path.join(self.src_path, "grokit_streaming_costs.json")
        self.token_counter = create_token_counter(cost_file)
        self.engine.token_counter = self.token_counter
        self.engine.cost_tracking_enabled = True
    
    def run(self):
        """Main chat loop - smooth as butter!"""
        try:
            # Start the session
            self.renderer.start_session("GroKit Streaming Chat")
            
            while self.running:
                try:
                    # Get user input (clean and simple)
                    user_input = self.renderer.get_input().strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.startswith('/'):
                        if self._handle_command(user_input):
                            continue
                        else:
                            break  # Exit requested
                    
                    # Note: user message display is already handled in get_input, no need to show again
                    
                    # Store user message
                    self.storage.add_message("user", user_input)
                    
                    # Start AI response
                    self.renderer.start_ai_response()
                    
                    # Stream AI response (the magic!)
                    response_content = self._stream_ai_response(user_input)
                    
                    # Finish AI response with cost info
                    cost_info = self._get_last_operation_cost()
                    self.renderer.finish_ai_response(response_content, cost_info)
                    
                    # Store AI response
                    self.storage.add_message("assistant", response_content)
                    
                except KeyboardInterrupt:
                    self.renderer.show_system_message("\nChat interrupted. Type /quit to exit or continue chatting.", "warning")
                    continue
                    
        except Exception as e:
            self.renderer.show_system_message(f"Error: {e}", "error")
        
        finally:
            self.renderer.show_system_message("Thanks for using GroKit! 🚀", "success")
    
    def _stream_ai_response(self, user_input: str) -> str:
        """Stream AI response in real-time with Rich formatting."""
        try:
            # Get API key
            api_key = os.getenv('XAI_API_KEY')
            if not api_key:
                error_msg = "Error: No XAI_API_KEY found in environment variables."
                self.renderer.stream_content(error_msg, True)
                return error_msg
            
            # Build messages for AI with conversation history
            system_prompt = self.engine.get_enhanced_system_prompt()
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history from storage
            chat_history = self.storage.get_chat_history()
            if chat_history:
                messages.extend(chat_history)
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Make streaming API call
            response = self.engine.api_call(
                api_key, messages, "grok-4-0709", 
                stream=True, tools=self.engine.tools
            )
            
            # Stream the response
            full_content = ""
            
            if hasattr(response, 'sdk_response'):
                # Non-streaming SDK response
                content = response.content if hasattr(response, 'content') else "No response"
                self.renderer.stream_content(content, True)
                return content
            
            # True streaming response
            for chunk in response.iter_lines():
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    if chunk_str.startswith('data: '):
                        data_str = chunk_str[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            import json
                            chunk_data = json.loads(data_str)
                            
                            if 'choices' in chunk_data and chunk_data['choices']:
                                delta = chunk_data['choices'][0].get('delta', {})
                                content_chunk = delta.get('content')
                                if content_chunk:
                                    full_content += content_chunk
                                    # Stream each chunk in real-time
                                    self.renderer.stream_content(content_chunk)
                                
                                # Check for finish reason
                                finish_reason = chunk_data['choices'][0].get('finish_reason')
                                if finish_reason:
                                    break
                                    
                        except json.JSONDecodeError as e:
                            # Debug: show JSON decode errors if debug mode is on
                            debug_mode = os.getenv('GROK_DEBUG', '0') == '1'
                            if debug_mode:
                                self.renderer.show_system_message(f"JSON decode error: {e} for chunk: {data_str[:100]}", "warning")
                            continue
                        except Exception as e:
                            # Catch any other streaming errors
                            debug_mode = os.getenv('GROK_DEBUG', '0') == '1'
                            if debug_mode:
                                self.renderer.show_system_message(f"Streaming error: {e}", "warning")
                            continue
            
            # Track the API call for cost calculation
            if self.token_counter:
                input_tokens = self.token_counter.count_messages_tokens(messages, "grok-4-0709")
                output_tokens = self.token_counter.count_tokens(full_content)
                self.token_counter.track_api_call(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model="grok-4-0709"
                )
            
            return full_content
            
        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            self.renderer.stream_content(error_msg, True)
            return error_msg
    
    def _handle_command(self, command: str) -> bool:
        """Handle chat commands. Returns True to continue, False to exit."""
        cmd = command.lower().strip()
        
        if cmd == "/quit" or cmd == "/exit":
            return False
        
        elif cmd == "/clear":
            # Clear terminal
            os.system('cls' if os.name == 'nt' else 'clear')
            # Clear session data
            self.storage.clear_session_history()
            if self.token_counter:
                self.token_counter.reset_session()
            # Restart session display
            self.renderer.session_started = False
            self.renderer.start_session("GroKit Streaming Chat")
            self.renderer.show_system_message("Chat history cleared!", "success")
        
        elif cmd == "/help":
            self.renderer.show_help()
        
        elif cmd == "/costs":
            if self.token_counter:
                summary = self.token_counter.get_session_summary()
                self.renderer.show_cost_summary(summary)
            else:
                self.renderer.show_system_message("Cost tracking not available", "warning")
        
        elif cmd.startswith("/leader"):
            objective = cmd[7:].strip()
            if not objective:
                objective = self.renderer.get_input("Enter objective")
            self.renderer.show_system_message(f"Leader mode: {objective}", "info")
            # TODO: Implement leader mode streaming
        
        elif cmd.startswith("/reasoning"):
            prompt = cmd[10:].strip()
            if not prompt:
                prompt = self.renderer.get_input("Enter reasoning prompt")
            self.renderer.show_system_message(f"Reasoning mode: {prompt}", "info")
            # TODO: Implement reasoning mode streaming
        
        else:
            self.renderer.show_system_message(f"Unknown command: {command}. Type /help for available commands.", "warning")
        
        return True
    
    def _get_last_operation_cost(self) -> Optional[Dict[str, str]]:
        """Get cost info for the last operation."""
        if not self.token_counter:
            return None
        
        try:
            summary = self.token_counter.get_session_summary()
            if summary and summary.get('operations_count', 0) > 0:
                operations = self.token_counter.session_costs.operations
                if operations:
                    last_op = operations[-1]
                    total_tokens = last_op.input_tokens + last_op.output_tokens
                    
                    from .tokenCount import GrokPricing
                    pricing = GrokPricing.get_model_pricing("grok-4-0709")
                    input_cost = GrokPricing.calculate_token_cost(last_op.input_tokens, pricing["input"])
                    output_cost = GrokPricing.calculate_token_cost(last_op.output_tokens, pricing["output"])
                    total_cost = input_cost + output_cost
                    
                    return {
                        'cost': f"${total_cost:.6f}",
                        'tokens': f"{total_tokens:,}"
                    }
        except Exception:
            pass
        
        return None