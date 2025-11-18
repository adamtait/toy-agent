import argparse
import logging
import os
from dotenv import load_dotenv
from src.llm import ClaudeClient, GeminiClient
from src.agent import ReactAgent

def main():
    """
    Command-line entry point for the Toy Agent.
    """
    load_dotenv()

    parser = argparse.ArgumentParser(description="React Agent for Software Development")
    parser.add_argument("--task", required=True, help="The task for the agent to perform.")
    parser.add_argument("--repo", default=".", help="The path to the code repository.")
    parser.add_argument("--max-iterations", type=int, default=10, help="The maximum number of iterations.")
    parser.add_argument("--llm-provider", default="claude", choices=["claude", "gemini"], help="The LLM provider to use.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="The logging level.")
    parser.add_argument("--log-file", help="The file to write logs to.")
    parser.add_argument("--mcp-server", help="The URL of the MCP server for remote tools.")

    args = parser.parse_args()

    # Configure logging
    log_handlers = [logging.StreamHandler()]
    if args.log_file:
        log_handlers.append(logging.FileHandler(args.log_file))

    logging.basicConfig(level=getattr(logging, args.log_level),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=log_handlers)

    logging.info("================================================================================")
    logging.info("React Agent for Software Development")
    logging.info("================================================================================")

    # Instantiate the LLM client
    if args.llm_provider == "claude":
        llm_client = ClaudeClient()
    elif args.llm_provider == "gemini":
        llm_client = GeminiClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {args.llm_provider}")

    # Agent execution
    success = False
    try:
        agent = ReactAgent(task=args.task,
                           repo=args.repo,
                           max_iterations=args.max_iterations,
                           llm_client=llm_client,
                           mcp_server=args.mcp_server)
        success = agent.run()
    except Exception as e:
        logging.critical(f"An error occurred: {e}", exc_info=True)
        success = False
    finally:
        logging.info("================================================================================")
        logging.info("FINAL RESULT")
        logging.info("================================================================================")
        logging.info(f"Success: {success}")

if __name__ == "__main__":
    main()
