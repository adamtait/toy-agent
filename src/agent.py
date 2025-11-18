import logging
import json
import xml.etree.ElementTree as ET
import os
from src import tools
from src import mcp_tools

class ReactAgent:
    def __init__(self, task, repo, max_iterations, llm_client, mcp_server=None):
        self.task = task
        self.repo = repo
        self.max_iterations = max_iterations
        self.llm_client = llm_client
        self.mcp_server = mcp_server
        self.conversation_history = []
        self.local_tools = {
            "list_files": tools.list_files,
            "read_file": tools.read_file,
            "write_file": tools.write_file,
            "task_complete": tools.task_complete,
        }
        self.remote_tool_schemas = mcp_tools.get_remote_tool_schemas(self.mcp_server)

    def run(self):
        logging.info("Starting ReAct agent run...")

        # Change to the specified repository directory
        if self.repo != ".":
            try:
                os.chdir(self.repo)
                logging.info(f"Changed working directory to: {self.repo}")
            except FileNotFoundError:
                logging.error(f"Repository directory not found: {self.repo}")
                return False

        self._initialize_conversation()

        for i in range(self.max_iterations):
            logging.info(f"--- Iteration {i+1}/{self.max_iterations} ---")

            # 1. Get LLM completion
            llm_response = self.llm_client.get_completion(self.conversation_history)
            logging.info(f"LLM Response:\n{llm_response}")

            # 2. Parse LLM response
            try:
                thought, tool_name, params = self._parse_llm_response(llm_response)
            except Exception as e:
                logging.error(f"Error parsing LLM response: {e}")
                self.conversation_history.append({"role": "user", "content": f"OBSERVATION: Invalid XML format. Please use the specified XML format."})
                continue

            self.conversation_history.append({"role": "assistant", "content": llm_response})

            # 3. Execute tool
            tool_result = self._execute_tool(tool_name, params)
            logging.info(f"Tool Result: {tool_result}")

            if tool_result.get("task_complete"):
                logging.info(f"Task completed: {tool_result.get('summary')}")
                print(f"Task completed: {tool_result.get('summary')}")
                return True

            self.conversation_history.append({"role": "user", "content": f"OBSERVATION: {json.dumps(tool_result)}"})

        logging.warning("Agent reached maximum iterations without completing the task.")
        print("Agent reached maximum iterations without completing the task.")
        return False

    def _initialize_conversation(self):
        system_prompt = self._construct_system_prompt()
        self.conversation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"The user wants me to perform the following task: {self.task}"}
        ]

    def _construct_system_prompt(self):
        tool_schemas = tools.get_tool_schemas() + self.remote_tool_schemas
        prompt = (
            "You are a helpful AI assistant that can write and edit code in a git repository.\n"
            "You are running in a loop of Thought, Action, Observation.\n"
            "At each step, you will be given a task to perform.\n"
            "You should first think about the task and then choose a tool to use.\n"
            "You will be given the result of the tool's execution as an observation.\n"
            "You can then continue with the next step.\n\n"
            "You must output your response in the following XML format:\n"
            "<response>\n"
            "  <thought>Your thought process goes here.</thought>\n"
            "  <action>\n"
            "    <tool_name>tool_name_here</tool_name>\n"
            "    <parameters>\n"
            "      <param_name>param_value</param_name>\n"
            "    </parameters>\n"
            "  </action>\n"
            "</response>\n\n"
            "Here are the available tools:\n"
        )
        for schema in tool_schemas:
            prompt += f"- {schema['name']}: {schema['description']}\n"
            prompt += f"  Parameters: {json.dumps(schema['parameters'], indent=2)}\n"
        return prompt

    def _parse_llm_response(self, response):
        root = ET.fromstring(response)
        thought = root.find("thought").text.strip()
        tool_name = root.find("action/tool_name").text.strip()
        params = {}
        for param in root.findall("action/parameters/*"):
            params[param.tag] = param.text.strip() if param.text else ""
        return thought, tool_name, params

    def _execute_tool(self, tool_name, params):
        if tool_name in self.local_tools:
            try:
                return self.local_tools[tool_name](**params)
            except Exception as e:
                return {"success": False, "error": f"Error executing tool '{tool_name}': {e}"}
        elif any(tool['name'] == tool_name for tool in self.remote_tool_schemas):
            return mcp_tools.execute_remote_tool(self.mcp_server, tool_name, params)
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
