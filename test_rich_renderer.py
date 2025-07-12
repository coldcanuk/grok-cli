#!/usr/bin/env python3
"""Test script for the enhanced markdown renderer with rich library."""

import sys
import os

# Add the grok_cli directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'grok_cli'))

from markdown_renderer import test_markdown_renderer, TerminalMarkdownRenderer, RICH_AVAILABLE

def test_basic_rendering():
    """Test basic markdown rendering functionality."""
    print("=" * 70)
    print("Testing Basic Markdown Rendering")
    print("=" * 70)
    
    renderer = TerminalMarkdownRenderer(width=70)
    
    # Test simple markdown
    simple_md = """# Test Header

This is a **bold** text and *italic* text with `inline code`.

## Code Block Test

```python
def hello():
    print("Hello, World!")
```

- List item 1
- List item 2
"""
    
    lines = renderer.render_markdown(simple_md)
    for line in lines:
        print(line)
    
    print("\n" + "=" * 70)
    print(f"Rich library available: {RICH_AVAILABLE}")
    print("=" * 70)

def test_language_highlighting():
    """Test syntax highlighting for different languages."""
    print("\n" + "=" * 70)
    print("Testing Language-Specific Syntax Highlighting")
    print("=" * 70)
    
    renderer = TerminalMarkdownRenderer(width=70)
    
    # Test PowerShell
    ps_code = """## PowerShell Test

```powershell
$name = "World"
Write-Host "Hello, $name!"
Get-Process | Where-Object {$_.CPU -gt 100}
```
"""
    
    # Test C#
    cs_code = """## C# Test

```csharp
public class Program {
    public static void Main(string[] args) {
        Console.WriteLine("Hello, World!");
        var list = new List<string> { "a", "b", "c" };
    }
}
```
"""
    
    # Test JSX
    jsx_code = """## React/JSX Test

```jsx
const App = () => {
    return (
        <div className="app">
            <Header title="Welcome" />
            <Button onClick={() => console.log('clicked')}>
                Click Me
            </Button>
        </div>
    );
};
```
"""
    
    for code in [ps_code, cs_code, jsx_code]:
        lines = renderer.render_markdown(code)
        for line in lines:
            print(line)
        print()

if __name__ == "__main__":
    print("Enhanced Markdown Renderer Test Suite")
    print("=====================================\n")
    
    # Run the original test
    test_markdown_renderer()
    
    print("\n\n")
    
    # Run additional tests
    test_basic_rendering()
    test_language_highlighting()
    
    print("\n\nAll tests completed!")
