"""
Terminal input handler for real-time character capture and grid UI integration.
"""

import sys
import os
import time
from typing import Optional, Tuple, Callable, List
from collections import deque


class TerminalInputHandler:
    """Cross-platform terminal input handler for character-by-character input."""
    
    def __init__(self, on_char_update: Callable[[str, int], None] = None):
        """
        Initialize the terminal input handler.
        
        Args:
            on_char_update: Callback function called when input buffer changes.
                           Receives (current_text, cursor_position)
        """
        self.on_char_update = on_char_update or self._default_char_update
        self.buffer = ""
        self.cursor_pos = 0
        self.history = deque(maxlen=100)
        self.history_index = -1
        
        # Platform-specific setup
        self._setup_platform_specific()
    
    def _default_char_update(self, text: str, cursor_pos: int):
        """Default character update handler."""
        pass
    
    def _setup_platform_specific(self):
        """Setup platform-specific input handling."""
        # Detect if running in WSL
        is_wsl = self._detect_wsl()
        
        if os.name == 'nt':  # Windows
            try:
                import msvcrt
                self._getch = msvcrt.getch
                self._kbhit = msvcrt.kbhit
                self.platform_supported = True
            except ImportError:
                print("Warning: msvcrt not available, using fallback input")
                self.platform_supported = False
                self._getch = None
                self._kbhit = None
        else:  # Unix/Linux/Mac/WSL
            try:
                import termios
                import tty
                self._setup_unix_terminal()
                self.platform_supported = True
                # WSL might have some terminal issues, warn user
                if is_wsl:
                    print("Note: Running in WSL - some terminal features may be limited")
            except ImportError:
                print("Warning: termios not available, using fallback input")
                self.platform_supported = False
                self._getch = None
                self._kbhit = None
    
    def _detect_wsl(self) -> bool:
        """Detect if running in Windows Subsystem for Linux."""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    def _setup_unix_terminal(self):
        """Setup Unix terminal for raw input."""
        import termios
        import tty
        import select
        
        self.old_settings = termios.tcgetattr(sys.stdin)
        
        def _unix_getch():
            """Get a single character on Unix."""
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                return ch.encode('utf-8')
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        
        def _unix_kbhit():
            """Check if a key has been pressed on Unix."""
            return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
        
        self._getch = _unix_getch
        self._kbhit = _unix_kbhit
    
    def get_line(self, multiline: bool = False) -> str:
        """
        Get a line of input with real-time character handling.
        
        Args:
            multiline: If True, allows multi-line input (Ctrl+Enter for newline)
            
        Returns:
            The entered text
        """
        self.buffer = ""
        self.cursor_pos = 0
        self.history_index = -1
        
        # Initial callback to clear the input field
        self.on_char_update(self.buffer, self.cursor_pos)
        
        # Check if platform-specific input is supported
        if not getattr(self, 'platform_supported', False) or not self._getch:
            # Platform not supported, use fallback with manual updates
            result = input("Input: ")
            self.on_char_update(result, len(result))
            return result
        
        try:
            while True:
                if os.name == 'nt':
                    # Windows: Use blocking getch for better reliability
                    try:
                        key = self._getch()
                        result = self._handle_key(key, multiline)
                        if result is not None:
                            return result
                    except Exception as e:
                        # If terminal input fails, fall back to standard input
                        print(f"\nTerminal input error: {e}")
                        print("Falling back to standard input...")
                        result = input("Input: ")
                        self.on_char_update(result, len(result))
                        return result
                else:
                    # Unix: Block on getch
                    try:
                        key = self._getch()
                        result = self._handle_key(key, multiline)
                        if result is not None:
                            return result
                    except Exception as e:
                        # If terminal input fails, fall back to standard input
                        print(f"\nTerminal input error: {e}")
                        print("Falling back to standard input...")
                        result = input("Input: ")
                        self.on_char_update(result, len(result))
                        return result
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Any other error, fall back to standard input
            print(f"\nTerminal handler error: {e}")
            result = input("Input: ")
            self.on_char_update(result, len(result))
            return result
    
    def _handle_key(self, key: bytes, multiline: bool) -> Optional[str]:
        """
        Handle a single key press.
        
        Returns:
            The final text if input is complete, None otherwise
        """
        # Handle special keys
        if os.name == 'nt':
            # Windows special keys
            if key == b'\r':  # Enter
                if not multiline:
                    self._add_to_history(self.buffer)
                    result = self.buffer
                    # Clear buffer and update display before returning
                    self.buffer = ""
                    self.cursor_pos = 0
                    self.on_char_update(self.buffer, self.cursor_pos)
                    return result
                else:
                    # In multiline mode, check for ### terminator
                    if self.buffer.endswith("###"):
                        text = self.buffer[:-3].strip()
                        self._add_to_history(text)
                        return text
                    else:
                        self.buffer += '\n'
                        self.cursor_pos = len(self.buffer)
            elif key == b'\x08':  # Backspace
                if self.cursor_pos > 0:
                    self.buffer = self.buffer[:self.cursor_pos-1] + self.buffer[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif key == b'\xe0':  # Special key prefix on Windows
                next_key = self._getch()
                self._handle_windows_special_key(next_key)
            elif key == b'\x03':  # Ctrl+C
                raise KeyboardInterrupt()
            elif 32 <= ord(key) <= 126:  # Printable characters
                self.buffer = self.buffer[:self.cursor_pos] + key.decode('utf-8') + self.buffer[self.cursor_pos:]
                self.cursor_pos += 1
        else:
            # Unix key handling
            if key == b'\n' or key == b'\r':  # Enter
                if not multiline:
                    self._add_to_history(self.buffer)
                    result = self.buffer
                    # Clear buffer and update display before returning
                    self.buffer = ""
                    self.cursor_pos = 0
                    self.on_char_update(self.buffer, self.cursor_pos)
                    return result
                else:
                    if self.buffer.endswith("###"):
                        text = self.buffer[:-3].strip()
                        self._add_to_history(text)
                        return text
                    else:
                        self.buffer += '\n'
                        self.cursor_pos = len(self.buffer)
            elif key == b'\x7f' or key == b'\x08':  # Backspace
                if self.cursor_pos > 0:
                    self.buffer = self.buffer[:self.cursor_pos-1] + self.buffer[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif key == b'\x1b':  # Escape sequence
                self._handle_unix_escape_sequence()
            elif key == b'\x03':  # Ctrl+C
                raise KeyboardInterrupt()
            elif 32 <= ord(key) <= 126:  # Printable characters
                self.buffer = self.buffer[:self.cursor_pos] + key.decode('utf-8') + self.buffer[self.cursor_pos:]
                self.cursor_pos += 1
        
        # Update the display
        self.on_char_update(self.buffer, self.cursor_pos)
        return None
    
    def _handle_windows_special_key(self, key: bytes):
        """Handle Windows special keys (arrows, etc.)."""
        if key == b'K':  # Left arrow
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
        elif key == b'M':  # Right arrow
            if self.cursor_pos < len(self.buffer):
                self.cursor_pos += 1
        elif key == b'H':  # Up arrow (history)
            self._navigate_history(-1)
        elif key == b'P':  # Down arrow (history)
            self._navigate_history(1)
        elif key == b'S':  # Delete
            if self.cursor_pos < len(self.buffer):
                self.buffer = self.buffer[:self.cursor_pos] + self.buffer[self.cursor_pos+1:]
        elif key == b'G':  # Home
            self.cursor_pos = 0
        elif key == b'O':  # End
            self.cursor_pos = len(self.buffer)
    
    def _handle_unix_escape_sequence(self):
        """Handle Unix escape sequences for special keys."""
        # Read the rest of the escape sequence
        seq = self._getch()
        if seq == b'[':
            seq2 = self._getch()
            if seq2 == b'A':  # Up arrow
                self._navigate_history(-1)
            elif seq2 == b'B':  # Down arrow
                self._navigate_history(1)
            elif seq2 == b'C':  # Right arrow
                if self.cursor_pos < len(self.buffer):
                    self.cursor_pos += 1
            elif seq2 == b'D':  # Left arrow
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
            elif seq2 == b'3':  # Delete
                seq3 = self._getch()
                if seq3 == b'~' and self.cursor_pos < len(self.buffer):
                    self.buffer = self.buffer[:self.cursor_pos] + self.buffer[self.cursor_pos+1:]
    
    def _navigate_history(self, direction: int):
        """Navigate through command history."""
        if not self.history:
            return
        
        if self.history_index == -1 and direction == -1:
            # Save current buffer before navigating
            self.current_buffer = self.buffer
            self.history_index = len(self.history) - 1
        elif self.history_index >= 0:
            self.history_index += direction
            
            if self.history_index < 0:
                self.history_index = 0
            elif self.history_index >= len(self.history):
                # Restore original buffer
                self.buffer = getattr(self, 'current_buffer', '')
                self.cursor_pos = len(self.buffer)
                self.history_index = -1
                return
        
        if 0 <= self.history_index < len(self.history):
            self.buffer = self.history[self.history_index]
            self.cursor_pos = len(self.buffer)
    
    def _add_to_history(self, text: str):
        """Add text to command history."""
        if text.strip():
            self.history.append(text)
    
    def cleanup(self):
        """Cleanup terminal settings."""
        if os.name != 'nt' and hasattr(self, 'old_settings'):
            import termios
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
