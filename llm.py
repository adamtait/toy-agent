"""
Unified interface for different LLM providers.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)


class LlmClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def call_llm(self, system_prompt: str, conversation_history: List[Dict[str, Any]]) -> str:
        """
        Call the LLM with the given prompt and conversation history.

        Args:
            system_prompt: The system prompt with instructions.
            conversation_history: The list of messages in the conversation.

        Returns:
            The LLM's response text.
        """
        pass


class ClaudeLlmClient(LlmClient):
    """LLM client for Anthropic's Claude API."""

    def __init__(self, api_key: str):
        """
        Initialize the Claude LLM client.

        Args:
            api_key: Anthropic API key.
        """
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("The 'anthropic' package is required to use the Claude LLM. Please install it with 'pip install anthropic'.")

        self.client = Anthropic(api_key=api_key)

    def call_llm(self, system_prompt: str, conversation_history: List[Dict[str, Any]]) -> str:
        """
        Call the Claude LLM with the current conversation history.

        Args:
            system_prompt: The system prompt with instructions.
            conversation_history: The list of messages in the conversation.

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
            max_tokens=2000,
            system=system_prompt,
            messages=conversation_history
        )

        response_text = response.content[0].text

        logger.info(f"\n--- LLM Response ---")
        logger.info(response_text)
        logger.info(f"--- End LLM Response ---\n")

        return response_text


class GeminiLlmClient(LlmClient):
    """LLM client for Google's Gemini API."""

    def __init__(self, api_key: str):
        """
        Initialize the Gemini LLM client.

        Args:
            api_key: Google Gemini API key.
        """
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("The 'google-generativeai' package is required to use the Gemini LLM. Please install it with 'pip install google-generativeai'.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def call_llm(self, system_prompt: str, conversation_history: List[Dict[str, Any]]) -> str:
        """
        Call the Gemini LLM with the current conversation history.

        Args:
            system_prompt: The system prompt with instructions (prepended to the chat).
            conversation_history: The list of messages in the conversation.

        Returns:
            The LLM's response text.
        """
        logger.info("\n--- Calling Gemini LLM ---")
        logger.debug(f"System prompt length: {len(system_prompt)} chars")
        logger.debug(f"Conversation history length: {len(conversation_history)} messages")

        # Combine system prompt and conversation history
        # Gemini API works with a chat-based conversation
        chat_history = self._prepare_chat_history(system_prompt, conversation_history)

        if conversation_history:
            last_message = conversation_history[-1]
            logger.info(f"Last message ({last_message['role']}): {last_message['content'][:200]}...")

        # Create a chat session with history
        chat = self.model.start_chat(history=chat_history)

        # The last message is the one we want to send
        last_user_message = conversation_history[-1]['content']

        response = chat.send_message(last_user_message)
        response_text = response.text

        logger.info(f"\n--- LLM Response ---")
        logger.info(response_text)
        logger.info(f"--- End LLM Response ---\n")

        return response_text

    def _prepare_chat_history(self, system_prompt: str, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare the chat history for the Gemini API.

        Args:
            system_prompt: The system prompt.
            conversation_history: The current conversation history.

        Returns:
            A list of messages formatted for the Gemini API.
        """
        # Gemini uses a different role model ('user' and 'model')
        # We need to adapt from our ('user' and 'assistant') format

        formatted_history = []

        # The system prompt can be added as the first user message
        # to set the context for the conversation.
        formatted_history.append({"role": "user", "parts": [system_prompt]})
        formatted_history.append({"role": "model", "parts": ["Understood. I'm ready to start the task."]}) # Priming response

        for message in conversation_history[:-1]: # Exclude the last message which will be sent
            role = "model" if message["role"] == "assistant" else "user"
            formatted_history.append({
                "role": role,
                "parts": [message["content"]]
            })

        return formatted_history
