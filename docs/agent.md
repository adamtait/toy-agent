# Agent Core (`agent.py`)

The `agent.py` module contains the `ReactAgent` class, which is the central component of the autonomous agent. It orchestrates the entire process of receiving a task, reasoning about it, and using tools to accomplish it.

## `ReactAgent` Class

The `ReactAgent` class implements the **ReAct (Reasoning + Acting)** pattern. This pattern involves a loop where the agent:
1.  **Thinks** about the current state of the task.
2.  **Acts** by choosing a tool to execute.
3.  **Observes** the result of the tool's execution.

This loop continues until the task is completed or a maximum number of iterations is reached.

### Key Attributes

-   `llm_client`: An instance of an `LlmClient` subclass, responsible for communication with the Large Language Model.
-   `tools`: An instance of `CodeRepositoryTools`, which provides methods for interacting with the local file system.
-   `mcp_tools_client`: An optional `McpTools` instance for fetching and executing tools from a remote MCP server.
-   `conversation_history`: A list that stores the entire interaction with the LLM, including thoughts, actions, and observations.
-   `max_iterations`: The maximum number of THINK/ACT cycles the agent can perform before stopping.

### Core Methods

#### `run(task: str)`

This is the main entry point for the agent. It takes a high-level task description as input and manages the ReAct loop until the task is marked as complete.

#### `_build_system_prompt()`

This method constructs the system prompt that is sent to the LLM at the beginning of a task. The prompt includes:
-   The agent's persona and instructions.
-   A detailed list of all available tools (both local and remote) and their parameters.
-   The required XML format for the LLM's response (`<THOUGHT>` and `<ACTION>` tags).

#### `_call_llm()`

This method sends the current conversation history (including the system prompt) to the LLM and returns the model's response.

#### `_parse_response(response: str)`

The agent parses the LLM's XML response to extract the `thought`, `tool_name`, and `parameters` for the chosen action. It includes robust error handling for malformed XML.

#### `_process_response(response: str)`

This method orchestrates the processing of an LLM response. It calls `_parse_response` and then `_execute_tool`. The result of the tool execution (the "observation") is then appended to the conversation history.

#### `_execute_tool(tool_name: str, parameters: Dict[str, Any])`

This method is responsible for executing the tool selected by the LLM. It can execute:
-   The special `task_complete` tool.
-   Remote tools from an MCP server.
-   Local tools from the `CodeRepositoryTools` class.

## Data Flow within the Agent

1.  The `run` method is called with a task.
2.  A system prompt is built using `_build_system_prompt`.
3.  The agent enters the ReAct loop.
4.  Inside the loop, `_call_llm` sends the conversation history to the LLM.
5.  The LLM's response is processed by `_process_response`.
6.  `_parse_response` extracts the tool and parameters from the XML.
7.  `_execute_tool` runs the specified tool.
8.  The tool's output is formatted as an `<OBSERVATION>` and added to the history.
9.  The loop repeats until the `task_complete` tool is called or `max_iterations` is reached.
