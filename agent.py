"""
React Agent implementation for software development tasks.
Uses reasoning and acting in a loop with Claude LLM.
"""

import json
import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from llm import LlmClient
from tools import CodeRepositoryTools, get_available_tools
from mcp_tools import McpTools

import time

logger = logging.getLogger(__name__)


class ReactAgent:
    """
    A React (Reasoning + Acting) agent that uses LLM to autonomously
    complete software development tasks.
    """
    
    def __init__(self, llm_client: LlmClient, repo_path: str = ".", max_iterations: int = 10, mcp_server_url: Optional[str] = None):
        """
        Initialize the React agent.
        
        Args:
            llm_client: An instance of a class that inherits from LlmClient
            repo_path: Path to the code repository
            max_iterations: Maximum number of reasoning-action cycles
        """
        self.llm_client = llm_client
        self.tools = CodeRepositoryTools(repo_path)
        self.max_iterations = max_iterations
        self.iteration_count = 0
        self.conversation_history = []
        self.is_complete = False
        self.mcp_tools_client = None
        self.mcp_tools = []

        if mcp_server_url:
            self.mcp_tools_client = McpTools(mcp_server_url)
            self.mcp_tools = self.mcp_tools_client.get_mcp_tools()

        logger.info(f"Initialized ReactAgent with repo_path: {repo_path}, max_iterations: {max_iterations}")

    def run(self, task: str) -> Dict[str, Any]:
        """
        Run the agent on a given task.
        
        Args:
            task: The task description for the agent to complete
            
        Returns:
            Dictionary with results and execution summary
        """
        logger.info(f"Starting agent run with task: {task}")
        logger.info("="*80)
        
        # Initialize conversation with the task
        system_prompt = self._build_system_prompt()
        self.conversation_history = [
            {
                "role": "user",
                "content": f"Task: {task}\n\nPlease complete this task using the available tools. Think step by step about what you need to do."
            }
        ]
        
        # Main React loop
        while not self.is_complete and self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            logger.info(f"\n{'='*80}")
            logger.info(f"ITERATION {self.iteration_count}/{self.max_iterations}")
            logger.info(f"{'='*80}")
            
            try:
                # Get LLM response
                response = self._call_llm(system_prompt)
                
                # Process the response and execute tools
                tool_result = self._process_response(response)
                
                # Check if task is complete
                if tool_result and tool_result.get("tool_name") == "task_complete":
                    self.is_complete = True
                    logger.info(f"\nTask completed! Summary: {tool_result.get('result', {}).get('summary', 'No summary provided')}")
                    break
                
            except Exception as e:
                logger.error(f"Error in iteration {self.iteration_count}: {str(e)}")
                self.conversation_history.append({
                    "role": "user",
                    "content": f"Error occurred: {str(e)}. Please try a different approach."
                })
        
        # Prepare final result
        result = {
            "success": self.is_complete,
            "iterations": self.iteration_count,
            "max_iterations_reached": self.iteration_count >= self.max_iterations,
            "conversation_length": len(self.conversation_history)
        }
        
        logger.info(f"\n{'='*80}")
        logger.info(f"AGENT RUN COMPLETED")
        logger.info(f"Success: {result['success']}")
        logger.info(f"Iterations: {result['iterations']}")
        logger.info(f"{'='*80}")
        
        return result
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with tool descriptions."""
        all_tools = get_available_tools()
        if self.mcp_tools:
            all_tools.extend(self.mcp_tools)

        tools_description = "\n\n".join([
            f"<tool>\n"
            f"  <name>{tool['name']}</name>\n"
            f"  <description>{tool['description']}</description>\n"
            f"  <parameters>{json.dumps(tool['parameters'], indent=2)}</parameters>\n"
            f"</tool>"
            for tool in all_tools
        ])
        
        prompt = f"""You are a software development agent that can interact with a code repository.
You follow the ReAct pattern: Reasoning + Acting.

For each step:
1. THINK: Reason about what you need to do next
2. ACT: Choose a tool to use and specify the parameters in XML format

Available Tools:
{tools_description}

Instructions:
- Always start by exploring the repository to understand its structure
- Think step by step about what needs to be done
- Use the tools to read, search, and modify files as needed
- When you've completed the task, call the 'task_complete' tool with a summary
- Format your responses using XML tags:

<THOUGHT>[Your reasoning about what to do next]</THOUGHT>
<ACTION>
  <tool_name>[Tool name]</tool_name>
  <parameters>
    <param_name>[param_value]</param_name>
  </parameters>
</ACTION>

Example:
<THOUGHT>I need to see what files are in the repository first.</THOUGHT>
<ACTION>
  <tool_name>list_files</tool_name>
  <parameters>
    <directory>.</directory>
  </parameters>
</ACTION>

After you use a tool, I will respond with:
<OBSERVATION>[Tool execution result]</OBSERVATION>

Then you continue with your next THOUGHT/ACTION cycle.
"""
        return prompt
    
    def _call_llm(self, system_prompt: str) -> str:
        """
        Call the configured LLM with the current conversation history.
        
        Args:
            system_prompt: The system prompt with instructions
            
        Returns:
            The LLM's response text
        """
        response_text = self.llm_client.call_llm(system_prompt, self.conversation_history)
        
        # Add assistant's response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })
        
        return response_text
    
    def _parse_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse the LLM's XML response.

        Args:
            response: The XML response from the LLM.

        Returns:
            A dictionary containing the parsed data or None if parsing fails.
        """
        try:
            # Wrap the response in a root element to handle fragmented XML
            xml_response = f"<root>{response}</root>"
            root = ET.fromstring(xml_response)

            thought_element = root.find("THOUGHT")
            thought = thought_element.text.strip() if thought_element is not None and thought_element.text else ""

            action_element = root.find("ACTION")
            tool_name_element = action_element.find("tool_name")
            tool_name = tool_name_element.text.strip() if tool_name_element is not None and tool_name_element.text else ""

            parameters = {}
            params_element = action_element.find("parameters")
            if params_element is not None:
                for param in params_element:
                    parameters[param.tag] = param.text.strip() if param.text else ""

            if not tool_name:
                raise ValueError("Tool name not found in response")

            return {
                "thought": thought,
                "tool_name": tool_name,
                "parameters": parameters,
            }
        except ET.ParseError as e:
            logger.error(f"Invalid XML response: {e}")
            return None
        except ValueError as e:
            logger.error(f"Error parsing response: {e}")
            return None

    def _process_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse the LLM response and execute the requested tool.
        
        Args:
            response: The LLM's response text
            
        Returns:
            Dictionary with tool execution results or None if no tool was called
        """
        try:
            # Parse the response to extract action and parameters
            parsed_response = self._parse_response(response)
            if not parsed_response:
                return None

            tool_name = parsed_response["tool_name"]
            parameters = parsed_response["parameters"]

            logger.info(f"\n--- Executing Tool ---")
            logger.info(f"Tool: {tool_name}")
            logger.info(f"Parameters: {json.dumps(parameters, indent=2)}")
            
            # Execute the tool
            result = self._execute_tool(tool_name, parameters)
            
            logger.info(f"Result: {json.dumps(result, indent=2)[:500]}...")
            logger.info(f"--- End Tool Execution ---\n")
            
            # Add observation to conversation history
            observation_text = f"<OBSERVATION>{json.dumps(result, indent=2)}</OBSERVATION>"
            self.conversation_history.append({
                "role": "user",
                "content": observation_text
            })
            
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return None
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        # Handle task_complete specially
        if tool_name == "task_complete":
            return {
                "success": True,
                "summary": parameters.get("summary", "Task completed")
            }

        # Check if the tool is from the MCP server
        mcp_tool_names = [tool['name'] for tool in self.mcp_tools]
        if self.mcp_tools_client and tool_name in mcp_tool_names:
            return self.mcp_tools_client.execute_mcp_tool(tool_name, parameters)

        # Get the tool method
        if not hasattr(self.tools, tool_name):
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

        tool_method = getattr(self.tools, tool_name)

        try:
            result = tool_method(**parameters)
            return result
        except TypeError as e:
            return {
                "success": False,
                "error": f"Invalid parameters for tool {tool_name}: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
