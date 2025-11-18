import requests
import json
import logging

def get_remote_tool_schemas(mcp_server_url):
    """
    Fetches tool schemas from a remote MCP server.
    """
    if not mcp_server_url:
        return []
    try:
        response = requests.get(f"{mcp_server_url}/tools")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Could not fetch remote tool schemas from {mcp_server_url}: {e}")
        return []

def execute_remote_tool(mcp_server_url, tool_name, params):
    """
    Executes a tool on a remote MCP server.
    """
    if not mcp_server_url:
        return {"success": False, "error": "MCP server URL not configured."}
    try:
        response = requests.post(f"{mcp_server_url}/tools/{tool_name}/execute", json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Could not execute remote tool '{tool_name}' on {mcp_server_url}: {e}")
        return {"success": False, "error": str(e)}
