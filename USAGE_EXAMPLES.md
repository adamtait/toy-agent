# Usage Examples

This document provides practical examples of using the React agent for various software development tasks.

## Setup

First, ensure you have set up your environment:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Example 1: Create a Simple Python Script

```bash
python main.py --task "Create a hello.py file that prints 'Hello World'"
```

**Expected behavior:**
- Agent lists existing files
- Creates hello.py with the requested content
- Verifies the file was created
- Marks task as complete

## Example 2: Add a Function to a File

```bash
python main.py --task "Create a utils.py file with a function that calculates factorial"
```

**Expected behavior:**
- Agent creates utils.py
- Implements a factorial function
- May include docstring and proper error handling
- Marks task as complete

## Example 3: Search and Modify

```bash
python main.py --task "Find all Python files and add a docstring to any that don't have one"
```

**Expected behavior:**
- Agent searches for .py files
- Reads each file to check for docstrings
- Adds appropriate docstrings where missing
- Reports what was modified

## Example 4: Code Organization

```bash
python main.py --task "Create a proper project structure with src/, tests/, and docs/ directories"
```

**Expected behavior:**
- Agent creates the directory structure
- May add appropriate files (README, __init__.py, etc.)
- Verifies the structure was created
- Marks task as complete

## Example 5: Debug Mode with Detailed Logging

```bash
python main.py \
  --task "Create a calculator.py with basic math operations" \
  --log-level DEBUG \
  --log-file logs/calculator_task.log
```

**Expected behavior:**
- Detailed logging to both console and file
- Shows full system prompts
- Shows detailed tool execution
- Saves complete log for later analysis

## Example 6: Working with a Specific Repository

```bash
python main.py \
  --task "Add error handling to all functions in the main module" \
  --repo /path/to/my/project \
  --max-iterations 15
```

**Expected behavior:**
- Agent works in specified directory
- Reads existing code
- Identifies functions without error handling
- Adds appropriate try-catch blocks
- More iterations available for complex task

## Understanding the Output

### Successful Run

```
================================================================================
React Agent for Software Development
================================================================================
Task: Create a hello.py file that prints 'Hello World'
Repository: /home/user/toy-agent
Max iterations: 10
Log level: INFO
================================================================================

================================================================================
ITERATION 1/10
================================================================================

--- Calling LLM ---
...

--- LLM Response ---
THOUGHT: I need to first check what files exist in the repository...
ACTION: list_files
PARAMETERS: {"directory": "."}
--- End LLM Response ---

--- Executing Tool ---
Tool: list_files
Parameters: {
  "directory": "."
}
Result: {"success": true, "files": [...], "count": 3}
--- End Tool Execution ---

[... more iterations ...]

Task completed! Summary: Created hello.py file with print statement

================================================================================
FINAL RESULT
================================================================================
Success: True
Iterations used: 3/10
Conversation length: 7 messages
================================================================================
```

### Failed or Incomplete Run

```
================================================================================
Agent reached maximum iterations without completing the task
================================================================================
```

This means the task was too complex for the iteration limit. Try:
- Increasing `--max-iterations`
- Breaking the task into smaller subtasks
- Simplifying the task description

## Tips for Writing Good Tasks

### ✅ Good Task Descriptions

1. **Specific and actionable:**
   ```
   "Create a file named config.py with a dictionary containing database settings"
   ```

2. **Clear objectives:**
   ```
   "Add input validation to the login function in auth.py"
   ```

3. **Measurable outcomes:**
   ```
   "Create unit tests for all functions in utils.py with at least 80% coverage"
   ```

### ❌ Avoid Vague Tasks

1. **Too vague:**
   ```
   "Make the code better"
   ```

2. **Too broad:**
   ```
   "Refactor the entire application"
   ```

3. **Ambiguous:**
   ```
   "Fix the bug"
   ```
   (Better: "Fix the IndexError in process_data() function")

## Advanced Usage

### Chaining Tasks

Run multiple related tasks in sequence:

```bash
# Task 1: Create structure
python main.py --task "Create a src/ directory with __init__.py"

# Task 2: Add main module
python main.py --task "Create src/main.py with a main() function"

# Task 3: Add tests
python main.py --task "Create tests/test_main.py with basic tests"
```

### Continuous Logging

Keep a persistent log of all agent runs:

```bash
# All runs append to the same log file
python main.py --task "Task 1" --log-file logs/agent.log
python main.py --task "Task 2" --log-file logs/agent.log
python main.py --task "Task 3" --log-file logs/agent.log
```

### Custom Repository Workflows

```bash
# Work on feature branch
cd /path/to/project
git checkout -b feature/new-feature

# Run agent on specific files
python /path/to/toy-agent/main.py \
  --task "Add type hints to all functions in src/api.py" \
  --repo .

# Review changes
git diff

# Commit if satisfied
git commit -am "Add type hints to API module"
```

## Monitoring and Debugging

### Enable Debug Logging

```bash
python main.py --task "Your task" --log-level DEBUG
```

This shows:
- Full system prompts sent to LLM
- Detailed parameter parsing
- File operation internals
- HTTP request details (Anthropic API)

### Save Logs for Analysis

```bash
python main.py \
  --task "Complex refactoring task" \
  --log-file logs/$(date +%Y%m%d_%H%M%S)_refactor.log
```

Creates timestamped log files for each run.

### Watch Agent Progress

In another terminal:
```bash
tail -f logs/agent.log
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"

**Solution:** Create a .env file with your API key:
```bash
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Agent Reaches Max Iterations

**Solutions:**
1. Increase iterations: `--max-iterations 20`
2. Simplify the task
3. Check logs to see where it's stuck
4. Break into smaller subtasks

### Tool Execution Fails

**Common causes:**
- File permissions issues
- Invalid file paths
- Directory doesn't exist

**Solution:** Check logs at DEBUG level to see exact error:
```bash
python main.py --task "Your task" --log-level DEBUG
```

### Agent Not Making Progress

**Symptoms:** Repeating the same actions

**Solutions:**
1. Make task more specific
2. Check if files already exist (agent may be confused)
3. Review the LLM responses in logs
4. Simplify the environment (fewer existing files)

## Performance Considerations

### Iteration Count
- Simple tasks: 3-5 iterations
- Medium tasks: 5-10 iterations
- Complex tasks: 10-20 iterations

### API Costs
Each iteration makes one API call to Claude. For cost efficiency:
- Be specific in task descriptions
- Use appropriate `--max-iterations`
- Test with simple tasks first

### File System Operations
- Large repositories may slow down search operations
- Consider working in subdirectories for large projects
- Use specific file patterns in task descriptions

## Best Practices

1. **Start simple:** Test with basic tasks before complex ones
2. **Use version control:** Always work in a git repository
3. **Review changes:** Check agent's modifications before committing
4. **Save logs:** Keep logs for debugging and learning
5. **Iterate:** Refine task descriptions based on results
6. **Monitor progress:** Watch logs during execution
7. **Set appropriate limits:** Choose max-iterations based on task complexity

## Example Session

Here's a complete session showing agent in action:

```bash
$ python main.py --task "Create a fibonacci.py with a function to calculate fibonacci numbers"

2025-11-04 01:00:00,000 - __main__ - INFO - ================================================================================
2025-11-04 01:00:00,000 - __main__ - INFO - React Agent for Software Development
2025-11-04 01:00:00,000 - __main__ - INFO - ================================================================================
2025-11-04 01:00:00,001 - agent - INFO - ================================================================================
2025-11-04 01:00:00,001 - agent - INFO - ITERATION 1/10
2025-11-04 01:00:00,001 - agent - INFO - ================================================================================
2025-11-04 01:00:00,500 - agent - INFO - --- LLM Response ---
2025-11-04 01:00:00,500 - agent - INFO - THOUGHT: I need to create a Python file with a fibonacci function...
2025-11-04 01:00:00,500 - agent - INFO - ACTION: write_file
2025-11-04 01:00:00,501 - tools - INFO - write_file: Wrote 234 characters to fibonacci.py
2025-11-04 01:00:00,501 - agent - INFO - ================================================================================
2025-11-04 01:00:00,501 - agent - INFO - ITERATION 2/10
2025-11-04 01:00:00,501 - agent - INFO - ================================================================================
2025-11-04 01:00:00,800 - agent - INFO - --- LLM Response ---
2025-11-04 01:00:00,800 - agent - INFO - THOUGHT: Let me verify the file was created correctly...
2025-11-04 01:00:00,800 - agent - INFO - ACTION: read_file
2025-11-04 01:00:00,801 - tools - INFO - read_file: Read 234 characters from fibonacci.py
2025-11-04 01:00:00,801 - agent - INFO - ================================================================================
2025-11-04 01:00:00,801 - agent - INFO - ITERATION 3/10
2025-11-04 01:00:00,801 - agent - INFO - ================================================================================
2025-11-04 01:00:01,100 - agent - INFO - --- LLM Response ---
2025-11-04 01:00:01,100 - agent - INFO - THOUGHT: The file is created with the fibonacci function. Task complete.
2025-11-04 01:00:01,100 - agent - INFO - ACTION: task_complete
2025-11-04 01:00:01,100 - agent - INFO - Task completed! Summary: Created fibonacci.py with recursive fibonacci function
2025-11-04 01:00:01,100 - __main__ - INFO - ================================================================================
2025-11-04 01:00:01,100 - __main__ - INFO - FINAL RESULT
2025-11-04 01:00:01,100 - __main__ - INFO - ================================================================================
2025-11-04 01:00:01,100 - __main__ - INFO - Success: True
2025-11-04 01:00:01,100 - __main__ - INFO - Iterations used: 3/10
2025-11-04 01:00:01,100 - __main__ - INFO - ================================================================================

$ cat fibonacci.py
def fibonacci(n):
    """Calculate the nth fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

if __name__ == "__main__":
    print(fibonacci(10))
```

## Next Steps

After getting comfortable with basic usage:
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how it works
2. Try more complex tasks
3. Experiment with different task descriptions
4. Consider extending the agent with new tools
5. Integrate into your development workflow
