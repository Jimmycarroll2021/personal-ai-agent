"""
Agent State Manager for the Agent Core component.

This module implements the Agent State Manager which maintains the overall state
of the agent, including user context, execution context, memory context, and tool context.
"""

import uuid
from typing import Dict, List, Any, Optional

from agent_core.models import (
    AgentState, UserContext, ExecutionContext, MemoryContext, 
    ToolContext, Plan, Event, Tool
)


class AgentStateManager:
    """
    Maintains the overall state of the agent, including user context,
    execution context, memory context, and tool context.
    """

    def __init__(self):
        """Initialize the AgentStateManager."""
        self.session_id = str(uuid.uuid4())
        self.user_context = self._create_default_user_context()
        self.execution_context = self._create_default_execution_context()
        self.memory_context = self._create_default_memory_context()
        self.tool_context = self._create_default_tool_context()

    def get_state(self) -> AgentState:
        """
        Get the current agent state.

        Returns:
            AgentState: The current agent state.
        """
        return AgentState(
            session_id=self.session_id,
            user_context=self.user_context,
            execution_context=self.execution_context,
            memory_context=self.memory_context,
            tool_context=self.tool_context
        )

    def update_user_context(self, user_id: str, preferences: Dict[str, Any], history: Dict[str, Any]) -> None:
        """
        Update the user context.

        Args:
            user_id: The user ID.
            preferences: User preferences.
            history: User history.
        """
        self.user_context = UserContext(
            user_id=user_id,
            preferences=preferences,
            history=history
        )

    def update_execution_context(
        self,
        current_plan: Optional[Plan],
        execution_history: List[Event],
        active_tools: List[str],
        last_llm_response: Optional[Dict[str, Any]]
    ) -> None:
        """
        Update the execution context.

        Args:
            current_plan: The current execution plan.
            execution_history: The execution history.
            active_tools: List of active tool IDs.
            last_llm_response: The last LLM response.
        """
        self.execution_context = ExecutionContext(
            current_plan=current_plan,
            execution_history=execution_history,
            active_tools=active_tools,
            last_llm_response=last_llm_response
        )

    def update_memory_context(self, short_term: Dict[str, Any], long_term: Dict[str, Any]) -> None:
        """
        Update the memory context.

        Args:
            short_term: Short-term memory.
            long_term: Long-term memory.
        """
        self.memory_context = MemoryContext(
            short_term=short_term,
            long_term=long_term
        )

    def update_tool_context(
        self,
        available_tools: List[Dict[str, Any]],
        tool_usage_history: Dict[str, Any]
    ) -> None:
        """
        Update the tool context.

        Args:
            available_tools: List of available tools.
            tool_usage_history: Tool usage history.
        """
        self.tool_context = ToolContext(
            available_tools=available_tools,
            tool_usage_history=tool_usage_history
        )

    def add_tool(self, tool: Tool) -> bool:
        """
        Add a tool to the available tools.

        Args:
            tool: The tool to add.

        Returns:
            bool: True if the tool was added successfully, False otherwise.
        """
        try:
            tool_dict = {
                'tool_id': tool.tool_id,
                'name': tool.name,
                'description': tool.description,
                'parameters': tool.parameters,
                'return_type': tool.return_type
            }
            
            # Check if tool already exists
            for existing_tool in self.tool_context.available_tools:
                if existing_tool.get('tool_id') == tool.tool_id:
                    # Replace existing tool
                    self.tool_context.available_tools.remove(existing_tool)
                    break
            
            self.tool_context.available_tools.append(tool_dict)
            return True
        except Exception:
            return False

    def remove_tool(self, tool_id: str) -> bool:
        """
        Remove a tool from the available tools.

        Args:
            tool_id: The ID of the tool to remove.

        Returns:
            bool: True if the tool was removed, False if it wasn't found.
        """
        for tool in self.tool_context.available_tools:
            if tool.get('tool_id') == tool_id:
                self.tool_context.available_tools.remove(tool)
                return True
        return False

    def record_tool_usage(self, tool_id: str, usage_data: Dict[str, Any]) -> None:
        """
        Record tool usage in the tool usage history.

        Args:
            tool_id: The ID of the tool.
            usage_data: Data about the tool usage.
        """
        if tool_id not in self.tool_context.tool_usage_history:
            self.tool_context.tool_usage_history[tool_id] = []
        
        self.tool_context.tool_usage_history[tool_id].append(usage_data)

    def reset_state(self) -> None:
        """Reset the agent state to default values."""
        self.session_id = str(uuid.uuid4())
        self.user_context = self._create_default_user_context()
        self.execution_context = self._create_default_execution_context()
        self.memory_context = self._create_default_memory_context()
        self.tool_context = self._create_default_tool_context()

    def _create_default_user_context(self) -> UserContext:
        """
        Create a default user context.

        Returns:
            UserContext: The default user context.
        """
        return UserContext(
            user_id="default",
            preferences={},
            history={}
        )

    def _create_default_execution_context(self) -> ExecutionContext:
        """
        Create a default execution context.

        Returns:
            ExecutionContext: The default execution context.
        """
        return ExecutionContext(
            current_plan=None,
            execution_history=[],
            active_tools=[],
            last_llm_response=None
        )

    def _create_default_memory_context(self) -> MemoryContext:
        """
        Create a default memory context.

        Returns:
            MemoryContext: The default memory context.
        """
        return MemoryContext(
            short_term={},
            long_term={}
        )

    def _create_default_tool_context(self) -> ToolContext:
        """
        Create a default tool context.

        Returns:
            ToolContext: The default tool context.
        """
        return ToolContext(
            available_tools=[],
            tool_usage_history={}
        )
