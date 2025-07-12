# Grok CLI

A high-performance command-line interface for interacting with xAI's Grok API, featuring advanced rate limiting, intelligent caching, and integrated MCP (Model Context Protocol) server support for function calling capabilities.

## ✨ Features

- 🚀 **Advanced Rate Limiting**: Smart request pacing with adaptive delays and progress indicators
- 💬 **Interactive Chat**: Full conversation history with `/quit`, `/clear`, and `/save` commands
- 🖼️ **Vision Support**: Process images with text prompts
- ⚡ **Optimized Performance**: Request batching, intelligent caching, and tool call optimization
- 🔧 **MCP Server Integration**: Function calling with Brave Search and local file system operations
- 📊 **Enhanced Tools**: Including `batch_read_files` for efficient multi-file operations
- 🎪 **Rich UX**: Progress bars during rate limits with entertaining status messages
- ⚙️ **Configurable**: Fully customizable via `settings.json`

## 📋 Prerequisites

- **Python 3.7 or higher**
- **pip** (Python package installer)
- **xAI API key** (get one at https://x.ai/api)

## 🚀 Installation

### Windows 11

#### Option 1: Using PowerShell (Recommended)

1. **Open PowerShell as Administrator** and install Python if not already installed:
   ```powershell
   # Check if Python is installed
   python --version
   
   # If not installed, download from https://python.org or use winget:
   winget install Python.Python.3.12
   ```

2. **Clone and install the Grok CLI**:
   ```powershell
   git clone https://github.com/yourusername/grok-cli.git
   cd grok-cli
   pip install -e .
   ```

3. **Set up environment variables**:
   ```powershell
   # Set permanently for current user
   [Environment]::SetEnvironmentVariable("XAI_API_KEY", "your-api-key-here", "User")
   [Environment]::SetEnvironmentVariable("BRAVE_SEARCH_API_KEY", "your-brave-api-key-here", "User")
   
   # Restart PowerShell or set for current session:
   $env:XAI_API_KEY="your-api-key-here"
   $env:BRAVE_SEARCH_API_KEY="your-brave-api-key-here"
   ```

4. **Test the installation**:
   ```powershell
   grok-cli --test
   grok-cli --help
   ```

#### Option 2: Using Virtual Environment (Isolated Installation)

```powershell
# Create and activate virtual environment
python -m venv grok-env
grok-env\Scripts\Activate.ps1

# Install and test
pip install -e .
grok-cli --test
```

### WSL Ubuntu

1. **Install WSL (if not already installed)**:
   ```powershell
   # In PowerShell as Administrator
   wsl --install Ubuntu
   wsl --update
   ```

2. **Open WSL Ubuntu terminal** and update system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3 python3-pip python3-venv git curl -y
   ```

3. **Clone and install**:
   ```bash
   git clone https://github.com/yourusername/grok-cli.git
   cd grok-cli
   pip install -e .
   ```

4. **Set up environment variables**:
   ```bash
   # Add to ~/.bashrc for persistence
   echo 'export XAI_API_KEY="your-api-key-here"' >> ~/.bashrc
   echo 'export BRAVE_SEARCH_API_KEY="your-brave-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

5. **Test the installation**:
   ```bash
   grok-cli --test
   grok-cli --help
   ```

### Debian/Ubuntu Linux

1. **Update system and install dependencies**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3 python3-pip python3-venv git curl -y
   ```

2. **Clone and install**:
   ```bash
   git clone https://github.com/yourusername/grok-cli.git
   cd grok-cli
   pip install -e .
   ```

3. **Set up environment variables**:
   ```bash
   # Add to ~/.bashrc for persistence
   echo 'export XAI_API_KEY="your-api-key-here"' >> ~/.bashrc
   echo 'export BRAVE_SEARCH_API_KEY="your-brave-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   
   # Or create a .env file in the project directory
   echo 'XAI_API_KEY=your-api-key-here' > .env
   echo 'BRAVE_SEARCH_API_KEY=your-brave-api-key-here' >> .env
   ```

4. **Test the installation**:
   ```bash
   grok-cli --test
   grok-cli --help
   ```

### Virtual Environment (All Platforms - Recommended)

For isolated installations that don't interfere with system Python:

```bash
# Create virtual environment
python3 -m venv grok-cli-env

# Activate virtual environment
# Linux/macOS/WSL:
source grok-cli-env/bin/activate
# Windows PowerShell:
grok-cli-env\Scripts\Activate.ps1

# Install and test
pip install -e .
grok-cli --test
```

## ⚙️ Configuration

Create or edit `settings.json` in the project directory:

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

**Brave Search** (`brave_search`):
- Enables web search capabilities
- Requires `BRAVE_SEARCH_API_KEY` environment variable
- Get API key at https://api.search.brave.com

**Local File System** (`local_file_system`):
- Enables file operations: `create_file`, `read_file`, `batch_read_files`, `list_files_recursive`
- No additional setup required

## 🎯 Usage

### Basic Commands

```bash
# Single prompt
grok-cli --prompt "What is the capital of France?"

# Interactive chat mode
grok-cli --chat

# With image analysis
grok-cli --prompt "What's in this image?" --image path/to/image.jpg

# Streaming mode with progress indicators
grok-cli --prompt "Write a poem about AI" --stream

# Using different model
grok-cli --prompt "Hello" --model grok-beta

# Run self-tests
grok-cli --test
```

### Interactive Chat Commands

Once in chat mode (`grok-cli --chat`):
- `/quit` - Exit the chat
- `/clear` - Clear conversation history  
- `/save <filename>` - Save conversation to JSON file

### Advanced Usage

```bash
# Complex prompts (use quotes to handle special characters)
grok-cli --prompt 'Create a `README.md` file with installation instructions'

# Enable debug mode for detailed tool execution logs
grok-cli --debug 1 --prompt "List all Python files in this project"

# Web search (requires BRAVE_SEARCH_API_KEY)
grok-cli --prompt "What are the latest developments in AI?"

# File operations
grok-cli --prompt "Create a Python script that prints 'Hello World' and save it as hello.py"

# Batch file operations
grok-cli --prompt "Read all Python files in the grok_cli directory and summarize their purpose"
```

## 🔧 Architecture

The CLI features a clean, optimized architecture:

```
grok_cli/
├── cli.py              # Clean entry point with argument parsing
├── engine.py           # Core functionality with integrated streaming
├── utils.py            # Shared utilities (config, vision, gitignore)
├── request_manager.py  # Advanced request batching and caching
├── thinking.json       # AI thinking prompts configuration
└── startup.json        # Startup messages configuration
```

### Performance Features

- **Smart Rate Limiting**: Adaptive delays with exponential backoff
- **Request Batching**: Multiple file operations combined efficiently  
- **Intelligent Caching**: Avoid redundant API calls for file reads
- **Progress Indicators**: Visual feedback during rate limit waits
- **Tool Call Optimization**: Enhanced JSON parsing and error recovery

## 🐛 Troubleshooting

### Common Issues

**1. Command Not Found**
```bash
# Ensure the package is installed
pip install -e .

# Check if the script directory is in PATH (Windows)
echo $env:PATH  # PowerShell
echo $PATH      # Linux/WSL
```

**2. API Key Issues**
```bash
# Test if API key is set
echo $XAI_API_KEY          # Linux/WSL
echo $env:XAI_API_KEY      # PowerShell

# Set temporarily for testing
export XAI_API_KEY="your-key"     # Linux/WSL
$env:XAI_API_KEY="your-key"       # PowerShell
```

**3. Special Characters in Prompts**
```bash
# WRONG - shell interprets backticks
grok-cli --prompt "Create a `file.md`"

# CORRECT - use single quotes
grok-cli --prompt 'Create a `file.md`'

# CORRECT - escape special characters  
grok-cli --prompt "Create a \`file.md\`"
```

**4. Tool Calls Not Working**
- Ensure `local_file_system` is enabled in `settings.json`
- Check that your prompt clearly requests file operations
- Try debug mode: `grok-cli --debug 1 --prompt "your prompt"`

**5. WSL-Specific Issues**
```bash
# Permission errors - ensure you're in user directory
cd ~

# Network issues - update DNS
sudo echo "nameserver 8.8.8.8" > /etc/resolv.conf

# Environment variables not persisting
source ~/.bashrc
```

### Debug Mode

Enable detailed logging to troubleshoot issues:

```bash
# Method 1: Command line flag
grok-cli --debug 1 --prompt "your prompt"

# Method 2: Environment variable
export GROK_DEBUG=1           # Linux/WSL
$env:GROK_DEBUG=1            # PowerShell
grok-cli --prompt "your prompt"
```

## 📚 Examples

### File Operations
```bash
# Create a project structure
grok-cli --prompt "Create a Python project with main.py, requirements.txt, and README.md"

# Analyze codebase
grok-cli --prompt "Read all Python files and create a summary of the project structure"

# Generate documentation
grok-cli --prompt "Create a table of contents for all files in this project"
```

### Web Search & Research
```bash
# Latest news (requires BRAVE_SEARCH_API_KEY)
grok-cli --prompt "What are the latest AI breakthroughs this month?"

# Technical research
grok-cli --prompt "Search for best practices in Python CLI development"
```

### Interactive Development
```bash
# Start interactive session
grok-cli --chat

# Example conversation:
# You: Analyze the structure of this codebase
# Grok: [analyzes files and provides summary]
# You: Create unit tests for the main functions
# Grok: [creates test files]
# You: /save project_analysis.json
# You: /quit
```

## 🔒 Security

- **Never commit API keys** to version control
- **Use environment variables** for sensitive data
- **Review file operations** when using local_file_system tools
- **Check .gitignore** - sensitive files are excluded by default

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **xAI** for the Grok API
- **Model Context Protocol (MCP)** specification
- **Brave Search API** for web search capabilities
- **Open source community** for inspiration and feedback

## 🆘 Support

- **Issues**: Report bugs and request features at [GitHub Issues](https://github.com/yourusername/grok-cli/issues)
- **API Help**: Check xAI documentation at https://x.ai/api
- **Brave Search**: API documentation at https://api.search.brave.com