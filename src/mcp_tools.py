"""
This module provides tools for interacting with an MCP (Model Context Protocol)
server, allowing the agent to discover and execute remote tools.
"""

import requests
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class McpTools:
    """
    Handles fetching and executing tools from an MCP server.

    This class provides a client for an MCP server, enabling the agent to
    dynamically load and use tools that are not part of its local toolset.

    Attributes:
        server_url (str): The base URL of the MCP server.
    """

    def __init__(self, server_url: str):
        """
        Initializes the McpTools client.

        Args:
            server_url (str): The base URL of the MCP server.
        """
        if not server_url.endswith('/'):
            server_url += '/'
        self.server_url = server_url
        logger.info(f"Initialized McpTools with server_url: {self.server_url}")

    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Gets the list of available tools from the MCP server.

        This method makes a GET request to the /tools endpoint of the server
        to retrieve the schema for all available remote tools.

        Returns:
            A list of dictionaries, each describing a remote tool. Returns an
            empty list if the request fails.
        """
        try:
            response = requests.get(f"{self.server_url}tools")
            response.raise_for_status()
            tools = response.json()
            logger.info(f"Fetched {len(tools)} tools from MCP server: {self.server_url}")
            return tools
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching tools from MCP server: {e}")
            return []
        except ValueError:
            logger.error(f"Error parsing JSON response from MCP server.")
            return []

    def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a tool on the MCP server.

        This method sends a POST request to the /execute/{tool_name} endpoint
        of the server with the tool's parameters in the request body.

        Args:
            tool_name (str): The name of the tool to execute.
            parameters (dict): The parameters for the tool.

        Returns:
            The result of the tool execution as a dictionary.
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
        except ValueError:
            logger.error(f"Error parsing JSON response from MCP tool execution.")
            return {"success": False, "error": "Invalid JSON response from server."}
