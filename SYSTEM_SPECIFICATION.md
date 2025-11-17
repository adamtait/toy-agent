# System Level Specification for the Toy Agent

## 1. Introduction

### 1.1 Purpose

This document provides a detailed specification for the Toy Agent, a ReAct-based autonomous agent for software development. It is intended to be a comprehensive guide for both language models and human developers, enabling them to understand, reproduce, and extend the system.

### 1.2 Scope

This specification covers the architecture, functionality, and operational environment of the Toy Agent as of the current version in the repository. It details all existing features and behaviors, without making assumptions about future enhancements.

### 1.3 Definitions and Acronyms

| Term | Definition |
| :--- | :--- |
| **ReAct** | Reasoning and Acting, a pattern for autonomous agents that combines chain-of-thought reasoning with tool use. |
| **LLM** | Large Language Model, the core reasoning engine for the agent. |
| **CLI** | Command-Line Interface, the primary user interface for the agent. |
| **MCP** | Model Context Protocol, a protocol for interacting with external tools and services. |
| **API** | Application Programming Interface, used for interacting with the LLM. |

## 2. Overall Description

### 2.1 Product Perspective

The Toy Agent is a standalone Python application that operates on a local code repository. It is designed to be invoked from the command line, with a specific task provided by the user. The agent then operates autonomously to complete the task.

### 2.2 Product Functions

The core functions of the Toy Agent are:
- **Task Interpretation**: Understanding the user's request and breaking it down into actionable steps.
- **Code Interaction**: Reading, writing, and searching files within a specified code repository.
- **Autonomous Operation**: Executing a loop of reasoning and acting until the task is complete.
- **LLM Integration**: Communicating with an LLM to make decisions and generate code.
- **Logging**: Providing detailed logs of its operations for debugging and analysis.

### 2.3 User Characteristics

The primary users of this system are:
- **Language Models**: Who will use this specification to understand and reproduce the code.
- **Software Developers**: Who will use this specification to understand, maintain, and extend the system.

### 2.4 Constraints

- The agent is implemented in Python 3.7+ and relies on the dependencies listed in `requirements.txt`.
- The agent's performance is dependent on the capabilities of the configured LLM.
- The agent operates on the local filesystem and requires appropriate read/write permissions.
- The agent's context is limited by the LLM's context window.

## 3. System Architecture

### 3.1 Architectural Pattern

The system is built on the ReAct (Reasoning + Acting) pattern. This pattern involves a continuous loop of:
1. **Reasoning**: The LLM thinks about the task and decides what to do next.
2. **Acting**: The agent executes a tool based on the LLM's decision.
3. **Observing**: The agent records the result of the action and feeds it back to the LLM.

### 3.2 Component Breakdown

The system is composed of the following key components:
- **`main.py`**: The command-line entry point.
- **`agent.py`**: The core `ReactAgent` class and its logic.
- **`tools.py`**: The `CodeRepositoryTools` class and its methods.
- **`llm.py`**: The LLM client for communicating with the LLM API.

## 4. Functional Requirements

### 4.1. `main.py`

- **4.1.1. Command-Line Argument Parsing**: The script must parse the following command-line arguments:
    - `--task` (string, required): The task for the agent to complete.
    - `--repo` (string, optional, default="."): The path to the code repository.
    - `--max-iterations` (integer, optional, default=10): The maximum number of reasoning-action cycles.
    - `--llm-provider` (string, optional, choices=["claude", "gemini"], default="claude"): The LLM provider to use.
    - `--log-level` (string, optional, choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"): The logging level.
    - `--log-file` (string, optional, default=None): The file to write logs to.
    - `--mcp-server` (string, optional, default=None): The URL of an MCP server to load remote tools from.
- **4.1.2. Logging Setup**: The script must configure logging based on the `--log-level` and `--log-file` arguments.
- **4.1.3. Environment Variable Loading**: The script must load environment variables from a `.env` file.
- **4.1.4. LLM Client Initialization**: The script must initialize the correct LLM client (`ClaudeLlmClient` or `GeminiLlmClient`) based on the `--llm-provider` argument. It must also retrieve the appropriate API key from the environment variables (`ANTHROPIC_API_KEY` or `GEMINI_API_KEY`).
- **4.1.5. Agent Initialization and Execution**: The script must initialize the `ReactAgent` with the parsed arguments and the LLM client, and then call the `run` method with the task.
- **4.1.6. Result Handling**: The script must print the final result of the agent's run, including success status, iterations used, and conversation length.

### 4.2. `agent.py` - `ReactAgent`

- **4.2.1. Initialization**: The `ReactAgent` class must be initialized with an LLM client, a repository path, a maximum number of iterations, and an optional MCP server URL.
- **4.2.2. `run` Method**: The `run` method must:
    - Initialize the conversation history with a system prompt and the user's task.
    - Loop until the task is complete or the maximum number of iterations is reached.
    - In each iteration, call the LLM, process the response, execute the chosen tool, and append the observation to the conversation history.
    - Return a dictionary with the final result.
- **4.2.3. `_build_system_prompt` Method**: This method must construct a system prompt that includes:
    - An introductory paragraph explaining the agent's purpose and the ReAct pattern.
    - A section titled "Available Tools:", under which each available tool (local and MCP) is listed.
    - Each tool's description must be formatted within `<tool>` tags, containing `<name>`, `<description>`, and `<parameters>` sub-tags. The parameters must be a JSON string.
    - A section with instructions on how the LLM must format its response, including the use of `<THOUGHT>` and `<ACTION>` XML tags, and a concrete example of a valid response.
- **4.2.4. `_call_llm` Method**: This method must call the LLM client with the system prompt and the current conversation history, and then append the LLM's response to the history.
- **4.2.5. `_parse_response` Method**: This method must parse the LLM's XML response to extract the thought, tool name, and parameters. To handle potentially malformed or incomplete XML from the LLM, the response string must be wrapped in a root element (e.g., `<root>...response...</root>`) before parsing. If parsing fails for any reason (e.g., `ET.ParseError`, missing required tags), the method must log the error and return `None`.
- **4.2.6. `_process_response` Method**: This method must orchestrate the parsing of the LLM's response and the execution of the chosen tool.
- **4.2.7. `_execute_tool` Method**: This method must:
    - Handle the `task_complete` tool separately.
    - Check if the tool is an MCP tool and execute it if so.
    - Otherwise, execute the tool from the `CodeRepositoryTools` class.

### 4.3. `tools.py` - `CodeRepositoryTools`

- **4.3.1. `list_files` Method**: This method must recursively list all files in a given directory, excluding hidden files and common ignore patterns.
- **4.3.2. `read_file` Method**: This method must read the entire content of a file.
- **4.3.3. `write_file` Method**: This method must write content to a file, creating it if it doesn't exist and overwriting it if it does.
- **4.3.4. `search_in_files` Method**: This method must search for a pattern in files. It must first attempt to use the system's `grep` command on non-Windows platforms for efficiency. The determination of the platform must be done via `platform.system()`. If the `grep` command fails (e.g., `subprocess.SubprocessError` or `FileNotFoundError`) or if the platform is Windows, it must fall back to a manual, line-by-line search through the files in Python. The search should be case-insensitive and recursive.
- **4.3.5. `get_file_info` Method**: This method must retrieve metadata about a file, such as its size and type.
- **4.3.6. `get_available_tools` Function**: This function must return a list of dictionaries, each describing a tool with its name, description, and parameters.

### 4.4. `llm.py`

- **4.4.1. `LlmClient` Abstract Base Class**: This class must define the interface for LLM clients, with an abstract `call_llm` method.
- **4.4.2. `ClaudeLlmClient` Class**: This class must implement the `LlmClient` interface for the Anthropic Claude API.
- **4.4.3. `GeminiLlmClient` Class**: This class must implement the `LlmClient` interface for the Google Gemini API.
- **4.4.4. API Error Handling**: All `LlmClient` implementations must include error handling for API calls. If an API request fails, the client should catch the exception, log a descriptive error message, and raise the exception or handle it in a way that prevents the agent from crashing.

### 4.5. `mcp_tools.py` - `McpTools`

- **4.5.1. Initialization**: The `McpTools` class must be initialized with the URL of an MCP server.
- **4.5.2. `get_mcp_tools` Method**: This method must fetch the list of available tools from the MCP server.
- **4.5.3. `execute_mcp_tool` Method**: This method must execute a tool on the MCP server.

## 5. External Interface Requirements

### 5.1 Command-Line Interface (CLI)

The agent is invoked with the following command-line arguments:
- `--task`: The task for the agent to complete.
- `--repo`: The path to the code repository.
- `--max-iterations`: The maximum number of reasoning-action cycles.
- `--llm-provider`: The LLM provider to use.
- `--log-level`: The logging level.
- `--log-file`: The file to write logs to.
- `--mcp-server`: The URL of an MCP server to load remote tools from.

### 5.2 LLM API

The agent interacts with an LLM via a REST API. The specific endpoint and authentication details are configured via environment variables.

## 6. Non-Functional Requirements

### 6.1 Performance

The agent's performance is primarily determined by the response time of the LLM API. Local file operations are expected to be fast.

### 6.2 Security

The agent operates with the same permissions as the user who invokes it. It does not implement any additional security measures.

### 6.3 Observability

The agent provides detailed logging of its operations, including all interactions with the LLM and the local filesystem.

## 7. Logging Specification

### 7.1 Agent State Logging

- Iteration counts
- Conversation history length
- Completion status
- Max iterations warnings

### 7.2 LLM Interaction Logging

- System prompt
- Full conversation history
- LLM request parameters
- Complete LLM responses

### 7.3 Tool Execution Logging

- Tool name and parameters
- Execution results (success/failure)
- File operations (paths, sizes, counts)
- Error messages with stack traces
