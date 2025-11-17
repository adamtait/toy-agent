# LLM Client (`llm.py`)

The `llm.py` module is responsible for abstracting the interaction with different Large Language Models (LLMs). It provides a unified interface that allows the agent to be backend-agnostic.

## `LlmClient` Abstract Base Class

The core of this module is the `LlmClient` abstract base class. It defines the contract that all concrete LLM client implementations must adhere to.

### `call_llm(system_prompt: str, conversation_history: List[Dict[str, Any]]) -> str`

This is the single abstract method that all subclasses must implement. It takes the system prompt and the current conversation history as input and is expected to return the LLM's response as a string.

## Concrete Implementations

The module includes concrete implementations for popular LLM providers.

### `ClaudeLlmClient`

-   **Provider**: Anthropic Claude
-   **Package**: `anthropic`
-   **Authentication**: Uses an Anthropic API key.
-   **Details**: This client communicates with the Claude API. It sends the system prompt and conversation history directly to the model.

### `GeminiLlmClient`

-   **Provider**: Google Gemini
-   **Package**: `google-generativeai`
-   **Authentication**: Uses a Google Gemini API key.
-   **Details**: This client is designed for the Gemini API. It includes a `_prepare_chat_history` method to adapt the agent's standard conversation format to the one required by the Gemini chat model.

## Extensibility

The architecture makes it straightforward to add support for new LLM providers:
1.  Create a new class that inherits from `LlmClient`.
2.  Implement the `call_llm` method, including any necessary logic to format the conversation history for the new provider's API.
3.  Update the `main.py` script to allow the selection of the new client via a command-line argument.
