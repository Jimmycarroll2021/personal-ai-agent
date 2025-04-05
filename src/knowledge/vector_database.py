"""
Vector Database for the Knowledge Module component.

This module implements the Vector Database which provides efficient storage and
retrieval of vector embeddings for semantic search.
"""

import uuid
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

from knowledge.models import (
    VectorCollection, VectorEntry, SearchResult, OptimizationResult
)


class VectorDatabase:
    """
    Provides efficient storage and retrieval of vector embeddings for semantic search.
    """

    def __init__(self):
        """Initialize the VectorDatabase."""
        self.collections = {}  # collection_id -> VectorCollection
        self.entries = {}      # collection_id -> {entry_id -> VectorEntry}
        self.item_mapping = {} # item_id -> List[Tuple[collection_id, entry_id]]
        self.logger = logging.getLogger(__name__)

    def create_collection(
        self,
        name: str,
        dimension: int,
        index_type: str = "flat"
    ) -> str:
        """
        Create a new vector collection.

        Args:
            name: The name of the collection.
            dimension: The dimension of vectors in the collection.
            index_type: The type of index to use.

        Returns:
            str: The ID of the created collection.
        """
        collection_id = str(uuid.uuid4())
        
        collection = VectorCollection(
            collection_id=collection_id,
            name=name,
            dimension=dimension,
            index_type=index_type,
            metadata={"created_at": str(uuid.uuid1())}
        )
        
        self.collections[collection_id] = collection
        self.entries[collection_id] = {}
        
        self.logger.info(f"Created vector collection: {name} (ID: {collection_id})")
        return collection_id

    def add_vector(
        self,
        collection_id: str,
        vector: List[float],
        item_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a vector to a collection.

        Args:
            collection_id: The ID of the collection.
            vector: The vector to add.
            item_id: The ID of the associated item.
            metadata: Optional metadata for the vector.

        Returns:
            str: The ID of the added vector entry.

        Raises:
            ValueError: If the collection doesn't exist or the vector has the wrong dimension.
        """
        # Check if collection exists
        if collection_id not in self.collections:
            raise ValueError(f"Collection not found: {collection_id}")
        
        collection = self.collections[collection_id]
        
        # Check vector dimension
        if len(vector) != collection.dimension:
            raise ValueError(
                f"Vector dimension mismatch: expected {collection.dimension}, got {len(vector)}"
            )
        
        # Create entry
        entry_id = str(uuid.uuid4())
        entry = VectorEntry(
            entry_id=entry_id,
            vector=vector,
            item_id=item_id,
            metadata=metadata or {}
        )
        
        # Store entry
        self.entries[collection_id][entry_id] = entry
        
        # Update item mapping
        if item_id not in self.item_mapping:
            self.item_mapping[item_id] = []
        self.item_mapping[item_id].append((collection_id, entry_id))
        
        self.logger.info(f"Added vector to collection {collection_id}: {entry_id}")
        return entry_id

    def search_vectors(
        self,
        collection_id: str,
        query_vector: List[float],
        top_k: int = 5,
        threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float]]:
        """
        Search for similar vectors in a collection.

        Args:
            collection_id: The ID of the collection to search.
            query_vector: The query vector.
            top_k: Maximum number of results to return.
            threshold: Minimum similarity score threshold.
            filter_metadata: Optional metadata filter.

        Returns:
            List[Tuple[str, float]]: List of (entry_id, score) tuples.

        Raises:
            ValueError: If the collection doesn't exist or the vector has the wrong dimension.
        """
        # Check if collection exists
        if collection_id not in self.collections:
            raise ValueError(f"Collection not found: {collection_id}")
        
        collection = self.collections[collection_id]
        
        # Check vector dimension
        if len(query_vector) != collection.dimension:
            raise ValueError(
                f"Vector dimension mismatch: expected {collection.dimension}, got {len(query_vector)}"
            )
        
        # Convert query vector to numpy array
        query_np = np.array(query_vector)
        
        # Calculate similarities
        similarities = []
        for entry_id, entry in self.entries[collection_id].items():
            # Apply metadata filter if provided
            if filter_metadata and not self._matches_metadata_filter(entry.metadata, filter_metadata):
                continue
            
            # Calculate cosine similarity
            vector_np = np.array(entry.vector)
            similarity = self._cosine_similarity(query_np, vector_np)
            
            # Apply threshold
            if similarity >= threshold:
                similarities.append((entry_id, similarity))
        
        # Sort by similarity (descending) and take top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def search_items(
        self,
        collection_id: str,
        query_vector: List[float],
        top_k: int = 5,
        threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float]]:
        """
        Search for similar items in a collection.

        Args:
            collection_id: The ID of the collection to search.
            query_vector: The query vector.
            top_k: Maximum number of results to return.
            threshold: Minimum similarity score threshold.
            filter_metadata: Optional metadata filter.

        Returns:
            List[Tuple[str, float]]: List of (item_id, score) tuples.

        Raises:
            ValueError: If the collection doesn't exist or the vector has the wrong dimension.
        """
        # Search for vectors
        vector_results = self.search_vectors(
            collection_id, query_vector, top_k, threshold, filter_metadata
        )
        
        # Convert entry_ids to item_ids
        item_results = []
        seen_items = set()
        
        for entry_id, score in vector_results:
            entry = self.entries[collection_id][entry_id]
            item_id = entry.item_id
            
            # Avoid duplicates
            if item_id not in seen_items:
                item_results.append((item_id, score))
                seen_items.add(item_id)
        
        return item_results

    def delete_vector(self, collection_id: str, entry_id: str) -> bool:
        """
        Delete a vector from a collection.

        Args:
            collection_id: The ID of the collection.
            entry_id: The ID of the vector entry to delete.

        Returns:
            bool: True if the vector was deleted, False if it wasn't found.
        """
        # Check if collection exists
        if collection_id not in self.collections:
            return False
        
        # Check if entry exists
        if entry_id not in self.entries[collection_id]:
            return False
        
        # Get item_id before deletion
        entry = self.entries[collection_id][entry_id]
        item_id = entry.item_id
        
        # Delete entry
        del self.entries[collection_id][entry_id]
        
        # Update item mapping
        if item_id in self.item_mapping:
            self.item_mapping[item_id] = [
                (c_id, e_id) for c_id, e_id in self.item_mapping[item_id]
                if c_id != collection_id or e_id != entry_id
            ]
            
            # Remove item mapping if empty
            if not self.item_mapping[item_id]:
                del self.item_mapping[item_id]
        
        self.logger.info(f"Deleted vector from collection {collection_id}: {entry_id}")
        return True

    def delete_item_vectors(self, item_id: str) -> int:
        """
        Delete all vectors associated with an item.

        Args:
            item_id: The ID of the item.

        Returns:
            int: Number of vectors deleted.
        """
        # Check if item has any vectors
        if item_id not in self.item_mapping:
            return 0
        
        # Get all vectors for the item
        vectors = self.item_mapping[item_id].copy()
        
        # Delete each vector
        count = 0
        for collection_id, entry_id in vectors:
            if self.delete_vector(collection_id, entry_id):
                count += 1
        
        return count

    def delete_collection(self, collection_id: str) -> bool:
        """
        Delete a collection.

        Args:
            collection_id: The ID of the collection to delete.

        Returns:
            bool: True if the collection was deleted, False if it wasn't found.
        """
        # Check if collection exists
        if collection_id not in self.collections:
            return False
        
        # Get all entries in the collection
        entries = list(self.entries[collection_id].values())
        
        # Update item mapping
        for entry in entries:
            item_id = entry.item_id
            if item_id in self.item_mapping:
                self.item_mapping[item_id] = [
                    (c_id, e_id) for c_id, e_id in self.item_mapping[item_id]
                    if c_id != collection_id
                ]
                
                # Remove item mapping if empty
                if not self.item_mapping[item_id]:
                    del self.item_mapping[item_id]
        
        # Delete collection and entries
        del self.collections[collection_id]
        del self.entries[collection_id]
        
        self.logger.info(f"Deleted collection: {collection_id}")
        return True

    def get_collection(self, collection_id: str) -> Optional[VectorCollection]:
        """
        Get a collection by ID.

        Args:
            collection_id: The ID of the collection.

        Returns:
            Optional[VectorCollection]: The collection if found, None otherwise.
        """
        return self.collections.get(collection_id)

    def get_entry(self, collection_id: str, entry_id: str) -> Optional[VectorEntry]:
        """
        Get a vector entry by ID.

        Args:
            collection_id: The ID of the collection.
            entry_id: The ID of the vector entry.

        Returns:
            Optional[VectorEntry]: The vector entry if found, None otherwise.
        """
        if collection_id not in self.collections:
            return None
        
        return self.entries[collection_id].get(entry_id)

    def get_item_vectors(self, item_id: str) -> List[Tuple[str, str]]:
        """
        Get all vectors associated with an item.

        Args:
            item_id: The ID of the item.

        Returns:
            List[Tuple[str, str]]: List of (collection_id, entry_id) tuples.
        """
        return self.item_mapping.get(item_id, [])

    def list_collections(self) -> List[VectorCollection]:
        """
        List all collections.

        Returns:
            List[VectorCollection]: List of all collections.
        """
        return list(self.collections.values())

    def optimize_index(self, collection_id: str) -> OptimizationResult:
        """
        Optimize the index for a collection.

        Args:
            collection_id: The ID of the collection.

        Returns:
            OptimizationResult: The result of the optimization.

        Raises:
            ValueError: If the collection doesn't exist.
        """
        # Check if collection exists
        if collection_id not in self.collections:
            raise ValueError(f"Collection not found: {collection_id}")
        
        # In a real implementation, this would rebuild the index
        # For this simplified version, we just return a success result
        
        collection = self.collections[collection_id]
        entry_count = len(self.entries[collection_id])
        
        result = OptimizationResult(
            success=True,
            items_affected=entry_count,
            space_saved=0,  # No actual optimization in this implementation
            time_taken=0.1,  # Simulated time
            details={
                "collection_id": collection_id,
                "collection_name": collection.name,
                "index_type": collection.index_type,
                "entry_count": entry_count
            }
        )
        
        self.logger.info(f"Optimized index for collection {collection_id}")
        return result

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector.
            vec2: Second vector.

        Returns:
            float: Cosine similarity.
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

    def _matches_metadata_filter(self, metadata: Dict[str, Any], filter_metadata: Dict[str, Any]) -> bool:
        """
        Check if metadata matches a filter.

        Args:
            metadata: The metadata to check.
            filter_metadata: The filter to apply.

        Returns:
            bool: True if the metadata matches the filter, False otherwise.
        """
        for key, value in filter_metadata.items():
            if key not in metadata or metadata[key] != value:
                return False
        
        return True
