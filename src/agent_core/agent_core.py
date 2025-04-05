"""
Main module for the Agent Core component.

This module initializes and connects all the components of the Agent Core.
"""

import logging
from typing import Dict, Any, Optional, Callable

from agent_core.agent_loop_controller import AgentLoopController
from agent_core.event_stream_processor import EventStreamProcessor
from agent_core.prompt_manager import PromptManager
from agent_core.state_manager import AgentStateManager
from agent_core.tool_manager import ToolManager
from agent_core.models import LLMRequest, LLMResponse


class AgentCore:
    """
    Main class for the Agent Core component that initializes and connects
    all the components.
    """

    def __init__(self, llm_service: Callable[[LLMRequest], LLMResponse]):
        """
        Initialize the AgentCore.

        Args:
            llm_service: Function that calls the LLM service.
        """
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.event_processor = EventStreamProcessor()
        self.prompt_manager = PromptManager()
        self.state_manager = AgentStateManager()
        self.tool_manager = ToolManager()
        
        # Initialize agent loop controller
        self.loop_controller = AgentLoopController(
            event_processor=self.event_processor,
            prompt_manager=self.prompt_manager,
            state_manager=self.state_manager,
            tool_manager=self.tool_manager,
            llm_service=llm_service
        )
        
        self.logger.info("AgentCore initialized successfully")

    def process_request(self, user_request: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Process a user request.

        Args:
            user_request: The user's request.
            max_iterations: Maximum number of iterations to run.

        Returns:
            Dict[str, Any]: Result of the processing.
        """
        self.logger.info(f"Processing user request: {user_request[:50]}...")
        
        # Initialize agent loop
        init_success = self.loop_controller.initialize_loop(user_request)
        if not init_success:
            self.logger.error("Failed to initialize agent loop")
            return {
                "success": False,
                "error": "Failed to initialize agent loop"
            }
        
        # Execute agent loop
        result = self.loop_controller.execute_loop(max_iterations)
        
        self.logger.info(f"Request processing completed with success={result['success']}")
        return result

    def register_tool(
        self,
        tool_id: str,
        name: str,
        description: str,
        parameters: list,
        return_type: str,
        executor: Callable,
        validator: Optional[Callable] = None
    ) -> bool:
        """
        Register a tool with the agent.

        Args:
            tool_id: Unique identifier for the tool.
            name: Display name of the tool.
            description: Description of what the tool does.
            parameters: List of parameter definitions.
            return_type: Type of value returned by the tool.
            executor: Function that executes the tool.
            validator: Optional function that validates tool parameters.

        Returns:
            bool: True if the tool was registered successfully, False otherwise.
        """
        from agent_core.models import Tool
        
        tool = Tool(
            tool_id=tool_id,
            name=name,
            description=description,
            parameters=parameters,
            return_type=return_type
        )
        
        success = self.tool_manager.register_tool(tool, executor, validator)
        
        if success:
            # Also add to state manager
            self.state_manager.add_tool(tool)
            self.logger.info(f"Tool registered successfully: {tool_id}")
        else:
            self.logger.error(f"Failed to register tool: {tool_id}")
        
        return success

    def add_system_instruction(
        self,
        instruction_id: str,
        instruction_text: str,
        priority: int,
        category: str
    ) -> bool:
        """
        Add a system instruction for the LLM.

        Args:
            instruction_id: Unique identifier for the instruction.
            instruction_text: The instruction text.
            priority: Priority of the instruction (higher values = higher priority).
            category: Category of the instruction.

        Returns:
            bool: True if the instruction was added successfully, False otherwise.
        """
        from agent_core.models import SystemInstruction
        
        instruction = SystemInstruction(
            instruction_id=instruction_id,
            instruction_text=instruction_text,
            priority=priority,
            category=category
        )
        
        success = self.prompt_manager.add_system_instruction(instruction)
        
        if success:
            self.logger.info(f"System instruction added successfully: {instruction_id}")
        else:
            self.logger.error(f"Failed to add system instruction: {instruction_id}")
        
        return success

    def add_prompt_template(
        self,
        template_id: str,
        template_text: str,
        variables: list,
        version: str
    ) -> bool:
        """
        Add a prompt template.

        Args:
            template_id: Unique identifier for the template.
            template_text: The template text with variable placeholders.
            variables: List of variable names used in the template.
            version: Version of the template.

        Returns:
            bool: True if the template was added successfully, False otherwise.
        """
        from agent_core.models import PromptTemplate
        
        template = PromptTemplate(
            template_id=template_id,
            template_text=template_text,
            variables=variables,
            version=version
        )
        
        success = self.prompt_manager.add_template(template)
        
        if success:
            self.logger.info(f"Prompt template added successfully: {template_id}")
        else:
            self.logger.error(f"Failed to add prompt template: {template_id}")
        
        return success

    def get_event_history(self, count: int = 10) -> list:
        """
        Get recent events from the event history.

        Args:
            count: Number of recent events to retrieve.

        Returns:
            list: List of recent events.
        """
        events = self.event_processor.get_latest_events(count)
        return [event.__dict__ for event in events]

    def get_agent_state(self) -> Dict[str, Any]:
        """
        Get the current agent state.

        Returns:
            Dict[str, Any]: The current agent state.
        """
        state = self.state_manager.get_state()
        return {
            "session_id": state.session_id,
            "user_context": state.user_context.__dict__,
            "execution_context": {
                "current_plan": state.execution_context.current_plan.__dict__ if state.execution_context.current_plan else None,
                "execution_history_length": len(state.execution_context.execution_history),
                "active_tools": state.execution_context.active_tools,
                "last_llm_response": state.execution_context.last_llm_response
            },
            "memory_context": {
                "short_term_size": len(state.memory_context.short_term),
                "long_term_size": len(state.memory_context.long_term)
            },
            "tool_context": {
                "available_tools_count": len(state.tool_context.available_tools),
                "tool_usage_history_size": len(state.tool_context.tool_usage_history)
            }
        }
