"""
Enhanced input handler with clipboard support and text optimization for GroKit Grid UI
"""

import sys
import os
import re
import time
from typing import Dict, List, Optional, Tuple, Callable, Any
from .persistence import ClipboardHandler


class TextOptimizer:
    """Optimize text before API processing to reduce costs and improve responses."""
    
    def __init__(self):
        self.optimizations_enabled = True
        self.min_length_for_optimization = 100  # Characters
        
    def optimize_text(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Optimize text and return optimized version with metadata."""
        if not self.optimizations_enabled or len(text) < self.min_length_for_optimization:
            return text, {"optimized": False, "original_length": len(text)}
        
        original_length = len(text)
        optimized = text
        optimizations_applied = []
        
        # Remove excessive whitespace
        if self._has_excessive_whitespace(optimized):
            optimized = self._clean_whitespace(optimized)
            optimizations_applied.append("whitespace_cleanup")
        
        # Normalize line endings
        if '\r\n' in optimized or '\r' in optimized:
            optimized = optimized.replace('\r\n', '\n').replace('\r', '\n')
            optimizations_applied.append("line_ending_normalization")
        
        # Remove excessive repetition
        repetition_removed = self._remove_excessive_repetition(optimized)
        if repetition_removed != optimized:
            optimized = repetition_removed
            optimizations_applied.append("repetition_removal")
        
        # Compress common patterns
        compressed = self._compress_common_patterns(optimized)
        if compressed != optimized:
            optimized = compressed
            optimizations_applied.append("pattern_compression")
        
        metadata = {
            "optimized": len(optimizations_applied) > 0,
            "original_length": original_length,
            "optimized_length": len(optimized),
            "savings": original_length - len(optimized),
            "optimizations_applied": optimizations_applied
        }
        
        return optimized, metadata
    
    def _has_excessive_whitespace(self, text: str) -> bool:
        """Check if text has excessive whitespace."""
        # Multiple consecutive spaces
        if re.search(r'  +', text):
            return True
        # Multiple consecutive newlines
        if re.search(r'\n\n\n+', text):
            return True
        # Trailing/leading whitespace on lines
        if re.search(r'[ \t]+\n', text):
            return True
        return False
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean excessive whitespace."""
        # Replace multiple spaces with single space
        text = re.sub(r'  +', ' ', text)
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\n\n+', '\n\n', text)
        # Remove trailing whitespace from lines
        text = re.sub(r'[ \t]+\n', '\n', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text
    
    def _remove_excessive_repetition(self, text: str) -> str:
        """Remove excessive repetitive patterns."""
        # Remove repeated words (more than 3 times)
        words = text.split()
        if len(words) < 4:
            return text
        
        cleaned_words = []
        for i, word in enumerate(words):
            # Check if this word appears 3+ times in a row
            count = 1
            j = i + 1
            while j < len(words) and words[j] == word:
                count += 1
                j += 1
            
            # Keep max 2 repetitions
            if count > 2:
                cleaned_words.extend([word] * 2)
                # Skip the extra repetitions
                for _ in range(count - 2):
                    if i + 1 < len(words):
                        words.pop(i + 1)
            else:
                cleaned_words.append(word)
        
        return ' '.join(cleaned_words)
    
    def _compress_common_patterns(self, text: str) -> str:
        """Compress common verbose patterns."""
        # Replace verbose phrases with concise equivalents
        patterns = {
            r'\bI would like to\b': "I want to",
            r'\bCould you please\b': "Please",
            r'\bIt would be great if you could\b': "Please",
            r'\bI was wondering if\b': "Can",
            r'\bDo you think you could\b': "Can you",
            r'\bI need you to help me\b': "Help me",
        }
        
        for pattern, replacement in patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text


class EnhancedInputHandler:
    """Enhanced input handler with clipboard support, history, and grid UI integration."""
    
    def __init__(self, on_status_update: Callable[[str], None] = None):
        self.clipboard = ClipboardHandler()
        self.text_optimizer = TextOptimizer()
        self.on_status_update = on_status_update or self._default_status_update
        
        # Input state
        self.current_text = ""
        self.cursor_position = 0
        self.multiline_mode = False
        self.history = []
        self.history_index = -1
        
        # Input buffer for multi-line
        self.buffer_lines = []
        self.current_line_index = 0
        
        # Special command handling
        self.special_commands = {
            "/paste": self._handle_paste,
            "/clear": self._handle_clear,
            "/multi": self._handle_multiline_toggle,
            "/optimize": self._handle_optimize_toggle,
            "/history": self._handle_history,
            "/undo": self._handle_undo,
            "/help": self._handle_help
        }
        
        # Undo stack
        self.undo_stack = []
        self.max_undo_stack = 20
    
    def _default_status_update(self, message: str):
        """Default status update handler."""
        pass
    
    def get_input(self, prompt: str = "You: ") -> Tuple[str, Dict]:
        """Get user input with enhanced features. Returns (text, metadata)."""
        self.on_status_update("Waiting for input...")
        
        try:
            if self.multiline_mode:
                return self._get_multiline_input(prompt)
            else:
                return self._get_single_line_input(prompt)
        except (KeyboardInterrupt, EOFError):
            return "/quit", {"cancelled": True}
    
    def _get_single_line_input(self, prompt: str) -> Tuple[str, Dict]:
        """Get single line input with special command handling."""
        while True:
            try:
                self.on_status_update("Single-line mode | /paste /multi /help")
                user_input = input(prompt).strip()
                
                # Handle special commands
                if user_input in self.special_commands:
                    result = self.special_commands[user_input]()
                    if result:
                        continue
                    else:
                        user_input = input(prompt).strip()
                
                # Handle commands with arguments
                if user_input.startswith("/"):
                    command_parts = user_input.split(maxsplit=1)
                    command = command_parts[0]
                    
                    if command in self.special_commands:
                        arg = command_parts[1] if len(command_parts) > 1 else None
                        result = self.special_commands[command](arg)
                        if result:
                            continue
                
                # Process normal input
                if user_input:
                    self._add_to_history(user_input)
                    optimized_text, optimization_metadata = self.text_optimizer.optimize_text(user_input)
                    
                    metadata = {
                        "input_mode": "single_line",
                        "original_text": user_input,
                        "optimization": optimization_metadata,
                        "timestamp": time.time()
                    }
                    
                    self.on_status_update(f"Input received ({len(optimized_text)} chars)")
                    return optimized_text, metadata
                
            except (KeyboardInterrupt, EOFError):
                return "/quit", {"cancelled": True}
    
    def _get_multiline_input(self, prompt: str) -> Tuple[str, Dict]:
        """Get multi-line input with enhanced editing."""
        self.buffer_lines = []
        self.on_status_update("Multi-line mode | ### to submit | /single to exit")
        
        print(f"{prompt}(Multi-line mode: Type '###' on new line to submit)")
        
        while True:
            try:
                line_prompt = "... " if self.buffer_lines else "> "
                line = input(line_prompt)
                
                # Check for submission
                if line.strip() == "###":
                    result_text = "\n".join(self.buffer_lines)
                    if result_text.strip():
                        self._add_to_history(result_text)
                        optimized_text, optimization_metadata = self.text_optimizer.optimize_text(result_text)
                        
                        metadata = {
                            "input_mode": "multi_line",
                            "original_text": result_text,
                            "optimization": optimization_metadata,
                            "line_count": len(self.buffer_lines),
                            "timestamp": time.time()
                        }
                        
                        self.on_status_update(f"Multi-line input received ({len(optimized_text)} chars)")
                        return optimized_text, metadata
                    else:
                        print("(Empty input, continuing...)")
                        continue
                
                # Check for mode change
                elif line.strip() == "/single":
                    self.multiline_mode = False
                    self.on_status_update("Switched to single-line mode")
                    return self._get_single_line_input(prompt)
                
                # Check for special commands
                elif line.strip().startswith("/"):
                    command_parts = line.strip().split(maxsplit=1)
                    command = command_parts[0]
                    
                    if command == "/paste":
                        clipboard_text = self.clipboard.get_clipboard_text()
                        if clipboard_text:
                            clipboard_lines = clipboard_text.split('\n')
                            self.buffer_lines.extend(clipboard_lines)
                            self.on_status_update(f"Pasted {len(clipboard_lines)} lines from clipboard")
                        else:
                            print("(No clipboard content available)")
                        continue
                    
                    elif command == "/clear":
                        self.buffer_lines = []
                        print("(Buffer cleared)")
                        continue
                    
                    elif command == "/help":
                        self._show_multiline_help()
                        continue
                    
                    elif command == "/undo":
                        if self.buffer_lines:
                            removed_line = self.buffer_lines.pop()
                            print(f"(Removed: {removed_line[:50]}...)")
                        else:
                            print("(Nothing to undo)")
                        continue
                
                # Add normal line
                self.buffer_lines.append(line)
                
            except (KeyboardInterrupt, EOFError):
                return "/quit", {"cancelled": True}
    
    def _add_to_history(self, text: str):
        """Add text to input history."""
        if text and (not self.history or self.history[-1] != text):
            self.history.append(text)
            # Keep history manageable
            if len(self.history) > 100:
                self.history = self.history[-100:]
    
    def _handle_paste(self, arg: str = None) -> bool:
        """Handle paste command."""
        clipboard_text = self.clipboard.get_clipboard_text()
        if clipboard_text:
            if self.multiline_mode:
                lines = clipboard_text.split('\n')
                self.buffer_lines.extend(lines)
                self.on_status_update(f"Pasted {len(lines)} lines")
            else:
                # For single line, just show what would be pasted
                preview = clipboard_text[:100] + "..." if len(clipboard_text) > 100 else clipboard_text
                print(f"Clipboard content: {preview}")
                response = input("Paste this content? (y/n): ").strip().lower()
                if response == 'y':
                    # Set as current input (will be returned)
                    self.current_text = clipboard_text
                    return False  # Don't continue loop
            return True
        else:
            self.on_status_update("No clipboard content available")
            return True
    
    def _handle_clear(self, arg: str = None) -> bool:
        """Handle clear command."""
        if self.multiline_mode:
            self.buffer_lines = []
            print("(Buffer cleared)")
        else:
            self.current_text = ""
            print("(Input cleared)")
        return True
    
    def _handle_multiline_toggle(self, arg: str = None) -> bool:
        """Handle multiline toggle command."""
        self.multiline_mode = not self.multiline_mode
        mode = "multi-line" if self.multiline_mode else "single-line"
        self.on_status_update(f"Switched to {mode} mode")
        print(f"(Now in {mode} mode)")
        return True
    
    def _handle_optimize_toggle(self, arg: str = None) -> bool:
        """Handle text optimization toggle."""
        self.text_optimizer.optimizations_enabled = not self.text_optimizer.optimizations_enabled
        status = "enabled" if self.text_optimizer.optimizations_enabled else "disabled"
        self.on_status_update(f"Text optimization {status}")
        print(f"(Text optimization {status})")
        return True
    
    def _handle_history(self, arg: str = None) -> bool:
        """Handle history command."""
        if not self.history:
            print("(No input history)")
            return True
        
        print("Recent input history:")
        for i, item in enumerate(self.history[-10:], 1):
            preview = item[:60] + "..." if len(item) > 60 else item
            print(f"  {i:2d}. {preview}")
        
        try:
            choice = input("Select item (number) or Enter to continue: ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(self.history[-10:]):
                    selected = self.history[-(10-index)]
                    self.current_text = selected
                    print(f"Selected: {selected[:100]}...")
                    return False  # Use this input
        except ValueError:
            pass
        
        return True
    
    def _handle_undo(self, arg: str = None) -> bool:
        """Handle undo command."""
        if self.undo_stack:
            previous_state = self.undo_stack.pop()
            self.current_text = previous_state
            print(f"(Undid to: {previous_state[:50]}...)")
            return False
        else:
            print("(Nothing to undo)")
            return True
    
    def _handle_help(self, arg: str = None) -> bool:
        """Handle help command."""
        if self.multiline_mode:
            self._show_multiline_help()
        else:
            self._show_single_line_help()
        return True
    
    def _show_single_line_help(self):
        """Show single-line mode help."""
        print("\nSingle-line Input Help:")
        print("  /paste     - Paste from clipboard")
        print("  /multi     - Switch to multi-line mode")
        print("  /history   - Show recent input history")
        print("  /optimize  - Toggle text optimization")
        print("  /clear     - Clear current input")
        print("  /help      - Show this help")
    
    def _show_multiline_help(self):
        """Show multi-line mode help."""
        print("\nMulti-line Input Help:")
        print("  ###        - Submit multi-line input")
        print("  /single    - Switch to single-line mode")
        print("  /paste     - Paste from clipboard")
        print("  /clear     - Clear current buffer")
        print("  /undo      - Remove last line")
        print("  /help      - Show this help")
    
    def get_current_state(self) -> Dict:
        """Get current input handler state."""
        return {
            "multiline_mode": self.multiline_mode,
            "current_text": self.current_text,
            "buffer_lines": self.buffer_lines,
            "history_count": len(self.history),
            "optimization_enabled": self.text_optimizer.optimizations_enabled
        }


# Test the enhanced input handler
if __name__ == "__main__":
    print("Testing Enhanced Input Handler...")
    
    def test_status_update(message):
        print(f"[STATUS] {message}")
    
    handler = EnhancedInputHandler(on_status_update=test_status_update)
    
    print("Enhanced Input Handler Test Mode")
    print("Commands: /multi, /paste, /help, /quit")
    
    while True:
        try:
            text, metadata = handler.get_input("Test> ")
            
            if text == "/quit":
                break
            
            print(f"\nReceived: {text}")
            print(f"Metadata: {metadata}")
            
            # Show optimization results if any
            if metadata.get("optimization", {}).get("optimized"):
                opt = metadata["optimization"]
                print(f"Optimization: {opt['savings']} chars saved ({opt['optimizations_applied']})")
            
            print("-" * 40)
            
        except KeyboardInterrupt:
            break
    
    print("Enhanced input test complete!")