# toy-agent

A basic LLM-based React (Reasoning + Acting) agent for software development tasks.

## Overview

This agent uses the React pattern to autonomously complete software development tasks. It can:
- Explore code repositories
- Search through files
- Read and write code
- Make decisions about what to do next
- Work autonomously until the task is complete

The agent uses Claude (via Anthropic API) as its LLM and includes comprehensive logging of all states, events, and LLM interactions.

## Features

- **React Pattern**: Implements the Reasoning + Acting loop for autonomous decision-making
- **Code Repository Tools**: Built-in CLI tools for file operations (list, read, write, search)
- **LLM Integration**: Uses Claude API for intelligent reasoning
- **Autonomous Execution**: Runs in a loop until the task is completed or max iterations reached
- **Comprehensive Logging**: Logs all agent states, tool executions, and LLM context/responses

## Installation

1. Clone the repository:
```bash
git clone https://github.com/adamtait/toy-agent.git
cd toy-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Anthropic API key:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

### Basic Usage

```bash
python main.py --task "Create a hello.py file that prints 'Hello World'"
```

### Advanced Options

```bash
# Run with a different repository path
python main.py --task "Add error handling to the main function" --repo /path/to/your/repo

# Increase max iterations for complex tasks
python main.py --task "Refactor the database module" --max-iterations 20

# Enable debug logging
python main.py --task "Fix the bug in utils.py" --log-level DEBUG

# Save logs to a file
python main.py --task "Add unit tests" --log-file logs/agent.log
```

### Command-Line Arguments

- `--task`: (required) The task description for the agent to complete
- `--repo`: Path to the code repository (default: current directory)
- `--max-iterations`: Maximum number of reasoning-action cycles (default: 10)
- `--log-level`: Logging level - DEBUG, INFO, WARNING, or ERROR (default: INFO)
- `--log-file`: Optional file path to write logs to

## How It Works

The agent follows the React (Reasoning + Acting) pattern:

1. **THINK**: The agent reasons about what needs to be done next
2. **ACT**: It chooses a tool and specifies parameters
3. **OBSERVE**: It receives the tool execution results
4. **REPEAT**: The cycle continues until the task is complete

### Available Tools

The agent has access to these tools:

- `list_files`: List all files in a directory
- `read_file`: Read the contents of a file
- `write_file`: Write content to a file
- `search_in_files`: Search for patterns in files using grep
- `get_file_info`: Get information about a file
- `task_complete`: Mark the task as complete with a summary

## Example

```bash
$ python main.py --task "Create a Python file that defines a fibonacci function"

================================================================================
React Agent for Software Development
================================================================================
Task: Create a Python file that defines a fibonacci function
Repository: /home/user/toy-agent
Max iterations: 10
Log level: INFO
================================================================================

[Agent explores the repository, reasons about the task, and creates the file...]

================================================================================
FINAL RESULT
================================================================================
Success: True
Iterations used: 3/10
Conversation length: 7 messages
================================================================================
```

## Architecture

```
toy-agent/
├── main.py           # Entry point and CLI
├── agent.py          # Core React agent implementation
├── tools.py          # Code repository tools
├── requirements.txt  # Python dependencies
├── .env.example     # Environment variable template
└── README.md        # This file
```

## Logging

The agent provides comprehensive logging:

- **Agent States**: Iteration counts, decisions, and completion status
- **Tool Executions**: All tool calls with parameters and results
- **LLM Context**: System prompts and conversation history
- **LLM Responses**: Full responses from Claude

Logs can be output to console (default) or saved to a file using `--log-file`.

## Requirements

- Python 3.7+
- Anthropic API key
- Dependencies listed in requirements.txt

## License

MIT