"""
Terminal-friendly Markdown renderer using the rich library.
Provides enhanced markdown rendering with syntax highlighting for multiple languages.
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from io import StringIO
import re
from typing import List, Dict, Optional


class TerminalMarkdownRenderer:
    """Renders markdown content for terminal display using rich library."""
    
    def __init__(self, width: int = 70):
        self.width = max(20, width)
        self.colors = self._init_colors()
        # Create console with specific settings for capturing output
        self.console = Console(
            width=self.width,
            force_terminal=True,
            highlight=True,
            legacy_windows=False,  # Use modern Windows terminal features
            color_system="truecolor"  # Use full color support
        )
        
    def _init_colors(self) -> Dict[str, str]:
        """Initialize ANSI color codes for terminal formatting."""
        return {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'italic': '\033[3m',
            'underline': '\033[4m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bg_black': '\033[40m',
            'bg_red': '\033[41m',
            'bg_green': '\033[42m',
            'bg_yellow': '\033[43m',
            'bg_blue': '\033[44m',
            'bg_magenta': '\033[45m',
            'bg_cyan': '\033[46m',
            'bg_white': '\033[47m',
        }
    
    def render_markdown(self, text: str) -> List[str]:
        """
        Convert markdown text to formatted terminal lines using rich.
        
        Args:
            text: Raw markdown text
            
        Returns:
            List of formatted lines ready for terminal display
        """
        if not text or not text.strip():
            return [""]
        
        try:
            # Use rich to render the markdown
            md = Markdown(text, code_theme="monokai", hyperlinks=False)
            
            # Capture the output to a string buffer
            buffer = StringIO()
            capture_console = Console(
                file=buffer,
                width=self.width,
                force_terminal=True,
                color_system="truecolor",
                legacy_windows=False
            )
            capture_console.print(md)
            rendered = buffer.getvalue()
            
            # Split into lines and remove trailing newline if present
            lines = rendered.strip().split('\n')
            
            return lines if lines else [""]
            
        except Exception as e:
            # Fallback to basic rendering if rich fails
            return self._fallback_render(text)
    
    def _fallback_render(self, text: str) -> List[str]:
        """Basic fallback rendering without rich library."""
        lines = []
        current_lines = text.split('\n')
        
        for line in current_lines:
            # Very basic formatting
            if line.startswith('#'):
                # Headers
                level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('#').strip()
                if level == 1:
                    lines.append("")
                    lines.append(f"{self.colors['bold']}{self.colors['underline']}{header_text}{self.colors['reset']}")
                    lines.append("")
                else:
                    lines.append(f"{self.colors['bold']}{header_text}{self.colors['reset']}")
            elif line.strip().startswith('```'):
                # Skip code blocks in fallback
                lines.append(line)
            else:
                # Regular text with basic inline formatting
                formatted = line
                # Bold
                formatted = re.sub(r'\*\*([^*]+)\*\*', f"{self.colors['bold']}\\1{self.colors['reset']}", formatted)
                # Italic
                formatted = re.sub(r'\*([^*]+)\*', f"{self.colors['italic']}\\1{self.colors['reset']}", formatted)
                # Inline code
                formatted = re.sub(r'`([^`]+)`', f"{self.colors['bg_black']}{self.colors['white']} \\1 {self.colors['reset']}", formatted)
                lines.append(formatted)
        
        return lines
    
    def render_code_block(self, code: str, language: str = "text") -> List[str]:
        """
        Render a code block with syntax highlighting using rich.
        
        Args:
            code: The code content
            language: The programming language for syntax highlighting
            
        Returns:
            List of formatted lines
        """
        try:
            # Map common language aliases
            language_map = {
                'js': 'javascript',
                'ts': 'typescript',
                'py': 'python',
                'sh': 'bash',
                'ps1': 'powershell',
                'cs': 'csharp',
                'jsx': 'javascript',  # Rich doesn't have specific JSX, but JS works well
                'tsx': 'typescript',
            }
            
            lang = language_map.get(language.lower(), language.lower())
            
            # Create syntax object
            syntax = Syntax(
                code,
                lang,
                theme="monokai",
                line_numbers=False,
                word_wrap=True,
                background_color=None,
                indent_guides=False
            )
            
            # Capture the output
            buffer = StringIO()
            capture_console = Console(
                file=buffer,
                width=self.width,
                force_terminal=True,
                color_system="truecolor"
            )
            capture_console.print(syntax)
            rendered = buffer.getvalue()
            
            # Split into lines
            lines = rendered.strip().split('\n')
            
            # Add code block borders (ASCII-safe)
            header = f"+-- Code: {language} " + "-" * (self.width - 15 - len(language)) + "+"
            footer = "+" + "-" * (self.width - 2) + "+"
            
            result = [f"{self.colors['cyan']}{header}{self.colors['reset']}"]
            for line in lines:
                # Wrap in box characters
                result.append(f"{self.colors['cyan']}|{self.colors['reset']} {line:<{self.width-4}} {self.colors['cyan']}|{self.colors['reset']}")
            result.append(f"{self.colors['cyan']}{footer}{self.colors['reset']}")
            result.append("")  # Empty line after code block
            
            return result
            
        except Exception:
            # Fallback to basic code rendering
            return self._fallback_code_block(code, language)
    
    def _fallback_code_block(self, code: str, language: str) -> List[str]:
        """Basic code block rendering without syntax highlighting."""
        lines = []
        header = f"+-- Code: {language} " + "-" * (self.width - 15 - len(language)) + "+"
        footer = "+" + "-" * (self.width - 2) + "+"
        
        lines.append(f"{self.colors['cyan']}{header}{self.colors['reset']}")
        for line in code.split('\n'):
            lines.append(f"{self.colors['cyan']}|{self.colors['reset']} {line:<{self.width-4}} {self.colors['cyan']}|{self.colors['reset']}")
        lines.append(f"{self.colors['cyan']}{footer}{self.colors['reset']}")
        lines.append("")
        
        return lines


def test_markdown_renderer():
    """Test the markdown renderer with sample content."""
    renderer = TerminalMarkdownRenderer(width=70)
    
    sample_text = """# Main Header

This is a paragraph with **bold text** and *italic text* and `inline code`.

## Code Examples

### Python Example

```python
def hello_world():
    print("Hello, World!")  # This is a comment
    return True

class Example:
    def __init__(self):
        self.value = "test string"
```

### JavaScript Example

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);  // Template literal
    return true;
}

const arrow = () => console.log("Arrow function");
```

### PowerShell Example

```powershell
function Get-Greeting {
    param([string]$Name)
    Write-Output "Hello, $Name!"  # PowerShell comment
}

Get-Greeting -Name "World"
```

### C# Example

```csharp
public class HelloWorld {
    public static void Main(string[] args) {
        Console.WriteLine("Hello, World!");  // C# comment
        var message = "Test string";
    }
}
```

### React/JSX Example

```jsx
const Component = ({ name }) => {
    return (
        <div className="greeting">
            <h1>Hello, {name}!</h1>
            <button onClick={() => console.log('Clicked')}>
                Click me
            </button>
        </div>
    );
};
```

## List Example

- First item with `code`
- Second item with **bold**
- Third item with *italic*

1. Numbered item
2. Another numbered item
3. Final item

Regular text continues here with a very long line that should wrap properly when rendered in the terminal without breaking the formatting or causing any display issues."""
    
    print("Testing Rich Markdown Renderer:")
    print("=" * 70)
    
    lines = renderer.render_markdown(sample_text)
    for line in lines:
        print(line)
    
    print("=" * 70)
    print("\nTesting individual code block:")
    print("=" * 70)
    
    python_code = '''def factorial(n):
    """Calculate factorial recursively."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)'''
    
    code_lines = renderer.render_code_block(python_code, "python")
    for line in code_lines:
        print(line)


if __name__ == "__main__":
    test_markdown_renderer()
