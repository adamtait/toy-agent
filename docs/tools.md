# Tools

The agent is equipped with a variety of tools to interact with the code repository and external services. These tools are the "actions" in the ReAct pattern.

## Local Tools (`tools.py`)

The `CodeRepositoryTools` class in `tools.py` provides a set of core tools for file system operations. The `get_available_tools` function returns a schema for these tools, which is used to construct the LLM's system prompt.

### `list_files(directory: str = ".")`

-   **Description**: Recursively lists all files in a specified directory.
-   **Parameters**:
    -   `directory` (optional): The directory path relative to the repository root. Defaults to the root.
-   **Returns**: A dictionary containing a list of file paths and the total count.

### `read_file(filepath: str)`

-   **Description**: Reads the entire content of a file.
-   **Parameters**:
    -   `filepath` (required): The relative path to the file.
-   **Returns**: A dictionary containing the file's content and line count.

### `write_file(filepath: str, content: str)`

-   **Description**: Writes content to a file. It creates the file if it doesn't exist and overwrites it if it does.
-   **Parameters**:
    -   `filepath` (required): The relative path to the file.
    -   `content` (required): The new content to write.
-   **Returns**: A dictionary indicating success and the number of bytes written.

### `search_in_files(pattern: str, file_extension: str = None)`

-   **Description**: Searches for a text pattern in files. It uses `grep` for performance on Unix-like systems and has a Python-based fallback.
-   **Parameters**:
    -   `pattern` (required): The text to search for.
    -   `file_extension` (optional): A file extension to filter the search (e.g., "py").
-   **Returns**: A dictionary with a list of matching lines and the total count.

### `get_file_info(filepath: str)`

-   **Description**: Retrieves metadata for a file.
-   **Parameters**:
    -   `filepath` (required): The relative path to the file.
-   **Returns**: A dictionary with metadata such as size, existence, and whether it's a file or directory.

### `task_complete(summary: str)`

-   **Description**: A special tool that the agent calls to signal that it has finished the assigned task.
-   **Parameters**:
    -   `summary` (required): A brief summary of the completed work.
-   **Returns**: A dictionary indicating success and the provided summary.

## Remote Tools (`mcp_tools.py`)

The `McpTools` class allows the agent to connect to an MCP (Model Context Protocol) server to discover and execute remote tools.

### `get_mcp_tools()`

-   **Description**: Fetches the list of available tools from the MCP server's `/tools` endpoint.
-   **Returns**: A list of tool schemas, similar to the local tools.

### `execute_mcp_tool(tool_name: str, parameters: Dict[str, Any])`

-   **Description**: Executes a tool on the MCP server by sending a request to the `/execute/{tool_name}` endpoint.
-   **Parameters**:
    -   `tool_name` (required): The name of the remote tool to execute.
    -   `parameters` (required): A dictionary of parameters for the tool.
-   **Returns**: The result of the remote tool's execution.
