"""
File Tool Provider for the tool integration framework.

This module implements the File Tool Provider which provides tools for
interacting with the file system.
"""

import os
import re
import glob
import logging
from typing import Dict, List, Any, Optional, Union, Callable

from tools.models import ToolCategory, ParameterType, ToolRegistry
from tools.provider import ToolProvider


class FileToolProvider(ToolProvider):
    """
    Provides tools for interacting with the file system.
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        """
        Initialize the FileToolProvider.
        
        Args:
            tool_registry: The tool registry to register tools with.
        """
        super().__init__(tool_registry)
    
    def register_tools(self) -> None:
        """Register file tools with the tool registry."""
        # File Read
        self.register_tool(
            self.create_tool(
                name="file_read",
                description="Read file content.",
                category=ToolCategory.FILE,
                function=self.file_read,
                parameters=[
                    self.create_parameter(
                        name="file",
                        description="Absolute path of the file to read",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="start_line",
                        description="(Optional) Starting line to read from, 0-based. If not specified, starts from beginning. Negative numbers count from end of file, -1 means last line.",
                        type=ParameterType.INTEGER,
                        required=False
                    ),
                    self.create_parameter(
                        name="end_line",
                        description="(Optional) Ending line number (exclusive). If not specified, reads entire file.",
                        type=ParameterType.INTEGER,
                        required=False
                    ),
                    self.create_parameter(
                        name="sudo",
                        description="(Optional) Whether to use sudo privileges, defaults to false",
                        type=ParameterType.BOOLEAN,
                        required=False,
                        default=False
                    )
                ]
            )
        )
        
        # File Write
        self.register_tool(
            self.create_tool(
                name="file_write",
                description="Overwrite or append content to a file.",
                category=ToolCategory.FILE,
                function=self.file_write,
                parameters=[
                    self.create_parameter(
                        name="file",
                        description="Absolute path of the file to overwrite or append to",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="content",
                        description="Text content to overwrite or append",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="append",
                        description="(Optional) Whether to use append mode, defaults to false",
                        type=ParameterType.BOOLEAN,
                        required=False,
                        default=False
                    ),
                    self.create_parameter(
                        name="leading_newline",
                        description="(Optional) Whether to add a leading newline, defaults to false if `append` is false, true if `append` is true.",
                        type=ParameterType.BOOLEAN,
                        required=False
                    ),
                    self.create_parameter(
                        name="trailing_newline",
                        description="(Optional) Whether to add a trailing newline, defaults to true as it is recommended best practice.",
                        type=ParameterType.BOOLEAN,
                        required=False,
                        default=True
                    ),
                    self.create_parameter(
                        name="sudo",
                        description="(Optional) Whether to use sudo privileges, defaults to false",
                        type=ParameterType.BOOLEAN,
                        required=False,
                        default=False
                    )
                ],
                has_side_effects=True
            )
        )
        
        # File String Replace
        self.register_tool(
            self.create_tool(
                name="file_str_replace",
                description="Replace specified string in a file.",
                category=ToolCategory.FILE,
                function=self.file_str_replace,
                parameters=[
                    self.create_parameter(
                        name="file",
                        description="Absolute path of the file to perform replacement on",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="old_str",
                        description="Original string to be replaced. Must match exactly in the source text.",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="new_str",
                        description="New string to replace with",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="sudo",
                        description="(Optional) Whether to use sudo privileges, defaults to false",
                        type=ParameterType.BOOLEAN,
                        required=False,
                        default=False
                    )
                ],
                has_side_effects=True
            )
        )
        
        # File Find in Content
        self.register_tool(
            self.create_tool(
                name="file_find_in_content",
                description="Search for matching text within file content.",
                category=ToolCategory.FILE,
                function=self.file_find_in_content,
                parameters=[
                    self.create_parameter(
                        name="file",
                        description="Absolute path of the file to search within",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="regex",
                        description="Regular expression pattern to match",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="sudo",
                        description="(Optional) Whether to use sudo privileges, defaults to false",
                        type=ParameterType.BOOLEAN,
                        required=False,
                        default=False
                    )
                ]
            )
        )
        
        # File Find by Name
        self.register_tool(
            self.create_tool(
                name="file_find_by_name",
                description="Find files by name pattern in specified directory.",
                category=ToolCategory.FILE,
                function=self.file_find_by_name,
                parameters=[
                    self.create_parameter(
                        name="path",
                        description="Absolute path of directory to search",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="glob",
                        description="Filename pattern using glob syntax wildcards",
                        type=ParameterType.STRING,
                        required=True
                    )
                ]
            )
        )
    
    # Tool implementations
    def file_read(
        self, 
        file: str, 
        start_line: Optional[int] = None, 
        end_line: Optional[int] = None, 
        sudo: bool = False
    ) -> Dict[str, Any]:
        """
        Read file content.
        
        Args:
            file: Absolute path of the file to read.
            start_line: Optional starting line (0-based).
            end_line: Optional ending line (exclusive).
            sudo: Whether to use sudo privileges.
            
        Returns:
            Dict[str, Any]: The file content and metadata.
        """
        try:
            # Check if file exists
            if not os.path.isfile(file):
                return {
                    "success": False,
                    "error": f"File not found: {file}"
                }
            
            # Read file content
            if sudo:
                # In a real implementation, this would use sudo
                # For this prototype, we'll just read the file directly
                with open(file, 'r') as f:
                    lines = f.readlines()
            else:
                with open(file, 'r') as f:
                    lines = f.readlines()
            
            # Apply line range if specified
            if start_line is not None:
                if start_line < 0:
                    start_line = len(lines) + start_line
                lines = lines[start_line:]
            
            if end_line is not None:
                if end_line < 0:
                    end_line = len(lines) + end_line
                lines = lines[:end_line - (start_line or 0)]
            
            content = ''.join(lines)
            
            return {
                "success": True,
                "content": content,
                "line_count": len(lines),
                "file_size": os.path.getsize(file)
            }
        
        except Exception as e:
            self.logger.error(f"Error reading file: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def file_write(
        self, 
        file: str, 
        content: str, 
        append: bool = False, 
        leading_newline: Optional[bool] = None, 
        trailing_newline: bool = True, 
        sudo: bool = False
    ) -> Dict[str, Any]:
        """
        Write content to a file.
        
        Args:
            file: Absolute path of the file to write to.
            content: Content to write.
            append: Whether to append to the file.
            leading_newline: Whether to add a leading newline.
            trailing_newline: Whether to add a trailing newline.
            sudo: Whether to use sudo privileges.
            
        Returns:
            Dict[str, Any]: The result of the write operation.
        """
        try:
            # Ensure directory exists
            directory = os.path.dirname(file)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Determine leading newline default based on append mode
            if leading_newline is None:
                leading_newline = append
            
            # Prepare content with optional newlines
            final_content = content
            if leading_newline:
                final_content = '\n' + final_content
            if trailing_newline and not content.endswith('\n'):
                final_content = final_content + '\n'
            
            # Write to file
            mode = 'a' if append else 'w'
            if sudo:
                # In a real implementation, this would use sudo
                # For this prototype, we'll just write to the file directly
                with open(file, mode) as f:
                    f.write(final_content)
            else:
                with open(file, mode) as f:
                    f.write(final_content)
            
            return {
                "success": True,
                "file": file,
                "bytes_written": len(final_content),
                "append": append
            }
        
        except Exception as e:
            self.logger.error(f"Error writing to file: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def file_str_replace(
        self, 
        file: str, 
        old_str: str, 
        new_str: str, 
        sudo: bool = False
    ) -> Dict[str, Any]:
        """
        Replace a string in a file.
        
        Args:
            file: Absolute path of the file.
            old_str: String to replace.
            new_str: Replacement string.
            sudo: Whether to use sudo privileges.
            
        Returns:
            Dict[str, Any]: The result of the replace operation.
        """
        try:
            # Check if file exists
            if not os.path.isfile(file):
                return {
                    "success": False,
                    "error": f"File not found: {file}"
                }
            
            # Read file content
            if sudo:
                # In a real implementation, this would use sudo
                # For this prototype, we'll just read/write the file directly
                with open(file, 'r') as f:
                    content = f.read()
            else:
                with open(file, 'r') as f:
                    content = f.read()
            
            # Check if old string exists
            if old_str not in content:
                return {
                    "success": False,
                    "error": f"String not found in file: {old_str}"
                }
            
            # Replace string
            new_content = content.replace(old_str, new_str)
            
            # Write back to file
            if sudo:
                # In a real implementation, this would use sudo
                # For this prototype, we'll just write to the file directly
                with open(file, 'w') as f:
                    f.write(new_content)
            else:
                with open(file, 'w') as f:
                    f.write(new_content)
            
            # Count occurrences
            occurrences = content.count(old_str)
            
            return {
                "success": True,
                "file": file,
                "occurrences": occurrences,
                "bytes_before": len(content),
                "bytes_after": len(new_content)
            }
        
        except Exception as e:
            self.logger.error(f"Error replacing string in file: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def file_find_in_content(
        self, 
        file: str, 
        regex: str, 
        sudo: bool = False
    ) -> Dict[str, Any]:
        """
        Find text in a file using regex.
        
        Args:
            file: Absolute path of the file.
            regex: Regular expression to search for.
            sudo: Whether to use sudo privileges.
            
        Returns:
            Dict[str, Any]: The search results.
        """
        try:
            # Check if file exists
            if not os.path.isfile(file):
                return {
                    "success": False,
                 <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>