"""
Tool Manager for the Agent Core component.

This module implements the Tool Manager which handles tool registration,
validation, execution, and result processing.
"""

import uuid
from typing import Dict, List, Any, Optional, Callable

from agent_core.models import Tool, ToolCall, ToolResult, ValidationError


class ToolManager:
    """
    Manages tool registration, validation, execution, and result processing.
    """

    def __init__(self):
        """Initialize the ToolManager."""
        self.tools: Dict[str, Tool] = {}
        self.tool_executors: Dict[str, Callable] = {}
        self.tool_validators: Dict[str, Callable] = {}

    def register_tool(
        self,
        tool: Tool,
        executor: Callable,
        validator: Optional[Callable] = None
    ) -> bool:
        """
        Register a tool with its executor and optional validator.

        Args:
            tool: The tool to register.
            executor: Function that executes the tool.
            validator: Optional function that validates tool parameters.

        Returns:
            bool: True if the tool was registered successfully, False otherwise.
        """
        try:
            self.tools[tool.tool_id] = tool
            self.tool_executors[tool.tool_id] = executor
            if validator:
                self.tool_validators[tool.tool_id] = validator
            return True
        except Exception:
            return False

    def unregister_tool(self, tool_id: str) -> bool:
        """
        Unregister a tool.

        Args:
            tool_id: The ID of the tool to unregister.

        Returns:
            bool: True if the tool was unregistered, False if it wasn't found.
        """
        if tool_id in self.tools:
            self.tools.pop(tool_id)
            self.tool_executors.pop(tool_id)
            if tool_id in self.tool_validators:
                self.tool_validators.pop(tool_id)
            return True
        return False

    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """
        Get a tool by ID.

        Args:
            tool_id: The ID of the tool to get.

        Returns:
            Optional[Tool]: The tool if found, None otherwise.
        """
        return self.tools.get(tool_id)

    def get_all_tools(self) -> List[Tool]:
        """
        Get all registered tools.

        Returns:
            List[Tool]: All registered tools.
        """
        return list(self.tools.values())

    def validate_tool_call(self, tool_call: ToolCall) -> List[ValidationError]:
        """
        Validate a tool call.

        Args:
            tool_call: The tool call to validate.

        Returns:
            List[ValidationError]: List of validation errors, empty if valid.
        """
        errors = []
        
        # Check if tool exists
        tool = self.get_tool(tool_call.tool_id)
        if not tool:
            errors.append(ValidationError(
                parameter="tool_id",
                error_type="not_found",
                message=f"Tool not found: {tool_call.tool_id}"
            ))
            return errors
        
        # Check required parameters
        for param in tool.parameters:
            if param.get('required', False) and param.get('name') not in tool_call.parameters:
                errors.append(ValidationError(
                    parameter=param.get('name'),
                    error_type="missing",
                    message=f"Missing required parameter: {param.get('name')}"
                ))
        
        # Use custom validator if available
        if tool_call.tool_id in self.tool_validators:
            validator = self.tool_validators[tool_call.tool_id]
            custom_errors = validator(tool_call.parameters)
            if custom_errors:
                errors.extend(custom_errors)
        
        return errors

    def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a tool call.

        Args:
            tool_call: The tool call to execute.

        Returns:
            ToolResult: The result of the tool execution.
        """
        # Validate tool call
        validation_errors = self.validate_tool_call(tool_call)
        if validation_errors:
            error_messages = [f"{e.parameter}: {e.message}" for e in validation_errors]
            return ToolResult(
                call_id=tool_call.call_id,
                success=False,
                result=None,
                error=f"Validation failed: {', '.join(error_messages)}"
            )
        
        # Execute tool
        try:
            executor = self.tool_executors.get(tool_call.tool_id)
            if not executor:
                return ToolResult(
                    call_id=tool_call.call_id,
                    success=False,
                    result=None,
                    error=f"Executor not found for tool: {tool_call.tool_id}"
                )
            
            result = executor(**tool_call.parameters)
            return ToolResult(
                call_id=tool_call.call_id,
                success=True,
                result=result,
                error=None
            )
        except Exception as e:
            return ToolResult(
                call_id=tool_call.call_id,
                success=False,
                result=None,
                error=f"Execution failed: {str(e)}"
            )

    def create_tool_call(self, tool_id: str, parameters: Dict[str, Any]) -> ToolCall:
        """
        Create a tool call with a unique ID.

        Args:
            tool_id: The ID of the tool to call.
            parameters: The parameters for the tool call.

        Returns:
            ToolCall: The created tool call.
        """
        call_id = str(uuid.uuid4())
        return ToolCall(
            tool_id=tool_id,
            parameters=parameters,
            call_id=call_id
        )
