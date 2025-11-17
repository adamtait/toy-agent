# Main Entry Point (`main.py`)

The `main.py` script serves as the command-line interface (CLI) for the autonomous agent. It is responsible for parsing arguments, setting up the environment, and initializing and running the `ReactAgent`.

## Key Functions

### `setup_logging(log_level: str, log_file: str = None)`

-   **Description**: Configures the application's logging.
-   **Details**:
    -   Sets up a logger that can stream to both `stdout` and an optional log file.
    -   Reduces the verbosity of third-party libraries (`anthropic`, `httpx`, `google-generativeai`) by setting their log levels to `WARNING`.

### `main()`

-   **Description**: The main function that orchestrates the entire process.
-   **Execution Flow**:
    1.  **Argument Parsing**: It uses `argparse` to define and parse command-line arguments.
    2.  **Logging Setup**: Calls `setup_logging` to configure logging based on the provided arguments.
    3.  **Environment Loading**: Uses `dotenv` to load environment variables (like API keys) from a `.env` file.
    4.  **LLM Client Initialization**: Based on the `--llm-provider` argument, it instantiates the appropriate LLM client (`ClaudeLlmClient` or `GeminiLlmClient`). It also checks for the required API keys.
    5.  **Agent Initialization**: It creates an instance of the `ReactAgent`, passing in the LLM client and other configuration from the command-line arguments.
    6.  **Agent Execution**: It calls the `agent.run()` method with the specified task.
    7.  **Result Reporting**: After the agent finishes, it logs a summary of the results, including success status and the number of iterations used.

## Command-Line Arguments

-   `--task` (required): The software development task for the agent.
-   `--repo` (optional): The path to the code repository. Defaults to the current directory.
-   `--max-iterations` (optional): The maximum number of THINK/ACT cycles. Defaults to 10.
-   `--llm-provider` (optional): The LLM to use (`claude` or `gemini`). Defaults to `claude`.
-   `--log-level` (optional): The logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). Defaults to `INFO`.
-   `--log-file` (optional): A file path to write logs to.
-   `--mcp-server` (optional): The URL of an MCP server to load remote tools from.
