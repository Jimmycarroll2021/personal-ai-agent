"""
Planning Module main class for the personal AI agent.

This module implements the main Planning Module class that integrates all planning
components and provides a unified interface for the Agent Core.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional

from planning.models import (
    Plan, PlanStep, PlanningStrategy, PlanStatus, StepStatus,
    PlanningContext, PlanningResult, PlanningTask
)
from planning.plan_generator import PlanGenerator
from planning.plan_executor import PlanExecutor
from planning.plan_evaluator import PlanEvaluator


class PlanningModule:
    """
    Main Planning Module class that integrates all planning components and
    provides a unified interface for the Agent Core.
    """

    def __init__(self, llm_service, tool_manager, event_processor):
        """
        Initialize the PlanningModule.

        Args:
            llm_service: Service for calling the LLM.
            tool_manager: The tool manager for executing tool calls.
            event_processor: The event processor for logging events.
        """
        self.llm_service = llm_service
        self.tool_manager = tool_manager
        self.event_processor = event_processor
        
        # Initialize components
        self.plan_generator = PlanGenerator(llm_service)
        self.plan_executor = PlanExecutor(tool_manager, event_processor)
        self.plan_evaluator = PlanEvaluator(llm_service)
        
        # Initialize storage
        self.plans = {}  # plan_id -> Plan
        self.tasks = {}  # task_id -> PlanningTask
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("PlanningModule initialized")

    def create_task(
        self,
        description: str,
        requirements: List[str] = None,
        constraints: List[str] = None,
        priority: int = 1,
        deadline: Any = None
    ) -> str:
        """
        Create a new planning task.

        Args:
            description: Description of the task.
            requirements: List of requirements for the task.
            constraints: List of constraints for the task.
            priority: Priority of the task (higher = more important).
            deadline: Optional deadline for the task.

        Returns:
            str: The ID of the created task.
        """
        task_id = f"task_{str(uuid.uuid4())[:8]}"
        
        task = PlanningTask(
            task_id=task_id,
            description=description,
            requirements=requirements or [],
            constraints=constraints or [],
            priority=priority,
            deadline=deadline
        )
        
        self.tasks[task_id] = task
        self.logger.info(f"Created task: {task_id}")
        
        return task_id

    def generate_plan(
        self,
        task_id: str,
        available_tools: List[Dict[str, Any]],
        strategy: PlanningStrategy = PlanningStrategy.CHAIN_OF_THOUGHT,
        relevant_knowledge: Dict[str, Any] = None
    ) -> str:
        """
        Generate a plan for a task.

        Args:
            task_id: ID of the task to plan for.
            available_tools: List of available tools.
            strategy: Planning strategy to use.
            relevant_knowledge: Relevant knowledge for planning.

        Returns:
            str: The ID of the generated plan.

        Raises:
            ValueError: If the task is not found.
        """
        # Check if task exists
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        task = self.tasks[task_id]
        
        # Create planning context
        context = PlanningContext(
            user_request=task.description,
            available_tools=available_tools,
            constraints={"requirements": task.requirements, "constraints": task.constraints},
            previous_plans=[p for p in self.plans.values() if p.task_id == task_id],
            relevant_knowledge=relevant_knowledge or {}
        )
        
        # Generate plan
        result = self.plan_generator.generate_plan(context, strategy)
        
        if not result.success or not result.plan:
            self.logger.error(f"Failed to generate plan for task {task_id}: {result.error}")
            return None
        
        # Store plan
        plan = result.plan
        self.plans[plan.plan_id] = plan
        
        self.logger.info(f"Generated plan {plan.plan_id} for task {task_id} using {strategy.value} strategy")
        return plan.plan_id

    def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute a plan.

        Args:
            plan_id: ID of the plan to execute.

        Returns:
            Dict[str, Any]: The result of the execution.

        Raises:
            ValueError: If the plan is not found.
        """
        # Check if plan exists
        if plan_id not in self.plans:
            raise ValueError(f"Plan not found: {plan_id}")
        
        plan = self.plans[plan_id]
        
        # Execute plan
        result = self.plan_executor.execute_plan(plan)
        
        # Update plan status
        self.plan_executor.update_plan_status(plan)
        
        self.logger.info(f"Executed plan {plan_id} with success={result['success']}")
        return result

    def evaluate_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Evaluate a plan.

        Args:
            plan_id: ID of the plan to evaluate.

        Returns:
            Dict[str, Any]: The evaluation result.

        Raises:
            ValueError: If the plan is not found.
        """
        # Check if plan exists
        if plan_id not in self.plans:
            raise ValueError(f"Plan not found: {plan_id}")
        
        plan = self.plans[plan_id]
        
        # Evaluate plan
        evaluation = self.plan_evaluator.evaluate_plan(plan)
        
        self.logger.info(f"Evaluated plan {plan_id} with score={evaluation.score}")
        return {
            "plan_id": evaluation.plan_id,
            "score": evaluation.score,
            "strengths": evaluation.strengths,
            "weaknesses": evaluation.weaknesses,
            "improvement_suggestions": evaluation.improvement_suggestions
        }

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a plan by ID.

        Args:
            plan_id: ID of the plan to get.

        Returns:
            Optional[Dict[str, Any]]: The plan if found, None otherwise.
        """
        if plan_id not in self.plans:
            return None
        
        plan = self.plans[plan_id]
        
        # Convert to dictionary
        return {
            "plan_id": plan.plan_id,
            "task_id": plan.task_id,
            "name": plan.name,
            "description": plan.description,
            "strategy": plan.strategy.value,
            "status": plan.status.value,
            "steps": [
                {
                    "step_id": step.step_id,
                    "description": step.description,
                    "status": step.status.value,
                    "dependencies": step.dependencies
                }
                for step in plan.steps
            ],
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None
        }

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task by ID.

        Args:
            task_id: ID of the task to get.

        Returns:
            Optional[Dict[str, Any]]: The task if found, None otherwise.
        """
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        # Convert to dictionary
        return {
            "task_id": task.task_id,
            "description": task.description,
            "requirements": task.requirements,
            "constraints": task.constraints,
            "priority": task.priority,
            "deadline": task.deadline.isoformat() if task.deadline else None
        }

    def list_plans(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all plans, optionally filtered by task ID.

        Args:
            task_id: Optional task ID to filter by.

        Returns:
            List[Dict[str, Any]]: List of plans.
        """
        plans_list = []
        
        for plan in self.plans.values():
            if task_id is None or plan.task_id == task_id:
                plans_list.append({
                    "plan_id": plan.plan_id,
                    "task_id": plan.task_id,
                    "name": plan.name,
                    "status": plan.status.value,
                    "strategy": plan.strategy.value,
                    "steps_count": len(plan.steps),
                    "created_at": plan.created_at.isoformat() if plan.created_at else None
                })
        
        return plans_list

    def list_tasks(self) -> List[Dict[str, Any]]:
        """
        List all tasks.

        Returns:
            List[Dict[str, Any]]: List of tasks.
        """
        tasks_list = []
        
        for task in self.tasks.values():
            tasks_list.append({
                "task_id": task.task_id,
                "description": task.description,
                "priority": task.priority,
                "deadline": task.deadline.isoformat() if task.deadline else None
            })
        
        return tasks_list

    def update_plan_step(self, plan_id: str, step_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a plan step.

        Args:
            plan_id: ID of the plan.
            step_id: ID of the step to update.
            updates: Dictionary of updates to apply.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ValueError: If the plan or step is not found.
        """
        # Check if plan exists
        if plan_id not in self.plans:
            raise ValueError(f"Plan not found: {plan_id}")
        
        plan = self.plans[plan_id]
        
        # Find step
        step = next((s for s in plan.steps if s.step_id == step_id), None)
        if not step:
            raise ValueError(f"Step not found: {step_id}")
        
        # Apply updates
        if "description" in updates:
            step.description = updates["description"]
        
        if "status" in updates:
            try:
                step.status = StepStatus(updates["status"])
            except ValueError:
                self.logger.warning(f"Invalid status: {updates['status']}")
        
        if "action" in updates:
            step.action = updates["action"]
        
        if "expected_outcome" in updates:
            step.expected_outcome = updates["expected_outcome"]
        
        if "verification_method" in updates:
            step.verification_method = updates["verification_method"]
        
        if "dependencies" in updates:
            step.dependencies = updates["dependencies"]
        
        if "result" in updates:
            step.result = updates["result"]
        
        # Update plan status
        self.plan_executor.update_plan_status(plan)
        
        self.logger.info(f"Updated step {step_id} in plan {plan_id}")
        return True

    def delete_plan(self, plan_id: str) -> bool:
        """
        Delete a plan.

        Args:
            plan_id: ID of the plan to delete.

        Returns:
            bool: True if the plan was deleted, False if it wasn't found.
        """
        if plan_id in self.plans:
            del self.plans[plan_id]
            self.logger.info(f"Deleted plan: {plan_id}")
            return True
        
        return False

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.

        Args:
            task_id: ID of the task to delete.

        Returns:
            bool: True if the task was deleted, False if it wasn't found.
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            
            # Also delete associated plans
            plan_ids_to_delete = [
                plan_id for plan_id, plan in self.plans.items()
                if plan.task_id == task_id
            ]
            
            for plan_id in plan_ids_to_delete:
                del self.plans[plan_id]
            
            self.logger.info(f"Deleted task: {task_id} and {len(plan_ids_to_delete)} associated plans")
            return True
        
        return False
