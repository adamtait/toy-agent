"""
This module provides a unified interface for different LLM providers,
allowing the agent to be backend-agnostic. It defines an abstract base
class `LlmClient` and concrete implementations for various services.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)


class LlmClient(ABC):
    """
    Abstract base class for LLM clients.

    This class defines the contract that all LLM clients must follow, ensuring
    that the agent can interact with them in a consistent way.
    """

    @abstractmethod
    def call_llm(self, system_prompt: str, conversation_history: List[Dict[str, Any]]) -> str:
        """
        Calls the LLM with a given system prompt and conversation history.

        Args:
            system_prompt (str): The system prompt with instructions for the LLM.
            conversation_history (list): A list of messages representing the
                                         conversation so far.

        Returns:
            The LLM's response text.
        """
        pass


class ClaudeLlmClient(LlmClient):
    """
    LLM client for Anthropic's Claude API.
    """

    def __init__(self, api_key: str):
        """
        Initializes the Claude LLM client.

        Args:
            api_key (str): The Anthropic API key.

        Raises:
            ImportError: If the 'anthropic' package is not installed.
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("The 'anthropic' package is required to use the Claude LLM. Please install it with 'pip install anthropic'.")

        self.client = Anthropic(api_key=api_key)

    def call_llm(self, system_prompt: str, conversation_history: List[Dict[str, Any]]) -> str:
        """
        Calls the Claude LLM with the current conversation history.

        Args:
            system_prompt (str): The system prompt with instructions.
            conversation_history (list): The list of messages in the conversation.

        Returns:
            The LLM's response text.
        """
        logger.info("\n--- Calling Claude LLM ---")
        logger.debug(f"System prompt length: {len(system_prompt)} chars")
        logger.debug(f"Conversation history length: {len(conversation_history)} messages")

        if conversation_history:
            last_message = conversation_history[-1]
            logger.info(f"Last message ({last_message['role']}): {last_message['content'][:200]}...")

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=system_prompt,
            messages=conversation_history
        )

        response_text = response.content[0].text

        logger.info(f"\n--- LLM Response ---")
        logger.info(response_text)
        logger.info(f"--- End LLM Response ---\n")

        return response_text


class GeminiLlmClient(LlmClient):
    """
    LLM client for Google's Gemini API.
    """

    def __init__(self, api_key: str):
        """
        Initializes the Gemini LLM client.

        Args:
            api_key (str): The Google Gemini API key.

        Raises:
            ImportError: If the 'google-generativeai' package is not installed.
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("The 'google-generativeai' package is required to use the Gemini LLM. Please install it with 'pip install google-generativeai'.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-latest')

    def call_llm(self, system_prompt: str, conversation_history: List[Dict[str, Any]]) -> str:
        """
        Calls the Gemini LLM with the current conversation history.

        This method adapts the conversation format to be compatible with the
        Gemini API's chat-based model.

        Args:
            system_prompt (str): The system prompt with instructions.
            conversation_history (list): The list of messages in the conversation.

        Returns:
            The LLM's response text.
        """
        logger.info("\n--- Calling Gemini LLM ---")
        logger.debug(f"System prompt length: {len(system_prompt)} chars")
        logger.debug(f"Conversation history length: {len(conversation_history)} messages")

        chat_history = self._prepare_chat_history(system_prompt, conversation_history)
        last_user_message = conversation_history[-1]['content']

        if conversation_history:
            last_message = conversation_history[-1]
            logger.info(f"Last message ({last_message['role']}): {last_message['content'][:200]}...")

        chat = self.model.start_chat(history=chat_history)
        response = chat.send_message(last_user_message)
        response_text = response.text

        logger.info(f"\n--- LLM Response ---")
        logger.info(response_text)
        logger.info(f"--- End LLM Response ---\n")

        return response_text

    def _prepare_chat_history(self, system_prompt: str, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepares the chat history for the Gemini API.

        Gemini uses a 'user'/'model' role system, so this method maps the
        agent's 'user'/'assistant' roles accordingly. The system prompt is
        prepended as the first message to set the context.

        Args:
            system_prompt (str): The system prompt.
            conversation_history (list): The current conversation history.

        Returns:
            A list of messages formatted for the Gemini API.
        """
        formatted_history = [
            {"role": "user", "parts": [system_prompt]},
            {"role": "model", "parts": ["Understood. I'm ready to start the task."]} # Priming response
        ]

        for message in conversation_history[:-1]:
            role = "model" if message["role"] == "assistant" else "user"
            formatted_history.append({
                "role": role,
                "parts": [message["content"]]
            })

        return formatted_history
