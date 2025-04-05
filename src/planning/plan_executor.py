"""
Plan Executor for the Planning Module component.

This module implements the Plan Executor which executes plans by coordinating
with the Agent Core and Tool Manager.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

from planning.models import Plan, PlanStep, StepStatus, PlanStatus


class PlanExecutor:
    """
    Executes plans by coordinating with the Agent Core and Tool Manager.
    """

    def __init__(self, tool_manager, event_processor):
        """
        Initialize the PlanExecutor.

        Args:
            tool_manager: The tool manager for executing tool calls.
            event_processor: The event processor for logging events.
        """
        self.tool_manager = tool_manager
        self.event_processor = event_processor
        self.logger = logging.getLogger(__name__)

    def execute_plan(self, plan: Plan) -> Dict[str, Any]:
        """
        Execute a plan.

        Args:
            plan: The plan to execute.

        Returns:
            Dict[str, Any]: The result of the execution.
        """
        self.logger.info(f"Starting execution of plan: {plan.plan_id}")
        
        # Update plan status
        plan.status = PlanStatus.IN_PROGRESS
        plan.updated_at = datetime.now()
        
        # Track execution results
        execution_results = {
            "plan_id": plan.plan_id,
            "start_time": datetime.now(),
            "end_time": None,
            "success": False,
            "steps_completed": 0,
            "steps_failed": 0,
            "step_results": {}
        }
        
        try:
            # Execute each step in order
            for step in plan.steps:
                # Check if dependencies are satisfied
                if not self._check_dependencies(step, plan, execution_results):
                    step.status = StepStatus.SKIPPED
                    execution_results["step_results"][step.step_id] = {
                        "status": "skipped",
                        "reason": "Dependencies not satisfied"
                    }
                    continue
                
                # Execute step
                step_result = self._execute_step(step, plan)
                
                # Update step status
                if step_result["success"]:
                    step.status = StepStatus.COMPLETED
                    execution_results["steps_completed"] += 1
                else:
                    step.status = StepStatus.FAILED
                    execution_results["steps_failed"] += 1
                
                # Store step result
                execution_results["step_results"][step.step_id] = step_result
                
                # If step failed and it's critical, stop execution
                if not step_result["success"] and self._is_critical_step(step, plan):
                    self.logger.warning(f"Critical step {step.step_id} failed, stopping execution")
                    plan.status = PlanStatus.FAILED
                    break
            
            # Update plan status if not already failed
            if plan.status != PlanStatus.FAILED:
                if execution_results["steps_failed"] > 0:
                    plan.status = PlanStatus.FAILED
                else:
                    plan.status = PlanStatus.COMPLETED
            
            # Update execution results
            execution_results["success"] = (plan.status == PlanStatus.COMPLETED)
            
        except Exception as e:
            self.logger.error(f"Error executing plan: {str(e)}")
            plan.status = PlanStatus.FAILED
            execution_results["success"] = False
            execution_results["error"] = str(e)
        
        # Update final timestamps
        plan.updated_at = datetime.now()
        execution_results["end_time"] = datetime.now()
        
        self.logger.info(f"Plan execution completed with status: {plan.status}")
        return execution_results

    def _execute_step(self, step: PlanStep, plan: Plan) -> Dict[str, Any]:
        """
        Execute a single plan step.

        Args:
            step: The step to execute.
            plan: The parent plan.

        Returns:
            Dict[str, Any]: The result of the step execution.
        """
        self.logger.info(f"Executing step {step.step_id}: {step.description}")
        
        # Update step status
        step.status = StepStatus.IN_PROGRESS
        
        # Prepare result structure
        step_result = {
            "step_id": step.step_id,
            "start_time": datetime.now(),
            "end_time": None,
            "success": False,
            "action_taken": None,
            "result": None,
            "error": None
        }
        
        try:
            # Determine action type
            action_type = step.action.get("type", "unknown")
            
            if action_type == "tool_call":
                # Execute tool call
                tool_id = step.action.get("tool_id")
                parameters = step.action.get("parameters", {})
                
                # Create tool call
                tool_call = self.tool_manager.create_tool_call(tool_id, parameters)
                
                # Log action
                step_result["action_taken"] = {
                    "type": "tool_call",
                    "tool_id": tool_id,
                    "parameters": parameters
                }
                
                # Execute tool
                tool_result = self.tool_manager.execute_tool(tool_call)
                
                # Store result
                step_result["success"] = tool_result.success
                step_result["result"] = tool_result.result
                
                if not tool_result.success:
                    step_result["error"] = tool_result.error
            
            elif action_type == "goal" or action_type == "subgoal":
                # This is a goal/subgoal step, mark as successful if all substeps are completed
                step_result["action_taken"] = {
                    "type": action_type
                }
                
                # Check if all substeps are completed
                substeps_completed = True
                for other_step in plan.steps:
                    if step.step_id in other_step.dependencies and other_step.status != StepStatus.COMPLETED:
                        substeps_completed = False
                        break
                
                step_result["success"] = substeps_completed
                step_result["result"] = {
                    "substeps_completed": substeps_completed
                }
            
            else:
                # Unknown action type, log warning
                self.logger.warning(f"Unknown action type: {action_type}")
                step_result["action_taken"] = {
                    "type": "unknown",
                    "details": step.action
                }
                step_result["success"] = False
                step_result["error"] = f"Unknown action type: {action_type}"
        
        except Exception as e:
            self.logger.error(f"Error executing step {step.step_id}: {str(e)}")
            step_result["success"] = False
            step_result["error"] = str(e)
        
        # Update final timestamp
        step_result["end_time"] = datetime.now()
        
        # Store result in step
        step.result = step_result
        
        self.logger.info(f"Step {step.step_id} execution completed with success={step_result['success']}")
        return step_result

    def _check_dependencies(self, step: PlanStep, plan: Plan, execution_results: Dict[str, Any]) -> bool:
        """
        Check if all dependencies of a step are satisfied.

        Args:
            step: The step to check.
            plan: The parent plan.
            execution_results: The current execution results.

        Returns:
            bool: True if all dependencies are satisfied, False otherwise.
        """
        if not step.dependencies:
            return True
        
        for dep_id in step.dependencies:
            # Find the dependency step
            dep_step = next((s for s in plan.steps if s.step_id == dep_id), None)
            
            if not dep_step:
                self.logger.warning(f"Dependency {dep_id} not found for step {step.step_id}")
                return False
            
            # Check if dependency was completed successfully
            if dep_step.status != StepStatus.COMPLETED:
                return False
            
            # Double-check in execution results
            if dep_id in execution_results["step_results"]:
                if execution_results["step_results"][dep_id]["status"] != "completed":
                    return False
        
        return True

    def _is_critical_step(self, step: PlanStep, plan: Plan) -> bool:
        """
        Determine if a step is critical for the plan.

        Args:
            step: The step to check.
            plan: The parent plan.

        Returns:
            bool: True if the step is critical, False otherwise.
        """
        # Check if other steps depend on this step
        for other_step in plan.steps:
            if step.step_id in other_step.dependencies:
                return True
        
        # Check if this is a high-level goal step
        if step.action.get("type") == "goal":
            return True
        
        return False

    def execute_step(self, step: PlanStep, plan: Plan) -> Dict[str, Any]:
        """
        Execute a single plan step independently.

        Args:
            step: The step to execute.
            plan: The parent plan.

        Returns:
            Dict[str, Any]: The result of the step execution.
        """
        return self._execute_step(step, plan)

    def verify_step_completion(self, step: PlanStep, result: Dict[str, Any]) -> bool:
        """
        Verify if a step was completed successfully.

        Args:
            step: The step to verify.
            result: The step execution result.

        Returns:
            bool: True if the step was completed successfully, False otherwise.
        """
        # Basic verification based on result success flag
        if not result.get("success", False):
            return False
        
        # Check verification method if specified
        verification_method = step.verification_method.get("type")
        
        if verification_method == "observation_match":
            # Check if result matches expected observation
            expected = step.expected_outcome
            actual = str(result.get("result", ""))
            
            # Simple string matching (could be more sophisticated)
            return expected.lower() in actual.lower()
        
        elif verification_method == "all_substeps_complete":
            # This should be verified by the execute_step method
            return result.get("success", False)
        
        # Default to using the success flag
        return result.get("success", False)

    def update_plan_status(self, plan: Plan) -> None:
        """
        Update the status of a plan based on its steps.

        Args:
            plan: The plan to update.
        """
        # Count steps by status
        total_steps = len(plan.steps)
        completed_steps = sum(1 for step in plan.steps if step.status == StepStatus.COMPLETED)
        failed_steps = sum(1 for step in plan.steps if step.status == StepStatus.FAILED)
        in_progress_steps = sum(1 for step in plan.steps if step.status == StepStatus.IN_PROGRESS)
        
        # Update plan status
        if failed_steps > 0:
            plan.status = PlanStatus.FAILED
        elif completed_steps == total_steps:
            plan.status = PlanStatus.COMPLETED
        elif in_progress_steps > 0:
            plan.status = PlanStatus.IN_PROGRESS
        else:
            plan.status = PlanStatus.CREATED
        
        # Update timestamp
        plan.updated_at = datetime.now()
