"""
System Instructions Manager for the personal AI agent.

This module implements the System Instructions Manager which handles the creation,
management, and application of system instructions for the LLM.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional, Union

from agent_core.models import SystemInstruction


class SystemInstructionsManager:
    """
    Handles the creation, management, and application of system instructions for the LLM.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SystemInstructionsManager.

        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self.instructions = {}  # category -> List[SystemInstruction]
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Load default instructions if configured
        if self.config.get("load_default_instructions", True):
            self._load_default_instructions()

    def _load_default_instructions(self) -> None:
        """Load default system instructions."""
        # Core capabilities
        self.add_instruction(
            category="core",
            instruction_text=(
                "You are a personal AI agent designed to assist users with a wide range of tasks. "
                "You can access tools, browse the web, process information, and generate content."
            ),
            priority=100
        )
        
        # Language settings
        self.add_instruction(
            category="language",
            instruction_text=(
                "- Default working language: English\n"
                "- Use the language specified by user in messages as the working language when explicitly provided\n"
                "- All thinking and responses must be in the working language\n"
                "- Natural language arguments in tool calls must be in the working language"
            ),
            priority=90
        )
        
        # System capabilities
        self.add_instruction(
            category="capabilities",
            instruction_text=(
                "- Communicate with users through message tools\n"
                "- Access a Linux sandbox environment with internet connection\n"
                "- Use shell, text editor, browser, and other software\n"
                "- Write and run code in Python and various programming languages\n"
                "- Independently install required software packages and dependencies via shell\n"
                "- Deploy websites or applications and provide public access\n"
                "- Suggest users to temporarily take control of the browser for sensitive operations when necessary\n"
                "- Utilize various tools to complete user-assigned tasks step by step"
            ),
            priority=80
        )
        
        # Agent loop
        self.add_instruction(
            category="agent_loop",
            instruction_text=(
                "You are operating in an agent loop, iteratively completing tasks through these steps:\n"
                "1. Analyze Events: Understand user needs and current state through event stream, focusing on latest user messages and execution results\n"
                "2. Select Tools: Choose next tool call based on current state, task planning, relevant knowledge and available data APIs\n"
                "3. Wait for Execution: Selected tool action will be executed by sandbox environment with new observations added to event stream\n"
                "4. Iterate: Choose only one tool call per iteration, patiently repeat above steps until task completion\n"
                "5. Submit Results: Send results to user via message tools, providing deliverables and related files as message attachments\n"
                "6. Enter Standby: Enter idle state when all tasks are completed or user explicitly requests to stop, and wait for new tasks"
            ),
            priority=70
        )
        
        # Planning module
        self.add_instruction(
            category="planning",
            instruction_text=(
                "- System is equipped with planner module for overall task planning\n"
                "- Task planning will be provided as events in the event stream\n"
                "- Task plans use numbered pseudocode to represent execution steps\n"
                "- Each planning update includes the current step number, status, and reflection\n"
                "- Pseudocode representing execution steps will update when overall task objective changes\n"
                "- Must complete all planned steps and reach the final step number by completion"
            ),
            priority=60
        )
        
        # Knowledge module
        self.add_instruction(
            category="knowledge",
            instruction_text=(
                "- System is equipped with knowledge and memory module for best practice references\n"
                "- Task-relevant knowledge will be provided as events in the event stream\n"
                "- Each knowledge item has its scope and should only be adopted when conditions are met"
            ),
            priority=50
        )
        
        # Message rules
        self.add_instruction(
            category="messaging",
            instruction_text=(
                "- Communicate with users via message tools instead of direct text responses\n"
                "- Reply immediately to new user messages before other operations\n"
                "- First reply must be brief, only confirming receipt without specific solutions\n"
                "- Events from Planner, Knowledge, and Datasource modules are system-generated, no reply needed\n"
                "- Notify users with brief explanation when changing methods or strategies\n"
                "- Message tools are divided into notify (non-blocking, no reply needed from users) and ask (blocking, reply required)\n"
                "- Actively use notify for progress updates, but reserve ask for only essential needs to minimize user disruption and avoid blocking progress\n"
                "- Provide all relevant files as attachments, as users may not have direct access to local filesystem\n"
                "- Must message users with results and deliverables before entering idle state upon task completion"
            ),
            priority=40
        )
        
        # Tool use rules
        self.add_instruction(
            category="tools",
            instruction_text=(
                "- Must respond with a tool use (function calling); plain text responses are forbidden\n"
                "- Do not mention any specific tool names to users in messages\n"
                "- Carefully verify available tools; do not fabricate non-existent tools\n"
                "- Events may originate from other system modules; only use explicitly provided tools"
            ),
            priority=30
        )
        
        # Browser rules
        self.add_instruction(
            category="browser",
            instruction_text=(
                "- Must use browser tools to access and comprehend all URLs provided by users in messages\n"
                "- Must use browser tools to access URLs from search tool results\n"
                "- Actively explore valuable links for deeper information, either by clicking elements or accessing URLs directly\n"
                "- Browser tools only return elements in visible viewport by default\n"
                "- Visible elements are returned as `index[:]<tag>text</tag>`, where index is for interactive elements in subsequent browser actions\n"
                "- Due to technical limitations, not all interactive elements may be identified; use coordinates to interact with unlisted elements\n"
                "- Browser tools automatically attempt to extract page content, providing it in Markdown format if successful\n"
                "- Extracted Markdown includes text beyond viewport but omits links and images; completeness not guaranteed\n"
                "- If extracted Markdown is complete and sufficient for the task, no scrolling is needed; otherwise, must actively scroll to view the entire page\n"
                "- Use message tools to suggest user to take over the browser for sensitive operations or actions with side effects when necessary"
            ),
            priority=20
        )
        
        # Coding rules
        self.add_instruction(
            category="coding",
            instruction_text=(
                "- Must save code to files before execution; direct code input to interpreter commands is forbidden\n"
                "- Write Python code for complex mathematical calculations and analysis\n"
                "- Use search tools to find solutions when encountering unfamiliar problems\n"
                "- For index.html referencing local resources, use deployment tools directly, or package everything into a zip file and provide it as a message attachment"
            ),
            priority=10
        )

    def add_instruction(
        self,
        category: str,
        instruction_text: str,
        priority: int = 0,
        instruction_id: Optional[str] = None
    ) -> str:
        """
        Add a system instruction.

        Args:
            category: Category of the instruction.
            instruction_text: The instruction text.
            priority: Priority of the instruction (higher = more important).
            instruction_id: Optional ID for the instruction.

        Returns:
            str: The ID of the added instruction.
        """
        # Generate ID if not provided
        if instruction_id is None:
            instruction_id = f"{category}_{len(self.instructions.get(category, []))}"
        
        # Create instruction
        instruction = SystemInstruction(
            instruction_id=instruction_id,
            category=category,
            instruction_text=instruction_text,
            priority=priority
        )
        
        # Add to instructions
        if category not in self.instructions:
            self.instructions[category] = []
        
        self.instructions[category].append(instruction)
        
        # Sort by priority (higher first)
        self.instructions[category].sort(key=lambda x: x.priority, reverse=True)
        
        self.logger.info(f"Added instruction {instruction_id} to category {category}")
        return instruction_id

    def get_instructions(
        self,
        categories: Optional[List[str]] = None,
        min_priority: int = 0
    ) -> List[SystemInstruction]:
        """
        Get system instructions.

        Args:
            categories: List of categories to get instructions for. If None, gets all categories.
            min_priority: Minimum priority of instructions to include.

        Returns:
            List[SystemInstruction]: The system instructions.
        """
        result = []
        
        # Get all categories if none specified
        if categories is None:
            categories = list(self.instructions.keys())
        
        # Get instructions for each category
        for category in categories:
            if category in self.instructions:
                for instruction in self.instructions[category]:
                    if instruction.priority >= min_priority:
                        result.append(instruction)
        
        # Sort by priority (higher first)
        result.sort(key=lambda x: x.priority, reverse=True)
        
        return result

    def get_instruction_text(
        self,
        categories: Optional[List[str]] = None,
        min_priority: int = 0,
        separator: str = "\n\n"
    ) -> str:
        """
        Get combined instruction text.

        Args:
            categories: List of categories to get instructions for. If None, gets all categories.
            min_priority: Minimum priority of instructions to include.
            separator: Separator between instructions.

        Returns:
            str: The combined instruction text.
        """
        instructions = self.get_instructions(categories, min_priority)
        return separator.join(instr.instruction_text for instr in instructions)

    def remove_instruction(self, instruction_id: str) -> bool:
        """
        Remove a system instruction.

        Args:
            instruction_id: ID of the instruction to remove.

        Returns:
            bool: True if the instruction was removed, False if it wasn't found.
        """
        for category, instructions in self.instructions.items():
            for i, instruction in enumerate(instructions):
                if instruction.instruction_id == instruction_id:
                    del self.instructions[category][i]
                    self.logger.info(f"Removed instruction {instruction_id} from category {category}")
                    return True
        
        return False

    def clear_category(self, category: str) -> bool:
        """
        Clear all instructions in a category.

        Args:
            category: Category to clear.

        Returns:
            bool: True if the category was cleared, False if it wasn't found.
        """
        if category in self.instructions:
            self.instructions[category] = []
            self.logger.info(f"Cleared all instructions in category {category}")
            return True
        
        return False

    def save_to_file(self, file_path: str) -> bool:
        """
        Save instructions to a file.

        Args:
            file_path: Path to save to.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Convert to serializable format
            data = {}
            for category, instructions in self.instructions.items():
                data[category] = [
                    {
                        "instruction_id": instr.instruction_id,
                        "category": instr.category,
                        "instruction_text": instr.instruction_text,
                        "priority": instr.priority
                    }
                    for instr in instructions
                ]
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved instructions to {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving instructions to {file_path}: {str(e)}")
            return False

    def load_from_file(self, file_path: str) -> bool:
        """
        Load instructions from a file.

        Args:
            file_path: Path to load from.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Read from file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear existing instructions
            self.instructions = {}
            
            # Load instructions
            for category, instructions in data.items():
                self.instructions[category] = []
                for instr_data in instructions:
                    instruction = SystemInstruction(
                        instruction_id=instr_data["instruction_id"],
                        category=instr_data["category"],
                        instruction_text=instr_data["instruction_text"],
                        priority=instr_data["priority"]
                    )
                    self.instructions[category].append(instruction)
            
            self.logger.info(f"Loaded instructions from {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error loading instructions from {file_path}: {str(e)}")
            return False
