#!/usr/bin/env python3
"""
Example test to demonstrate the agent's functionality without requiring an API key.
This tests the tool execution and agent structure.
"""

import logging
from src.tools import CodeRepositoryTools, get_available_tools

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_tools():
    """Test the code repository tools."""
    logger.info("="*80)
    logger.info("Testing Code Repository Tools")
    logger.info("="*80)
    
    # Create a test directory
    import os
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info(f"\nTest directory: {tmpdir}")
        
        tools = CodeRepositoryTools(tmpdir)
        
        # Test 1: List files (empty directory)
        logger.info("\n--- Test 1: List files in empty directory ---")
        result = tools.list_files()
        logger.info(f"Result: {result}")
        assert result['success'] == True
        assert result['count'] == 0
        
        # Test 2: Write a file
        logger.info("\n--- Test 2: Write a file ---")
        result = tools.write_file("test.py", "print('Hello, World!')\n")
        logger.info(f"Result: {result}")
        assert result['success'] == True
        
        # Test 3: Read the file
        logger.info("\n--- Test 3: Read the file ---")
        result = tools.read_file("test.py")
        logger.info(f"Result: {result}")
        assert result['success'] == True
        assert "Hello, World!" in result['content']
        
        # Test 4: List files (should find the file now)
        logger.info("\n--- Test 4: List files again ---")
        result = tools.list_files()
        logger.info(f"Result: {result}")
        assert result['success'] == True
        assert result['count'] == 1
        
        # Test 5: Get file info
        logger.info("\n--- Test 5: Get file info ---")
        result = tools.get_file_info("test.py")
        logger.info(f"Result: {result}")
        assert result['success'] == True
        assert result['exists'] == True
        
        # Test 6: Search in files
        logger.info("\n--- Test 6: Search in files ---")
        result = tools.search_in_files("Hello")
        logger.info(f"Result: {result}")
        assert result['success'] == True
        
        logger.info("\n" + "="*80)
        logger.info("All tool tests passed!")
        logger.info("="*80)


def test_available_tools():
    """Test that all tools are properly documented."""
    logger.info("\n" + "="*80)
    logger.info("Testing Available Tools Documentation")
    logger.info("="*80)
    
    tools = get_available_tools()
    logger.info(f"\nFound {len(tools)} available tools:")
    
    for tool in tools:
        logger.info(f"\n  Tool: {tool['name']}")
        logger.info(f"  Description: {tool['description']}")
        logger.info(f"  Parameters: {tool['parameters']}")
    
    assert len(tools) == 6  # Should have 6 tools
    tool_names = [t['name'] for t in tools]
    assert 'list_files' in tool_names
    assert 'read_file' in tool_names
    assert 'write_file' in tool_names
    assert 'search_in_files' in tool_names
    assert 'get_file_info' in tool_names
    assert 'task_complete' in tool_names
    
    logger.info("\n" + "="*80)
    logger.info("Tool documentation test passed!")
    logger.info("="*80)


def test_agent_structure():
    """Test that the agent can be imported and initialized (without API key)."""
    logger.info("\n" + "="*80)
    logger.info("Testing Agent Structure")
    logger.info("="*80)
    
    # Test imports
    try:
        from src.agent import ReactAgent
        logger.info("✓ Agent module imported successfully")
    except ImportError as e:
        logger.error(f"✗ Failed to import agent module: {e}")
        raise
    
    logger.info("\n" + "="*80)
    logger.info("Agent structure test passed!")
    logger.info("="*80)


if __name__ == "__main__":
    try:
        test_available_tools()
        test_tools()
        test_agent_structure()
        
        logger.info("\n" + "="*80)
        logger.info("ALL TESTS PASSED!")
        logger.info("="*80)
        logger.info("\nThe React agent is ready to use.")
        logger.info("To run with real tasks, set ANTHROPIC_API_KEY in .env and use:")
        logger.info('  python main.py --task "Your task here"')
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\n✗ Test failed: {e}", exc_info=True)
        exit(1)
