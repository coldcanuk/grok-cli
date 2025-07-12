# Grok CLI

A command-line interface for interacting with xAI's Grok API with integrated MCP (Model Context Protocol) server support for function calling capabilities.

## Features

- 🚀 Stream or standard response modes
- 💬 Interactive chat with conversation history
- 🖼️ Vision support for image inputs
- 🔧 MCP server integration with function calling
- 🔍 Brave Search integration
- 📁 Local file system operations
- ⚙️ Configurable via settings.json

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- xAI API key (get one at https://x.ai/api)

### Standard Installation (Ubuntu/Debian)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/grok-cli.git
cd grok-cli
```

2. Install the package:
```bash
pip install -e .
```

3. Set up your API key:
```bash
export XAI_API_KEY="your-api-key-here"
```

4. (Optional) For Brave Search functionality:
```bash
export BRAVE_SEARCH_API_KEY="your-brave-api-key-here"
```

### WSL (Windows Subsystem for Linux) Installation

1. First, ensure WSL is installed and updated:
```powershell
# In PowerShell as Administrator
wsl --install
wsl --update
```

2. Open WSL terminal (Ubuntu):
```bash
wsl
```

3. Update packages and install Python:
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
```

4. Clone and install the Grok CLI:
```bash
git clone https://github.com/yourusername/grok-cli.git
cd grok-cli
pip install -e .
```

5. Set up environment variables in WSL:
```bash
# Add to ~/.bashrc for persistence
echo 'export XAI_API_KEY="your-api-key-here"' >> ~/.bashrc
echo 'export BRAVE_SEARCH_API_KEY="your-brave-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Alternative: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS/WSL:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install the package
pip install -e .
```

## Configuration

Edit `settings.json` to configure the CLI:

```json
{
  "model": "grok-4",
  "stream": true,
  "mcp_servers": {
    "brave_search": {
      "enabled": true,
      "api_url": "https://api.search.brave.com/res/v1/web/search"
    },
    "local_file_system": {
      "enabled": true
    }
  }
}
```

### MCP Server Configuration

Each MCP server can be enabled/disabled by setting the `enabled` flag. Currently supported servers:

1. **brave_search**: Web search capabilities
   - Requires `BRAVE_SEARCH_API_KEY` environment variable
   - Provides `brave_search` function

2. **local_file_system**: File system operations
   - Functions: `create_file`, `read_file`, `append_to_file`, `delete_file`, `list_files`

## Usage

### Single Prompt
```bash
grok-cli --prompt "What is the capital of France?"
```

### Interactive Chat
```bash
grok-cli --chat
```

### With Image
```bash
grok-cli --prompt "What's in this image?" --image path/to/image.jpg
```

### Streaming Mode
```bash
grok-cli --prompt "Write a poem" --stream
```

### Using Different Model
```bash
grok-cli --prompt "Hello" --model grok-beta
```

### Complex Prompts with Special Characters
When your prompt contains special characters like backticks, use single quotes:
```bash
grok-cli --prompt 'Create a `README.md` file'
```

Or escape the special characters:
```bash
grok-cli --prompt "Create a \`README.md\` file"
```

### Interactive Chat Commands
- `/quit` - Exit the chat
- `/clear` - Clear conversation history
- `/save <filename>` - Save conversation to file

## Function Calling with MCP Servers

When enabled, Grok can automatically use tools provided by MCP servers. For example:

```bash
# With Brave Search enabled
grok-cli --prompt "What's the latest news about AI?"

# With Local File System enabled
grok-cli --prompt "Create a file called test.txt with 'Hello World' content"
```

The CLI will automatically:
1. Detect when Grok wants to use a tool
2. Execute the tool with the provided parameters
3. Return the results to Grok for a final response

## API Limits and Considerations

- **Context Window**: Grok models support up to 128,000 tokens
- **Tool Definitions**: The number of tools is limited by the context window
- **Streaming**: When streaming is enabled, tool calls are returned in whole chunks
- **Rate Limits**: The API has rate limits based on your subscription tier

## Development

### Running Tests
```bash
grok-cli --test
```

### Project Structure
```
grok-cli/
├── grok_cli/
│   ├── __init__.py
│   └── cli.py          # Main CLI implementation
├── settings.json       # Configuration file
├── setup.py           # Package setup
├── README.md          # This file
└── .gitignore         # Git ignore file
```

## Troubleshooting

### Command Line Issues

1. **Shell Command Substitution Error** (e.g., "tableofcontents.md: command not found"):
   
   This happens when using backticks (`) in your prompt without proper quoting:
   ```bash
   # WRONG - shell interprets backticks as command substitution
   grok-cli --prompt "Create a `file.md`"
   
   # CORRECT - use single quotes
   grok-cli --prompt 'Create a `file.md`'
   
   # CORRECT - escape backticks
   grok-cli --prompt "Create a \`file.md\`"
   ```

2. **Tool Calls Not Creating Files**:
   
   Make sure:
   - Your prompt clearly asks Grok to create/write a file
   - The `local_file_system` server is enabled in settings.json
   - You're using the correct syntax for complex prompts

   Example that works:
   ```bash
   grok-cli --prompt "Create a file called test.txt with the content 'Hello World'"
   ```

3. **No Output After Tool Calls**:
   
   If you see "[Executing tool calls...]" but no final response:
   - Try running without `--stream` flag to see non-streaming output
   - Enable debug mode: `export GROK_DEBUG=1`
   - Check if the API key has sufficient credits

### WSL Specific Issues

1. **Permission Denied**: If you get permission errors, ensure you're not in a Windows directory:
```bash
cd ~
# Then clone the repository there
```

2. **API Key Not Found**: Make sure to source your `.bashrc` after adding environment variables:
```bash
source ~/.bashrc
```

3. **Network Issues in WSL**: If you have connectivity issues, check WSL's DNS settings:
```bash
sudo echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

### General Issues

1. **Module Not Found**: Ensure you've installed the package:
```bash
pip install -e .
```

2. **API Errors**: Check your API key and credits at https://x.ai/api

3. **Tool Execution Failures**: Ensure required environment variables are set for enabled MCP servers

### Debugging

Enable debug mode to see detailed tool results:
```bash
export GROK_DEBUG=1
grok-cli --prompt "Your prompt here"
```

### Common Use Cases

1. **Creating a Table of Contents**:
   ```bash
   grok-cli --stream --prompt 'Read our codebase and create a tableofcontents.md file. List each file in the format: /path/to/file;{description of what the file does}'
   ```

2. **Web Search**:
   ```bash
   # Requires BRAVE_SEARCH_API_KEY
   grok-cli --prompt "Search for the latest news about artificial intelligence"
   ```

3. **File Operations**:
   ```bash
   # List all files
   grok-cli --prompt "List all files in the project respecting .gitignore"
   
   # Read a file
   grok-cli --prompt "Read the README.md file and summarize it"
   
   # Create multiple files
   grok-cli --prompt "Create a Python hello world script and a README for it"
   ```

## Security Considerations

- Never commit API keys to version control
- Use environment variables for sensitive data
- The `.gitignore` file excludes common sensitive files
- Be cautious with file system operations when using the local_file_system MCP server

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built for xAI's Grok API
- Inspired by the Model Context Protocol (MCP) specification
- Uses Brave Search API for web search capabilities
