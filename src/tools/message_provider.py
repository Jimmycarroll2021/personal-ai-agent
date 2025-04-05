"""
Message Tool Provider for the tool integration framework.

This module implements the Message Tool Provider which provides tools for
communicating with users.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Callable

from tools.models import ToolCategory, ParameterType, ToolRegistry
from tools.provider import ToolProvider


class MessageToolProvider(ToolProvider):
    """
    Provides tools for communicating with users.
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        """
        Initialize the MessageToolProvider.
        
        Args:
            tool_registry: The tool registry to register tools with.
        """
        super().__init__(tool_registry)
    
    def register_tools(self) -> None:
        """Register message tools with the tool registry."""
        # Notify User
        self.register_tool(
            self.create_tool(
                name="message_notify_user",
                description="Send a message to user.",
                category=ToolCategory.MESSAGE,
                function=self.message_notify_user,
                parameters=[
                    self.create_parameter(
                        name="text",
                        description="Message text to display to user. e.g. \"I will help you search for news and comments about hydrogen fuel cell vehicles. This may take a few minutes.\"",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="attachments",
                        description="(Optional) List of attachments to show to user, must include all files mentioned in message text.\nCan be absolute path of single file or URL, e.g., \"/home/example/report.pdf\" or \"http://example.com/webpage\".\nCan also be list of multiple absolute file paths or URLs, e.g., [\"/home/example/part_1.md\", \"/home/example/part_2.md\"].\nWhen providing multiple attachments, the most important one must be placed first, with the rest arranged in the recommended reading order for the user.",
                        type=ParameterType.ARRAY,
                        required=False,
                        items={"type": "string"}
                    )
                ]
            )
        )
        
        # Ask User
        self.register_tool(
            self.create_tool(
                name="message_ask_user",
                description="Ask user a question and wait for response.",
                category=ToolCategory.MESSAGE,
                function=self.message_ask_user,
                parameters=[
                    self.create_parameter(
                        name="text",
                        description="Question text to present to user",
                        type=ParameterType.STRING,
                        required=True
                    ),
                    self.create_parameter(
                        name="attachments",
                        description="(Optional) List of question-related files or reference materials, must include all files mentioned in message text.\nCan be absolute path of single file or URL, e.g., \"/home/example/report.pdf\" or \"http://example.com/webpage\".\nCan also be list of multiple absolute file paths or URLs, e.g., [\"/home/example/part_1.md\", \"/home/example/part_2.md\"].\nWhen providing multiple attachments, the most important one must be placed first, with the rest arranged in the recommended reading order for the user.",
                        type=ParameterType.ARRAY,
                        required=False,
                        items={"type": "string"}
                    ),
                    self.create_parameter(
                        name="suggest_user_takeover",
                        description="(Optional) Suggested operation for user takeover. Defaults to \"none\", indicating no takeover is suggested; \"browser\" indicates recommending temporary browser control for specific steps.",
                        type=ParameterType.STRING,
                        required=False,
                        default="none",
                        enum=["none", "browser"]
                    )
                ]
            )
        )
    
    # Tool implementations
    def message_notify_user(
        self, 
        text: str, 
        attachments: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Send a notification message to the user.
        
        Args:
            text: The message text.
            attachments: Optional attachments.
            
        Returns:
            Dict[str, Any]: The result of sending the message.
        """
        try:
            # Normalize attachments to list
            attachment_list = []
            if attachments:
                if isinstance(attachments, str):
                    attachment_list = [attachments]
                else:
                    attachment_list = attachments
            
            # In a real implementation, this would send a message to the user
            # For this prototype, we'll return a simulated response
            
            return {
                "success": True,
                "message_type": "notification",
                "text": text,
                "attachments": attachment_list,
                "attachment_count": len(attachment_list)
            }
        
        except Exception as e:
            self.logger.error(f"Error sending notification to user: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def message_ask_user(
        self, 
        text: str, 
        attachments: Optional[Union[str, List[str]]] = None,
        suggest_user_takeover: str = "none"
    ) -> Dict[str, Any]:
        """
        Ask the user a question and wait for response.
        
        Args:
            text: The question text.
            attachments: Optional attachments.
            suggest_user_takeover: Suggested operation for user takeover.
            
        Returns:
            Dict[str, Any]: The result of asking the question, including the user's response.
        """
        try:
            # Normalize attachments to list
            attachment_list = []
            if attachments:
                if isinstance(attachments, str):
                    attachment_list = [attachments]
                else:
                    attachment_list = attachments
            
            # Validate takeover suggestion
            valid_takeover_options = ["none", "browser"]
            if suggest_user_takeover not in valid_takeover_options:
                return {
                    "success": False,
                    "error": f"Invalid takeover suggestion: {suggest_user_takeover}. Must be one of: {', '.join(valid_takeover_options)}"
                }
            
            # In a real implementation, this would ask the user and wait for response
            # For this prototype, we'll return a simulated response
            
            # Simulate user response
            simulated_response = "This is a simulated user response."
            
            return {
                "success": True,
                "message_type": "question",
                "text": text,
                "attachments": attachment_list,
                "attachment_count": len(attachment_list),
                "suggest_user_takeover": suggest_user_takeover,
                "user_response": simulated_response
            }
        
        except Exception as e:
            self.logger.error(f"Error asking user: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
