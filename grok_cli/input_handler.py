"""
Enhanced input handler with multi-line support for GroKit.
"""

import sys
import os


class MultiLineInputHandler:
    """Simplified multi-line input handler that works across platforms."""
    
    def __init__(self):
        self.multiline_mode = False
        self.history = []
        
    def get_input(self, prompt: str = "You: ") -> str:
        """Get input with optional multi-line support."""
        if self.multiline_mode:
            return self._get_multiline_input(prompt)
        else:
            return self._get_single_line_input(prompt)
    
    def _get_single_line_input(self, prompt: str) -> str:
        """Get single line input."""
        try:
            result = input(prompt).strip()
            if result:
                self.history.append(result)
            return result
        except (KeyboardInterrupt, EOFError):
            return "/quit"
    
    def _get_multiline_input(self, prompt: str) -> str:
        """Get multi-line input with special commands."""
        print(f"{prompt}(Multi-line mode: Type '###' on new line to submit, '/single' to exit multi-line)")
        lines = []
        
        while True:
            try:
                line = input("... " if lines else prompt)
                
                if line.strip() == "###":
                    # Submit multi-line input
                    result = "\n".join(lines)
                    if result.strip():
                        self.history.append(result)
                    return result
                elif line.strip() == "/single":
                    # Exit multi-line mode
                    self.multiline_mode = False
                    print("(Switched to single-line mode)")
                    return self._get_single_line_input(prompt)
                elif line.strip() == "/quit":
                    return "/quit"
                else:
                    lines.append(line)
                    
            except (KeyboardInterrupt, EOFError):
                return "/quit"
    
    def enable_multiline(self):
        """Enable multi-line input mode."""
        self.multiline_mode = True
        print("Multi-line mode enabled. Type '###' on a new line to submit.")
    
    def disable_multiline(self):
        """Disable multi-line input mode."""
        self.multiline_mode = False
        print("Multi-line mode disabled.")
    
    def toggle_multiline(self):
        """Toggle multi-line mode."""
        if self.multiline_mode:
            self.disable_multiline()
        else:
            self.enable_multiline()


class GroKitInterface:
    """Enhanced GroKit interface with better input handling."""
    
    def __init__(self):
        self.input_handler = MultiLineInputHandler()
        self.colors = self._init_colors()
    
    def _init_colors(self):
        """Initialize color codes, disable on Windows if needed."""
        if os.name == 'nt':
            # Enable ANSI colors on Windows 10+
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
            "underline": "\033[4m",
            "end": "\033[0m"
        }
    
    def print_styled(self, text: str, color: str = "end"):
        """Print text with color styling."""
        print(f"{self.colors.get(color, '')}{text}{self.colors['end']}")
    
    def print_box(self, title: str, content: str = "", width: int = None):
        """Print content in a styled box with dynamic width."""
        # Calculate dynamic width if not provided
        if width is None:
            title_len = len(title)
            content_len = len(content) if content else 0
            # Use the longer of title or content, with padding
            width = max(title_len, content_len) + 6  # Add padding
            width = max(width, 50)  # Minimum width
        
        try:
            # Try Unicode box drawing
            print(f"{self.colors['blue']}╔" + "═" * (width - 2) + f"╗{self.colors['end']}")
            print(f"{self.colors['blue']}║{title.center(width - 2)}║{self.colors['end']}")
            if content:
                print(f"{self.colors['blue']}║{content.center(width - 2)}║{self.colors['end']}")
            print(f"{self.colors['blue']}╚" + "═" * (width - 2) + f"╝{self.colors['end']}")
        except UnicodeEncodeError:
            # Fallback to ASCII box drawing
            print(f"{self.colors['blue']}+" + "-" * (width - 2) + f"+{self.colors['end']}")
            print(f"{self.colors['blue']}|{title.center(width - 2)}|{self.colors['end']}")
            if content:
                print(f"{self.colors['blue']}|{content.center(width - 2)}|{self.colors['end']}")
            print(f"{self.colors['blue']}+" + "-" * (width - 2) + f"+{self.colors['end']}")
    
    def clear_screen(self):
        """Clear screen cross-platform."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def wait_for_key(self, message: str = "Press Enter to continue..."):
        """Wait for user to press Enter."""
        try:
            input(f"\n{self.colors['blue']}{message}{self.colors['end']}")
        except (KeyboardInterrupt, EOFError):
            pass


# Test the input handler
if __name__ == "__main__":
    print("Testing Multi-Line Input Handler")
    print("Commands: /multi (enable), /single (disable), /quit (exit)")
    
    handler = MultiLineInputHandler()
    
    while True:
        user_input = handler.get_input("Test: ")
        
        if user_input == "/quit":
            break
        elif user_input == "/multi":
            handler.enable_multiline()
            continue
        elif user_input == "/single":
            handler.disable_multiline()
            continue
        
        print(f"You entered: {repr(user_input)}")
    
    print("Test complete!")