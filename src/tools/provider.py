"""
Tool Provider interface and base class for the tool integration framework.

This module defines the ToolProvider interface and base class which is used
to implement specific tool providers for different categories of tools.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable

from tools.models import (
    ToolDefinition, ToolCategory, ToolParameter, ParameterType, ToolRegistry
)


class ToolProvider(ABC):
    """
    Abstract base class for tool providers.
    
    A tool provider is responsible for registering and implementing a set of
    related tools in a specific category.
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        """
        Initialize the tool provider.
        
        Args:
            tool_registry: The tool registry to register tools with.
        """
        self.tool_registry = tool_registry
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.tools: Dict[str, ToolDefinition] = {}
        
        # Register tools with the registry
        self.register_tools()
    
    @abstractmethod
    def register_tools(self) -> None:
        """
        Register tools with the tool registry.
        
        This method should be implemented by subclasses to register their tools.
        """
        pass
    
    def register_tool(self, tool: ToolDefinition) -> bool:
        """
        Register a tool with the tool registry.
        
        Args:
            tool: The tool to register.
            
        Returns:
            bool: True if the tool was registered successfully, False otherwise.
        """
        # Store in local dictionary
        self.tools[tool.name] = tool
        
        # Register with the registry
        success = self.tool_registry.register_tool(tool)
        
        if success:
            self.logger.info(f"Registered tool: {tool.name}")
        else:
            self.logger.warning(f"Failed to register tool: {tool.name}")
        
        return success
    
    def create_tool(
        self,
        name: str,
        description: str,
        category: ToolCategory,
        function: Callable,
        parameters: List[ToolParameter] = None,
        enabled: bool = True,
        requires_confirmation: bool = False,
        has_side_effects: bool = False,
        is_dangerous: bool = False,
        rate_limit: Optional[int] = None
    ) -> ToolDefinition:
        """
        Create a tool definition.
        
        Args:
            name: The name of the tool.
            description: The description of the tool.
            category: The category of the tool.
            function: The function that implements the tool.
            parameters: The parameters for the tool.
            enabled: Whether the tool is enabled.
            requires_confirmation: Whether the tool requires confirmation.
            has_side_effects: Whether the tool has side effects.
            is_dangerous: Whether the tool is dangerous.
            rate_limit: Optional rate limit in seconds.
            
        Returns:
            ToolDefinition: The created tool definition.
        """
        return ToolDefinition(
            name=name,
            description=description,
            category=category,
            function=function,
            parameters=parameters or [],
            enabled=enabled,
            requires_confirmation=requires_confirmation,
            has_side_effects=has_side_effects,
            is_dangerous=is_dangerous,
            rate_limit=rate_limit
        )
    
    def create_parameter(
        self,
        name: str,
        description: str,
        type: Union[ParameterType, str],
        required: bool = False,
        default: Optional[Any] = None,
        enum: Optional[List[Any]] = None,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        items: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> ToolParameter:
        """
        Create a parameter definition.
        
        Args:
            name: The name of the parameter.
            description: The description of the parameter.
            type: The type of the parameter.
            required: Whether the parameter is required.
            default: The default value of the parameter.
            enum: Optional list of allowed values.
            min_value: Optional minimum value for numeric parameters.
            max_value: Optional maximum value for numeric parameters.
            min_length: Optional minimum length for string parameters.
            max_length: Optional maximum length for string parameters.
            pattern: Optional regex pattern for string parameters.
            items: Optional schema for array items.
            properties: Optional schema for object properties.
            
        Returns:
            ToolParameter: The created parameter definition.
        """
        # Convert string type to enum
        if isinstance(type, str):
            type = ParameterType(type)
        
        return ToolParameter(
            name=name,
            description=description,
            type=type,
            required=required,
            default=default,
            enum=enum,
            min_value=min_value,
            max_value=max_value,
            min_length=min_length,
            max_length=max_length,
            pattern=pattern,
            items=items,
            properties=properties
        )
