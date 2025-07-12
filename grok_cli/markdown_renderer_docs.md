# Enhanced Markdown Renderer Documentation

## Overview

The GroKit CLI now features an enhanced markdown renderer powered by the `rich` library, providing professional-grade syntax highlighting and improved terminal rendering for AI responses.

## Features

### 1. **Rich Library Integration**
- When `rich` is available, the renderer uses it for advanced markdown rendering
- Automatic fallback to the original regex-based renderer if `rich` is not installed
- No breaking changes to the existing API

### 2. **Enhanced Syntax Highlighting**
Supports multiple programming languages with IDE-like highlighting:

#### Python
- Keywords: magenta (def, class, if, else, etc.)
- Built-in functions: yellow (print, len, range, etc.)
- Strings: green
- Comments: dim gray
- Numbers: cyan

#### JavaScript/JSX/TypeScript
- Keywords: magenta (function, const, let, var, etc.)
- JSX tags: cyan (<div>, <Component />, etc.)
- Strings: green (including template literals)
- Comments: dim gray
- React hooks: yellow (useState, useEffect, etc.)

#### PowerShell
- Keywords: blue (function, if, else, foreach, etc.)
- Variables: yellow ($variable)
- Cmdlets: cyan (Get-Process, Write-Host, etc.)
- Strings: green
- Comments: dim gray

#### C#
- Keywords: blue (public, class, async, await, etc.)
- Types: cyan (string, int, Task, etc.)
- Strings: red
- Comments: green
- Attributes: yellow

#### Bash/Shell
- Commands: yellow
- Variables: cyan
- Strings: green
- Comments: dim gray

### 3. **Improved Word Wrapping**
- Rich properly handles ANSI escape codes when calculating line lengths
- No more broken lines due to color codes
- Respects terminal width for proper text flow

### 4. **Terminal Compatibility**
- Automatic detection of terminal capabilities
- Graceful degradation for terminals without color support
- Windows terminal compatibility with proper ANSI code handling

## Installation

```bash
# Install with rich support
pip install -r requirements.txt

# Or install rich separately
pip install rich>=13.7.0
```

## Usage

The enhanced renderer is automatically used by the Grid UI. No code changes are required.

```python
from grok_cli.markdown_renderer import TerminalMarkdownRenderer

# Create renderer with specific width
renderer = TerminalMarkdownRenderer(width=80)

# Render markdown text
markdown_text = """
# Header

This is **bold** and *italic* text.

```python
def hello():
    print("Hello, World!")
```
"""

lines = renderer.render_markdown(markdown_text)
for line in lines:
    print(line)
```

## Customization

### 1. **Custom Themes**
To customize the color scheme when using rich:

```python
# In markdown_renderer.py, modify the render_markdown method
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "markdown.code": "cyan",
    "markdown.code_block": "dim cyan",
    "markdown.h1": "bold magenta",
    "markdown.h2": "bold blue",
})

console = Console(theme=custom_theme, width=self.width)
```

### 2. **Language-Specific Highlighting**
To add support for additional languages in the fallback renderer:

```python
def _apply_syntax_highlighting(self, line: str, language: str) -> str:
    # Add your language here
    if language.lower() in ['rust', 'rs']:
        # Rust keywords
        line = re.sub(r'\b(fn|let|mut|impl|trait|pub|use|mod)\b', 
                     f'{self.MAGENTA}\\1{self.RESET}', line)
        # ... add more patterns
```

### 3. **Width Configuration**
The renderer respects the terminal width:

```python
# Automatic terminal width detection
renderer = TerminalMarkdownRenderer()

# Or specify custom width
renderer = TerminalMarkdownRenderer(width=100)
```

## Fallback Behavior

When `rich` is not available, the renderer falls back to the original implementation:

1. **Detection**: The module checks for `rich` availability at import time
2. **Graceful Degradation**: If `rich` import fails, `RICH_AVAILABLE` is set to `False`
3. **Original Renderer**: Uses regex-based syntax highlighting with ANSI escape codes
4. **Limited Features**: Fallback supports basic highlighting but may have word-wrapping issues

### Fallback Limitations
- Less accurate syntax highlighting
- Manual ANSI code handling may cause wrapping issues
- Limited language support compared to rich/pygments
- No automatic theme support

## Environment Variables

No specific environment variables are required for the markdown renderer. It automatically detects the terminal capabilities.

## Troubleshooting

### Issue: Colors not showing in terminal
**Solution**: Ensure your terminal supports ANSI color codes. On Windows, use Windows Terminal or enable ANSI support.

### Issue: Word wrapping is incorrect
**Solution**: Install `rich` library for proper ANSI code handling: `pip install rich`

### Issue: Syntax highlighting not working for a language
**Solution**: 
1. Ensure `rich` is installed for full language support
2. Use proper language identifiers in code blocks (e.g., ```python, ```javascript)
3. Check if the language is supported by pygments

### Issue: Performance with large markdown documents
**Solution**: The renderer is optimized for typical AI responses. For very large documents, consider:
- Splitting content into smaller chunks
- Using pagination for display
- Limiting syntax highlighting to visible portions

## Testing

Run the test suite to verify the renderer is working correctly:

```bash
# Test basic functionality
python grok_cli/markdown_renderer.py

# Test Grid UI integration
python test_integration.py

# Test help command display
python test_help_fix.py
```

## Future Enhancements

Potential improvements for future versions:
1. Custom lexer support for domain-specific languages
2. Configurable color schemes via configuration file
3. Export rendered output to HTML/PDF
4. Support for tables and advanced markdown features
5. Integration with terminal hyperlink support

## Contributing

When adding new features to the markdown renderer:
1. Maintain backward compatibility with the existing API
2. Ensure fallback behavior works without `rich`
3. Add tests for new language support
4. Update this documentation with new features

## License

The enhanced markdown renderer is part of GroKit CLI and follows the same GPL-3.0 license.
