"""
This module provides a set of tools for the React agent to interact with
a code repository. These tools cover file system operations like listing,
reading, and writing files, as well as searching within files.
"""

import os
import subprocess
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class CodeRepositoryTools:
    """
    A collection of tools for searching and modifying code repositories.

    This class encapsulates methods that the agent can call to perform actions
    on the file system within a specified repository path. All methods return
    a dictionary with a 'success' flag and other relevant information.

    Attributes:
        repo_path (str): The absolute path to the code repository.
    """
    
    def __init__(self, repo_path: str = "."):
        """
        Initializes the CodeRepositoryTools.

        Args:
            repo_path (str): The file path to the code repository. Defaults to the
                             current working directory.
        """
        self.repo_path = os.path.abspath(repo_path)
        logger.info(f"Initialized CodeRepositoryTools with repo_path: {self.repo_path}")
    
    def list_files(self, directory: str = ".") -> Dict[str, Any]:
        """
        Lists all files in a specified directory, recursively.

        It skips common unnecessary directories like '.git', 'node_modules', etc.

        Args:
            directory (str): The directory to scan, relative to the repository root.

        Returns:
            A dictionary containing a list of file paths and their count.
        """
        try:
            full_path = os.path.join(self.repo_path, directory)
            files = []
            for root, dirs, filenames in os.walk(full_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
                for filename in filenames:
                    if not filename.startswith('.'):
                        rel_path = os.path.relpath(os.path.join(root, filename), self.repo_path)
                        files.append(rel_path)
            
            result = {
                "success": True,
                "files": files,
                "count": len(files)
            }
            logger.info(f"list_files: Found {len(files)} files in {directory}")
            return result
        except Exception as e:
            logger.error(f"list_files error: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """
        Reads the contents of a file.

        Args:
            filepath (str): The path to the file, relative to the repository root.

        Returns:
            A dictionary containing the file's content and line count.
        """
        try:
            full_path = os.path.join(self.repo_path, filepath)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = {
                "success": True,
                "filepath": filepath,
                "content": content,
                "lines": len(content.splitlines())
            }
            logger.info(f"read_file: Read {len(content)} characters from {filepath}")
            return result
        except Exception as e:
            logger.error(f"read_file error for {filepath}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e), "filepath": filepath}
    
    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """
        Writes content to a file, creating it if it doesn't exist.
        If the file exists, its content will be overwritten.

        Args:
            filepath (str): The path to the file, relative to the repository root.
            content (str): The content to write to the file.

        Returns:
            A dictionary indicating success and the number of bytes written.
        """
        try:
            full_path = os.path.join(self.repo_path, filepath)
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(full_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result = {
                "success": True,
                "filepath": filepath,
                "bytes_written": len(content.encode('utf-8'))
            }
            logger.info(f"write_file: Wrote {len(content)} characters to {filepath}")
            return result
        except Exception as e:
            logger.error(f"write_file error for {filepath}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e), "filepath": filepath}
    
    def search_in_files(self, pattern: str, file_extension: str = None) -> Dict[str, Any]:
        """
        Searches for a pattern in files using 'grep' (on Unix-like systems) for
        efficiency, with a Python-based fallback for cross-platform compatibility.

        Args:
            pattern (str): The search pattern.
            file_extension (str, optional): An optional file extension to filter the search.

        Returns:
            A dictionary with a list of matching lines.
        """
        try:
            import platform
            use_grep = platform.system() != 'Windows'
            
            if use_grep:
                try:
                    cmd = ["grep", "-r", "-n", "-i", pattern, self.repo_path]
                    if file_extension:
                        cmd.extend(["--include", f"*.{file_extension}"])
                    for exclude in ['.git', '__pycache__', 'node_modules', 'venv']:
                        cmd.extend(["--exclude-dir", exclude])
                    
                    result_proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
                    matches = [line for line in result_proc.stdout.strip().split('\n') if line]
                    
                    return {
                        "success": True,
                        "pattern": pattern,
                        "matches": matches,
                        "count": len(matches)
                    }
                except (subprocess.SubprocessError, FileNotFoundError):
                    use_grep = False # Fallback to Python search
            
            if not use_grep:
                matches = []
                pattern_lower = pattern.lower()
                for root, dirs, files in os.walk(self.repo_path):
                    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'venv']]
                    for filename in files:
                        if file_extension and not filename.endswith(f'.{file_extension}'):
                            continue
                        filepath = os.path.join(root, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                for line_num, line in enumerate(f, 1):
                                    if pattern_lower in line.lower():
                                        rel_path = os.path.relpath(filepath, self.repo_path)
                                        matches.append(f"{rel_path}:{line_num}:{line.strip()}")
                        except Exception:
                            continue
                return {
                    "success": True,
                    "pattern": pattern,
                    "matches": matches,
                    "count": len(matches)
                }
        except Exception as e:
            logger.error(f"search_in_files error: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e), "pattern": pattern}
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """
        Gets metadata about a file.

        Args:
            filepath (str): The path to the file, relative to the repository root.

        Returns:
            A dictionary with file metadata (size, existence, type).
        """
        try:
            full_path = os.path.join(self.repo_path, filepath)
            if not os.path.exists(full_path):
                return {"success": False, "error": "File does not exist", "filepath": filepath}
            
            stat = os.stat(full_path)
            return {
                "success": True,
                "filepath": filepath,
                "size": stat.st_size,
                "exists": True,
                "is_file": os.path.isfile(full_path),
                "is_dir": os.path.isdir(full_path)
            }
        except Exception as e:
            logger.error(f"get_file_info error for {filepath}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e), "filepath": filepath}


def get_available_tools() -> List[Dict[str, Any]]:
    """
    Returns a list of available tools with their descriptions for the LLM.

    This function provides the schema that the LLM uses to understand how to
    call the available tools, including their names, descriptions, and parameters.

    Returns:
        A list of dictionaries, each describing a tool.
    """
    return [
        {
            "name": "list_files",
            "description": "Recursively lists all files in a directory. Use '.' for the repository root.",
            "parameters": {
                "directory": "string (optional, default='.') - The directory to list files from."
            }
        },
        {
            "name": "read_file",
            "description": "Reads the entire content of a specified file.",
            "parameters": {
                "filepath": "string (required) - The relative path of the file from the repository root."
            }
        },
        {
            "name": "write_file",
            "description": "Writes content to a file, creating it if it doesn't exist or overwriting it if it does.",
            "parameters": {
                "filepath": "string (required) - The relative path of the file to write to.",
                "content": "string (required) - The new content for the file."
            }
        },
        {
            "name": "search_in_files",
            "description": "Searches for a pattern in files and returns the matching lines.",
            "parameters": {
                "pattern": "string (required) - The text pattern to search for.",
                "file_extension": "string (optional) - The extension of files to search in (e.g., 'py', 'js')."
            }
        },
        {
            "name": "get_file_info",
            "description": "Retrieves metadata about a file, such as its size and type.",
            "parameters": {
                "filepath": "string (required) - The relative path of the file."
            }
        },
        {
            "name": "task_complete",
            "description": "Call this tool when the assigned task is fully completed.",
            "parameters": {
                "summary": "string (required) - A brief summary of what was accomplished."
            }
        }
    ]
