from abc import ABC, abstractmethod
import os
import anthropic
import google.generativeai as genai

class LlmClient(ABC):
    """
    Abstract base class for LLM clients.
    """
    @abstractmethod
    def get_completion(self, messages):
        pass

class ClaudeClient(LlmClient):
    """
    LlmClient implementation for Anthropic's Claude API.
    """
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")
        self.client = anthropic.Anthropic(api_key=api_key)

    def get_completion(self, messages):
        """
        Gets a completion from the Claude API.
        """
        system_prompt = messages[0]['content']
        conversation_history = messages[1:]

        response = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            system=system_prompt,
            messages=conversation_history
        )
        return response.content[0].text

class GeminiClient(LlmClient):
    """
    LlmClient implementation for Google's Gemini API.
    """
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')

    def get_completion(self, messages):
        """
        Gets a completion from the Gemini API.
        """
        system_prompt = messages[0]['content']
        conversation_history = messages[1:]

        # Gemini uses 'model' for the assistant role
        gemini_history = []
        for msg in conversation_history:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        # Prepend the system prompt to the chat history
        if system_prompt:
             gemini_history.insert(0, {"role": "user", "parts": [system_prompt]})
             gemini_history.insert(1, {"role": "model", "parts": ["Understood. I will follow your instructions."]})


        response = self.model.generate_content(gemini_history)
        return response.text
