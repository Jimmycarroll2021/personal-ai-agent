"""
Prompt Manager for the Agent Core component.

This module implements the Prompt Manager which handles system instructions
and prompt templates for effective communication with the LLM.
"""

import string
from typing import Dict, List, Any, Optional

from agent_core.models import PromptTemplate, SystemInstruction


class PromptManager:
    """
    Manages system instructions and prompt templates, ensuring effective
    communication with the LLM.
    """

    def __init__(self):
        """Initialize the PromptManager."""
        self.templates: Dict[str, PromptTemplate] = {}
        self.system_instructions: Dict[str, List[SystemInstruction]] = {}

    def add_template(self, template: PromptTemplate) -> bool:
        """
        Add a prompt template to the manager.

        Args:
            template: The template to add.

        Returns:
            bool: True if the template was added successfully, False otherwise.
        """
        try:
            self.templates[template.template_id] = template
            return True
        except Exception:
            return False

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        Get a prompt template by ID.

        Args:
            template_id: The ID of the template to get.

        Returns:
            Optional[PromptTemplate]: The template if found, None otherwise.
        """
        return self.templates.get(template_id)

    def render_prompt(self, template_id: str, variables: Dict[str, Any]) -> str:
        """
        Render a prompt using a template and variables.

        Args:
            template_id: The ID of the template to use.
            variables: The variables to substitute in the template.

        Returns:
            str: The rendered prompt.

        Raises:
            ValueError: If the template is not found or variables are missing.
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        # Check for missing variables
        missing_vars = [var for var in template.variables if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing variables: {', '.join(missing_vars)}")

        # Use string.Template for variable substitution
        template_obj = string.Template(template.template_text)
        return template_obj.substitute(variables)

    def add_system_instruction(self, instruction: SystemInstruction) -> bool:
        """
        Add a system instruction to the manager.

        Args:
            instruction: The instruction to add.

        Returns:
            bool: True if the instruction was added successfully, False otherwise.
        """
        try:
            if instruction.category not in self.system_instructions:
                self.system_instructions[instruction.category] = []
            
            self.system_instructions[instruction.category].append(instruction)
            
            # Sort instructions by priority (higher priority first)
            self.system_instructions[instruction.category].sort(
                key=lambda x: x.priority, reverse=True
            )
            
            return True
        except Exception:
            return False

    def get_system_instructions(self, categories: List[str]) -> List[SystemInstruction]:
        """
        Get system instructions for the specified categories.

        Args:
            categories: The categories of instructions to get.

        Returns:
            List[SystemInstruction]: The system instructions.
        """
        instructions = []
        for category in categories:
            if category in self.system_instructions:
                instructions.extend(self.system_instructions[category])
        
        # Sort by priority (higher priority first)
        instructions.sort(key=lambda x: x.priority, reverse=True)
        
        return instructions

    def construct_full_prompt(
        self,
        user_input: str,
        system_categories: List[str],
        history: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> str:
        """
        Construct a full prompt including system instructions, history, and tools.

        Args:
            user_input: The user's input.
            system_categories: Categories of system instructions to include.
            history: Conversation history.
            tools: Available tools.

        Returns:
            str: The full prompt.
        """
        # Get system instructions
        instructions = self.get_system_instructions(system_categories)
        system_text = "\n\n".join([instr.instruction_text for instr in instructions])
        
        # Format tools
        tools_text = ""
        if tools:
            tools_text = "Available tools:\n"
            for tool in tools:
                tools_text += f"- {tool['name']}: {tool['description']}\n"
                if 'parameters' in tool:
                    tools_text += "  Parameters:\n"
                    for param in tool['parameters']:
                        tools_text += f"  - {param['name']}: {param['description']}\n"
        
        # Format history
        history_text = ""
        if history:
            for entry in history:
                role = entry.get('role', 'unknown')
                content = entry.get('content', '')
                history_text += f"{role}: {content}\n\n"
        
        # Combine all parts
        full_prompt = f"""System Instructions:
{system_text}

{tools_text}

Conversation History:
{history_text}

User: {user_input}
"""
        return full_prompt
