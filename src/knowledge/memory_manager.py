"""
Memory Manager for the Knowledge Module component.

This module implements the Memory Manager which oversees both short-term and
long-term memory systems, handling memory operations and optimization.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from knowledge.models import (
    MemoryItem, MemoryType, MemoryCategory, 
    ContextItem, ContextWindow, OptimizationResult
)


class MemoryManager:
    """
    Oversees both short-term and long-term memory systems, handling memory
    operations and optimization.
    """

    def __init__(self):
        """Initialize the MemoryManager."""
        self.short_term_memory = {}  # item_id -> MemoryItem
        self.long_term_memory = {}   # item_id -> MemoryItem
        self.categories = {}         # category_id -> MemoryCategory
        self.logger = logging.getLogger(__name__)

    def store_item(self, item: MemoryItem) -> str:
        """
        Store an item in memory.

        Args:
            item: The memory item to store.

        Returns:
            str: The ID of the stored item.
        """
        # Generate ID if not provided
        if not item.item_id:
            item.item_id = str(uuid.uuid4())
        
        # Store in appropriate memory type
        if item.memory_type == MemoryType.SHORT_TERM:
            self.short_term_memory[item.item_id] = item
        else:
            self.long_term_memory[item.item_id] = item
        
        self.logger.info(f"Stored item {item.item_id} in {item.memory_type.value} memory")
        return item.item_id

    def retrieve_item(self, item_id: str) -> Optional[MemoryItem]:
        """
        Retrieve an item from memory.

        Args:
            item_id: The ID of the item to retrieve.

        Returns:
            Optional[MemoryItem]: The retrieved item, or None if not found.
        """
        # Check short-term memory first
        if item_id in self.short_term_memory:
            item = self.short_term_memory[item_id]
            # Update access metadata
            item.last_accessed = datetime.now()
            item.access_count += 1
            return item
        
        # Then check long-term memory
        if item_id in self.long_term_memory:
            item = self.long_term_memory[item_id]
            # Update access metadata
            item.last_accessed = datetime.now()
            item.access_count += 1
            return item
        
        return None

    def update_item(self, item: MemoryItem) -> bool:
        """
        Update an existing memory item.

        Args:
            item: The updated memory item.

        Returns:
            bool: True if the item was updated, False if it wasn't found.
        """
        # Check if item exists
        if item.item_id in self.short_term_memory:
            self.short_term_memory[item.item_id] = item
            return True
        elif item.item_id in self.long_term_memory:
            self.long_term_memory[item.item_id] = item
            return True
        
        return False

    def delete_item(self, item_id: str) -> bool:
        """
        Delete an item from memory.

        Args:
            item_id: The ID of the item to delete.

        Returns:
            bool: True if the item was deleted, False if it wasn't found.
        """
        # Check if item exists in short-term memory
        if item_id in self.short_term_memory:
            del self.short_term_memory[item_id]
            
            # Also remove from any categories
            for category in self.categories.values():
                if item_id in category.items:
                    category.items.remove(item_id)
            
            return True
        
        # Check if item exists in long-term memory
        if item_id in self.long_term_memory:
            del self.long_term_memory[item_id]
            
            # Also remove from any categories
            for category in self.categories.values():
                if item_id in category.items:
                    category.items.remove(item_id)
            
            return True
        
        return False

    def create_category(
        self,
        name: str,
        description: str,
        parent_id: Optional[str] = None
    ) -> str:
        """
        Create a new memory category.

        Args:
            name: The name of the category.
            description: The description of the category.
            parent_id: The ID of the parent category, if any.

        Returns:
            str: The ID of the created category.
        """
        category_id = str(uuid.uuid4())
        
        category = MemoryCategory(
            category_id=category_id,
            name=name,
            description=description,
            parent_id=parent_id,
            items=[]
        )
        
        self.categories[category_id] = category
        return category_id

    def add_item_to_category(self, item_id: str, category_id: str) -> bool:
        """
        Add an item to a category.

        Args:
            item_id: The ID of the item to add.
            category_id: The ID of the category.

        Returns:
            bool: True if the item was added, False if the item or category wasn't found.
        """
        # Check if category exists
        if category_id not in self.categories:
            return False
        
        # Check if item exists
        if item_id not in self.short_term_memory and item_id not in self.long_term_memory:
            return False
        
        # Add item to category
        category = self.categories[category_id]
        if item_id not in category.items:
            category.items.append(item_id)
        
        return True

    def get_items_by_category(self, category_id: str) -> List[MemoryItem]:
        """
        Get all items in a category.

        Args:
            category_id: The ID of the category.

        Returns:
            List[MemoryItem]: The items in the category.
        """
        # Check if category exists
        if category_id not in self.categories:
            return []
        
        category = self.categories[category_id]
        items = []
        
        for item_id in category.items:
            item = self.retrieve_item(item_id)
            if item:
                items.append(item)
        
        return items

    def move_to_long_term(self, item_id: str) -> bool:
        """
        Move an item from short-term to long-term memory.

        Args:
            item_id: The ID of the item to move.

        Returns:
            bool: True if the item was moved, False if it wasn't found in short-term memory.
        """
        # Check if item exists in short-term memory
        if item_id not in self.short_term_memory:
            return False
        
        # Get item
        item = self.short_term_memory[item_id]
        
        # Change memory type
        item.memory_type = MemoryType.LONG_TERM
        
        # Move to long-term memory
        self.long_term_memory[item_id] = item
        del self.short_term_memory[item_id]
        
        return True

    def move_to_short_term(self, item_id: str) -> bool:
        """
        Move an item from long-term to short-term memory.

        Args:
            item_id: The ID of the item to move.

        Returns:
            bool: True if the item was moved, False if it wasn't found in long-term memory.
        """
        # Check if item exists in long-term memory
        if item_id not in self.long_term_memory:
            return False
        
        # Get item
        item = self.long_term_memory[item_id]
        
        # Change memory type
        item.memory_type = MemoryType.SHORT_TERM
        
        # Move to short-term memory
        self.short_term_memory[item_id] = item
        del self.long_term_memory[item_id]
        
        return True

    def optimize_memory(self) -> OptimizationResult:
        """
        Optimize memory by moving less important items to long-term memory.

        Returns:
            OptimizationResult: The result of the optimization.
        """
        start_time = datetime.now()
        
        # Count initial items
        initial_short_term_count = len(self.short_term_memory)
        
        # Find items to move to long-term memory
        items_to_move = []
        
        for item_id, item in self.short_term_memory.items():
            # Simple heuristic: move items with low importance and access count
            if item.importance < 0.3 and item.access_count < 3:
                items_to_move.append(item_id)
        
        # Move items
        for item_id in items_to_move:
            self.move_to_long_term(item_id)
        
        # Calculate metrics
        end_time = datetime.now()
        time_taken = (end_time - start_time).total_seconds()
        items_affected = len(items_to_move)
        
        # Prepare result
        result = OptimizationResult(
            success=True,
            items_affected=items_affected,
            space_saved=items_affected,  # Simplified metric
            time_taken=time_taken,
            details={
                "initial_short_term_count": initial_short_term_count,
                "final_short_term_count": initial_short_term_count - items_affected,
                "items_moved": items_to_move
            }
        )
        
        self.logger.info(f"Memory optimization moved {items_affected} items to long-term memory")
        return result

    def create_context_window(
        self,
        max_tokens: int,
        strategy: str = "importance_recency"
    ) -> ContextWindow:
        """
        Create a context window from the most relevant items in memory.

        Args:
            max_tokens: Maximum number of tokens in the context window.
            strategy: Strategy for selecting items.

        Returns:
            ContextWindow: The created context window.
        """
        window_id = str(uuid.uuid4())
        
        # Get all items from short-term memory
        all_items = list(self.short_term_memory.values())
        
        # Convert to context items
        context_items = []
        for item in all_items:
            context_item = ContextItem(
                item_id=item.item_id,
                content=item.content,
                importance=item.importance,
                recency=self._calculate_recency(item.last_accessed),
                token_count=self._estimate_token_count(item.content),
                source="memory",
                metadata=item.metadata
            )
            context_items.append(context_item)
        
        # Sort items based on strategy
        if strategy == "importance_recency":
            # Sort by combined score of importance and recency
            context_items.sort(
                key=lambda x: (x.importance * 0.7 + x.recency * 0.3),
                reverse=True
            )
        elif strategy == "importance":
            # Sort by importance only
            context_items.sort(key=lambda x: x.importance, reverse=True)
        elif strategy == "recency":
            # Sort by recency only
            context_items.sort(key=lambda x: x.recency, reverse=True)
        
        # Select items up to max_tokens
        selected_items = []
        current_tokens = 0
        
        for item in context_items:
            if current_tokens + item.token_count <= max_tokens:
                selected_items.append(item)
                current_tokens += item.token_count
            else:
                break
        
        # Create context window
        context_window = ContextWindow(
            window_id=window_id,
            items=selected_items,
            max_tokens=max_tokens,
            current_tokens=current_tokens,
            strategy=strategy
        )
        
        return context_window

    def _calculate_recency(self, timestamp: datetime) -> float:
        """
        Calculate recency score based on timestamp.

        Args:
            timestamp: The timestamp to calculate recency for.

        Returns:
            float: Recency score between 0 and 1, where 1 is most recent.
        """
        now = datetime.now()
        time_diff = (now - timestamp).total_seconds()
        
        # Exponential decay: 1.0 for now, 0.5 for 1 hour ago, 0.25 for 2 hours ago, etc.
        recency = 2 ** (-time_diff / 3600)
        
        # Ensure value is between 0 and 1
        return max(0.0, min(1.0, recency))

    def _estimate_token_count(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.

        Args:
            text: The text to estimate tokens for.

        Returns:
            int: Estimated token count.
        """
        # Simple estimation: 1 token ≈ 4 characters
        return len(text) // 4 + 1

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory.

        Returns:
            Dict[str, Any]: Memory statistics.
        """
        return {
            "short_term_count": len(self.short_term_memory),
            "long_term_count": len(self.long_term_memory),
            "category_count": len(self.categories),
            "total_items": len(self.short_term_memory) + len(self.long_term_memory)
        }
