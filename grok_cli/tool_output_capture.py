"""
Tool output capture and diff generation for Grid UI integration.
"""

import io
import sys
import difflib
import os
from typing import Dict, Any, List, Optional, Tuple
from contextlib import contextmanager


class ToolOutputCapture:
    """Captures tool execution output for Grid UI display."""
    
    def __init__(self):
        self.captured_output = []
        self.file_modifications = {}  # Track file changes for diff generation
        
    @contextmanager
    def capture_stdout(self):
        """Context manager to capture stdout during tool execution."""
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            yield sys.stdout
        finally:
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            if output:
                self.captured_output.append(output)
    
    def track_file_modification(self, filename: str, old_content: Optional[str], new_content: str):
        """Track a file modification for diff generation."""
        self.file_modifications[filename] = {
            'old_content': old_content,
            'new_content': new_content,
            'diff': self._generate_diff(filename, old_content, new_content)
        }
    
    def _generate_diff(self, filename: str, old_content: Optional[str], new_content: str) -> List[str]:
        """Generate a unified diff between old and new content."""
        if old_content is None:
            # New file
            return [
                f"=== Created new file: {filename} ===",
                f"+ {len(new_content.splitlines())} lines added"
            ]
        
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{filename} (before)",
            tofile=f"{filename} (after)",
            n=3  # Context lines
        ))
        
        # Convert to simpler format for display
        simple_diff = []
        for line in diff:
            if line.startswith('+++') or line.startswith('---'):
                continue
            elif line.startswith('@@'):
                simple_diff.append(f"\n{line.strip()}")
            elif line.startswith('+'):
                simple_diff.append(f"+ {line[1:].rstrip()}")
            elif line.startswith('-'):
                simple_diff.append(f"- {line[1:].rstrip()}")
            else:
                # Context line
                if len(simple_diff) < 100:  # Limit diff size
                    simple_diff.append(f"  {line.rstrip()}")
        
        return simple_diff
    
    def get_formatted_output(self) -> str:
        """Get all captured output formatted for Grid UI display."""
        output_parts = []
        
        # Add file modification summary if any
        if self.file_modifications:
            output_parts.append("📝 FILE MODIFICATIONS:")
            for filename, info in self.file_modifications.items():
                output_parts.append(f"\n✏️  Modified: {filename}")
                if info['diff']:
                    output_parts.append("```diff")
                    output_parts.extend(info['diff'][:50])  # Limit diff lines
                    if len(info['diff']) > 50:
                        output_parts.append(f"... ({len(info['diff']) - 50} more lines)")
                    output_parts.append("```")
            output_parts.append("")
        
        # Add captured stdout
        if self.captured_output:
            output_parts.append("🔧 TOOL OUTPUT:")
            for output in self.captured_output:
                output_parts.append(output.rstrip())
        
        return "\n".join(output_parts)
    
    def clear(self):
        """Clear captured output and modifications."""
        self.captured_output.clear()
        self.file_modifications.clear()


class EnhancedToolExecutor:
    """Enhanced tool executor with output capture and diff generation."""
    
    def __init__(self, original_executor):
        self.original_executor = original_executor
        self.output_capture = ToolOutputCapture()
    
    def execute_with_capture(self, function_name: str, arguments: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Execute a tool with output capture and diff generation."""
        self.output_capture.clear()
        
        # Special handling for file operations
        if function_name == "create_file":
            return self._execute_file_creation(arguments)
        elif function_name == "read_file":
            return self._execute_file_read(arguments)
        else:
            # For other tools, just capture stdout
            with self.output_capture.capture_stdout():
                result = self.original_executor(function_name, arguments)
            
            return result, self.output_capture.get_formatted_output()
    
    def _execute_file_creation(self, arguments: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Execute file creation with diff tracking."""
        filename = arguments.get("filename", "")
        new_content = arguments.get("content", "")
        
        # Check if file exists and read old content
        old_content = None
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    old_content = f.read()
            except Exception:
                pass
        
        # Execute the file creation
        with self.output_capture.capture_stdout():
            result = self.original_executor("create_file", arguments)
        
        # Track the modification
        if result.get("success"):
            self.output_capture.track_file_modification(filename, old_content, new_content)
        
        return result, self.output_capture.get_formatted_output()
    
    def _execute_file_read(self, arguments: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Execute file read with enhanced output."""
        with self.output_capture.capture_stdout():
            result = self.original_executor("read_file", arguments)
        
        # Add file info to output
        if result.get("success") and "content" in result:
            filename = arguments.get("filename", "")
            content = result["content"]
            lines = content.splitlines()
            self.output_capture.captured_output.insert(0, 
                f"📄 Read file: {filename} ({len(lines)} lines, {len(content)} chars)\n"
            )
        
        return result, self.output_capture.get_formatted_output()
