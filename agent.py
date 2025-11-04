"""
React Agent implementation for software development tasks.
Uses reasoning and acting in a loop with Claude LLM.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from tools import CodeRepositoryTools, get_available_tools

logger = logging.getLogger(__name__)


class ReactAgent:
    """
    A React (Reasoning + Acting) agent that uses LLM to autonomously
    complete software development tasks.
    """
    
    def __init__(self, api_key: str, repo_path: str = ".", max_iterations: int = 10):
        """
        Initialize the React agent.
        
        Args:
            api_key: Anthropic API key
            repo_path: Path to the code repository
            max_iterations: Maximum number of reasoning-action cycles
        """
        self.client = Anthropic(api_key=api_key)
        self.tools = CodeRepositoryTools(repo_path)
        self.max_iterations = max_iterations
        self.iteration_count = 0
        self.conversation_history = []
        self.is_complete = False
        
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
        tools_description = "\n\n".join([
            f"Tool: {tool['name']}\n"
            f"Description: {tool['description']}\n"
            f"Parameters: {json.dumps(tool['parameters'], indent=2)}"
            for tool in get_available_tools()
        ])
        
        prompt = f"""You are a software development agent that can interact with a code repository.
You follow the ReAct pattern: Reasoning + Acting.

For each step:
1. THINK: Reason about what you need to do next
2. ACT: Choose a tool to use and specify the parameters
3. OBSERVE: You'll receive the result of the tool execution

Available Tools:
{tools_description}

Instructions:
- Always start by exploring the repository to understand its structure
- Think step by step about what needs to be done
- Use the tools to read, search, and modify files as needed
- When you've completed the task, call the 'task_complete' tool with a summary
- Format your responses as:

THOUGHT: [Your reasoning about what to do next]
ACTION: [Tool name]
PARAMETERS: [JSON object with parameters]

Example:
THOUGHT: I need to see what files are in the repository first.
ACTION: list_files
PARAMETERS: {{"directory": "."}}

After you use a tool, I will respond with:
OBSERVATION: [Tool execution result]

Then you continue with your next THOUGHT/ACTION cycle.
"""
        return prompt
    
    def _call_llm(self, system_prompt: str) -> str:
        """
        Call the Claude LLM with the current conversation history.
        
        Args:
            system_prompt: The system prompt with instructions
            
        Returns:
            The LLM's response text
        """
        logger.info("\n--- Calling LLM ---")
        logger.debug(f"System prompt length: {len(system_prompt)} chars")
        logger.debug(f"Conversation history length: {len(self.conversation_history)} messages")
        
        # Log the last user message
        if self.conversation_history:
            last_message = self.conversation_history[-1]
            logger.info(f"Last message ({last_message['role']}): {last_message['content'][:200]}...")
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=system_prompt,
            messages=self.conversation_history
        )
        
        response_text = response.content[0].text
        
        logger.info(f"\n--- LLM Response ---")
        logger.info(response_text)
        logger.info(f"--- End LLM Response ---\n")
        
        # Add assistant's response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })
        
        return response_text
    
    def _process_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse the LLM response and execute the requested tool.
        
        Args:
            response: The LLM's response text
            
        Returns:
            Dictionary with tool execution results or None if no tool was called
        """
        try:
            # Parse the response to extract ACTION and PARAMETERS
            lines = response.strip().split('\n')
            action_line = None
            parameters_line = None
            
            for i, line in enumerate(lines):
                if line.startswith('ACTION:'):
                    action_line = line.replace('ACTION:', '').strip()
                elif line.startswith('PARAMETERS:'):
                    # Collect all lines that are part of the JSON parameters
                    parameters_text = line.replace('PARAMETERS:', '').strip()
                    # Look for multi-line JSON
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith(('THOUGHT:', 'ACTION:', 'OBSERVATION:')):
                        parameters_text += '\n' + lines[j]
                        j += 1
                    parameters_line = parameters_text
            
            if not action_line:
                logger.warning("No ACTION found in response, waiting for next iteration")
                return None
            
            tool_name = action_line
            parameters = {}
            
            if parameters_line:
                try:
                    # Try to parse as JSON
                    parameters = json.loads(parameters_line)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse parameters JSON: {e}")
                    logger.error(f"Parameters text: {parameters_line}")
                    
                    # Try to extract JSON using regex as fallback
                    import re
                    json_match = re.search(r'\{.*\}', parameters_line, re.DOTALL)
                    if json_match:
                        try:
                            parameters = json.loads(json_match.group())
                            logger.info("Successfully extracted JSON using regex fallback")
                        except json.JSONDecodeError:
                            logger.warning("Regex fallback also failed, using empty parameters")
                            parameters = {}
                    else:
                        parameters = {}
            
            logger.info(f"\n--- Executing Tool ---")
            logger.info(f"Tool: {tool_name}")
            logger.info(f"Parameters: {json.dumps(parameters, indent=2)}")
            
            # Execute the tool
            result = self._execute_tool(tool_name, parameters)
            
            logger.info(f"Result: {json.dumps(result, indent=2)[:500]}...")
            logger.info(f"--- End Tool Execution ---\n")
            
            # Add observation to conversation history
            observation_text = f"OBSERVATION: {json.dumps(result, indent=2)}"
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
