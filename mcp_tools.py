"""
Tools for interacting with an MCP server.
"""

import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class McpTools:
    """
    Handles fetching and executing tools from an MCP server.
    """

    def __init__(self, server_url: str):
        """
        Initialize the McpTools client.

        Args:
            server_url: The base URL of the MCP server.
        """
        if not server_url.endswith('/'):
            server_url += '/'
        self.server_url = server_url
        logger.info(f"Initialized McpTools with server_url: {self.server_url}")

    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Get the list of available tools from the MCP server.
        """
        try:
            response = requests.get(f"{self.server_url}tools")
            response.raise_for_status()  # Raise an exception for bad status codes
            tools = response.json()
            logger.info(f"Fetched {len(tools)} tools from MCP server: {self.server_url}")
            return tools
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching tools from MCP server: {e}")
            return []
        except ValueError as e:
            logger.error(f"Error parsing JSON response from MCP server: {e}")
            return []

    def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool on the MCP server.

        Args:
            tool_name: The name of the tool to execute.
            parameters: The parameters for the tool.

        Returns:
            The result of the tool execution.
        """
        try:
            url = f"{self.server_url}execute/{tool_name}"
            response = requests.post(url, json=parameters)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Executed MCP tool '{tool_name}' with parameters {parameters}")
            logger.debug(f"MCP tool result: {result}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Error executing MCP tool '{tool_name}': {e}")
            return {"success": False, "error": str(e)}
        except ValueError as e:
            logger.error(f"Error parsing JSON response from MCP tool execution: {e}")
            return {"success": False, "error": "Invalid JSON response from server."}
