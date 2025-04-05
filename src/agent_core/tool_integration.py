"""
Integration module between Agent Core and Tool Framework.

This module provides the integration between the Agent Core and the Tool Framework,
allowing the agent to discover and execute tools based on LLM decisions.
"""

import logging
from typing import Dict, List, Any, Optional

from agent_core.models import Event, EventType
from agent_core.tool_manager import ToolManagerInterface
from tools.tool_manager import ToolManager


class ToolIntegration(ToolManagerInterface):
    """
    Integrates the Tool Framework with the Agent Core.
    
    This class implements the ToolManagerInterface required by the Agent Core
    and delegates the actual tool management to the ToolManager from the
    tools package.
    """
    
    def __init__(self):
        """Initialize the ToolIntegration."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.tool_manager = ToolManager()
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get all available tools in a format suitable for LLM function calling.
        
        Returns:
            List[Dict[str, Any]]: List of tool definitions in function calling format.
        """
        return self.tool_manager.get_all_tools()
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: The name of the tool to execute.
            parameters: The parameters to pass to the tool.
            
        Returns:
            Dict[str, Any]: The result of the tool execution.
        """
        result = self.tool_manager.execute_tool(tool_name, parameters)
        
        # Log the tool execution
        if result.get("success", False):
            self.logger.info(f"Successfully executed tool: {tool_name}")
        else:
            self.logger.warning(f"Failed to execute tool: {tool_name}, error: {result.get('error', 'Unknown error')}")
        
        return result
    
    def create_tool_event(self, tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> Event:
        """
        Create an event for a tool execution.
        
        Args:
            tool_name: The name of the tool that was executed.
            parameters: The parameters that were passed to the tool.
            result: The result of the tool execution.
            
        Returns:
            Event: The created event.
        """
        # Create an event for the tool execution
        event = Event(
            type=EventType.ACTION if result.get("success", False) else EventType.ERROR,
            source="tool_framework",
            content={
                "tool": tool_name,
                "parameters": parameters,
                "result": result
            }
        )
        
        return event
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the schema for a specific tool.
        
        Args:
            tool_name: The name of the tool.
            
        Returns:
            Optional[Dict[str, Any]]: The tool schema, or None if not found.
        """
        tools = self.get_available_tools()
        for tool in tools:
            if tool["name"] == tool_name:
                return tool
        
        return None
