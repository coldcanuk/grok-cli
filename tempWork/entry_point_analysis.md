# Entry Point Flow Analysis

## Command Line Entry Point

When you type `grok-cli` on command line:

1. **setup.py** defines the entry point:
   ```python
   entry_points={
       'console_scripts': [
           'grok-cli = grok_cli.cli:main'
       ]
   }
   ```

2. This calls `main()` function in `grok_cli/cli.py`

## Current Entry Point: cli.py:main()

From setup.py line 10: `'grok-cli = grok_cli.cli:main'`

**Question: What does cli.py:main() actually do?**
- Need to read the full cli.py file to understand
- From snippet read: imports from utils, api_client, file_tools, request_manager, streaming
- Has run_chat_loop function with iteration limits

## Other CLI Files

**optimized_cli.py** - Why does this exist?
- Has own entry point logic
- Mentions "advanced rate limiting and batching"
- Are we supposed to use this instead of cli.py?
- Is this a replacement or alternative implementation?

**Key Questions:**
1. Which CLI file is actually used by setup.py?
2. Why do we have two CLI implementations?
3. Are they competing or complementary?
4. Which one should be the "real" entry point?