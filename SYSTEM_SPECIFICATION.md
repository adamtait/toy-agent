# System Level Specification for the Toy Agent

## 1. Introduction

### 1.1 Purpose

This document provides a detailed, implementation-agnostic specification for the Toy Agent, a ReAct-based autonomous agent for software development. It is intended to be a comprehensive guide for both language models and human developers, enabling them to understand, reproduce, and extend the system.

### 1.2 Scope

This specification covers the architecture, functionality, and operational environment of the Toy Agent. It details all existing features and behaviors, without making assumptions about future enhancements or specific implementation choices.

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

The Toy Agent is a standalone application that operates on a local code repository. It is designed to be invoked from the command line, with a specific task provided by the user. The agent then operates autonomously to complete the task.

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

- The agent must be implementable in a modern, high-level programming language (e.g., Python 3.7+).
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

The system is composed of the following logical components:
- **Command-Line Entry Point**: The user-facing interface for starting and configuring the agent.
- **Agent Core**: The central component that orchestrates the ReAct loop.
- **LLM Subsystem**: The component responsible for all communication with the LLM.
- **Local Tooling Subsystem**: The component that provides the agent with the ability to interact with the local filesystem.
- **Remote Tooling Subsystem**: The component that provides the agent with the ability to interact with remote tools via MCP.

## 4. Component Specifications

### 4.1. Command-Line Entry Point

- **Description**: This component is responsible for parsing user input, configuring the agent, and initiating a run.
- **Inputs**:
    - A required "task" string.
    - An optional "repository path" string.
    - An optional "max iterations" integer.
    - An optional "LLM provider" string.
    - An optional "log level" string.
    - An optional "log file" string.
    - An optional "MCP server URL" string.
- **Pre-conditions**:
    - The user has provided a valid task.
- **Post-conditions**:
    - The Agent Core is initialized with the correct configuration.
    - The agent's main execution loop is started.
    - The final result of the agent's run is reported to the user.
- **Behaviors**:
    - It must parse all documented command-line arguments.
    - It must configure the system's logging based on the user's input.
    - It must load any required environment variables (e.g., API keys).
    - It must instantiate the appropriate LLM client based on the user's selection.

### 4.2. Agent Core

- **Description**: This component is the heart of the agent, responsible for managing the ReAct loop and the conversation with the LLM.
- **Inputs**:
    - An LLM client.
    - A repository path.
    - A maximum number of iterations.
    - An optional MCP server URL.
- **Pre-conditions**:
    - The component is initialized with a valid configuration.
- **Post-conditions**:
    - The task is completed successfully, or the agent stops after reaching the maximum number of iterations.
- **Behaviors**:
    - It must manage the conversation history with the LLM.
    - It must construct a system prompt that explains the ReAct pattern and lists the available tools.
    - It must repeatedly call the LLM Subsystem to get the next action.
    - It must parse the LLM's response to identify the chosen tool and its parameters.
    - It must delegate the execution of the chosen tool to the appropriate Tooling Subsystem.
    - It must feed the result of the tool's execution back to the LLM as an "observation."

### 4.3. LLM Subsystem

- **Description**: This component provides a standardized interface for communicating with different LLMs.
- **Inputs**:
    - A system prompt.
    - The current conversation history.
- **Pre-conditions**:
    - The subsystem is initialized with a valid API key.
- **Post-conditions**:
    - The LLM's response is returned to the Agent Core.
- **Behaviors**:
    - It must provide a common interface for different LLM providers (e.g., Anthropic Claude, Google Gemini).
    - It must handle the specifics of making API calls to the selected LLM.
    - It must include error handling for API failures.

### 4.4. Local Tooling Subsystem

- **Description**: This component provides the agent with a set of tools for interacting with the local filesystem.
- **Inputs**:
    - A tool name and a set of parameters.
- **Pre-conditions**:
    - The tool name is valid and the parameters are correct.
- **Post-conditions**:
    - The tool's action is performed on the filesystem.
    - The result of the action is returned to the Agent Core.
- **Behaviors**:
    - It must provide the following tools:
        - `list_files`: Recursively lists all files in a directory.
        - `read_file`: Reads the content of a file.
        - `write_file`: Writes content to a file.
        - `search_in_files`: Searches for a pattern in files.
        - `get_file_info`: Retrieves metadata about a file.
        - `task_complete`: Signals that the task is finished.
    - It must provide a mechanism for the Agent Core to discover the available tools and their schemas.

### 4.5. Remote Tooling Subsystem

- **Description**: This component provides the agent with the ability to discover and execute tools from a remote MCP server.
- **Inputs**:
    - The URL of an MCP server.
- **Pre-conditions**:
    - The MCP server is available and responsive.
- **Post-conditions**:
    - The list of remote tools is available to the Agent Core.
    - Remote tools can be executed and their results returned to the Agent Core.
- **Behaviors**:
    - It must be able to fetch a list of available tools from the MCP server.
    - It must be able to execute a tool on the MCP server with a given set of parameters.

## 5. Non-Functional Requirements

### 5.1 Performance

The agent's performance is primarily determined by the response time of the LLM API. Local file operations are expected to be fast.

### 5.2 Security

The agent operates with the same permissions as the user who invokes it. It does not implement any additional security measures.

### 5.3 Observability

The agent provides detailed logging of its operations, including all interactions with the LLM and the local filesystem.
