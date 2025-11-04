"""
Tools for the React agent to interact with code repositories.
"""

import os
import subprocess
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class CodeRepositoryTools:
    """CLI tools for searching and modifying code repositories."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        logger.info(f"Initialized CodeRepositoryTools with repo_path: {self.repo_path}")
    
    def list_files(self, directory: str = ".") -> Dict[str, Any]:
        """List all files in a directory."""
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
            logger.error(f"list_files error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read the contents of a file."""
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
            logger.error(f"read_file error for {filepath}: {str(e)}")
            return {"success": False, "error": str(e), "filepath": filepath}
    
    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            full_path = os.path.join(self.repo_path, filepath)
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
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
            logger.error(f"write_file error for {filepath}: {str(e)}")
            return {"success": False, "error": str(e), "filepath": filepath}
    
    def search_in_files(self, pattern: str, file_extension: str = None) -> Dict[str, Any]:
        """Search for a pattern in files using grep."""
        try:
            cmd = ["grep", "-r", "-n", "-i", pattern, self.repo_path]
            
            # Add file extension filter if specified
            if file_extension:
                cmd.extend(["--include", f"*.{file_extension}"])
            
            # Exclude common directories
            for exclude in ['.git', '__pycache__', 'node_modules', 'venv']:
                cmd.extend(["--exclude-dir", exclude])
            
            result_proc = subprocess.run(cmd, capture_output=True, text=True)
            
            matches = []
            if result_proc.stdout:
                for line in result_proc.stdout.strip().split('\n'):
                    if line:
                        matches.append(line)
            
            result = {
                "success": True,
                "pattern": pattern,
                "matches": matches,
                "count": len(matches)
            }
            logger.info(f"search_in_files: Found {len(matches)} matches for pattern '{pattern}'")
            return result
        except Exception as e:
            logger.error(f"search_in_files error: {str(e)}")
            return {"success": False, "error": str(e), "pattern": pattern}
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """Get information about a file."""
        try:
            full_path = os.path.join(self.repo_path, filepath)
            
            if not os.path.exists(full_path):
                return {"success": False, "error": "File does not exist", "filepath": filepath}
            
            stat = os.stat(full_path)
            
            result = {
                "success": True,
                "filepath": filepath,
                "size": stat.st_size,
                "exists": True,
                "is_file": os.path.isfile(full_path),
                "is_dir": os.path.isdir(full_path)
            }
            logger.info(f"get_file_info: Retrieved info for {filepath}")
            return result
        except Exception as e:
            logger.error(f"get_file_info error for {filepath}: {str(e)}")
            return {"success": False, "error": str(e), "filepath": filepath}


def get_available_tools() -> List[Dict[str, Any]]:
    """Get list of available tools with their descriptions for the LLM."""
    return [
        {
            "name": "list_files",
            "description": "List all files in a directory. Use '.' for the root of the repository.",
            "parameters": {
                "directory": "string (optional, default='.')"
            }
        },
        {
            "name": "read_file",
            "description": "Read the contents of a file. Provide the relative path from repository root.",
            "parameters": {
                "filepath": "string (required)"
            }
        },
        {
            "name": "write_file",
            "description": "Write content to a file. Creates the file if it doesn't exist.",
            "parameters": {
                "filepath": "string (required)",
                "content": "string (required)"
            }
        },
        {
            "name": "search_in_files",
            "description": "Search for a pattern in files using grep. Returns matching lines with file paths and line numbers.",
            "parameters": {
                "pattern": "string (required)",
                "file_extension": "string (optional, e.g., 'py', 'js')"
            }
        },
        {
            "name": "get_file_info",
            "description": "Get information about a file (size, existence, type).",
            "parameters": {
                "filepath": "string (required)"
            }
        },
        {
            "name": "task_complete",
            "description": "Call this when the task is complete. Provide a summary of what was accomplished.",
            "parameters": {
                "summary": "string (required)"
            }
        }
    ]
