"""
Knowledge Module main class for the personal AI agent.

This module implements the main Knowledge Module class that integrates all knowledge
components and provides a unified interface for the Agent Core.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from knowledge.models import (
    MemoryItem, MemoryType, KnowledgeQuery, KnowledgeItem, KnowledgeResponse,
    QueryType, ContextWindow, KnowledgeState, KnowledgeEvent, KnowledgeEventType,
    ValidationResult, FactCheckResult, ConsistencyResult
)
from knowledge.memory_manager import MemoryManager
from knowledge.vector_database import VectorDatabase
from knowledge.retrieval_engine import RetrievalEngine


class KnowledgeModule:
    """
    Main Knowledge Module class that integrates all knowledge components and
    provides a unified interface for the Agent Core.
    """

    def __init__(self, embedding_service, llm_service):
        """
        Initialize the KnowledgeModule.

        Args:
            embedding_service: Service for generating embeddings.
            llm_service: Service for calling the LLM.
        """
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        
        # Initialize components
        self.memory_manager = MemoryManager()
        self.vector_database = VectorDatabase()
        self.retrieval_engine = RetrievalEngine(self.vector_database, embedding_service)
        
        # Initialize storage
        self.knowledge_items = {}  # item_id -> KnowledgeItem
        self.session_states = {}   # session_id -> KnowledgeState
        self.events = []           # List of KnowledgeEvent
        
        # Create default vector collection
        self.default_collection_id = self.vector_database.create_collection(
            name="default_knowledge",
            dimension=768  # Default dimension for embeddings
        )
        self.retrieval_engine.set_default_collection(self.default_collection_id)
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("KnowledgeModule initialized")

    def add_knowledge_item(
        self,
        content: str,
        source: str,
        confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a knowledge item.

        Args:
            content: The content of the knowledge item.
            source: The source of the knowledge.
            confidence: Confidence level in the knowledge.
            metadata: Optional metadata for the knowledge item.

        Returns:
            str: The ID of the added knowledge item.
        """
        item_id = str(uuid.uuid4())
        
        # Create knowledge item
        item = KnowledgeItem(
            item_id=item_id,
            content=content,
            source=source,
            confidence=confidence,
            metadata=metadata or {},
            created_at=datetime.now()
        )
        
        # Store item
        self.knowledge_items[item_id] = item
        
        # Generate embedding and add to vector database
        embedding = self.embedding_service.get_embedding(content)
        self.vector_database.add_vector(
            collection_id=self.default_collection_id,
            vector=embedding,
            item_id=item_id,
            metadata=metadata
        )
        
        # Also store in memory
        memory_item = MemoryItem(
            item_id=item_id,
            content=content,
            memory_type=MemoryType.SEMANTIC,
            embedding=embedding,
            metadata={
                "source": source,
                "confidence": confidence,
                **metadata or {}
            },
            importance=confidence
        )
        self.memory_manager.store_item(memory_item)
        
        # Log event
        self._log_event(
            event_type=KnowledgeEventType.ITEM_ADDED,
            details={
                "item_id": item_id,
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "source": source
            }
        )
        
        self.logger.info(f"Added knowledge item: {item_id}")
        return item_id

    def query_knowledge(
        self,
        query_text: str,
        query_type: QueryType = QueryType.SEMANTIC,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> KnowledgeResponse:
        """
        Query knowledge.

        Args:
            query_text: The query text.
            query_type: The type of query.
            filters: Optional filters to apply.
            top_k: Maximum number of results to return.
            threshold: Minimum similarity score threshold.

        Returns:
            KnowledgeResponse: The query response.
        """
        query_id = str(uuid.uuid4())
        
        # Create query
        query = KnowledgeQuery(
            query_id=query_id,
            query_text=query_text,
            query_type=query_type,
            filters=filters,
            top_k=top_k,
            threshold=threshold
        )
        
        # Process query
        response = self.retrieval_engine.process_query(query, self.knowledge_items)
        
        # Log event
        self._log_event(
            event_type=KnowledgeEventType.QUERY_EXECUTED,
            details={
                "query_id": query_id,
                "query_text": query_text,
                "query_type": query_type.value,
                "result_count": len(response.items)
            }
        )
        
        self.logger.info(f"Executed query: {query_text} (type: {query_type.value})")
        return response

    def create_context_window(
        self,
        session_id: str,
        max_tokens: int = 4000,
        strategy: str = "importance_recency"
    ) -> ContextWindow:
        """
        Create a context window for a session.

        Args:
            session_id: The ID of the session.
            max_tokens: Maximum number of tokens in the context window.
            strategy: Strategy for selecting items.

        Returns:
            ContextWindow: The created context window.
        """
        # Create context window
        context_window = self.memory_manager.create_context_window(
            max_tokens=max_tokens,
            strategy=strategy
        )
        
        # Update session state
        if session_id in self.session_states:
            self.session_states[session_id].context_window = context_window
        else:
            self.session_states[session_id] = KnowledgeState(
                session_id=session_id,
                context_window=context_window,
                recent_queries=[],
                recent_results={}
            )
        
        # Log event
        self._log_event(
            event_type=KnowledgeEventType.CONTEXT_UPDATED,
            details={
                "session_id": session_id,
                "context_size": context_window.current_tokens,
                "item_count": len(context_window.items)
            }
        )
        
        self.logger.info(f"Created context window for session {session_id}")
        return context_window

    def update_context(
        self,
        session_id: str,
        query_text: str,
        max_tokens: int = 4000
    ) -> ContextWindow:
        """
        Update context based on a query.

        Args:
            session_id: The ID of the session.
            query_text: The query text.
            max_tokens: Maximum number of tokens in the context window.

        Returns:
            ContextWindow: The updated context window.
        """
        # Query knowledge
        response = self.query_knowledge(
            query_text=query_text,
            query_type=QueryType.SEMANTIC,
            top_k=5
        )
        
        # Create or update session state
        if session_id not in self.session_states:
            self.session_states[session_id] = KnowledgeState(
                session_id=session_id,
                context_window=None,
                recent_queries=[],
                recent_results={}
            )
        
        # Update recent queries and results
        state = self.session_states[session_id]
        
        # Add query to recent queries
        query = KnowledgeQuery(
            query_id=response.query_id,
            query_text=query_text,
            query_type=QueryType.SEMANTIC,
            top_k=5,
            threshold=0.0
        )
        state.recent_queries.append(query)
        
        # Limit recent queries to last 10
        if len(state.recent_queries) > 10:
            state.recent_queries = state.recent_queries[-10:]
        
        # Add response to recent results
        state.recent_results[response.query_id] = response
        
        # Create context window
        context_window = self.create_context_window(
            session_id=session_id,
            max_tokens=max_tokens
        )
        
        return context_window

    def validate_knowledge(self, item_id: str) -> ValidationResult:
        """
        Validate a knowledge item.

        Args:
            item_id: The ID of the knowledge item to validate.

        Returns:
            ValidationResult: The validation result.

        Raises:
            ValueError: If the item is not found.
        """
        # Check if item exists
        if item_id not in self.knowledge_items:
            raise ValueError(f"Knowledge item not found: {item_id}")
        
        item = self.knowledge_items[item_id]
        
        # In a real implementation, this would use the LLM to validate the knowledge
        # For this simplified version, we just return a success result
        
        # Create validation result
        result = ValidationResult(
            item_id=item_id,
            is_valid=True,
            confidence=0.9,
            issues=[]
        )
        
        self.logger.info(f"Validated knowledge item: {item_id}")
        return result

    def fact_check(self, statement: str) -> FactCheckResult:
        """
        Fact check a statement.

        Args:
            statement: The statement to fact check.

        Returns:
            FactCheckResult: The fact check result.
        """
        # In a real implementation, this would use the LLM and knowledge base to fact check
        # For this simplified version, we just return a placeholder result
        
        # Query knowledge for relevant information
        response = self.query_knowledge(
            query_text=statement,
            query_type=QueryType.SEMANTIC,
            top_k=3
        )
        
        # Get sources
        sources = [item.source for item in response.items]
        
        # Create fact check result
        result = FactCheckResult(
            statement=statement,
            is_factual=True,
            confidence=0.8,
            sources=sources,
            explanation="Statement appears to be factual based on available knowledge."
        )
        
        self.logger.info(f"Fact checked statement: {statement}")
        return result

    def check_consistency(self, statements: List[str]) -> ConsistencyResult:
        """
        Check consistency between statements.

        Args:
            statements: The statements to check.

        Returns:
            ConsistencyResult: The consistency check result.
        """
        # In a real implementation, this would use the LLM to check consistency
        # For this simplified version, we just return a placeholder result
        
        # Create consistency result
        result = ConsistencyResult(
            is_consistent=True,
            conflicts=[],
            confidence=0.9
        )
        
        self.logger.info(f"Checked consistency of {len(statements)} statements")
        return result

    def get_knowledge_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """
        Get a knowledge item by ID.

        Args:
            item_id: The ID of the knowledge item.

        Returns:
            Optional[KnowledgeItem]: The knowledge item if found, None otherwise.
        """
        return self.knowledge_items.get(item_id)

    def delete_knowledge_item(self, item_id: str) -> bool:
        """
        Delete a knowledge item.

        Args:
            item_id: The ID of the knowledge item to delete.

        Returns:
            bool: True if the item was deleted, False if it wasn't found.
        """
        # Check if item exists
        if item_id not in self.knowledge_items:
            return False
        
        # Delete from knowledge items
        del self.knowledge_items[item_id]
        
        # Delete from vector database
        self.vector_database.delete_item_vectors(item_id)
        
        # Delete from memory
        self.memory_manager.delete_item(item_id)
        
        # Log event
        self._log_event(
            event_type=KnowledgeEventType.ITEM_REMOVED,
            details={"item_id": item_id}
        )
        
        self.logger.info(f"Deleted knowledge item: {item_id}")
        return True

    def get_session_state(self, session_id: str) -> Optional[KnowledgeState]:
        """
        Get the state of a session.

        Args:
            session_id: The ID of the session.

        Returns:
            Optional[KnowledgeState]: The session state if found, None otherwise.
        """
        return self.session_states.get(session_id)

    def get_recent_events(self, limit: int = 10) -> List[KnowledgeEvent]:
        """
        Get recent knowledge events.

        Args:
            limit: Maximum number of events to return.

        Returns:
            List[KnowledgeEvent]: List of recent events.
        """
        return self.events[-limit:] if self.events else []

    def _log_event(self, event_type: KnowledgeEventType, details: Dict[str, Any]) -> None:
        """
        Log a knowledge event.

        Args:
            event_type: The type of event.
            details: Event details.
        """
        event = KnowledgeEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            details=details,
            timestamp=datetime.now()
        )
        
        self.events.append(event)
        
        # Limit events to last 1000
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
