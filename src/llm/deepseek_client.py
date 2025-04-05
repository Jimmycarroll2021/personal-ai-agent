"""
LLM Service Client for DeepSeek-R1 model.

This module implements the LLM Service Client for the DeepSeek-R1 model,
providing a unified interface for the Agent Core to interact with the model.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Union, Callable

import openai


class DeepSeekR1Client:
    """
    LLM Service Client for the DeepSeek-R1 model.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        model_name: str = "deepseek-reasoner",
        timeout: int = 120,
        max_retries: int = 3
    ):
        """
        Initialize the DeepSeekR1Client.

        Args:
            api_key: DeepSeek API key. If None, will try to get from environment variable.
            base_url: Base URL for the DeepSeek API.
            model_name: Model name to use.
            timeout: Timeout for API calls in seconds.
            max_retries: Maximum number of retries for API calls.
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Please provide it or set DEEPSEEK_API_KEY environment variable.")
        
        self.base_url = base_url
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"DeepSeekR1Client initialized with model: {model_name}")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate text using the DeepSeek-R1 model.

        Args:
            prompt: The prompt to generate text from.
            system_prompt: Optional system prompt to guide the model.
            temperature: Temperature for text generation.
            max_tokens: Maximum number of tokens to generate.
            stream: Whether to stream the response.
            callback: Optional callback function for streaming responses.

        Returns:
            Dict[str, Any]: The generated text and metadata.
        """
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Call the API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            # Handle streaming response
            if stream:
                return self._handle_streaming_response(response, callback)
            
            # Handle non-streaming response
            return self._process_response(response)
        
        except Exception as e:
            self.logger.error(f"Error generating text: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "reasoning_content": None
            }

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Chat with the DeepSeek-R1 model.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            temperature: Temperature for text generation.
            max_tokens: Maximum number of tokens to generate.
            stream: Whether to stream the response.
            callback: Optional callback function for streaming responses.

        Returns:
            Dict[str, Any]: The chat response and metadata.
        """
        try:
            # Call the API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            # Handle streaming response
            if stream:
                return self._handle_streaming_response(response, callback)
            
            # Handle non-streaming response
            return self._process_response(response)
        
        except Exception as e:
            self.logger.error(f"Error in chat: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "reasoning_content": None
            }

    def _process_response(self, response) -> Dict[str, Any]:
        """
        Process a non-streaming response.

        Args:
            response: The API response.

        Returns:
            Dict[str, Any]: Processed response data.
        """
        try:
            # Extract content and reasoning_content
            content = response.choices[0].message.content
            reasoning_content = response.choices[0].message.reasoning_content
            
            return {
                "success": True,
                "content": content,
                "reasoning_content": reasoning_content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "id": response.id
            }
        except Exception as e:
            self.logger.error(f"Error processing response: {str(e)}")
            
            # Fallback to simpler extraction if the structure is different
            try:
                content = response.choices[0].message.content
                return {
                    "success": True,
                    "content": content,
                    "reasoning_content": None,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "model": response.model,
                    "id": response.id
                }
            except:
                return {
                    "success": False,
                    "error": str(e),
                    "content": None,
                    "reasoning_content": None
                }

    def _handle_streaming_response(
        self,
        response,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Handle a streaming response.

        Args:
            response: The streaming API response.
            callback: Optional callback function for streaming chunks.

        Returns:
            Dict[str, Any]: Aggregated response data.
        """
        content_chunks = []
        reasoning_chunks = []
        
        for chunk in response:
            try:
                # Extract content from chunk
                delta = chunk.choices[0].delta
                
                if hasattr(delta, 'content') and delta.content:
                    content_chunks.append(delta.content)
                
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    reasoning_chunks.append(delta.reasoning_content)
                
                # Call callback if provided
                if callback:
                    callback(delta)
            
            except Exception as e:
                self.logger.error(f"Error processing chunk: {str(e)}")
        
        # Combine chunks
        content = "".join(content_chunks)
        reasoning_content = "".join(reasoning_chunks)
        
        return {
            "success": True,
            "content": content,
            "reasoning_content": reasoning_content,
            "is_streaming": True
        }

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using DeepSeek's embedding model.

        Args:
            text: The text to get embedding for.

        Returns:
            List[float]: The embedding vector.
        """
        try:
            response = self.client.embeddings.create(
                model="deepseek-embedding",
                input=text
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            self.logger.error(f"Error getting embedding: {str(e)}")
            # Return empty embedding in case of error
            return []
