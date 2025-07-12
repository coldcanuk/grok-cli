"""
Grid-based UI system for GroKit - Terminal layout with persistent storage
"""

import os
import sys
import json
import time
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from .markdown_renderer import TerminalMarkdownRenderer


class GridRenderer:
    """Terminal grid rendering system with updateable content areas."""
    
    def __init__(self, terminal_width: int = None, terminal_height: int = None):
        self.width = terminal_width or shutil.get_terminal_size().columns
        self.height = terminal_height or shutil.get_terminal_size().lines
        
        # Grid layout configuration
        self.header_height = 3
        self.input_height = 3
        self.status_height = 1
        
        # Calculate AI window height (remaining space)
        self.ai_window_height = max(10, self.height - self.header_height - self.input_height - self.status_height - 2)
        
        # Color support
        self.colors = self._init_colors()
        
        # Markdown renderer for chat content
        self.markdown_renderer = TerminalMarkdownRenderer(width=self.width - 6)
        
        # Content storage
        self.header_content = {"title": "GROKIT", "subtitle": "Interactive Grok Interface", "version": ""}
        self.ai_content = []  # List of message objects
        self.input_content = {"text": "", "cursor_pos": 0}
        self.status_content = {"message": "Ready", "cost": "$0.0000", "tokens": "0"}
        
    def _init_colors(self):
        """Initialize color codes with Windows compatibility."""
        if os.name == 'nt':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass
        
        return {
            "header": "\033[95m",
            "blue": "\033[94m", 
            "cyan": "\033[96m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "bold": "\033[1m",
            "dim": "\033[2m",
            "end": "\033[0m",
            "bg_blue": "\033[44m",
            "bg_green": "\033[42m",
            "bg_yellow": "\033[43m"
        }
    
    def clear_screen(self):
        """Clear terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def move_cursor(self, row: int, col: int):
        """Move cursor to specific position."""
        print(f"\033[{row};{col}H", end="")
    
    def draw_box(self, x: int, y: int, width: int, height: int, title: str = "", color: str = "blue"):
        """Draw a box at specified coordinates."""
        try:
            # Top border
            self.move_cursor(y, x)
            print(f"{self.colors[color]}╔{title.center(width-2, '═')}╗{self.colors['end']}", end="")
            
            # Side borders
            for i in range(1, height-1):
                self.move_cursor(y+i, x)
                print(f"{self.colors[color]}║{' ' * (width-2)}║{self.colors['end']}", end="")
            
            # Bottom border
            self.move_cursor(y+height-1, x)
            print(f"{self.colors[color]}╚{'═' * (width-2)}╝{self.colors['end']}", end="")
            
        except UnicodeEncodeError:
            # ASCII fallback
            self.move_cursor(y, x)
            print(f"{self.colors[color]}+{title.center(width-2, '-')}+{self.colors['end']}", end="")
            
            for i in range(1, height-1):
                self.move_cursor(y+i, x)
                print(f"{self.colors[color]}|{' ' * (width-2)}|{self.colors['end']}", end="")
            
            self.move_cursor(y+height-1, x)
            print(f"{self.colors[color]}+{'-' * (width-2)}+{self.colors['end']}", end="")
    
    def render_header(self):
        """Render the header grid section."""
        # Header box
        self.draw_box(1, 1, self.width - 2, self.header_height, color="header")
        
        # Header content
        self.move_cursor(2, 3)
        title_text = f"{self.header_content['title']} - {self.header_content['subtitle']}"
        print(f"{self.colors['bold']}{title_text}{self.colors['end']}", end="")
        
        # Version in top-right
        if self.header_content['version']:
            version_text = f"v{self.header_content['version']}"
            version_x = self.width - len(version_text) - 3
            if version_x > 10:  # Only show if there's enough space
                self.move_cursor(2, version_x)
                print(f"{self.colors['dim']}{version_text}{self.colors['end']}", end="")
    
    def render_ai_window(self):
        """Render the AI conversation window."""
        ai_y = self.header_height + 1
        self.draw_box(1, ai_y, self.width - 2, self.ai_window_height, title="AI CONVERSATION", color="cyan")
        
        # Render conversation history (last messages that fit)
        content_start_y = ai_y + 1
        content_height = self.ai_window_height - 2
        content_width = self.width - 6
        
        # Calculate visible messages
        visible_messages = self._calculate_visible_messages(content_height, content_width)
        
        # Render each message
        current_y = content_start_y
        for msg in visible_messages:
            if current_y >= content_start_y + content_height:
                break
                
            lines_used = self._render_message(msg, 3, current_y, content_width)
            current_y += lines_used
    
    def _calculate_visible_messages(self, available_height: int, width: int) -> List[Dict]:
        """Calculate which messages can fit in the available space."""
        if not self.ai_content:
            return []
        
        visible = []
        total_height = 0
        
        # Work backwards from most recent messages
        for msg in reversed(self.ai_content):
            msg_height = self._calculate_message_height(msg, width)
            if total_height + msg_height <= available_height:
                visible.insert(0, msg)  # Insert at beginning to maintain order
                total_height += msg_height
            else:
                break
        
        return visible
    
    def _calculate_message_height(self, msg: Dict, width: int) -> int:
        """Calculate how many lines a message will take."""
        # Role line + markdown-rendered content lines
        if msg['role'] in ['assistant', 'user'] and msg.get('content'):
            # Use markdown renderer to get actual line count
            rendered_lines = self.markdown_renderer.render_markdown(msg['content'])
            return 1 + len(rendered_lines)  # +1 for role header
        else:
            # Fallback for system messages
            content_lines = len(self._wrap_text(msg.get('content', ''), width - 4))
            return 1 + content_lines
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to fit within specified width."""
        if not text:
            return [""]
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + len(current_line) <= width:
                current_line.append(word)
                current_length += len(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines if lines else [""]
    
    def _render_message(self, msg: Dict, x: int, y: int, width: int) -> int:
        """Render a single message and return lines used."""
        # Role header
        role = msg.get('role', 'unknown')
        timestamp = msg.get('timestamp', '')
        color = 'green' if role == 'user' else 'yellow'
        
        self.move_cursor(y, x)
        header = f"{role.upper()}: {timestamp}"
        print(f"{self.colors[color]}{header}{self.colors['end']}", end="")
        
        lines_used = 1
        
        # Message content with markdown rendering
        if role in ['assistant', 'user'] and msg.get('content'):
            # Use markdown renderer for rich formatting
            rendered_lines = self.markdown_renderer.render_markdown(msg['content'])
            
            for i, line in enumerate(rendered_lines):
                self.move_cursor(y + 1 + i, x + 2)
                # Note: line already contains ANSI color codes from markdown renderer
                print(line, end="")
                lines_used += 1
        else:
            # Fallback for system messages (no markdown)
            content_lines = self._wrap_text(msg.get('content', ''), width - 2)
            
            for i, line in enumerate(content_lines):
                self.move_cursor(y + 1 + i, x + 2)
                print(f"{self.colors['end']}{line}{self.colors['end']}", end="")
                lines_used += 1
        
        return lines_used
    
    def render_input_area(self):
        """Render the user input area."""
        input_y = self.height - self.input_height - self.status_height
        self.draw_box(1, input_y, self.width - 2, self.input_height, title="USER INPUT", color="green")
        
        # Clear the input line first
        self.move_cursor(input_y + 1, 3)
        print(" " * (self.width - 6), end="")
        
        # Input text content
        self.move_cursor(input_y + 1, 3)
        input_text = self.input_content.get('text', '')
        cursor_pos = self.input_content.get('cursor_pos', 0)
        
        # Handle text that's longer than display width
        display_width = self.width - 6
        if len(input_text) > display_width:
            # Scroll text to keep cursor visible
            if cursor_pos < display_width - 10:
                # Cursor near start, show beginning
                display_text = input_text[:display_width]
                display_cursor_pos = cursor_pos
            else:
                # Cursor further along, scroll to show cursor
                start = max(0, cursor_pos - display_width + 10)
                display_text = input_text[start:start + display_width]
                display_cursor_pos = cursor_pos - start
        else:
            display_text = input_text
            display_cursor_pos = cursor_pos
        
        # Print the text
        print(f"{self.colors['end']}{display_text}{self.colors['end']}", end="")
        
        # Show cursor at correct position
        if display_cursor_pos <= len(display_text):
            cursor_x = 3 + display_cursor_pos
            self.move_cursor(input_y + 1, cursor_x)
            print(f"{self.colors['bg_green']} {self.colors['end']}", end="")
    
    def render_status_bar(self):
        """Render the status bar at bottom."""
        status_y = self.height - self.status_height
        
        # Status bar background
        self.move_cursor(status_y, 1)
        print(f"{self.colors['bg_blue']}{' ' * (self.width - 2)}{self.colors['end']}", end="")
        
        # Status content
        self.move_cursor(status_y, 2)
        status_text = f"Status: {self.status_content['message']}"
        print(f"{self.colors['bg_blue']}{self.colors['bold']}{status_text}{self.colors['end']}", end="")
        
        # Cost and tokens on right side
        cost_text = f"Cost: {self.status_content['cost']} | Tokens: {self.status_content['tokens']}"
        cost_x = self.width - len(cost_text) - 2
        self.move_cursor(status_y, cost_x)
        print(f"{self.colors['bg_blue']}{self.colors['yellow']}{cost_text}{self.colors['end']}", end="")
    
    def update_input(self, text: str, cursor_pos: int):
        """Update input content and re-render input area only."""
        self.input_content['text'] = text
        self.input_content['cursor_pos'] = cursor_pos
        self.render_input_area()
        
        # Keep cursor in input area
        input_y = self.height - self.input_height - self.status_height
        display_width = self.width - 6
        
        # Calculate visible cursor position
        if len(text) > display_width:
            if cursor_pos < display_width - 10:
                display_cursor_pos = cursor_pos
            else:
                start = max(0, cursor_pos - display_width + 10)
                display_cursor_pos = cursor_pos - start
        else:
            display_cursor_pos = cursor_pos
        
        cursor_x = min(3 + display_cursor_pos, self.width - 3)
        self.move_cursor(input_y + 1, cursor_x)
    
    def render_full_screen(self):
        """Render the complete grid layout."""
        self.clear_screen()
        self.render_header()
        self.render_ai_window()
        self.render_input_area()
        self.render_status_bar()
        
        # Position cursor in input area
        input_y = self.height - self.input_height - self.status_height
        self.move_cursor(input_y + 1, 3)
        sys.stdout.flush()
    
    def update_header(self, title: str = None, subtitle: str = None, version: str = None):
        """Update header content."""
        if title is not None:
            self.header_content['title'] = title
        if subtitle is not None:
            self.header_content['subtitle'] = subtitle
        if version is not None:
            self.header_content['version'] = version
    
    def add_ai_message(self, role: str, content: str, timestamp: str = None):
        """Add a message to the AI conversation."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.ai_content.append({
            "role": role,
            "content": content,
            "timestamp": timestamp
        })
    
    def update_input(self, text: str, cursor_pos: int = None):
        """Update input area content."""
        self.input_content['text'] = text
        if cursor_pos is not None:
            self.input_content['cursor_pos'] = cursor_pos
    
    def update_status(self, message: str = None, cost: str = None, tokens: str = None):
        """Update status bar content."""
        if message is not None:
            self.status_content['message'] = message
        if cost is not None:
            self.status_content['cost'] = cost
        if tokens is not None:
            self.status_content['tokens'] = tokens
    
    def clear_ai_history(self):
        """Clear the AI conversation history."""
        self.ai_content = []


class VersionManager:
    """Manage version information for header display."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self._version = None
    
    def get_version(self) -> str:
        """Get current version from various sources."""
        if self._version:
            return self._version
        
        # Try __init__.py first (most direct)
        init_path = self.project_path / "grok_cli" / "__init__.py"
        if init_path.exists():
            try:
                with open(init_path, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if '__version__ = ' in line and '"' in line:
                            version = line.split('"')[1]
                            self._version = version
                            return version
            except Exception:
                pass
        
        # Try pyproject.toml
        pyproject_path = self.project_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, 'r') as f:
                    content = f.read()
                    # Simple regex-like search for version
                    for line in content.split('\n'):
                        if 'version = ' in line and '"' in line:
                            version = line.split('"')[1]
                            self._version = version
                            return version
            except Exception:
                pass
        
        # Try setup.py
        setup_path = self.project_path / "setup.py"
        if setup_path.exists():
            try:
                with open(setup_path, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if 'version=' in line and ('"' in line or "'" in line):
                            quote_char = '"' if '"' in line else "'"
                            version = line.split(quote_char)[1]
                            self._version = version
                            return version
            except Exception:
                pass
        
        # Try git tag
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self._version = version
                return version
        except Exception:
            pass
        
        # Default
        self._version = "2025.1.0"
        return self._version


# Test the grid renderer
if __name__ == "__main__":
    print("Testing Grid UI System...")
    
    # Create renderer
    renderer = GridRenderer()
    version_mgr = VersionManager(".")
    
    # Set up test content
    renderer.update_header(
        title="GROKIT", 
        subtitle="Interactive Grok Interface",
        version=version_mgr.get_version()
    )
    
    # Add test messages
    renderer.add_ai_message("user", "Hello, how are you?")
    renderer.add_ai_message("assistant", "I'm doing well! This is a test of the new grid-based UI system for GroKit. The system supports multi-line messages, persistent storage, and real-time updates.")
    renderer.add_ai_message("user", "That's great! Can you show me more features?")
    renderer.add_ai_message("assistant", "Absolutely! The grid UI includes: header with version info, scrolling chat history, input area with cursor tracking, and a status bar with cost/token monitoring.")
    
    # Update status
    renderer.update_status("Testing Grid UI", "$0.0123", "1,234")
    renderer.update_input("This is a test input message...")
    
    # Render the screen
    renderer.render_full_screen()
    
    print(f"\n\nGrid UI Test Complete!")
    print(f"Terminal size: {renderer.width}x{renderer.height}")
    print(f"AI window height: {renderer.ai_window_height}")
    print(f"Version detected: {version_mgr.get_version()}")