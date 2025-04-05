"""
Agent Loop Controller for the Agent Core component.

This module implements the Agent Loop Controller which manages the main agent loop,
coordinating between different components and handling the flow of execution.
"""

import logging
from typing import Dict, List, Any, Optional, Callable

from agent_core.models import (
    AgentLoopState, Event, EventType, Plan, PlanStep, 
    ToolCall, ToolResult, LLMRequest, LLMResponse
)
from agent_core.event_stream_processor import EventStreamProcessor
from agent_core.prompt_manager import PromptManager
from agent_core.state_manager import AgentStateManager
from agent_core.tool_manager import ToolManager


class AgentLoopController:
    """
    Manages the main agent loop, coordinating between different components
    and handling the flow of execution.
    """

    def __init__(
        self,
        event_processor: EventStreamProcessor,
        prompt_manager: PromptManager,
        state_manager: AgentStateManager,
        tool_manager: ToolManager,
        llm_service: Callable[[LLMRequest], LLMResponse]
    ):
        """
        Initialize the AgentLoopController.

        Args:
            event_processor: The event stream processor.
            prompt_manager: The prompt manager.
            state_manager: The agent state manager.
            tool_manager: The tool manager.
            llm_service: Function that calls the LLM service.
        """
        self.event_processor = event_processor
        self.prompt_manager = prompt_manager
        self.state_manager = state_manager
        self.tool_manager = tool_manager
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)
        self.loop_state = self._create_default_loop_state()

    def initialize_loop(self, user_request: str) -> bool:
        """
        Initialize the agent loop with a user request.

        Args:
            user_request: The user's request.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            # Reset state for new request
            self.state_manager.reset_state()
            
            # Create initial loop state
            self.loop_state = AgentLoopState(
                user_request=user_request,
                current_step=0,
                execution_plan=[],
                execution_history=[],
                is_complete=False,
                error_state=None
            )
            
            # Add user request event
            event = self.event_processor.create_event(
                event_type=EventType.USER_MESSAGE,
                source="user",
                payload={"message": user_request}
            )
            self.event_processor.add_event(event)
            
            # Update execution history
            self.loop_state.execution_history.append(event)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize agent loop: {str(e)}")
            return False

    def execute_loop(self, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Execute the agent loop for a maximum number of iterations.

        Args:
            max_iterations: Maximum number of iterations to run.

        Returns:
            Dict[str, Any]: Result of the execution.
        """
        iteration = 0
        
        while iteration < max_iterations and not self.loop_state.is_complete:
            try:
                # Execute one iteration of the loop
                self._execute_iteration()
                iteration += 1
                
                # Check if task is complete
                if self._check_completion():
                    self.loop_state.is_complete = True
                    self.logger.info("Task completed successfully")
            except Exception as e:
                self.logger.error(f"Error in agent loop iteration {iteration}: {str(e)}")
                self.loop_state.error_state = {
                    "iteration": iteration,
                    "error": str(e)
                }
                break
        
        # Prepare result
        result = {
            "success": self.loop_state.is_complete,
            "iterations": iteration,
            "error": self.loop_state.error_state
        }
        
        if self.loop_state.is_complete:
            # Add final response
            result["response"] = self._generate_final_response()
        
        return result

    def _execute_iteration(self) -> None:
        """Execute one iteration of the agent loop."""
        # 1. Analyze current state and events
        current_state = self.state_manager.get_state()
        recent_events = self.event_processor.get_latest_events(10)
        
        # 2. Generate or update plan if needed
        if not self.loop_state.execution_plan:
            self._generate_plan()
        
        # 3. Determine next action
        next_action = self._determine_next_action()
        
        # 4. Execute action
        action_result = self._execute_action(next_action)
        
        # 5. Process result
        self._process_action_result(next_action, action_result)
        
        # 6. Update state
        self.loop_state.current_step += 1

    def _generate_plan(self) -> None:
        """Generate an execution plan for the current request."""
        # Prepare prompt for planning
        planning_prompt = self.prompt_manager.construct_full_prompt(
            user_input=self.loop_state.user_request,
            system_categories=["planning"],
            history=[],
            tools=[]
        )
        
        # Call LLM for planning
        llm_request = LLMRequest(
            prompt=planning_prompt,
            temperature=0.2,  # Lower temperature for planning
            max_tokens=1000,
            stop_sequences=[],
            model_params={"planning_mode": True}
        )
        
        llm_response = self.llm_service(llm_request)
        
        # Parse plan from LLM response
        plan_steps = self._parse_plan_from_llm_response(llm_response.text)
        
        # Update loop state with plan
        self.loop_state.execution_plan = plan_steps
        
        # Create plan event
        plan_event = self.event_processor.create_event(
            event_type=EventType.PLAN_UPDATE,
            source="planner",
            payload={"plan": [step.__dict__ for step in plan_steps]}
        )
        self.event_processor.add_event(plan_event)
        self.loop_state.execution_history.append(plan_event)

    def _determine_next_action(self) -> Dict[str, Any]:
        """
        Determine the next action to take.

        Returns:
            Dict[str, Any]: The next action to execute.
        """
        # Get current plan step
        current_step_index = self.loop_state.current_step
        if current_step_index < len(self.loop_state.execution_plan):
            current_step = self.loop_state.execution_plan[current_step_index]
            return current_step.action
        
        # If no plan step available, use LLM to decide next action
        recent_events = self.event_processor.get_latest_events(5)
        tools = [tool.__dict__ for tool in self.tool_manager.get_all_tools()]
        
        # Prepare prompt for action selection
        action_prompt = self.prompt_manager.construct_full_prompt(
            user_input="What should I do next?",
            system_categories=["action_selection"],
            history=[{"role": "system", "content": str(event.__dict__)} for event in recent_events],
            tools=tools
        )
        
        # Call LLM for action selection
        llm_request = LLMRequest(
            prompt=action_prompt,
            temperature=0.5,
            max_tokens=500,
            stop_sequences=[],
            model_params={}
        )
        
        llm_response = self.llm_service(llm_request)
        
        # Parse action from LLM response
        action = self._parse_action_from_llm_response(llm_response.text)
        return action

    def _execute_action(self, action: Dict[str, Any]) -> Any:
        """
        Execute an action.

        Args:
            action: The action to execute.

        Returns:
            Any: The result of the action.
        """
        action_type = action.get("type")
        
        if action_type == "tool_call":
            # Execute tool call
            tool_id = action.get("tool_id")
            parameters = action.get("parameters", {})
            
            tool_call = self.tool_manager.create_tool_call(tool_id, parameters)
            
            # Create tool call event
            tool_call_event = self.event_processor.create_event(
                event_type=EventType.TOOL_CALL,
                source="agent",
                payload={"tool_call": tool_call.__dict__}
            )
            self.event_processor.add_event(tool_call_event)
            self.loop_state.execution_history.append(tool_call_event)
            
            # Execute tool
            tool_result = self.tool_manager.execute_tool(tool_call)
            
            # Create tool result event
            tool_result_event = self.event_processor.create_event(
                event_type=EventType.TOOL_RESULT,
                source="tool_manager",
                payload={"tool_result": tool_result.__dict__}
            )
            self.event_processor.add_event(tool_result_event)
            self.loop_state.execution_history.append(tool_result_event)
            
            return tool_result
        
        elif action_type == "llm_call":
            # Call LLM directly
            prompt = action.get("prompt")
            temperature = action.get("temperature", 0.7)
            max_tokens = action.get("max_tokens", 500)
            
            llm_request = LLMRequest(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stop_sequences=[],
                model_params={}
            )
            
            llm_response = self.llm_service(llm_request)
            return llm_response
        
        else:
            # Unknown action type
            self.logger.warning(f"Unknown action type: {action_type}")
            return None

    def _process_action_result(self, action: Dict[str, Any], result: Any) -> None:
        """
        Process the result of an action.

        Args:
            action: The action that was executed.
            result: The result of the action.
        """
        action_type = action.get("type")
        
        if action_type == "tool_call" and isinstance(result, ToolResult):
            # Update tool usage history
            self.state_manager.record_tool_usage(
                tool_id=action.get("tool_id"),
                usage_data={
                    "parameters": action.get("parameters", {}),
                    "success": result.success,
                    "error": result.error
                }
            )
            
            # If tool call failed, log error
            if not result.success:
                self.logger.warning(f"Tool call failed: {result.error}")
        
        elif action_type == "llm_call" and isinstance(result, LLMResponse):
            # Update last LLM response in execution context
            current_plan = self.state_manager.execution_context.current_plan
            execution_history = self.state_manager.execution_context.execution_history
            active_tools = self.state_manager.execution_context.active_tools
            
            self.state_manager.update_execution_context(
                current_plan=current_plan,
                execution_history=execution_history,
                active_tools=active_tools,
                last_llm_response={
                    "text": result.text,
                    "usage": result.usage.__dict__,
                    "model_info": result.model_info.__dict__
                }
            )

    def _check_completion(self) -> bool:
        """
        Check if the task is complete.

        Returns:
            bool: True if the task is complete, False otherwise.
        """
        # If there's a plan, check if all steps are completed
        if self.loop_state.execution_plan:
            return self.loop_state.current_step >= len(self.loop_state.execution_plan)
        
        # Otherwise, use heuristics to determine completion
        recent_events = self.event_processor.get_latest_events(3)
        
        # Check for explicit completion markers in recent events
        for event in recent_events:
            if event.event_type == EventType.SYSTEM_MESSAGE:
                payload = event.payload
                if payload.get("type") == "completion" and payload.get("is_complete", False):
                    return True
        
        return False

    def _generate_final_response(self) -> Dict[str, Any]:
        """
        Generate the final response for the user.

        Returns:
            Dict[str, Any]: The final response.
        """
        # Prepare prompt for final response
        recent_events = self.event_processor.get_latest_events(10)
        
        response_prompt = self.prompt_manager.construct_full_prompt(
            user_input="Generate final response",
            system_categories=["response_generation"],
            history=[{"role": "system", "content": str(event.__dict__)} for event in recent_events],
            tools=[]
        )
        
        # Call LLM for response generation
        llm_request = LLMRequest(
            prompt=response_prompt,
            temperature=0.7,
            max_tokens=1000,
            stop_sequences=[],
            model_params={}
        )
        
        llm_response = self.llm_service(llm_request)
        
        # Parse response
        return {
            "text": llm_response.text,
            "usage": llm_response.usage.__dict__,
            "model_info": llm_response.model_info.__dict__
        }

    def _parse_plan_from_llm_response(self, response_text: str) -> List[PlanStep]:
        """
        Parse a plan from an LLM response.

        Args:
            response_text: The LLM response text.

        Returns:
            List[PlanStep]: The parsed plan steps.
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated parsing
        
        plan_steps = []
        lines = response_text.strip().split('\n')
        
        current_step = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with a step number
            if line[0].isdigit() and '.' in line[:5]:
                # New step
                if current_step:
                    plan_steps.append(current_step)
                
                step_id = f"step_{len(plan_steps) + 1}"
                description = line.split('.', 1)[1].strip()
                
                current_step = PlanStep(
                    step_id=step_id,
                    description=description,
                    action={"type": "unknown"},
                    expected_outcome="",
                    verification_method={},
                    dependencies=[]
                )
            elif current_step:
                # Add to current step description
                current_step.description += f" {line}"
        
        # Add the last step
        if current_step:
            plan_steps.append(current_step)
        
        return plan_steps

    def _parse_action_from_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse an action from an LLM response.

        Args:
            response_text: The LLM response text.

        Returns:
            Dict[str, Any]: The parsed action.
        """
        # This is a simplified imp<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>