import os
import glob
import json

def list_files(directory="."):
    """Recursively lists all files in a directory."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return {"success": True, "files": files, "count": len(files)}

def read_file(filepath):
    """Reads the content of a file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}

def write_file(filepath, content):
    """Writes content to a file."""
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return {"success": True, "message": f"File '{filepath}' written successfully."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def task_complete(summary):
    """Signals that the task is finished."""
    return {"success": True, "summary": summary, "task_complete": True}

def get_tool_schemas():
    """Returns the schemas for all available tools."""
    return [
        {
            "name": "list_files",
            "description": "Recursively lists all files in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The directory to list files from. Defaults to the current directory."
                    }
                },
                "required": []
            }
        },
        {
            "name": "read_file",
            "description": "Reads the content of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path to the file to read."
                    }
                },
                "required": ["filepath"]
            }
        },
        {
            "name": "write_file",
            "description": "Writes content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path to the file to write to."
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file."
                    }
                },
                "required": ["filepath", "content"]
            }
        },
        {
            "name": "task_complete",
            "description": "Signals that the task is finished.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "A summary of the work done."
                    }
                },
                "required": ["summary"]
            }
        }
    ]

# For standalone testing
if __name__ == '__main__':
    print("--- Tool Schemas ---")
    print(json.dumps(get_tool_schemas(), indent=2))

    print("\n--- Testing list_files ---")
    print(list_files("src"))

    print("\n--- Testing write_file and read_file ---")
    write_file("test.txt", "Hello, world!")
    print(read_file("test.txt"))
    os.remove("test.txt")
