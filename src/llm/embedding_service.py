"""
Embedding Service for the personal AI agent.

This module implements the Embedding Service which provides vector embeddings
for text using various LLM providers.
"""

import os
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union

from llm.llm_service_manager import LLMServiceManager


class EmbeddingService:
    """
    Provides vector embeddings for text using various LLM providers.
    """

    def __init__(self, llm_service_manager: Optional[LLMServiceManager] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the EmbeddingService.

        Args:
            llm_service_manager: LLM Service Manager instance.
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self.llm_service_manager = llm_service_manager or LLMServiceManager(self.config)
        self.default_provider = self.config.get("default_embedding_provider", "deepseek")
        self.default_model = self.config.get("default_embedding_model", "deepseek-embedding")
        self.embedding_dimension = self.config.get("embedding_dimension", 768)
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("EmbeddingService initialized")
        
        # Cache for embeddings
        self.cache_enabled = self.config.get("enable_embedding_cache", True)
        self.cache = {}
        self.max_cache_size = self.config.get("max_embedding_cache_size", 10000)

    def get_embedding(
        self,
        text: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        use_cache: bool = True
    ) -> List[float]:
        """
        Get embedding for text.

        Args:
            text: The text to get embedding for.
            provider: Provider to use. If None, uses the default provider.
            model: Model to use. If None, uses the default embedding model.
            use_cache: Whether to use the embedding cache.

        Returns:
            List[float]: The embedding vector.
        """
        provider = provider or self.default_provider
        model = model or self.default_model
        
        # Check cache if enabled and requested
        cache_key = f"{provider}:{model}:{text}"
        if self.cache_enabled and use_cache and cache_key in self.cache:
            self.logger.debug(f"Using cached embedding for text: {text[:50]}...")
            return self.cache[cache_key]
        
        try:
            # Get embedding from LLM service
            embedding = self.llm_service_manager.get_embedding(
                text=text,
                provider=provider,
                model=model
            )
            
            # Cache the embedding if enabled
            if self.cache_enabled and use_cache:
                self._add_to_cache(cache_key, embedding)
            
            return embedding
        
        except Exception as e:
            self.logger.error(f"Error getting embedding: {str(e)}")
            # Return zero vector in case of error
            return [0.0] * self.embedding_dimension

    def get_embeddings(
        self,
        texts: List[str],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        use_cache: bool = True
    ) -> List[List[float]]:
        """
        Get embeddings for multiple texts.

        Args:
            texts: The texts to get embeddings for.
            provider: Provider to use. If None, uses the default provider.
            model: Model to use. If None, uses the default embedding model.
            use_cache: Whether to use the embedding cache.

        Returns:
            List[List[float]]: The embedding vectors.
        """
        return [self.get_embedding(text, provider, model, use_cache) for text in texts]

    def compute_similarity(
        self,
        text1: str,
        text2: str,
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> float:
        """
        Compute cosine similarity between two texts.

        Args:
            text1: First text.
            text2: Second text.
            provider: Provider to use. If None, uses the default provider.
            model: Model to use. If None, uses the default embedding model.

        Returns:
            float: Cosine similarity between the texts.
        """
        # Get embeddings
        embedding1 = self.get_embedding(text1, provider, model)
        embedding2 = self.get_embedding(text2, provider, model)
        
        # Compute cosine similarity
        return self._cosine_similarity(embedding1, embedding2)

    def find_most_similar(
        self,
        query_text: str,
        candidate_texts: List[str],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find the most similar texts to a query text.

        Args:
            query_text: The query text.
            candidate_texts: List of candidate texts to compare against.
            provider: Provider to use. If None, uses the default provider.
            model: Model to use. If None, uses the default embedding model.
            top_k: Number of top results to return.

        Returns:
            List[Dict[str, Any]]: List of dictionaries with 'text', 'similarity', and 'index' keys.
        """
        # Get query embedding
        query_embedding = self.get_embedding(query_text, provider, model)
        
        # Get embeddings for all candidate texts
        candidate_embeddings = self.get_embeddings(candidate_texts, provider, model)
        
        # Compute similarities
        similarities = [
            self._cosine_similarity(query_embedding, candidate_embedding)
            for candidate_embedding in candidate_embeddings
        ]
        
        # Create result items
        result_items = [
            {
                "text": text,
                "similarity": similarity,
                "index": i
            }
            for i, (text, similarity) in enumerate(zip(candidate_texts, similarities))
        ]
        
        # Sort by similarity (descending) and take top_k
        result_items.sort(key=lambda x: x["similarity"], reverse=True)
        return result_items[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector.
            vec2: Second vector.

        Returns:
            float: Cosine similarity.
        """
        # Convert to numpy arrays
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        # Calculate dot product and magnitudes
        dot_product = np.dot(vec1_np, vec2_np)
        magnitude1 = np.linalg.norm(vec1_np)
        magnitude2 = np.linalg.norm(vec2_np)
        
        # Handle zero magnitudes
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    def _add_to_cache(self, key: str, embedding: List[float]) -> None:
        """
        Add an embedding to the cache.

        Args:
            key: Cache key.
            embedding: Embedding vector.
        """
        # If cache is full, remove oldest item
        if len(self.cache) >= self.max_cache_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        # Add to cache
        self.cache[key] = embedding

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self.cache = {}
        self.logger.info("Embedding cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the embedding cache.

        Returns:
            Dict[str, Any]: Cache statistics.
        """
        return {
            "enabled": self.cache_enabled,
            "size": len(self.cache),
            "max_size": self.max_cache_size,
            "providers": list(set(key.split(":")[0] for key in self.cache.keys()))
        }
