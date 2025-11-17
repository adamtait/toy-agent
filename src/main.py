#!/usr/bin/env python3
"""
Main entry point for the React Agent.

This script initializes and runs the React Agent based on command-line arguments.
It handles argument parsing, logging setup, environment variable loading,
and initialization of the appropriate LLM client.
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
    Set up logging configuration for the application.

    This function configures a root logger that streams to stdout and optionally
    to a file. It also sets the logging level for third-party libraries to WARNING
    to reduce verbosity.

    Args:
        log_level (str): The desired logging level (e.g., "DEBUG", "INFO").
        log_file (str, optional): A path to a file where logs should be written.
                                  If None, logs are only sent to stdout.
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

    # Reduce noise from third-party libraries
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google.generativeai").setLevel(logging.WARNING)


def main():
    """
    Main entry point for the script.

    Parses command-line arguments, initializes the LLM client and the ReactAgent,
    and starts the agent's execution loop.
    """
    parser = argparse.ArgumentParser(
        description="React Agent for Software Development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with Claude and a simple task
  python main.py --task "Create a hello.py file"

  # Run with Gemini, specifying a different repository and logging level
  python main.py --task "Add a function to utils.py" --llm-provider gemini --repo /path/to/repo --log-level DEBUG

  # Run with an MCP server to load remote tools
  python main.py --task "Run a security scan" --mcp-server http://localhost:8000
"""
    )

    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="The software development task for the agent to complete."
    )

    parser.add_argument(
        "--repo",
        type=str,
        default=".",
        help="The file path to the code repository the agent should work on. Defaults to the current directory."
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="The maximum number of reasoning-action cycles the agent can perform. Defaults to 10."
    )

    parser.add_argument(
        "--llm-provider",
        type=str,
        default="claude",
        choices=["claude", "gemini"],
        help="The LLM provider to use. Defaults to 'claude'."
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="The logging level for the application. Defaults to 'INFO'."
    )

    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Optional file path to write logs to. If not provided, logs are printed to stdout."
    )

    parser.add_argument(
        "--mcp-server",
        type=str,
        default=None,
        help="The URL of an MCP (Model Context Protocol) server to load remote tools from."
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)

    # Load environment variables from a .env file
    load_dotenv()

    # Initialize the appropriate LLM client
    llm_client = None
    if args.llm_provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY environment variable not found for Claude provider.")
            sys.exit(1)
        llm_client = ClaudeLlmClient(api_key)
    elif args.llm_provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable not found for Gemini provider.")
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
    if args.mcp_server:
        logger.info(f"MCP Server: {args.mcp_server}")
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
            logger.warning("Agent reached maximum iterations without completing the task.")
            sys.exit(1)

        logger.info("="*80)

    except KeyboardInterrupt:
        logger.info("\nAgent execution interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Agent failed with an unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
