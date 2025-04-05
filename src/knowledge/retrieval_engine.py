"""
Retrieval Engine for the Knowledge Module component.

This module implements the Retrieval Engine which handles the search and retrieval
of knowledge items based on queries.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from knowledge.models import (
    KnowledgeQuery, KnowledgeItem, KnowledgeResponse, QueryType,
    SearchResult, OptimizationStrategy
)


class RetrievalEngine:
    """
    Handles the search and retrieval of knowledge items based on queries.
    """

    def __init__(self, vector_database, embedding_service):
        """
        Initialize the RetrievalEngine.

        Args:
            vector_database: The vector database for semantic search.
            embedding_service: Service for generating embeddings.
        """
        self.vector_database = vector_database
        self.embedding_service = embedding_service
        self.logger = logging.getLogger(__name__)
        self.default_collection_id = None

    def set_default_collection(self, collection_id: str) -> None:
        """
        Set the default vector collection for searches.

        Args:
            collection_id: The ID of the collection.
        """
        self.default_collection_id = collection_id

    def process_query(
        self,
        query: KnowledgeQuery,
        items_dict: Dict[str, KnowledgeItem]
    ) -> KnowledgeResponse:
        """
        Process a knowledge query.

        Args:
            query: The query to process.
            items_dict: Dictionary of knowledge items (item_id -> KnowledgeItem).

        Returns:
            KnowledgeResponse: The query response.
        """
        self.logger.info(f"Processing query: {query.query_text} (type: {query.query_type.value})")
        
        # Select search method based on query type
        if query.query_type == QueryType.SEMANTIC:
            results = self._semantic_search(query, items_dict)
        elif query.query_type == QueryType.KEYWORD:
            results = self._keyword_search(query, items_dict)
        elif query.query_type == QueryType.HYBRID:
            results = self._hybrid_search(query, items_dict)
        elif query.query_type == QueryType.EXACT:
            results = self._exact_search(query, items_dict)
        else:
            # Default to semantic search
            results = self._semantic_search(query, items_dict)
        
        # Create response
        response = KnowledgeResponse(
            query_id=query.query_id,
            items=[items_dict[item_id] for item_id, _ in results],
            scores={item_id: score for item_id, score in results},
            metadata={
                "query_type": query.query_type.value,
                "timestamp": datetime.now().isoformat(),
                "result_count": len(results)
            }
        )
        
        self.logger.info(f"Query processed with {len(results)} results")
        return response

    def _semantic_search(
        self,
        query: KnowledgeQuery,
        items_dict: Dict[str, KnowledgeItem]
    ) -> List[Tuple[str, float]]:
        """
        Perform semantic search using vector embeddings.

        Args:
            query: The query to process.
            items_dict: Dictionary of knowledge items.

        Returns:
            List[Tuple[str, float]]: List of (item_id, score) tuples.
        """
        # Check if default collection is set
        if not self.default_collection_id:
            self.logger.warning("No default collection set for semantic search")
            return []
        
        # Generate embedding for query
        query_embedding = self.embedding_service.get_embedding(query.query_text)
        
        # Search vector database
        results = self.vector_database.search_items(
            collection_id=self.default_collection_id,
            query_vector=query_embedding,
            top_k=query.top_k,
            threshold=query.threshold,
            filter_metadata=query.filters
        )
        
        # Filter results to only include items that exist in items_dict
        filtered_results = [
            (item_id, score) for item_id, score in results
            if item_id in items_dict
        ]
        
        return filtered_results

    def _keyword_search(
        self,
        query: KnowledgeQuery,
        items_dict: Dict[str, KnowledgeItem]
    ) -> List[Tuple[str, float]]:
        """
        Perform keyword-based search.

        Args:
            query: The query to process.
            items_dict: Dictionary of knowledge items.

        Returns:
            List[Tuple[str, float]]: List of (item_id, score) tuples.
        """
        # Tokenize query
        query_tokens = set(query.query_text.lower().split())
        
        # Calculate scores for each item
        scores = []
        for item_id, item in items_dict.items():
            # Apply filters if specified
            if query.filters and not self._matches_filters(item, query.filters):
                continue
            
            # Tokenize item content
            item_tokens = set(item.content.lower().split())
            
            # Calculate score based on token overlap
            if not query_tokens or not item_tokens:
                score = 0.0
            else:
                overlap = len(query_tokens.intersection(item_tokens))
                score = overlap / len(query_tokens)
            
            if score >= query.threshold:
                scores.append((item_id, score))
        
        # Sort by score (descending) and take top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:query.top_k]

    def _hybrid_search(
        self,
        query: KnowledgeQuery,
        items_dict: Dict[str, KnowledgeItem]
    ) -> List[Tuple[str, float]]:
        """
        Perform hybrid search combining semantic and keyword approaches.

        Args:
            query: The query to process.
            items_dict: Dictionary of knowledge items.

        Returns:
            List[Tuple[str, float]]: List of (item_id, score) tuples.
        """
        # Perform both search types
        semantic_results = self._semantic_search(query, items_dict)
        keyword_results = self._keyword_search(query, items_dict)
        
        # Combine results with weighted scores
        semantic_weight = 0.7
        keyword_weight = 0.3
        
        # Create dictionaries for easy lookup
        semantic_scores = {item_id: score for item_id, score in semantic_results}
        keyword_scores = {item_id: score for item_id, score in keyword_results}
        
        # Combine all item IDs
        all_item_ids = set(semantic_scores.keys()).union(set(keyword_scores.keys()))
        
        # Calculate combined scores
        combined_scores = []
        for item_id in all_item_ids:
            semantic_score = semantic_scores.get(item_id, 0.0)
            keyword_score = keyword_scores.get(item_id, 0.0)
            
            combined_score = (semantic_score * semantic_weight) + (keyword_score * keyword_weight)
            
            if combined_score >= query.threshold:
                combined_scores.append((item_id, combined_score))
        
        # Sort by score (descending) and take top_k
        combined_scores.sort(key=lambda x: x[1], reverse=True)
        return combined_scores[:query.top_k]

    def _exact_search(
        self,
        query: KnowledgeQuery,
        items_dict: Dict[str, KnowledgeItem]
    ) -> List[Tuple[str, float]]:
        """
        Perform exact match search.

        Args:
            query: The query to process.
            items_dict: Dictionary of knowledge items.

        Returns:
            List[Tuple[str, float]]: List of (item_id, score) tuples.
        """
        # Normalize query
        query_text = query.query_text.lower()
        
        # Find exact matches
        matches = []
        for item_id, item in items_dict.items():
            # Apply filters if specified
            if query.filters and not self._matches_filters(item, query.filters):
                continue
            
            # Check for exact match
            if query_text in item.content.lower():
                # Score is 1.0 for exact match
                matches.append((item_id, 1.0))
        
        # Sort by item ID (for consistent results) and take top_k
        matches.sort(key=lambda x: x[0])
        return matches[:query.top_k]

    def compute_relevance(
        self,
        query: str,
        item: KnowledgeItem
    ) -> float:
        """
        Compute relevance score between a query and an item.

        Args:
            query: The query text.
            item: The knowledge item.

        Returns:
            float: Relevance score between 0 and 1.
        """
        # Generate embeddings
        query_embedding = self.embedding_service.get_embedding(query)
        item_embedding = self.embedding_service.get_embedding(item.content)
        
        # Calculate cosine similarity
        similarity = self._cosine_similarity(query_embedding, item_embedding)
        
        return similarity

    def rank_results(
        self,
        items: List[KnowledgeItem],
        query: str
    ) -> List[KnowledgeItem]:
        """
        Rank items by relevance to a query.

        Args:
            items: The items to rank.
            query: The query text.

        Returns:
            List[KnowledgeItem]: The ranked items.
        """
        # Calculate relevance scores
        scored_items = [
            (item, self.compute_relevance(query, item))
            for item in items
        ]
        
        # Sort by score (descending)
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Return ranked items
        return [item for item, _ in scored_items]

    def optimize_retrieval(self, query_type: QueryType) -> OptimizationStrategy:
        """
        Get optimization strategy for a query type.

        Args:
            query_type: The query type.

        Returns:
            OptimizationStrategy: The optimization strategy.
        """
        if query_type == QueryType.SEMANTIC:
            return OptimizationStrategy(
                strategy_id="semantic_optimization",
                name="Semantic Search Optimization",
                parameters={
                    "use_approximate_search": True,
                    "index_type": "hnsw",
                    "ef_construction": 200,
                    "m": 16
                },
                description="Optimizes semantic search using HNSW index"
            )
        elif query_type == QueryType.KEYWORD:
            return OptimizationStrategy(
                strategy_id="keyword_optimization",
                name="Keyword Search Optimization",
                parameters={
                    "use_inverted_index": True,
                    "min_token_length": 3,
                    "use_stemming": True
                },
                description="Optimizes keyword search using inverted index"
            )
        elif query_type == QueryType.HYBRID:
            return OptimizationStrategy(
                strategy_id="hybrid_optimization",
                name="Hybrid Search Optimization",
                parameters={
                    "semantic_weight": 0.7,
                    "keyword_weight": 0.3,
                    "use_caching": True
                },
                description="Optimizes hybrid search with weighted combination"
            )
        else:
            return OptimizationStrategy(
                strategy_id="default_optimization",
                name="Default Optimization",
                parameters={},
                description="Default optimization strategy"
            )

    def _matches_filters(self, item: KnowledgeItem, filters: Dict[str, Any]) -> bool:
        """
        Check if an item matches filters.

        Args:
            item: The item to check.
            filters: The filters to apply.

        Returns:
            bool: True if the item matches the filters, False otherwise.
        """
        # Check metadata filters
        for key, value in filters.items():
            if key == "source" and value != item.source:
                return False
            elif key == "min_confidence" and item.confidence < float(value):
                return False
            elif key == "max_age" and item.created_at:
                age = (datetime.now() - item.created_at).total_seconds() / 86400  # days
                if age > float(value):
                    return False
            elif key in item.metadata and item.metadata[key] != value:
                return False
        
        return True

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector.
            vec2: Second vector.

        Returns:
            float: Cosine similarity.
        """
        # Simple implementation using dot product and magnitudes
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
