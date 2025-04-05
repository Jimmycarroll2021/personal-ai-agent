"""
Event Stream Processor for the Agent Core component.

This module implements the Event Stream Processor which handles the flow of events
between components, including user messages, tool results, and system events.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from agent_core.models import Event, EventFilter, EventStream, EventType


class EventStreamProcessor:
    """
    Processes the flow of events between components, including user messages,
    tool results, and system events.
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize the EventStreamProcessor.

        Args:
            max_history: Maximum number of events to keep in history.
        """
        self.events: List[Event] = []
        self.filters: List[EventFilter] = []
        self.max_history = max_history

    def add_event(self, event: Event) -> bool:
        """
        Add an event to the event stream.

        Args:
            event: The event to add.

        Returns:
            bool: True if the event was added successfully, False otherwise.
        """
        try:
            self.events.append(event)
            
            # Trim history if it exceeds max_history
            if len(self.events) > self.max_history:
                self.events = self.events[-self.max_history:]
                
            return True
        except Exception:
            return False

    def create_event(
        self,
        event_type: EventType,
        source: str,
        payload: Dict[str, Any]
    ) -> Event:
        """
        Create a new event with a unique ID and current timestamp.

        Args:
            event_type: The type of event.
            source: The source of the event.
            payload: The event payload.

        Returns:
            Event: The created event.
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now()
        return Event(event_id, event_type, timestamp, source, payload)

    def get_events(self, filters: Optional[List[EventFilter]] = None) -> List[Event]:
        """
        Get events that match the specified filters.

        Args:
            filters: List of filters to apply. If None, all events are returned.

        Returns:
            List[Event]: The filtered events.
        """
        if not filters:
            return self.events.copy()

        filtered_events = []
        for event in self.events:
            if self._matches_filters(event, filters):
                filtered_events.append(event)

        return filtered_events

    def get_latest_events(
        self,
        count: int,
        event_types: Optional[List[EventType]] = None
    ) -> List[Event]:
        """
        Get the latest events, optionally filtered by event type.

        Args:
            count: Number of events to return.
            event_types: Types of events to include. If None, all types are included.

        Returns:
            List[Event]: The latest events.
        """
        if not event_types:
            return self.events[-count:] if count < len(self.events) else self.events.copy()

        filtered_events = [e for e in self.events if e.event_type in event_types]
        return filtered_events[-count:] if count < len(filtered_events) else filtered_events

    def clear_events(self, older_than: Optional[datetime] = None) -> int:
        """
        Clear events from the event stream.

        Args:
            older_than: If provided, only events older than this timestamp are cleared.

        Returns:
            int: Number of events cleared.
        """
        if not older_than:
            count = len(self.events)
            self.events = []
            return count

        original_count = len(self.events)
        self.events = [e for e in self.events if e.timestamp >= older_than]
        return original_count - len(self.events)

    def add_filter(self, filter_obj: EventFilter) -> None:
        """
        Add a filter to the event stream.

        Args:
            filter_obj: The filter to add.
        """
        self.filters.append(filter_obj)

    def remove_filter(self, filter_obj: EventFilter) -> bool:
        """
        Remove a filter from the event stream.

        Args:
            filter_obj: The filter to remove.

        Returns:
            bool: True if the filter was removed, False if it wasn't found.
        """
        if filter_obj in self.filters:
            self.filters.remove(filter_obj)
            return True
        return False

    def get_event_stream(self) -> EventStream:
        """
        Get the current event stream.

        Returns:
            EventStream: The current event stream.
        """
        return EventStream(self.events.copy(), self.filters.copy(), self.max_history)

    def _matches_filters(self, event: Event, filters: List[EventFilter]) -> bool:
        """
        Check if an event matches the specified filters.

        Args:
            event: The event to check.
            filters: The filters to apply.

        Returns:
            bool: True if the event matches all filters, False otherwise.
        """
        for filter_obj in filters:
            # Check event type
            if filter_obj.event_types and event.event_type not in filter_obj.event_types:
                return False

            # Check source
            if filter_obj.sources and event.source not in filter_obj.sources:
                return False

            # Check time range
            if filter_obj.start_time and event.timestamp < filter_obj.start_time:
                return False
            if filter_obj.end_time and event.timestamp > filter_obj.end_time:
                return False

        return True
