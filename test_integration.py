#!/usr/bin/env python3
"""Test the integration of the enhanced markdown renderer with Grid UI."""

import sys
import os

# Add the grok_cli directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'grok_cli'))

from grid_ui import GridRenderer
from markdown_renderer import RICH_AVAILABLE

def test_grid_ui_markdown_integration():
    """Test that Grid UI properly uses the enhanced markdown renderer."""
    print("Testing Grid UI Markdown Integration")
    print("=" * 70)
    print(f"Rich library available: {RICH_AVAILABLE}")
    print("=" * 70)
    
    # Create a Grid renderer
    grid = GridRenderer(terminal_width=80, terminal_height=30)
    
    # Test markdown content with various languages
    test_content = """# Welcome to GroKit!

This is a test of the **enhanced** markdown renderer with `rich` library support.

## Python Example

```python
def greet(name: str) -> str:
    \"\"\"Return a greeting message.\"\"\"
    return f"Hello, {name}!"

# Call the function
message = greet("World")
print(message)
```

## JavaScript/React Example

```jsx
const Greeting = ({ name }) => {
    return (
        <div className="greeting">
            <h1>Hello, {name}!</h1>
        </div>
    );
};
```

## PowerShell Example

```powershell
function Get-Greeting {
    param([string]$Name = "World")
    Write-Output "Hello, $Name!"
}

Get-Greeting -Name "GroKit"
```

## Features

- **Bold text** and *italic text*
- `Inline code` highlighting
- Multi-language syntax highlighting
- Proper word wrapping for long lines that exceed the terminal width
"""
    
    # Add the test content as an AI message
    grid.add_ai_message(test_content)
    
    # Check that the content was properly rendered
    print("\nRendered AI content:")
    print("-" * 70)
    
    # Get the rendered lines from the AI content
    if grid.ai_content:
        last_message = grid.ai_content[-1]
        if 'rendered_lines' in last_message:
            for line in last_message['rendered_lines'][:20]:  # Show first 20 lines
                print(line)
            if len(last_message['rendered_lines']) > 20:
                print(f"... and {len(last_message['rendered_lines']) - 20} more lines")
        else:
            print("No rendered lines found in message")
    
    print("-" * 70)
    print("\nIntegration test completed!")
    
    # Test specific language rendering
    print("\n\nTesting individual language rendering:")
    print("=" * 70)
    
    # Test C# rendering
    cs_test = """```csharp
public class Test {
    public string Name { get; set; }
    public async Task<bool> ProcessAsync() {
        await Task.Delay(100);
        return true;
    }
}
```"""
    
    rendered = grid.markdown_renderer.render_markdown(cs_test)
    print("\nC# Code Block:")
    for line in rendered:
        print(line)

if __name__ == "__main__":
    test_grid_ui_markdown_integration()
