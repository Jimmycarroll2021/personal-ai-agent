"""
LLM Service Manager for the personal AI agent.

This module implements the LLM Service Manager which provides a unified interface
for interacting with different LLM providers and models.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union, Callable

from llm.deepseek_client import DeepSeekR1Client


class LLMServiceManager:
    """
    Provides a unified interface for interacting with different LLM providers and models.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLMServiceManager.

        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self.clients = {}
        self.default_provider = self.config.get("default_provider", "deepseek")
        self.default_model = self.config.get("default_model", "deepseek-reasoner")
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize default clients
        self._initialize_default_clients()

    def _initialize_default_clients(self) -> None:
        """Initialize default LLM clients based on configuration."""
        # Initialize DeepSeek client if configured
        if "deepseek" in self.config.get("providers", ["deepseek"]):
            deepseek_config = self.config.get("deepseek", {})
            api_key = deepseek_config.get("api_key") or os.environ.get("DEEPSEEK_API_KEY")
            
            if api_key:
                try:
                    self.clients["deepseek"] = DeepSeekR1Client(
                        api_key=api_key,
                        base_url=deepseek_config.get("base_url", "https://api.deepseek.com"),
                        model_name=deepseek_config.get("model_name", "deepseek-reasoner"),
                        timeout=deepseek_config.get("timeout", 120),
                        max_retries=deepseek_config.get("max_retries", 3)
                    )
                    self.logger.info("DeepSeek client initialized successfully")
                except Exception as e:
                    self.logger.error(f"Failed to initialize DeepSeek client: {str(e)}")
            else:
                self.logger.warning("DeepSeek API key not found, client not initialized")

    def add_client(self, provider: str, client: Any) -> None:
        """
        Add a new LLM client.

        Args:
            provider: Provider name.
            client: Client instance.
        """
        self.clients[provider] = client
        self.logger.info(f"Added client for provider: {provider}")

    def get_client(self, provider: Optional[str] = None) -> Any:
        """
        Get an LLM client.

        Args:
            provider: Provider name. If None, returns the default provider's client.

        Returns:
            Any: The LLM client.

        Raises:
            ValueError: If the provider is not found or not initialized.
        """
        provider = provider or self.default_provider
        
        if provider not in self.clients:
            raise ValueError(f"Provider '{provider}' not found or not initialized")
        
        return self.clients[provider]

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using an LLM.

        Args:
            prompt: The prompt to generate text from.
            system_prompt: Optional system prompt to guide the model.
            provider: Provider to use. If None, uses the default provider.
            model: Model to use. If None, uses the default model for the provider.
            temperature: Temperature for text generation.
            max_tokens: Maximum number of tokens to generate.
            stream: Whether to stream the response.
            callback: Optional callback function for streaming responses.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Dict[str, Any]: The generated text and metadata.
        """
        provider = provider or self.default_provider
        client = self.get_client(provider)
        
        # Override model if specified
        if model and hasattr(client, "model_name"):
            original_model = client.model_name
            client.model_name = model
        
        try:
            result = client.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                callback=callback,
                **kwargs
            )
            
            # Add provider and model info to result
            result["provider"] = provider
            result["model"] = getattr(client, "model_name", model or self.default_model)
            
            return result
        
        finally:
            # Restore original model if it was changed
            if model and hasattr(client, "model_name"):
                client.model_name = original_model

    def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat with an LLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            provider: Provider to use. If None, uses the default provider.
            model: Model to use. If None, uses the default model for the provider.
            temperature: Temperature for text generation.
            max_tokens: Maximum number of tokens to generate.
            stream: Whether to stream the response.
            callback: Optional callback function for streaming responses.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Dict[str, Any]: The chat response and metadata.
        """
        provider = provider or self.default_provider
        client = self.get_client(provider)
        
        # Override model if specified
        if model and hasattr(client, "model_name"):
            original_model = client.model_name
            client.model_name = model
        
        try:
            result = client.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                callback=callback,
                **kwargs
            )
            
            # Add provider and model info to result
            result["provider"] = provider
            result["model"] = getattr(client, "model_name", model or self.default_model)
            
            return result
        
        finally:
            # Restore original model if it was changed
            if model and hasattr(client, "model_name"):
                client.model_name = original_model

    def get_embedding(
        self,
        text: str,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> List[float]:
        """
        Get embedding for text.

        Args:
            text: The text to get embedding for.
            provider: Provider to use. If None, uses the default provider.
            model: Model to use. If None, uses the default embedding model for the provider.

        Returns:
            List[float]: The embedding vector.
        """
        provider = provider or self.default_provider
        client = self.get_client(provider)
        
        # Use provider-specific embedding method
        if hasattr(client, "get_embedding"):
            return client.get_embedding(text)
        else:
            self.logger.error(f"Provider '{provider}' does not support embeddings")
            return []

    def get_available_providers(self) -> List[str]:
        """
        Get list of available providers.

        Returns:
            List[str]: List of available provider names.
        """
        return list(self.clients.keys())

    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a provider is available.

        Args:
            provider: Provider name to check.

        Returns:
            bool: True if the provider is available, False otherwise.
        """
        return provider in self.clients
