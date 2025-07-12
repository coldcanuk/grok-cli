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
- 🎯 **Leader-Follower Mode**: Strategic planning with grok-3-mini creating execution plans for grok-4-0709

## 📋 Prerequisites

- **Python 3.8 or higher**
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
   grok-cli --src . --test
   grok-cli --help
   ```

#### Option 2: Using Virtual Environment (Isolated Installation)

```powershell
# Create and activate virtual environment
python -m venv grok-env
grok-env\Scripts\Activate.ps1

# Install and test
pip install -e .
grok-cli --src . --test
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
   grok-cli --src . --test
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
   grok-cli --src . --test
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
grok-cli --src . --test
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

### ⚠️ IMPORTANT: Source Directory Requirement

**All commands require the `--src` flag** to specify your working directory. This enables:

- **Portable operation**: Run Grok CLI from anywhere while working on specific projects
- **Project context**: Automatic loading of `.grok/` directory for project-specific instructions
- **Security boundary**: Limits file operations to your specified directory
- **Context awareness**: Grok understands your project structure and requirements

```bash
# REQUIRED: Always specify source directory
grok-cli --src /path/to/your/project --prompt "Your question here"

# Examples:
grok-cli --src /home/user/my-webapp --prompt "Review the React components"
grok-cli --src /mnt/c/dev/my-api --chat
grok-cli --src . --prompt "What is this project about?"  # Current directory
```

### Project Context with .grok Directory

Grok CLI automatically looks for a `.grok/` directory in your source directory to understand your project better:

- **`.grok/README.md`**: Project overview and goals
- **`.grok/*.mdc`**: Markdown context files with coding standards, architecture docs, etc.

If `.grok/` doesn't exist, Grok CLI will create a template for you.

**Example .mdc files:**
```
.grok/
├── README.md              # Project overview
├── coding-standards.mdc   # Your coding style
├── architecture.mdc       # System design
└── api-docs.mdc          # API documentation
```

### Basic Commands

```bash
# Single prompt (note: --src is required)
grok-cli --src /path/to/project --prompt "What is the capital of France?"

# Interactive chat mode
grok-cli --src /path/to/project --chat

# Leader-Follower strategic planning mode 🎯
grok-cli --src /path/to/project --lead --prompt "Implement user authentication system"
grok-cli --src /path/to/project --lead  # Interactive objective input

# Cost tracking mode 💰
grok-cli --src /path/to/project --cost --prompt "Your question here"
grok-cli --src /path/to/project --cost --chat  # Interactive chat with cost tracking

# With image analysis
grok-cli --src /path/to/project --prompt "What's in this image?" --image path/to/image.jpg

# Streaming mode with progress indicators
grok-cli --src /path/to/project --prompt "Write a poem about AI" --stream

# Using different model
grok-cli --src /path/to/project --prompt "Hello" --model grok-beta

# Run self-tests
grok-cli --src /path/to/project --test
```

### Interactive Chat Commands

Once in chat mode (`grok-cli --src /path/to/project --chat`):
- `/quit` - Exit the chat
- `/clear` - Clear conversation history  
- `/save <filename>` - Save conversation to JSON file
- `/costs` - Show session cost summary (when --cost flag is used)

### 🎯 Leader-Follower Mode (`--lead`)

Revolutionary dual-model approach for complex task execution with strategic oversight:

#### How It Works

**🧠 Leader (grok-3-mini)** - Strategic Planner:
- Performs systemic analysis with error boundary identification
- Creates comprehensive 3-phase execution plans
- Breaks down complex objectives into manageable milestones and tasks
- Generates `tempWork/followMe.md` optimized for AI execution
- Cost-efficient planning with focused strategic thinking

**🚀 Follower (grok-4-0709)** - Execution Engine:
- Follows strategic plan systematically using full tool suite
- Implements solutions through Investigation → Heavy Lifting → Polish phases
- Reports progress through each milestone and task
- Adapts intelligently while maintaining strategic direction
- High-performance execution with complete API access

#### Usage Examples

```bash
# Strategic planning for complex development tasks
grok-cli --src . --lead --prompt "Build a REST API with authentication and database integration"

# Interactive mode - enter objective when prompted
grok-cli --src . --lead
# Enter your objective: Optimize this React application for performance

# Web application development
grok-cli --src ./my-webapp --lead --prompt "Add user dashboard with data visualization"

# System architecture planning
grok-cli --src ./microservices --lead --prompt "Implement distributed logging and monitoring"
```

#### The 3-Phase Execution Framework

**Phase 1: Investigation 🔍**
- Requirements analysis and system exploration
- Dependency mapping and constraint identification
- Current state assessment and gap analysis
- Risk evaluation and error boundary identification

**Phase 2: Heavy Lifting ⚡**
- Core implementation work and coding
- Testing and iterative development
- Integration and system connectivity
- Performance optimization and refactoring

**Phase 3: Polish & Finalization ✨**
- Comprehensive testing and quality assurance
- Documentation and code cleanup
- Final optimizations and tweaking
- Deployment preparation and validation

#### Strategic Plan Output

The leader creates `tempWork/followMe.md` containing:
- **Systemic Analysis**: Error boundaries, dependencies, and system context
- **Detailed Milestones**: Major work efforts for each phase
- **Meticulous Todo Tasks**: Step-by-step implementation checklist
- **Execution Notes**: Implementation guidance and success criteria

#### Best Use Cases

- 🏗️ **Complex Development Projects**: Multi-component systems requiring coordination
- 🔄 **System Refactoring**: Large-scale code improvements with multiple dependencies
- 🚀 **Feature Implementation**: New functionality requiring multiple phases
- 🔧 **Architecture Changes**: System-wide modifications with careful planning
- 📊 **Performance Optimization**: Systematic approach to bottleneck resolution

### 💰 Cost Tracking Mode (`--cost`)

Real-time token usage and cost monitoring for transparent billing:

#### How It Works

**Token Counting**: Uses OpenAI-compatible tiktoken tokenizer for accurate counting
- Handles text prompts, system messages, tool calls, and vision content
- Real-time estimation before API calls with cost warnings
- Actual token tracking from API responses

**Cost Calculation**: Accurate USD pricing for all Grok models
- **grok-beta**: $5 input, $15 output per 1M tokens
- **grok-4**: $3 input, $15 output, $0.75 cached per 1M tokens  
- **grok-3-mini**: $1 input, $3 output per 1M tokens
- **Live Search**: $25 per 1K searches

#### Usage Examples

```bash
# Single prompt with cost tracking
grok-cli --src . --cost --prompt "Explain quantum computing"

# Interactive chat with cost monitoring
grok-cli --src . --cost --chat

# Leader-follower mode with cost analysis
grok-cli --src . --cost --lead --prompt "Build a REST API"

# Combine with streaming and other features
grok-cli --src . --cost --stream --prompt "Write a Python script"
```

#### Cost Tracking Features

**Pre-Call Estimation**:
- Token count estimation before API calls
- Cost warnings for expensive operations (>$1.00)
- Model-specific pricing calculations

**Real-Time Monitoring**:
- Actual token usage from API responses
- Cost breakdown by input/output/cached tokens
- Session accumulation across multiple calls

**Session Management**:
- Persistent cost tracking across CLI sessions
- Cost history saved to `grok_session_costs.json`
- Session summaries with duration and total costs

**Interactive Commands** (in `--chat` mode):
- `/costs` - Display current session cost summary
- Automatic cost display at session end

#### Cost Efficiency Tips

```bash
# Use grok-3-mini for simple tasks (cheaper)
grok-cli --src . --cost --model grok-3-mini --prompt "Simple question"

# Leader-follower for complex tasks (cost-optimized planning)
grok-cli --src . --cost --lead --prompt "Complex development task"

# Monitor costs in long interactive sessions
grok-cli --src . --cost --chat
# Use /costs regularly to check spending
```

### Advanced Usage

```bash
# Complex prompts (use quotes to handle special characters)
grok-cli --src /path/to/project --prompt 'Create a `README.md` file with installation instructions'

# Enable debug mode for detailed tool execution logs
grok-cli --src /path/to/project --debug 1 --prompt "List all Python files in this project"

# Web search (requires BRAVE_SEARCH_API_KEY)
grok-cli --src /path/to/project --prompt "What are the latest developments in AI?"

# File operations
grok-cli --src /path/to/project --prompt "Create a Python script that prints 'Hello World' and save it as hello.py"

# Batch file operations
grok-cli --src /path/to/project --prompt "Read all Python files in the grok_cli directory and summarize their purpose"

# Leader-Follower strategic execution
grok-cli --src /path/to/project --lead --prompt "Implement comprehensive test suite with unit and integration tests"

# Leader-Follower with complex system architecture
grok-cli --src /path/to/project --lead --prompt "Migrate this monolith to microservices architecture"
```

## 🔧 Architecture

The CLI features a clean, optimized architecture:

```
grok_cli/
├── cli.py              # Clean entry point with argument parsing and mode routing
├── engine.py           # Core functionality with integrated streaming and tools
├── leader.py           # Leader-Follower orchestration for strategic planning 🎯
├── utils.py            # Shared utilities (config, vision, gitignore, project context)
├── request_manager.py  # Advanced request batching and caching optimization
├── thinking.json       # AI thinking prompts configuration
└── startup.json        # Startup messages configuration
```

### Performance Features

- **Smart Rate Limiting**: Adaptive delays with exponential backoff
- **Request Batching**: Multiple file operations combined efficiently  
- **Intelligent Caching**: Avoid redundant API calls for file reads
- **Progress Indicators**: Visual feedback during rate limit waits
- **Tool Call Optimization**: Enhanced JSON parsing and error recovery
- **Strategic Planning**: Leader-Follower architecture for complex task execution
- **Cost Optimization**: grok-3-mini for planning, grok-4-0709 for execution

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
grok-cli --src /path/to/project --prompt "Create a Python project with main.py, requirements.txt, and README.md"

# Analyze codebase
grok-cli --src /path/to/project --prompt "Read all Python files and create a summary of the project structure"

# Generate documentation
grok-cli --src /path/to/project --prompt "Create a table of contents for all files in this project"
```

### Web Search & Research
```bash
# Latest news (requires BRAVE_SEARCH_API_KEY)
grok-cli --src /path/to/project --prompt "What are the latest AI breakthroughs this month?"

# Technical research
grok-cli --src /path/to/project --prompt "Search for best practices in Python CLI development"
```

### Interactive Development
```bash
# Start interactive session
grok-cli --src /path/to/project --chat

# Example conversation:
# You: Analyze the structure of this codebase
# Grok: [analyzes files and provides summary]
# You: Create unit tests for the main functions
# Grok: [creates test files]
# You: /save project_analysis.json
# You: /quit
```

### 🎯 Leader-Follower Strategic Execution
```bash
# Complex system development with strategic planning
grok-cli --src ./my-project --lead --prompt "Build a complete CI/CD pipeline with testing, staging, and deployment"

# Example workflow:
# 🧠 Leader (grok-3-mini) creates strategic plan:
#   - Phase 1: Investigate current build system and requirements
#   - Phase 2: Implement pipeline components and testing
#   - Phase 3: Polish configuration and add monitoring
#   - Saves detailed plan to tempWork/followMe.md

# 🚀 Follower (grok-4-0709) executes systematically:
#   - Reads strategic plan from followMe.md
#   - Executes each phase methodically
#   - Reports milestone completion
#   - Adapts plan based on discovered requirements

# Result: Complete CI/CD system with strategic oversight
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