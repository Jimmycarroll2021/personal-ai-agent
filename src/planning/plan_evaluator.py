"""
Plan Evaluator for the Planning Module component.

This module implements the Plan Evaluator which evaluates plans for quality,
feasibility, and effectiveness.
"""

import logging
from typing import Dict, List, Any, Optional

from planning.models import Plan, PlanEvaluation


class PlanEvaluator:
    """
    Evaluates plans for quality, feasibility, and effectiveness.
    """

    def __init__(self, llm_service):
        """
        Initialize the PlanEvaluator.

        Args:
            llm_service: Service for calling the LLM.
        """
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)

    def evaluate_plan(self, plan: Plan, evaluation_criteria: Dict[str, float] = None) -> PlanEvaluation:
        """
        Evaluate a plan based on specified criteria.

        Args:
            plan: The plan to evaluate.
            evaluation_criteria: Dictionary of criteria and their weights.
                                If None, default criteria are used.

        Returns:
            PlanEvaluation: The evaluation result.
        """
        self.logger.info(f"Evaluating plan: {plan.plan_id}")
        
        # Use default criteria if none provided
        if not evaluation_criteria:
            evaluation_criteria = {
                "completeness": 0.25,  # Does the plan cover all aspects of the task?
                "feasibility": 0.25,   # Is the plan feasible to execute?
                "efficiency": 0.2,     # Is the plan efficient?
                "robustness": 0.15,    # Does the plan handle potential issues?
                "clarity": 0.15        # Is the plan clear and understandable?
            }
        
        # Prepare prompt for evaluation
        prompt = self._create_evaluation_prompt(plan, evaluation_criteria)
        
        # Call LLM for evaluation
        evaluation_response = self._call_llm_for_evaluation(prompt)
        
        # Parse evaluation from LLM response
        evaluation_result = self._parse_evaluation(evaluation_response, plan.plan_id)
        
        self.logger.info(f"Plan evaluation completed with score: {evaluation_result.score}")
        return evaluation_result

    def compare_plans(self, plans: List[Plan]) -> Dict[str, Any]:
        """
        Compare multiple plans and identify the best one.

        Args:
            plans: List of plans to compare.

        Returns:
            Dict[str, Any]: Comparison results with rankings and recommendations.
        """
        self.logger.info(f"Comparing {len(plans)} plans")
        
        # Evaluate each plan
        evaluations = []
        for plan in plans:
            evaluation = self.evaluate_plan(plan)
            evaluations.append({
                "plan_id": plan.plan_id,
                "plan_name": plan.name,
                "score": evaluation.score,
                "strengths": evaluation.strengths,
                "weaknesses": evaluation.weaknesses
            })
        
        # Rank plans by score
        ranked_plans = sorted(evaluations, key=lambda x: x["score"], reverse=True)
        
        # Identify best plan
        best_plan = ranked_plans[0] if ranked_plans else None
        
        # Prepare comparison result
        comparison_result = {
            "rankings": ranked_plans,
            "best_plan_id": best_plan["plan_id"] if best_plan else None,
            "score_range": {
                "min": min(e["score"] for e in evaluations) if evaluations else 0,
                "max": max(e["score"] for e in evaluations) if evaluations else 0,
                "avg": sum(e["score"] for e in evaluations) / len(evaluations) if evaluations else 0
            },
            "recommendation": self._generate_recommendation(ranked_plans) if ranked_plans else "No plans to compare"
        }
        
        self.logger.info(f"Plan comparison completed, best plan: {comparison_result['best_plan_id']}")
        return comparison_result

    def identify_improvement_areas(self, plan: Plan) -> List[Dict[str, Any]]:
        """
        Identify areas where a plan can be improved.

        Args:
            plan: The plan to analyze.

        Returns:
            List[Dict[str, Any]]: List of improvement suggestions.
        """
        self.logger.info(f"Identifying improvement areas for plan: {plan.plan_id}")
        
        # Evaluate the plan first
        evaluation = self.evaluate_plan(plan)
        
        # Extract improvement suggestions
        improvements = []
        for i, suggestion in enumerate(evaluation.improvement_suggestions):
            improvements.append({
                "id": f"improvement_{i+1}",
                "description": suggestion,
                "priority": "high" if i < 2 else "medium" if i < 4 else "low"
            })
        
        # If no suggestions from evaluation, generate some
        if not improvements:
            # Prepare prompt for improvement suggestions
            prompt = f"""
            Analyze this plan and suggest specific improvements:
            
            Plan Name: {plan.name}
            Plan Description: {plan.description}
            
            Steps:
            {self._format_plan_steps(plan)}
            
            Provide 3-5 specific suggestions for improving this plan. Each suggestion should:
            1. Identify a specific issue or weakness
            2. Explain why it's a problem
            3. Offer a concrete solution
            
            Format each suggestion as a separate paragraph.
            """
            
            # Call LLM for suggestions
            suggestions_response = self._call_llm_for_evaluation(prompt)
            
            # Parse suggestions
            raw_suggestions = suggestions_response.strip().split('\n\n')
            for i, suggestion in enumerate(raw_suggestions):
                if suggestion.strip():
                    improvements.append({
                        "id": f"improvement_{i+1}",
                        "description": suggestion.strip(),
                        "priority": "high" if i < 2 else "medium" if i < 4 else "low"
                    })
        
        self.logger.info(f"Identified {len(improvements)} improvement areas")
        return improvements

    def check_plan_feasibility(self, plan: Plan, constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check if a plan is feasible given certain constraints.

        Args:
            plan: The plan to check.
            constraints: Dictionary of constraints to consider.

        Returns:
            Dict[str, Any]: Feasibility assessment.
        """
        self.logger.info(f"Checking feasibility of plan: {plan.plan_id}")
        
        # Default constraints if none provided
        if not constraints:
            constraints = {
                "time_limit": None,
                "resource_limits": {},
                "tool_availability": []
            }
        
        # Prepare prompt for feasibility check
        prompt = f"""
        Assess the feasibility of this plan given the following constraints:
        
        Plan Name: {plan.name}
        Plan Description: {plan.description}
        
        Steps:
        {self._format_plan_steps(plan)}
        
        Constraints:
        {self._format_constraints(constraints)}
        
        Provide a detailed feasibility assessment including:
        1. Overall feasibility score (0-100%)
        2. Specific issues that might make the plan infeasible
        3. Suggestions to address feasibility issues
        4. Whether the plan can be executed within the given constraints
        """
        
        # Call LLM for feasibility check
        feasibility_response = self._call_llm_for_evaluation(prompt)
        
        # Parse feasibility assessment
        feasibility_result = self._parse_feasibility(feasibility_response)
        
        self.logger.info(f"Feasibility check completed with score: {feasibility_result['score']}%")
        return feasibility_result

    def _create_evaluation_prompt(self, plan: Plan, criteria: Dict[str, float]) -> str:
        """
        Create a prompt for plan evaluation.

        Args:
            plan: The plan to evaluate.
            criteria: Evaluation criteria and weights.

        Returns:
            str: The evaluation prompt.
        """
        # Format criteria
        criteria_text = "Evaluation Criteria:\n"
        for criterion, weight in criteria.items():
            criteria_text += f"- {criterion.capitalize()} ({weight*100:.0f}%): "
            
            if criterion == "completeness":
                criteria_text += "Does the plan cover all aspects of the task?\n"
            elif criterion == "feasibility":
                criteria_text += "Is the plan feasible to execute?\n"
            elif criterion == "efficiency":
                criteria_text += "Is the plan efficient in terms of steps and resources?\n"
            elif criterion == "robustness":
                criteria_text += "Does the plan handle potential issues and edge cases?\n"
            elif criterion == "clarity":
                criteria_text += "Is the plan clear, specific, and understandable?\n"
            else:
                criteria_text += f"Evaluate the plan's {criterion}.\n"
        
        # Create prompt
        prompt = f"""
        Evaluate the following plan based on the specified criteria:
        
        Plan Name: {plan.name}
        Plan Description: {plan.description}
        
        Steps:
        {self._format_plan_steps(plan)}
        
        {criteria_text}
        
        Provide a detailed evaluation including:
        1. Overall score (0-100)
        2. At least 3 strengths of the plan
        3. At least 3 weaknesses or areas for improvement
        4. Specific suggestions to improve the plan
        
        Format your response as follows:
        
        Score: [0-100]
        
        Strengths:
        - [Strength 1]
        - [Strength 2]
        - [Strength 3]
        
        Weaknesses:
        - [Weakness 1]
        - [Weakness 2]
        - [Weakness 3]
        
        Improvement Suggestions:
        - [Suggestion 1]
        - [Suggestion 2]
        - [Suggestion 3]
        """
        
        return prompt

    def _format_plan_steps(self, plan: Plan) -> str:
        """
        Format plan steps for inclusion in prompts.

        Args:
            plan: The plan to format.

        Returns:
            str: Formatted plan steps.
        """
        steps_text = ""
        for i, step in enumerate(plan.steps):
            steps_text += f"{i+1}. {step.description}\n"
            
            # Add action details if available
            action_type = step.action.get("type", "unknown")
            if action_type != "unknown":
                steps_text += f"   Action: {action_type}"
                
                if action_type == "tool_call" and "tool_id" in step.action:
                    steps_text += f" - {step.action.get('tool_id')}"
                
                steps_text += "\n"
            
            # Add expected outcome if available
            if step.expected_outcome:
                steps_text += f"   Expected Outcome: {step.expected_outcome}\n"
            
            # Add dependencies if available
            if step.dependencies:
                deps = ", ".join(step.dependencies)
                steps_text += f"   Dependencies: {deps}\n"
            
            steps_text += "\n"
        
        return steps_text

    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """
        Format constraints for inclusion in prompts.

        Args:
            constraints: The constraints to format.

        Returns:
            str: Formatted constraints.
        """
        constraints_text = ""
        
        # Time limit
        if constraints.get("time_limit"):
            constraints_text += f"- Time Limit: {constraints['time_limit']}\n"
        
        # Resource limits
        if constraints.get("resource_limits"):
            constraints_text += "- Resource Limits:\n"
            for resource, limit in constraints["resource_limits"].items():
                constraints_text += f"  - {resource}: {limit}\n"
        
        # Tool availability
        if constraints.get("tool_availability"):
            constraints_text += "- Available Tools:\n"
            for tool in constraints["tool_availability"]:
                constraints_text += f"  - {tool}\n"
        
        # Other constraints
        for key, value in constraints.items():
            if key not in ["time_limit", "resource_limits", "tool_availability"]:
                constraints_text += f"- {key}: {value}\n"
        
        return constraints_text

    def _call_llm_for_evaluation(self, prompt: str) -> str:
        """
        Call the LLM service for evaluation.

        Args:
            prompt: The evaluation prompt.

        Returns:
            str: The LLM response.
        """
        # This is a simplified implementation
        # In a real system, this would call the actual LLM service
        
        # Create request for LLM service
        request = {
            "prompt": prompt,
            "temperature": 0.1,  # Low temperature for evaluation
            "max_tokens": 1000,
            "stop_sequences": [],
            "model_params": {"evaluation_mode": True}
        }
        
        # Call LLM service
        response = self.llm_service(request)
        
        # Extract text from response
        if isinstance(response, dict) and "text" in response:
            return response["text"]
        elif isinstance(response, str):
            return response
        else:
            return str(response)

    def _parse_evaluation(self, response: str, plan_id: str) -> PlanEvaluation:
        """
        Parse an evaluation from an LLM response.

        Args:
            response: The LLM response.
            plan_id: ID of the evaluated plan.

        Returns:
            PlanEvaluation: The parsed evaluation.
        """
        lines = response.strip().split('\n')
        
        # Default values
        score = 0.0
        strengths = []
        weaknesses = []
        suggestions = []
        
        # Current section being parsed
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            lower_line = line.lower()
            
            if lower_line.startswith("score:"):
                # Extract score
                score_text = line.split(":", 1)[1].strip()
                try:
                    # Handle percentage or raw score
                    if "%" in score_text:
                        score = float(score_text.replace("%", "")) / 100.0
                    else:
                        score = float(score_text) / 100.0
                except ValueError:
                    # Default to middle score if parsing fails
                    score = 0.5
                
                # Ensure score is in range [0, 1]
                score = max(0.0, min(1.0, score))
            
            elif lower_line.startswith("strengths:") or lower_line == "strengths":
                current_section = "strengths"
            elif lower_line.startswith("weaknesses:") or lower_line == "weaknesses":
                current_section = "weaknesses"
            elif lower_line.startswith("improvement") or lower_line.startswith("suggestions"):
                current_section = "suggestions"
            elif line.startswith("-") and current_section:
                # Extract item from bullet point
                item = line[1:].strip()
                
                if current_section == "strengths":
                    strengths.append(item)
                elif current_section == "weaknesses":
        <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>