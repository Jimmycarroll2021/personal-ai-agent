"""
Tool Executor for the tool integration framework.

This module implements the Tool Executor which is responsible for executing
tools and handling their results.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

from tools.models import (
    ToolDefinition, ToolExecutionRequest, ToolExecutionResult, ToolRegistry
)


class ToolExecutor:
    """
    Responsible for executing tools and handling their results.
    """

    def __init__(self, tool_registry: ToolRegistry):
        """
        Initialize the ToolExecutor.

        Args:
            tool_registry: Registry of available tools.
        """
        self.tool_registry = tool_registry
        self.logger = logging.getLogger(__name__)
        self.execution_history: List[ToolExecutionResult] = []
        self.max_history_size = 1000
        self.callbacks: Dict[str, List[Callable]] = {}

    def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """
        Execute a tool.

        Args:
            request: The tool execution request.

        Returns:
            ToolExecutionResult: The result of the tool execution.
        """
        # Get the tool definition
        tool = self.tool_registry.get_tool(request.tool_name)
        if tool is None:
            return ToolExecutionResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                success=False,
                error=f"Tool not found: {request.tool_name}"
            )

        # Check if the tool is enabled
        if not tool.enabled:
            return ToolExecutionResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                success=False,
                error=f"Tool is disabled: {request.tool_name}"
            )

        # Check rate limit
        if tool.rate_limit is not None and tool.last_used is not None:
            elapsed = (datetime.now() - tool.last_used).total_seconds()
            if elapsed < tool.rate_limit:
                return ToolExecutionResult(
                    request_id=request.request_id,
                    tool_name=request.tool_name,
                    success=False,
                    error=f"Rate limit exceeded. Try again in {tool.rate_limit - elapsed:.1f} seconds."
                )

        # Validate parameters
        validation_result = self._validate_parameters(tool, request.parameters)
        if not validation_result["valid"]:
            return ToolExecutionResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                success=False,
                error=f"Parameter validation failed: {validation_result['error']}"
            )

        # Execute the tool
        start_time = time.time()
        try:
            if tool.function is None:
                return ToolExecutionResult(
                    request_id=request.request_id,
                    tool_name=request.tool_name,
                    success=False,
                    error=f"Tool has no implementation: {request.tool_name}"
                )

            result = tool.function(**request.parameters)
            execution_time = time.time() - start_time

            # Update last used timestamp
            tool.last_used = datetime.now()

            # Create success result
            execution_result = ToolExecutionResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                success=True,
                result=result,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Error executing tool {request.tool_name}: {str(e)}")

            # Create error result
            execution_result = ToolExecutionResult(
                request_id=request.request_id,
                tool_name=request.tool_name,
                success=False,
                error=str(e),
                execution_time=execution_time
            )

        # Add to history
        self._add_to_history(execution_result)

        # Trigger callbacks
        self._trigger_callbacks(execution_result)

        return execution_result

    def _validate_parameters(self, tool: ToolDefinition, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters against tool definition.

        Args:
            tool: The tool definition.
            parameters: The parameters to validate.

        Returns:
            Dict[str, Any]: Validation result with 'valid' and optional 'error' keys.
        """
        # Check for missing required parameters
        for param in tool.parameters:
            if param.required and param.name not in parameters:
                return {
                    "valid": False,
                    "error": f"Missing required parameter: {param.name}"
                }

        # Check parameter types and constraints
        for param_name, param_value in parameters.items():
            # Find parameter definition
            param_def = next((p for p in tool.parameters if p.name == param_name), None)
            if param_def is None:
                return {
                    "valid": False,
                    "error": f"Unknown parameter: {param_name}"
                }

            # Check type
            if param_def.type == "string" and not isinstance(param_value, str):
                return {
                    "valid": False,
                    "error": f"Parameter {param_name} must be a string"
                }
            elif param_def.type == "integer" and not isinstance(param_value, int):
                return {
                    "valid": False,
                    "error": f"Parameter {param_name} must be an integer"
                }
            elif param_def.type == "float" and not isinstance(param_value, (int, float)):
                return {
                    "valid": False,
                    "error": f"Parameter {param_name} must be a number"
                }
            elif param_def.type == "boolean" and not isinstance(param_value, bool):
                return {
                    "valid": False,
                    "error": f"Parameter {param_name} must be a boolean"
                }
            elif param_def.type == "array" and not isinstance(param_value, list):
                return {
                    "valid": False,
                    "error": f"Parameter {param_name} must be an array"
                }
            elif param_def.type == "object" and not isinstance(param_value, dict):
                return {
                    "valid": False,
                    "error": f"Parameter {param_name} must be an object"
                }

            # Check enum
            if param_def.enum is not None and param_value not in param_def.enum:
                return {
                    "valid": False,
                    "error": f"Parameter {param_name} must be one of: {', '.join(map(str, param_def.enum))}"
                }

            # Check numeric constraints
            if param_def.type in ["integer", "float"]:
                if param_def.min_value is not None and param_value < param_def.min_value:
                    return {
                        "valid": False,
                        "error": f"Parameter {param_name} must be at least {param_def.min_value}"
                    }
                if param_def.max_value is not None and param_value > param_def.max_value:
                    return {
                        "valid": False,
                        "error": f"Parameter {param_name} must be at most {param_def.max_value}"
                    }

            # Check string constraints
            if param_def.type == "string":
                if param_def.min_length is not None and len(param_value) < param_def.min_length:
                    return {
                        "valid": False,
                        "error": f"Parameter {param_name} must be at least {param_def.min_length} characters"
                    }
                if param_def.max_length is not None and len(param_value) > param_def.max_length:
                    return {
                        "valid": False,
                        "error": f"Parameter {param_name} must be at most {param_def.max_length} characters"
                    }
                if param_def.pattern is not None:
                    import re
                    if not re.match(param_def.pattern, param_value):
                        return {
                            "valid": False,
                            "error": f"Parameter {param_name} must match pattern: {param_def.pattern}"
                        }

            # Check array constraints
            if param_def.type == "array" and param_def.items is not None:
                # TODO: Implement array item validation
                pass

            # Check object constraints
            if param_def.type == "object" and param_def.properties is not None:
                # TODO: Implement object property validation
                pass

        return {"valid": True}

    def _add_to_history(self, result: ToolExecutionResult) -> None:
        """
        Add a result to the execution history.

        Args:
            result: The result to add.
        """
        self.execution_history.append(result)
        
        # Trim history if it exceeds max size
        if len(self.execution_history) > self.max_history_size:
            self.execution_history = self.execution_history[-self.max_history_size:]

    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register a callback for a specific event.

        Args:
            event: The event to register for (e.g., 'success', 'error', 'any').
            callback: The callback function.
        """
        if event not in self.callbacks:
            self.callbacks[event] = []
        
        self.callbacks[event].append(callback)

    def _trigger_callbacks(self, result: ToolExecutionResult) -> None:
        """
        Trigger callbacks for a result.

        Args:
            result: The result to trigger callbacks for.
        """
        # Trigger 'any' callbacks
        for callback in self.callbacks.get('any', []):
            try:
                callback(result)
            except Exception as e:
                self.logger.error(f"Error in callback: {str(e)}")
        
        # Trigger 'success' or 'error' callbacks
        event = 'success' if result.success else 'error'
        for callback in self.callbacks.get(event, []):
            try:
                callback(result)
            except Exception as e:
                self.logger.error(f"Error in callback: {str(e)}")
        
        # Trigger tool-specific callbacks
        tool_event = f"tool:{result.tool_name}"
        for callback in self.callbacks.get(tool_event, []):
            try:
                callback(result)
            except Exception as e:
                self.logger.error(f"Error in callback: {str(e)}")

    def get_history(self, tool_name: Optional[str] = None, limit: int = 10) -> List[ToolExecutionResult]:
        """
        Get execution history, optionally filtered by tool name.

        Args:
            tool_name: Optional tool name to filter by.
            limit: Maximum number of results to return.

        Returns:
            List[ToolExecutionResult]: The execution history.
        """
        if tool_name is None:
            return self.execution_history[-limit:]
        
        filtered = [r for r in self.execution_history if r.tool_name == tool_name]
        return filtered[-limit:]

    def clear_history(self) -> None:
        """Clear the execution history."""
        self.execution_history = []
