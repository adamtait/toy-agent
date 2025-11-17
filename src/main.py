#!/usr/bin/env python3
"""
Main entry point for the React Agent.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv
from .agent import ReactAgent
from .llm import ClaudeLlmClient, GeminiLlmClient


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to write logs to
    """
    # Create logs directory if logging to file
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:  # Only create directory if log_file includes a directory
            os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Set up handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    # Also set up logging for the anthropic and google libraries
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google.generativeai").setLevel(logging.WARNING)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="React Agent for Software Development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with Claude
  python main.py --task "Create a hello.py file"

  # Run with Gemini
  python main.py --task "Create a hello.py file" --llm-provider gemini
  
  # Run with custom repository path and logging
  python main.py --task "Add a function to utils.py" --repo /path/to/repo --log-level DEBUG
"""
    )
    
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="The task for the agent to complete"
    )
    
    parser.add_argument(
        "--repo",
        type=str,
        default=".",
        help="Path to the code repository (default: current directory)"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum number of reasoning-action cycles (default: 10)"
    )
    
    parser.add_argument(
        "--llm-provider",
        type=str,
        default="claude",
        choices=["claude", "gemini"],
        help="The LLM provider to use (default: claude)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Optional file to write logs to"
    )

    parser.add_argument(
        "--mcp-server",
        type=str,
        default=None,
        help="URL of the MCP server"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key and initialize LLM client
    llm_client = None
    if args.llm_provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not found for Claude provider")
            sys.exit(1)
        llm_client = ClaudeLlmClient(api_key)
    elif args.llm_provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found for Gemini provider")
            sys.exit(1)
        llm_client = GeminiLlmClient(api_key)
    
    logger.info("="*80)
    logger.info("React Agent for Software Development")
    logger.info("="*80)
    logger.info(f"Task: {args.task}")
    logger.info(f"Repository: {os.path.abspath(args.repo)}")
    logger.info(f"LLM Provider: {args.llm_provider}")
    logger.info(f"Max iterations: {args.max_iterations}")
    logger.info(f"Log level: {args.log_level}")
    if args.log_file:
        logger.info(f"Log file: {args.log_file}")
    logger.info("="*80)
    
    # Create and run the agent
    agent = ReactAgent(
        llm_client=llm_client,
        repo_path=args.repo,
        max_iterations=args.max_iterations,
        mcp_server_url=args.mcp_server
    )
    
    try:
        result = agent.run(args.task)
        
        logger.info("\n" + "="*80)
        logger.info("FINAL RESULT")
        logger.info("="*80)
        logger.info(f"Success: {result['success']}")
        logger.info(f"Iterations used: {result['iterations']}/{args.max_iterations}")
        logger.info(f"Conversation length: {result['conversation_length']} messages")
        
        if result['max_iterations_reached'] and not result['success']:
            logger.warning("Agent reached maximum iterations without completing the task")
            sys.exit(1)
        
        logger.info("="*80)
        
    except KeyboardInterrupt:
        logger.info("\nAgent interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Agent failed with error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
