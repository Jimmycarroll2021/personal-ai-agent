"""
Shell Tool Provider for the tool integration framework.

This module implements the Shell Tool Provider which provides tools for
interacting with the shell environment.
"""

import os
import subprocess
import logging
import shlex
from typing import Dict, List, Any, Optional, Union, Callable

from tools.models import ToolCategory, ParameterType, ToolRegistry
from tools.provider import ToolProvider


class ShellToolProvider(ToolProvider):
    """
    Provides tools for interacting with the shell environment.
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        """
        Initialize the ShellToolProvider.
        
        Args:
            tool_registry: The tool registry to register tools with.
        """
        super().__init__(tool_registry)
    
    def register_tools(self) -> None:
        """Register shell tools with the tool registry."""
        # Shell Execute
        self.register_tool(
            self.create_tool(
                name="shell_exec",
                description="Execute commands in a specified shell session.",
                category=ToolCategory.SHELL,
                function=self.shell_exec,
                parameters=[
                    self.create_parameter(
                        name="id",
                        description="Unique identifier of the target shell session; automatically creates new session if not exists",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="exec_dir",
                        description="Working directory for command execution (must use absolute path)",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="command",
                        description="Shell command to execute",
                        type=ParameterType.STRING,
                        required=True
                    )
                ],
                has_side_effects=True
            )
        )
        
        # Shell View
        self.register_tool(
            self.create_tool(
                name="shell_view",
                description="View the content of a specified shell session.",
                category=ToolCategory.SHELL,
                function=self.shell_view,
                parameters=[
                    self.create_parameter(
                        name="id",
                        description="Unique identifier of the target shell session",
                        type=ParameterType.STRING,
                        required=True
                    )
                ]
            )
        )
        
        # Shell Wait
        self.register_tool(
            self.create_tool(
                name="shell_wait",
                description="Wait for the running process in a specified shell session to return.",
                category=ToolCategory.SHELL,
                function=self.shell_wait,
                parameters=[
                    self.create_parameter(
                        name="id",
                        description="Unique identifier of the target shell session",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="seconds",
                        description="Wait duration in seconds. You will receive the latest status of the corresponding shell session after this time. If not specified, defaults to 30 seconds.",
                        type=ParameterType.INTEGER,
                        required=False,
                        default=30
                    )
                ]
            )
        )
        
        # Shell Write to Process
        self.register_tool(
            self.create_tool(
                name="shell_write_to_process",
                description="Write input to a running process in a specified shell session.",
                category=ToolCategory.SHELL,
                function=self.shell_write_to_process,
                parameters=[
                    self.create_parameter(
                        name="id",
                        description="Unique identifier of the target shell session",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="input",
                        description="Input content to write to the process",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="press_enter",
                        description="Whether to press Enter key after input",
                        type=ParameterType.BOOLEAN,
                        required=True
                    )
                ],
                has_side_effects=True
            )
        )
        
        # Shell Kill Process
        self.register_tool(
            self.create_tool(
                name="shell_kill_process",
                description="Terminate a running process in a specified shell session.",
                category=ToolCategory.SHELL,
                function=self.shell_kill_process,
                parameters=[
                    self.create_parameter(
                        name="id",
                        description="Unique identifier of the target shell session",
                        type=ParameterType.STRING,
                        required=True
                    )
                ],
                has_side_effects=True
            )
        )
    
    # Shell session management
    def _get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get or create a shell session.
        
        Args:
            session_id: The session ID.
            
        Returns:
            Dict[str, Any]: The session data.
        """
        # In a real implementation, this would manage persistent shell sessions
        # For this prototype, we'll simulate shell sessions with a simple dictionary
        
        # This is a placeholder implementation
        # In a real implementation, this would use something like pexpect or pty
        # to create and manage interactive shell sessions
        
        return {
            "id": session_id,
            "status": "active",
            "output": ""
        }
    
    # Tool implementations
    def shell_exec(self, id: str, exec_dir: str, command: str) -> Dict[str, Any]:
        """
        Execute a command in a shell session.
        
        Args:
            id: The session ID.
            exec_dir: The working directory.
            command: The command to execute.
            
        Returns:
            Dict[str, Any]: The execution result.
        """
        try:
            # Ensure the directory exists
            if not os.path.isdir(exec_dir):
                return {
                    "success": False,
                    "error": f"Directory does not exist: {exec_dir}"
                }
            
            # Get or create session
            session = self._get_or_create_session(id)
            
            # Execute the command
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=exec_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            exit_code = process.returncode
            
            # Update session output
            session["output"] = stdout if exit_code == 0 else stderr
            
            return {
                "success": exit_code == 0,
                "output": stdout,
                "error": stderr if exit_code != 0 else None,
                "exit_code": exit_code
            }
        
        except Exception as e:
            self.logger.error(f"Error executing shell command: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def shell_view(self, id: str) -> Dict[str, Any]:
        """
        View the content of a shell session.
        
        Args:
            id: The session ID.
            
        Returns:
            Dict[str, Any]: The session content.
        """
        try:
            # Get session
            session = self._get_or_create_session(id)
            
            return {
                "success": True,
                "output": session["output"],
                "status": session["status"]
            }
        
        except Exception as e:
            self.logger.error(f"Error viewing shell session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def shell_wait(self, id: str, seconds: int = 30) -> Dict[str, Any]:
        """
        Wait for a process in a shell session to complete.
        
        Args:
            id: The session ID.
            seconds: The number of seconds to wait.
            
        Returns:
            Dict[str, Any]: The session status after waiting.
        """
        try:
            # Get session
            session = self._get_or_create_session(id)
            
            # In a real implementation, this would wait for the process to complete
            # For this prototype, we'll just return the current status
            
            return {
                "success": True,
                "status": session["status"],
                "waited_seconds": seconds
            }
        
        except Exception as e:
            self.logger.error(f"Error waiting for shell process: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def shell_write_to_process(self, id: str, input: str, press_enter: bool) -> Dict[str, Any]:
        """
        Write input to a process in a shell session.
        
        Args:
            id: The session ID.
            input: The input to write.
            press_enter: Whether to press Enter after writing.
            
        Returns:
            Dict[str, Any]: The result of writing to the process.
        """
        try:
            # Get session
            session = self._get_or_create_session(id)
            
            # In a real implementation, this would write to the process
            # For this prototype, we'll just update the session output
            
            session["output"] += f"\nInput: {input}"
            if press_enter:
                session["output"] += "\n"
            
            return {
                "success": True,
                "input_written": input,
                "press_enter": press_enter
            }
        
        except Exception as e:
            self.logger.error(f"Error writing to shell process: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def shell_kill_process(self, id: str) -> Dict[str, Any]:
        """
        Kill a process in a shell session.
        
        Args:
            id: The session ID.
            
        Returns:
            Dict[str, Any]: The result of killing the process.
        """
        try:
            # Get session
            session = self._get_or_create_session(id)
            
            # In a real implementation, this would kill the process
            # For this prototype, we'll just update the session status
            
            session["status"] = "terminated"
            
            return {
                "success": True,
                "status": session["status"]
            }
        
        except Exception as e:
            self.logger.error(f"Error killing shell process: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
