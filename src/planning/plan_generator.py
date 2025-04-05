"""
Plan Generator for the Planning Module component.

This module implements the Plan Generator which creates execution plans
based on user requests and available tools.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from planning.models import (
    Plan, PlanStep, PlanningStrategy, PlanStatus, StepStatus,
    PlanningContext, PlanningResult, ThoughtNode, ThoughtTree
)


class PlanGenerator:
    """
    Creates execution plans based on user requests and available tools.
    """

    def __init__(self, llm_service):
        """
        Initialize the PlanGenerator.

        Args:
            llm_service: Service for calling the LLM.
        """
        self.llm_service = llm_service
        self.default_strategy = PlanningStrategy.CHAIN_OF_THOUGHT

    def generate_plan(
        self,
        planning_context: PlanningContext,
        strategy: Optional[PlanningStrategy] = None
    ) -> PlanningResult:
        """
        Generate a plan based on the planning context.

        Args:
            planning_context: Context information for planning.
            strategy: Planning strategy to use. If None, uses default strategy.

        Returns:
            PlanningResult: The result of the planning operation.
        """
        strategy = strategy or self.default_strategy
        
        # Select planning method based on strategy
        if strategy == PlanningStrategy.CHAIN_OF_THOUGHT:
            return self._plan_with_chain_of_thought(planning_context)
        elif strategy == PlanningStrategy.TREE_OF_THOUGHTS:
            return self._plan_with_tree_of_thoughts(planning_context)
        elif strategy == PlanningStrategy.REACT:
            return self._plan_with_react(planning_context)
        elif strategy == PlanningStrategy.HIERARCHICAL:
            return self._plan_with_hierarchical(planning_context)
        elif strategy == PlanningStrategy.GOAL_DECOMPOSITION:
            return self._plan_with_goal_decomposition(planning_context)
        else:
            # Default to Chain of Thought
            return self._plan_with_chain_of_thought(planning_context)

    def _plan_with_chain_of_thought(self, planning_context: PlanningContext) -> PlanningResult:
        """
        Generate a plan using Chain of Thought reasoning.

        Args:
            planning_context: Context information for planning.

        Returns:
            PlanningResult: The result of the planning operation.
        """
        # Prepare prompt for planning
        prompt = self._create_planning_prompt(
            planning_context,
            "Chain of Thought",
            "Break down the task step by step, thinking through each step carefully."
        )
        
        # Call LLM for planning
        response = self._call_llm_for_planning(prompt)
        
        # Parse plan from LLM response
        try:
            plan = self._parse_plan_from_response(
                response,
                planning_context.user_request,
                PlanningStrategy.CHAIN_OF_THOUGHT
            )
            
            return PlanningResult(
                success=True,
                plan=plan,
                error=None,
                alternatives=[],
                reasoning="Plan generated using Chain of Thought reasoning."
            )
        except Exception as e:
            return PlanningResult(
                success=False,
                plan=None,
                error=f"Failed to parse plan: {str(e)}",
                alternatives=[],
                reasoning="Error occurred during plan generation."
            )

    def _plan_with_tree_of_thoughts(self, planning_context: PlanningContext) -> PlanningResult:
        """
        Generate a plan using Tree of Thoughts reasoning.

        Args:
            planning_context: Context information for planning.

        Returns:
            PlanningResult: The result of the planning operation.
        """
        # Create thought tree
        thought_tree = self._generate_thought_tree(planning_context)
        
        # Extract best path from tree
        best_path = thought_tree.best_path
        
        # Convert best path to plan
        try:
            plan_steps = []
            for i, node_id in enumerate(best_path):
                node = thought_tree.nodes[node_id]
                
                # Create plan step from thought node
                step = PlanStep(
                    step_id=f"step_{i+1}",
                    description=node.content,
                    action={"type": "unknown"},  # Will be refined later
                    expected_outcome="",  # Will be refined later
                    verification_method={},  # Will be refined later
                    dependencies=[f"step_{j+1}" for j in range(i)]
                )
                plan_steps.append(step)
            
            # Create plan
            plan = Plan(
                plan_id=str(uuid.uuid4()),
                task_id="task_" + str(uuid.uuid4())[-8:],
                name=f"Plan for: {planning_context.user_request[:50]}...",
                description=planning_context.user_request,
                steps=plan_steps,
                strategy=PlanningStrategy.TREE_OF_THOUGHTS,
                status=PlanStatus.CREATED,
                metadata={"thought_tree_id": thought_tree.tree_id}
            )
            
            return PlanningResult(
                success=True,
                plan=plan,
                error=None,
                alternatives=[],
                reasoning="Plan generated using Tree of Thoughts reasoning."
            )
        except Exception as e:
            return PlanningResult(
                success=False,
                plan=None,
                error=f"Failed to create plan from thought tree: {str(e)}",
                alternatives=[],
                reasoning="Error occurred during plan generation."
            )

    def _plan_with_react(self, planning_context: PlanningContext) -> PlanningResult:
        """
        Generate a plan using ReAct (Reasoning + Acting) approach.

        Args:
            planning_context: Context information for planning.

        Returns:
            PlanningResult: The result of the planning operation.
        """
        # Prepare prompt for ReAct planning
        prompt = self._create_planning_prompt(
            planning_context,
            "ReAct",
            "For each step, include Thought (reasoning), Action (tool to use), and Observation (expected result)."
        )
        
        # Call LLM for planning
        response = self._call_llm_for_planning(prompt)
        
        # Parse ReAct plan from LLM response
        try:
            plan_steps = []
            react_steps = self._parse_react_steps(response)
            
            for i, react_step in enumerate(react_steps):
                # Create plan step from ReAct step
                step = PlanStep(
                    step_id=f"step_{i+1}",
                    description=react_step["thought"],
                    action={
                        "type": "tool_call",
                        "tool_id": react_step["action"],
                        "parameters": react_step.get("parameters", {})
                    },
                    expected_outcome=react_step["observation"],
                    verification_method={"type": "observation_match"},
                    dependencies=[f"step_{j+1}" for j in range(i)]
                )
                plan_steps.append(step)
            
            # Create plan
            plan = Plan(
                plan_id=str(uuid.uuid4()),
                task_id="task_" + str(uuid.uuid4())[-8:],
                name=f"Plan for: {planning_context.user_request[:50]}...",
                description=planning_context.user_request,
                steps=plan_steps,
                strategy=PlanningStrategy.REACT,
                status=PlanStatus.CREATED
            )
            
            return PlanningResult(
                success=True,
                plan=plan,
                error=None,
                alternatives=[],
                reasoning="Plan generated using ReAct approach."
            )
        except Exception as e:
            return PlanningResult(
                success=False,
                plan=None,
                error=f"Failed to parse ReAct plan: {str(e)}",
                alternatives=[],
                reasoning="Error occurred during plan generation."
            )

    def _plan_with_hierarchical(self, planning_context: PlanningContext) -> PlanningResult:
        """
        Generate a hierarchical plan with high-level goals and sub-plans.

        Args:
            planning_context: Context information for planning.

        Returns:
            PlanningResult: The result of the planning operation.
        """
        # First, generate high-level goals
        high_level_prompt = self._create_planning_prompt(
            planning_context,
            "Hierarchical Planning - High Level",
            "Identify 3-5 high-level goals that need to be achieved to complete this task."
        )
        
        high_level_response = self._call_llm_for_planning(high_level_prompt)
        high_level_goals = self._parse_high_level_goals(high_level_response)
        
        # Then, create sub-plans for each goal
        all_steps = []
        current_step_index = 1
        
        for i, goal in enumerate(high_level_goals):
            # Create context for sub-plan
            sub_context = PlanningContext(
                user_request=goal,
                available_tools=planning_context.available_tools,
                constraints=planning_context.constraints,
                previous_plans=planning_context.previous_plans,
                relevant_knowledge=planning_context.relevant_knowledge
            )
            
            # Generate sub-plan
            sub_plan_prompt = self._create_planning_prompt(
                sub_context,
                f"Sub-Plan for Goal {i+1}",
                f"Create detailed steps to achieve this goal: {goal}"
            )
            
            sub_plan_response = self._call_llm_for_planning(sub_plan_prompt)
            sub_plan_steps = self._parse_plan_steps(sub_plan_response)
            
            # Add goal as a header step
            goal_step = PlanStep(
                step_id=f"step_{current_step_index}",
                description=f"GOAL: {goal}",
                action={"type": "goal"},
                expected_outcome="All sub-steps completed",
                verification_method={"type": "all_substeps_complete"},
                dependencies=[f"step_{j+1}" for j in range(current_step_index-1)]
            )
            all_steps.append(goal_step)
            current_step_index += 1
            
            # Add sub-steps with dependencies on the goal step
            for sub_step in sub_plan_steps:
                step = PlanStep(
                    step_id=f"step_{current_step_index}",
                    description=sub_step,
                    action={"type": "unknown"},  # Will be refined later
                    expected_outcome="",  # Will be refined later
                    verification_method={},  # Will be refined later
                    dependencies=[f"step_{current_step_index-1}"]  # Depend on previous step
                )
                all_steps.append(step)
                current_step_index += 1
        
        # Create plan
        plan = Plan(
            plan_id=str(uuid.uuid4()),
            task_id="task_" + str(uuid.uuid4())[-8:],
            name=f"Hierarchical Plan for: {planning_context.user_request[:50]}...",
            description=planning_context.user_request,
            steps=all_steps,
            strategy=PlanningStrategy.HIERARCHICAL,
            status=PlanStatus.CREATED
        )
        
        return PlanningResult(
            success=True,
            plan=plan,
            error=None,
            alternatives=[],
            reasoning="Plan generated using Hierarchical planning approach."
        )

    def _plan_with_goal_decomposition(self, planning_context: PlanningContext) -> PlanningResult:
        """
        Generate a plan by decomposing goals into subgoals and actions.

        Args:
            planning_context: Context information for planning.

        Returns:
            PlanningResult: The result of the planning operation.
        """
        # Prepare prompt for goal decomposition
        prompt = self._create_planning_prompt(
            planning_context,
            "Goal Decomposition",
            "Break down the main goal into subgoals, and then into specific actions."
        )
        
        # Call LLM for planning
        response = self._call_llm_for_planning(prompt)
        
        # Parse decomposed goals and actions
        try:
            decomposition = self._parse_goal_decomposition(response)
            
            # Convert decomposition to plan steps
            plan_steps = []
            step_index = 1
            
            for goal in decomposition:
                # Add goal as a header step
                goal_step = PlanStep(
                    step_id=f"step_{step_index}",
                    description=f"GOAL: {goal['goal']}",
                    action={"type": "goal"},
                    expected_outcome="All sub-steps completed",
                    verification_method={"type": "all_substeps_complete"},
                    dependencies=[f"step_{j+1}" for j in range(step_index-1)]
                )
                plan_steps.append(goal_step)
                goal_step_id = f"step_{step_index}"
                step_index += 1
                
                # Add subgoals
                for subgoal in goal['subgoals']:
                    subgoal_step = PlanStep(
                        step_id=f"step_{step_index}",
                        description=f"SUBGOAL: {subgoal['subgoal']}",
                        action={"type": "subgoal"},
                        expected_outcome="All actions completed",
                        verification_method={"type": "all_actions_complete"},
                        dependencies=[goal_step_id]
                    )
                    plan_steps.append(subgoal_step)
                    subgoal_step_id = f"step_{step_index}"
                    step_index += 1
                    
                    # Add actions for this subgoal
                    for action in subgoal['actions']:
                        action_step = PlanStep(
                            step_id=f"step_{step_index}",
                            description=action,
                            action={"type": "unknown"},  # Will be refined later
                            expected_outcome="",  # Will be refined later
                            verification_method={},  # Will be refined later
                            dependencies=[subgoal_step_id]
                        )
                        plan_steps.append(action_step)
                        step_index += 1
            
            # Create plan
            plan = Plan(
                plan_id=str(uuid.uuid4()),
                task_id="task_" + str(uuid.uuid4())[-8:],
                name=f"Plan for: {planning_context.user_request[:50]}...",
                description=planning_context.user_request,
                steps=plan_steps,
                strategy=PlanningStrategy.GOAL_DECOMPOSITION,
                status=PlanStatus.CREATED
            )
            
            return PlanningResult(
                success=True,
                plan=plan,
                error=None,
                alternatives=[],
                reasoning="Plan generated using Goal Decomposition approach."
            )
        except Exception as e:
            return PlanningResult(
                success=False,
                plan=None,
                error=f"Faile<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>