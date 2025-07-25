"""
Terminal-friendly Markdown renderer using the rich library.
Provides enhanced markdown rendering with syntax highlighting for multiple languages.
"""

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from io import StringIO
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

import re
import textwrap
from typing import List, Dict, Tuple, Optional

class TerminalMarkdownRenderer:
    """Renders markdown content for terminal display with colors and formatting."""
    
    def __init__(self, width: int = 70):
        self.width = max(20, width)  # Ensure minimum width
        self.colors = self._init_colors()
        
        # Initialize rich console if available
        if RICH_AVAILABLE:
            self.console = Console(
                width=self.width,
                force_terminal=True,
                highlight=True,
                legacy_windows=False,
                color_system="truecolor"
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
        Convert markdown text to formatted terminal lines.
        
        Args:
            text: Raw markdown text
            
        Returns:
            List of formatted lines ready for terminal display
        """
        if not text or not text.strip():
            return [""]
        
        # Use rich if available
        if RICH_AVAILABLE:
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
                
            except Exception:
                # Fall through to original implementation
                pass
        
        # Original implementation (fallback)
        lines = []
        current_lines = text.split('\n')
        i = 0
        
        while i < len(current_lines):
            line = current_lines[i]
            
            # Code blocks (fenced with ```)
            if line.strip().startswith('```'):
                block_lines, new_i = self._render_code_block(current_lines, i)
                lines.extend(block_lines)
                i = new_i
                continue
            
            # Headers
            if line.startswith('#'):
                lines.extend(self._render_header(line))
            
            # Lists
            elif re.match(r'^[\s]*[-*+]\s', line) or re.match(r'^[\s]*\d+\.\s', line):
                lines.extend(self._render_list_item(line))
            
            # Inline code and formatting
            else:
                lines.extend(self._render_text_line(line))
            
            i += 1
        
        return lines
    
    def _render_code_block(self, lines: List[str], start_idx: int) -> Tuple[List[str], int]:
        """Render a fenced code block with syntax highlighting."""
        result_lines = []
        i = start_idx
        
        # Parse language from opening fence
        fence_line = lines[i].strip()
        language = fence_line[3:].strip() if len(fence_line) > 3 else ""
        
        # Add code block header (ASCII-safe)
        header = f"+-- Code: {language or 'text'} " + "-" * (self.width - 15 - len(language or 'text')) + "+"
        result_lines.append(f"{self.colors['cyan']}{header}{self.colors['reset']}")
        
        i += 1
        code_lines = []
        
        # Collect code content
        while i < len(lines) and not lines[i].strip().startswith('```'):
            code_lines.append(lines[i])
            i += 1
        
        # Skip the closing ``` line
        if i < len(lines) and lines[i].strip().startswith('```'):
            i += 1
        
        # Render code with basic syntax highlighting
        for code_line in code_lines:
            formatted_line = self._apply_syntax_highlighting(code_line, language)
            # Wrap in box characters (ASCII-safe)
            result_lines.append(f"{self.colors['cyan']}|{self.colors['reset']} {formatted_line:<{self.width-4}} {self.colors['cyan']}|{self.colors['reset']}")
        
        # Add code block footer (ASCII-safe)
        footer = "+" + "-" * (self.width - 2) + "+"
        result_lines.append(f"{self.colors['cyan']}{footer}{self.colors['reset']}")
        result_lines.append("")  # Empty line after code block
        
        return result_lines, i  # Return the index after processing
    
    def _apply_syntax_highlighting(self, line: str, language: str) -> str:
        """Apply basic syntax highlighting to code lines."""
        if not line.strip():
            return line
        
        # Python highlighting
        if language.lower() in ['python', 'py']:
            # Keywords
            line = re.sub(r'\b(def|class|if|else|elif|for|while|try|except|import|from|return|yield|with|as|lambda|pass|break|continue|global|nonlocal|assert|del|raise|finally|is|and|or|not|in)\b', 
                         f'{self.colors["magenta"]}\\1{self.colors["reset"]}', line)
            # Built-in functions
            line = re.sub(r'\b(print|len|range|int|str|float|list|dict|set|tuple|type|isinstance|hasattr|getattr|setattr|delattr|open|input|help|dir|zip|map|filter|sorted|reversed|enumerate|all|any|sum|min|max|abs|round|pow|divmod|complex|bool|bytes|bytearray|memoryview|hex|oct|bin|format|ord|chr|ascii|repr|eval|exec|compile|globals|locals|vars)\b(?=\()', 
                         f'{self.colors["yellow"]}\\1{self.colors["reset"]}', line)
            # Strings
            line = re.sub(r'(["\'])([^"\']*)\\1', 
                         f'{self.colors["green"]}\\1\\2\\1{self.colors["reset"]}', line)
            # Comments
            line = re.sub(r'(#.*)', 
                         f'{self.colors["dim"]}\\1{self.colors["reset"]}', line)
        
        # JavaScript/JSX highlighting
        elif language.lower() in ['javascript', 'js', 'jsx', 'typescript', 'ts', 'tsx']:
            # Keywords
            line = re.sub(r'\b(function|const|let|var|if|else|for|while|return|class|async|await|new|this|super|extends|static|get|set|try|catch|finally|throw|switch|case|default|break|continue|do|instanceof|typeof|void|delete|in|of|yield|import|export|from|as|require)\b', 
                         f'{self.colors["magenta"]}\\1{self.colors["reset"]}', line)
            # JSX/React elements (basic support)
            line = re.sub(r'<(/?)([A-Z][a-zA-Z0-9]*)', 
                         f'{self.colors["cyan"]}<\\1\\2{self.colors["reset"]}', line)
            line = re.sub(r'(/>|>)', 
                         f'{self.colors["cyan"]}\\1{self.colors["reset"]}', line)
            # Strings
            line = re.sub(r'(["\'])([^"\']*)\\1', 
                         f'{self.colors["green"]}\\1\\2\\1{self.colors["reset"]}', line)
            # Template literals
            line = re.sub(r'`([^`]*)`', 
                         f'{self.colors["green"]}`\\1`{self.colors["reset"]}', line)
            # Comments
            line = re.sub(r'(//.*)', 
                         f'{self.colors["dim"]}\\1{self.colors["reset"]}', line)
        
        # PowerShell highlighting
        elif language.lower() in ['powershell', 'ps1', 'ps']:
            # Keywords
            line = re.sub(r'\b(function|if|else|elseif|switch|foreach|for|while|do|break|continue|return|filter|in|trap|throw|param|begin|process|end|try|catch|finally|class|enum|using|namespace|module|New|Get|Set|Add|Remove|Clear|Invoke|Out|Write|Read|ConvertTo|ConvertFrom|Select|Where|ForEach|Sort|Group|Measure|Compare|Test|Start|Stop|Restart|Suspend|Resume|Wait|Enter|Exit|Push|Pop|Import|Export)\b', 
                         f'{self.colors["blue"]}\\1{self.colors["reset"]}', line)
            # Variables
            line = re.sub(r'(\$[a-zA-Z_][a-zA-Z0-9_]*)', 
                         f'{self.colors["yellow"]}\\1{self.colors["reset"]}', line)
            # Strings
            line = re.sub(r'(["\'])([^"\']*)\\1', 
                         f'{self.colors["green"]}\\1\\2\\1{self.colors["reset"]}', line)
            # Comments
            line = re.sub(r'(#.*)', 
                         f'{self.colors["dim"]}\\1{self.colors["reset"]}', line)
        
        # C# highlighting
        elif language.lower() in ['csharp', 'cs', 'c#']:
            # Keywords
            line = re.sub(r'\b(abstract|as|base|bool|break|byte|case|catch|char|checked|class|const|continue|decimal|default|delegate|do|double|else|enum|event|explicit|extern|false|finally|fixed|float|for|foreach|goto|if|implicit|in|int|interface|internal|is|lock|long|namespace|new|null|object|operator|out|override|params|private|protected|public|readonly|ref|return|sbyte|sealed|short|sizeof|stackalloc|static|string|struct|switch|this|throw|true|try|typeof|uint|ulong|unchecked|unsafe|ushort|using|var|virtual|void|volatile|while|async|await|dynamic|partial|yield|value|get|set)\b', 
                         f'{self.colors["blue"]}\\1{self.colors["reset"]}', line)
            # Types
            line = re.sub(r'\b(Console|String|DateTime|List|Dictionary|Array|Exception|Task|IEnumerable|IList|IDictionary|StringBuilder|Stream|File|Directory)\b', 
                         f'{self.colors["cyan"]}\\1{self.colors["reset"]}', line)
            # Strings
            line = re.sub(r'(["\'])([^"\']*)\\1', 
                         f'{self.colors["red"]}\\1\\2\\1{self.colors["reset"]}', line)
            # Comments
            line = re.sub(r'(//.*)', 
                         f'{self.colors["green"]}\\1{self.colors["reset"]}', line)
        
        # Bash highlighting
        elif language.lower() in ['bash', 'sh', 'shell']:
            # Commands
            line = re.sub(r'^(\s*)([\w-]+)', 
                         f'\\1{self.colors["yellow"]}\\2{self.colors["reset"]}', line)
            # Variables
            line = re.sub(r'(\$[a-zA-Z_][a-zA-Z0-9_]*|\${[^}]+})', 
                         f'{self.colors["cyan"]}\\1{self.colors["reset"]}', line)
            # Strings
            line = re.sub(r'(["\'])([^"\']*)\\1', 
                         f'{self.colors["green"]}\\1\\2\\1{self.colors["reset"]}', line)
            # Comments
            line = re.sub(r'(#.*)', 
                         f'{self.colors["dim"]}\\1{self.colors["reset"]}', line)
        
        return line
    
    def _render_header(self, line: str) -> List[str]:
        """Render markdown headers with appropriate styling."""
        level = len(line) - len(line.lstrip('#'))
        text = line.lstrip('#').strip()
        
        if level == 1:
            # H1: Bold, underlined
            styled_text = f"{self.colors['bold']}{self.colors['underline']}{text}{self.colors['reset']}"
            return ["", styled_text, ""]
        elif level == 2:
            # H2: Bold, colored
            styled_text = f"{self.colors['bold']}{self.colors['cyan']}{text}{self.colors['reset']}"
            return ["", styled_text, ""]
        elif level == 3:
            # H3: Bold
            styled_text = f"{self.colors['bold']}{text}{self.colors['reset']}"
            return ["", styled_text, ""]
        else:
            # H4+: Just colored
            styled_text = f"{self.colors['yellow']}{text}{self.colors['reset']}"
            return [styled_text]
    
    def _render_list_item(self, line: str) -> List[str]:
        """Render list items with proper indentation."""
        # Count leading whitespace
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        
        # Detect list type
        if re.match(r'^[-*+]\s', stripped):
            # Unordered list (ASCII-safe)
            bullet = f"{self.colors['yellow']}*{self.colors['reset']}"
            content = stripped[2:]  # Remove '- '
        else:
            # Ordered list
            number_match = re.match(r'^(\d+)\.\s', stripped)
            if number_match:
                number = number_match.group(1)
                bullet = f"{self.colors['cyan']}{number}.{self.colors['reset']}"
                content = stripped[len(number) + 2:]  # Remove '1. '
            else:
                return [line]  # Fallback
        
        # Apply inline formatting to content
        formatted_content = self._apply_inline_formatting(content)
        
        # Wrap long lines
        prefix = " " * indent + bullet + " "
        wrapped_lines = textwrap.wrap(formatted_content, 
                                    width=self.width - len(prefix),
                                    subsequent_indent=" " * len(prefix))
        
        if not wrapped_lines:
            return [prefix]
        
        result = [prefix + wrapped_lines[0]]
        for wrapped_line in wrapped_lines[1:]:
            result.append(" " * len(prefix) + wrapped_line)
        
        return result
    
    def _render_text_line(self, line: str) -> List[str]:
        """Render regular text with inline formatting."""
        if not line.strip():
            return [""]

        formatted_line = self._apply_inline_formatting(line)
        
        # Wrap long lines with proper width handling
        # Account for ANSI escape sequences when wrapping
        import re
        # Remove ANSI codes for length calculation
        clean_line = re.sub(r'\033\[[0-9;]*m', '', formatted_line)
        
        if len(clean_line) <= self.width:
            return [formatted_line]
        
        # Manual wrapping to preserve ANSI codes
        wrapped_lines = []
        current_line = ""
        current_length = 0
        words = formatted_line.split(' ')
        
        for word in words:
            # Calculate word length without ANSI codes
            clean_word = re.sub(r'\033\[[0-9;]*m', '', word)
            word_length = len(clean_word)
            
            if current_length + word_length + (1 if current_line else 0) <= self.width:
                if current_line:
                    current_line += " " + word
                    current_length += 1 + word_length
                else:
                    current_line = word
                    current_length = word_length
            else:
                if current_line:
                    wrapped_lines.append(current_line)
                current_line = word
                current_length = word_length
        
        if current_line:
            wrapped_lines.append(current_line)
        
        return wrapped_lines if wrapped_lines else [""]

    def _apply_inline_formatting(self, text: str) -> str:
        """Apply inline markdown formatting like bold, italic, code."""
        if not text:
            return text
        
        # Inline code (backticks)
        text = re.sub(r'`([^`]+)`', 
                     f'{self.colors["bg_black"]}{self.colors["white"]} \\1 {self.colors["reset"]}', text)
        
        # Bold (**text** or __text__)
        text = re.sub(r'\*\*([^*]+)\*\*', 
                     f'{self.colors["bold"]}\\1{self.colors["reset"]}', text)
        text = re.sub(r'__([^_]+)__', 
                     f'{self.colors["bold"]}\\1{self.colors["reset"]}', text)
        
        # Italic (*text* or _text_)
        text = re.sub(r'\*([^*]+)\*', 
                     f'{self.colors["italic"]}\\1{self.colors["reset"]}', text)
        text = re.sub(r'_([^_]+)_', 
                     f'{self.colors["italic"]}\\1{self.colors["reset"]}', text)
        
        return text


def test_markdown_renderer():
    """Test the markdown renderer with sample content."""
    renderer = TerminalMarkdownRenderer(width=70)
    
    sample_text = """# Enhanced Markdown Renderer Test

This is a paragraph with **bold text** and *italic text* and `inline code`.

## Code Examples

### Python Example

```python
def factorial(n: int) -> int:
    \"\"\"Calculate factorial recursively.\"\"\"
    if n <= 1:
        return 1
    return n * factorial(n - 1)

class Example:
    def __init__(self):
        self.value = "test string"  # This is a comment
        print(f"Initialized with {self.value}")
```

### JavaScript/React Example

```jsx
const Component = ({ name }) => {
    const [count, setCount] = useState(0);
    
    return (
        <div className="greeting">
            <h1>Hello, {name}!</h1>
            <button onClick={() => setCount(count + 1)}>
                Clicked {count} times
            </button>
        </div>
    );
};

export default Component;
```

### PowerShell Example

```powershell
function Get-SystemInfo {
    param(
        [string]$ComputerName = $env:COMPUTERNAME
    )
    
    $info = Get-WmiObject -Class Win32_ComputerSystem -ComputerName $ComputerName
    Write-Output "Computer: $($info.Name)"
    Write-Output "RAM: $([math]::Round($info.TotalPhysicalMemory / 1GB, 2)) GB"
}

Get-SystemInfo -ComputerName "Server01"
```

### C# Example

```csharp
public class HelloWorld {
    private string message;
    
    public HelloWorld(string msg) {
        this.message = msg ?? "Default message";
    }
    
    public async Task<string> GetGreetingAsync() {
        await Task.Delay(100);  // Simulate async work
        return $"Hello, {message}!";
    }
    
    public static void Main(string[] args) {
        var hw = new HelloWorld("World");
        Console.WriteLine(hw.GetGreetingAsync().Result);
    }
}
```

### Bash Example

```bash
#!/bin/bash
# System backup script

BACKUP_DIR="/backup"
SOURCE_DIR="/home"
DATE=$(date +%Y%m%d)

if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
fi

echo "Starting backup of $SOURCE_DIR..."
tar -czf "$BACKUP_DIR/backup-$DATE.tar.gz" "$SOURCE_DIR"
echo "Backup completed!"
```

## List Examples

- First item with `inline code`
- Second item with **bold text**
- Third item with *italic text*
  - Nested item 1
  - Nested item 2

1. Numbered item
2. Another numbered item with `code`
3. Final item with **bold** and *italic*

Regular text continues here with a very long line that should wrap properly when rendered in the terminal without breaking the formatting or causing any display issues in the Grid UI."""
    
    print("Testing Enhanced Markdown Renderer:")
    print("=" * 70)
    
    lines = renderer.render_markdown(sample_text)
    for line in lines:
        print(line)
    
    print("=" * 70)
    print("\nRich library available:", RICH_AVAILABLE)


if __name__ == "__main__":
    test_markdown_renderer()