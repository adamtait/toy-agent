# Architecture

## Overview

The toy-agent implements the **ReAct** (Reasoning + Acting) pattern for autonomous software development tasks. The agent combines large language model reasoning with concrete actions through a set of code repository tools.

## Components

### 1. Agent Core (`agent.py`)

The `ReactAgent` class implements the main reasoning-action loop:

```
┌─────────────────────────────────────┐
│         ReactAgent                   │
├─────────────────────────────────────┤
│  • Manages conversation history      │
│  • Coordinates LLM calls             │
│  • Orchestrates tool execution       │
│  • Controls the React loop           │
│  • Logs all interactions             │
└─────────────────────────────────────┘
           │
           ├──> LLM (Claude API)
           │
           └──> CodeRepositoryTools
```

#### React Loop Flow

```
1. THINK (LLM Reasoning)
   ↓
   "I need to understand the repository structure first..."
   
2. ACT (Tool Selection)
   ↓
   ACTION: list_files
   PARAMETERS: {"directory": "."}
   
3. OBSERVE (Tool Result)
   ↓
   OBSERVATION: {"success": true, "files": [...], "count": 5}
   
4. REPEAT (Until Complete)
   ↓
   Back to THINK with new information
```

### 2. Code Repository Tools (`tools.py`)

The `CodeRepositoryTools` class provides the agent with capabilities to interact with code:

**Available Tools:**

1. **list_files** - Browse repository structure
   - Lists all files in a directory
   - Filters out hidden files and common ignore patterns
   - Returns file count and paths

2. **read_file** - Read file contents
   - Reads any text file
   - Returns content with line count
   - Handles encoding errors gracefully

3. **write_file** - Create or modify files
   - Creates new files or overwrites existing ones
   - Automatically creates parent directories
   - Returns bytes written

4. **search_in_files** - Search for patterns
   - Uses grep for fast pattern matching
   - Supports file extension filtering
   - Returns matches with line numbers

5. **get_file_info** - Query file metadata
   - Check file existence
   - Get file size
   - Determine file type

6. **task_complete** - Signal completion
   - Agent calls this when task is done
   - Provides summary of work completed
   - Exits the React loop

### 3. Main Entry Point (`main.py`)

Command-line interface that:
- Parses arguments
- Sets up logging
- Loads environment configuration
- Initializes and runs the agent
- Reports final results

## Data Flow

```
User Task
    ↓
main.py (CLI)
    ↓
    ├─> Load .env configuration
    ├─> Setup logging
    └─> Initialize ReactAgent
         ↓
         React Loop:
         ├─> Build system prompt with tool descriptions
         ├─> Call LLM with conversation history
         │   ├─> Claude API (Anthropic)
         │   └─> Returns reasoning + action
         ├─> Parse response (ACTION + PARAMETERS)
         ├─> Execute tool via CodeRepositoryTools
         │   ├─> File system operations
         │   └─> Returns results
         ├─> Add observation to history
         └─> Repeat until task_complete or max iterations
              ↓
         Final Result
```

## Logging Strategy

The agent implements comprehensive logging at multiple levels:

### 1. Agent State Logging
- Iteration counts
- Conversation history length
- Completion status
- Max iterations warnings

### 2. LLM Interaction Logging
- System prompt (DEBUG level)
- Full conversation history
- LLM request parameters
- Complete LLM responses
- Token usage (if available)

### 3. Tool Execution Logging
- Tool name and parameters
- Execution results (success/failure)
- File operations (paths, sizes, counts)
- Error messages with stack traces

### 4. Log Levels
- **DEBUG**: Full system prompts, detailed tool operations
- **INFO**: Iterations, tool calls, results (default)
- **WARNING**: Non-critical issues, max iterations approaching
- **ERROR**: Tool failures, API errors

## Example Interaction

```
Task: "Create a hello.py file that prints 'Hello World'"

[Iteration 1]
LLM THINKS: "I should first check what files exist..."
LLM ACTS: list_files(directory=".")
OBSERVATION: Found 3 files

[Iteration 2]
LLM THINKS: "No hello.py exists, I'll create it..."
LLM ACTS: write_file(filepath="hello.py", content="print('Hello World')")
OBSERVATION: Successfully wrote 19 bytes

[Iteration 3]
LLM THINKS: "File created successfully, task is complete"
LLM ACTS: task_complete(summary="Created hello.py file")
RESULT: Success
```

## Design Decisions

### 1. Autonomous Loop
The agent runs autonomously until it decides the task is complete or reaches max iterations. This allows for:
- Self-directed exploration
- Adaptive problem-solving
- Error recovery

### 2. Tool-Based Architecture
Tools are cleanly separated from the agent logic, enabling:
- Easy addition of new tools
- Independent testing of tools
- Clear separation of concerns

### 3. Comprehensive Logging
All interactions are logged because:
- Debugging agent behavior requires full context
- Understanding LLM reasoning helps improve prompts
- Tracking tool usage identifies bottlenecks

### 4. Claude API Integration
Using Claude (Sonnet 3.5) because:
- Strong reasoning capabilities
- Good at following structured formats
- Reliable API with good rate limits

## Extending the Agent

### Adding New Tools

1. Add method to `CodeRepositoryTools`:
```python
def new_tool(self, param: str) -> Dict[str, Any]:
    """Tool description."""
    try:
        # Tool logic here
        return {"success": True, "result": ...}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

2. Add tool description to `get_available_tools()`:
```python
{
    "name": "new_tool",
    "description": "What the tool does",
    "parameters": {
        "param": "string (required)"
    }
}
```

3. The agent will automatically have access to the new tool!

### Improving the System Prompt

The system prompt in `_build_system_prompt()` can be enhanced with:
- More specific instructions for code quality
- Language-specific guidelines
- Best practices for software development
- Examples of good reasoning

### Changing the LLM Model

Update the model in `_call_llm()`:
```python
response = self.client.messages.create(
    model="claude-3-opus-20240229",  # Change model here
    ...
)
```

## Limitations

1. **Context Window**: Long conversations may exceed LLM context limits
2. **Tool Errors**: No automatic retry logic for failed tools
3. **File Types**: Only handles text files, not binary files
4. **Repository Size**: May struggle with very large repositories
5. **Concurrency**: Single-threaded, no parallel tool execution

## Future Enhancements

- Add git integration tools (commit, push, branch)
- Implement code analysis tools (lint, test, build)
- Add memory/context management for long conversations
- Support for binary file operations
- Parallel tool execution
- Retry logic with exponential backoff
- Progress persistence and resume capability
