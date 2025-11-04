import os
import json

def list_files(path='.'):
    """Lists all files and directories under the given directory."""
    return json.dumps(os.listdir(path))

def read_file(filepath):
    """Reads the content of the specified file in the repo."""
    with open(filepath, 'r') as f:
        return f.read()

def replace_with_git_merge_diff(filepath, merge_diff):
    """Performs a targeted search-and-replace to modify an existing file. The format is a Git merge diff."""
    with open(filepath, 'r') as f:
        original_content = f.read()

    lines = merge_diff.split('\n')
    search_lines = []
    replace_lines = []
    in_search_block = False
    in_replace_block = False

    for line in lines:
        if line.startswith('<<<<<<< SEARCH'):
            in_search_block = True
            continue
        if line.startswith('======='):
            in_search_block = False
            in_replace_block = True
            continue
        if line.startswith('>>>>>>> REPLACE'):
            in_replace_block = False
            continue
        if in_search_block:
            search_lines.append(line)
        if in_replace_block:
            replace_lines.append(line)

    search_content = '\n'.join(search_lines)
    replace_content = '\n'.join(replace_lines)

    new_content = original_content.replace(search_content, replace_content, 1)

    with open(filepath, 'w') as f:
        f.write(new_content)

    return f"Successfully modified {filepath}"

def finish(message):
    """Signals that the agent has completed the task."""
    return {"finish": True, "message": message}

tools = [
    {
        "name": "list_files",
        "description": "Lists all files and directories under the given directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory path to list files from. Defaults to the root of the repo.",
                },
            },
        },
    },
    {
        "name": "read_file",
        "description": "Reads the content of the specified file in the repo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path of the file to read, relative to the repo root.",
                },
            },
            "required": ["filepath"],
        },
    },
    {
        "name": "replace_with_git_merge_diff",
        "description": "Performs a targeted search-and-replace to modify an existing file. The format is a Git merge diff.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path of the file to modify.",
                },
                "merge_diff": {
                    "type": "string",
                    "description": "The diff to apply to the file.",
                },
            },
            "required": ["filepath", "merge_diff"],
        },
    },
    {
        "name": "finish",
        "description": "Signals that the agent has completed the task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "A message to the user indicating that the task is complete.",
                },
            },
        },
    },
]

tool_functions = {
    "list_files": list_files,
    "read_file": read_file,
    "replace_with_git_merge_diff": replace_with_git_merge_diff,
    "finish": finish,
}

def execute_tool(tool_name, tool_input):
    if tool_name in tool_functions:
        try:
            return tool_functions[tool_name](**tool_input)
        except Exception as e:
            return f"Error executing tool {tool_name}: {e}"
    else:
        return f"Unknown tool: {tool_name}"
