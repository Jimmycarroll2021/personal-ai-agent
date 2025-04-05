"""
Models for the Agent Core component.

This module defines the data structures used by the Agent Core component.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class EventType(Enum):
    """Types of events in the event stream."""
    USER_MESSAGE = "user_message"
    SYSTEM_MESSAGE = "system_message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    PLAN_UPDATE = "plan_update"
    KNOWLEDGE_UPDATE = "knowledge_update"
    ERROR = "error"


class Event:
    """An event in the agent's event stream."""
    def __init__(
        self,
        event_id: str,
        event_type: EventType,
        timestamp: datetime,
        source: str,
        payload: Dict[str, Any]
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.timestamp = timestamp
        self.source = source
        self.payload = payload


class EventFilter:
    """Filter for events in the event stream."""
    def __init__(
        self,
        event_types: Optional[List[EventType]] = None,
        sources: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ):
        self.event_types = event_types
        self.sources = sources
        self.start_time = start_time
        self.end_time = end_time


class EventStream:
    """A stream of events in the agent's history."""
    def __init__(self, events: List[Event], filters: List[EventFilter], max_history: int):
        self.events = events
        self.filters = filters
        self.max_history = max_history


class PlanStep:
    """A step in an execution plan."""
    def __init__(
        self,
        step_id: str,
        description: str,
        action: Dict[str, Any],
        expected_outcome: str,
        verification_method: Dict[str, Any],
        dependencies: List[str]
    ):
        self.step_id = step_id
        self.description = description
        self.action = action
        self.expected_outcome = expected_outcome
        self.verification_method = verification_method
        self.dependencies = dependencies


class Plan:
    """An execution plan for a task."""
    def __init__(
        self,
        plan_id: str,
        name: str,
        description: str,
        steps: List[PlanStep],
        metadata: Dict[str, Any],
        version: str
    ):
        self.plan_id = plan_id
        self.name = name
        self.description = description
        self.steps = steps
        self.metadata = metadata
        self.version = version


class AgentLoopState:
    """The state of the agent loop."""
    def __init__(
        self,
        user_request: str,
        current_step: int,
        execution_plan: List[PlanStep],
        execution_history: List[Event],
        is_complete: bool,
        error_state: Optional[Dict[str, Any]] = None
    ):
        self.user_request = user_request
        self.current_step = current_step
        self.execution_plan = execution_plan
        self.execution_history = execution_history
        self.is_complete = is_complete
        self.error_state = error_state


class PromptTemplate:
    """A template for generating prompts."""
    def __init__(
        self,
        template_id: str,
        template_text: str,
        variables: List[str],
        version: str
    ):
        self.template_id = template_id
        self.template_text = template_text
        self.variables = variables
        self.version = version


class SystemInstruction:
    """A system instruction for the LLM."""
    def __init__(
        self,
        instruction_id: str,
        instruction_text: str,
        priority: int,
        category: str
    ):
        self.instruction_id = instruction_id
        self.instruction_text = instruction_text
        self.priority = priority
        self.category = category


class UserContext:
    """Context information about the user."""
    def __init__(
        self,
        user_id: str,
        preferences: Dict[str, Any],
        history: Dict[str, Any]
    ):
        self.user_id = user_id
        self.preferences = preferences
        self.history = history


class ExecutionContext:
    """Context information about the current execution."""
    def __init__(
        self,
        current_plan: Optional[Plan],
        execution_history: List[Event],
        active_tools: List[str],
        last_llm_response: Optional[Dict[str, Any]]
    ):
        self.current_plan = current_plan
        self.execution_history = execution_history
        self.active_tools = active_tools
        self.last_llm_response = last_llm_response


class MemoryContext:
    """Context information about the agent's memory."""
    def __init__(
        self,
        short_term: Dict[str, Any],
        long_term: Dict[str, Any]
    ):
        self.short_term = short_term
        self.long_term = long_term


class ToolContext:
    """Context information about available tools."""
    def __init__(
        self,
        available_tools: List[Dict[str, Any]],
        tool_usage_history: Dict[str, Any]
    ):
        self.available_tools = available_tools
        self.tool_usage_history = tool_usage_history


class AgentState:
    """The overall state of the agent."""
    def __init__(
        self,
        session_id: str,
        user_context: UserContext,
        execution_context: ExecutionContext,
        memory_context: MemoryContext,
        tool_context: ToolContext
    ):
        self.session_id = session_id
        self.user_context = user_context
        self.execution_context = execution_context
        self.memory_context = memory_context
        self.tool_context = tool_context


class ComponentType(Enum):
    """Types of components in the agent."""
    CORE = "core"
    PLANNING = "planning"
    KNOWLEDGE = "knowledge"
    TOOL = "tool"
    LLM = "llm"
    UI = "ui"


class Component:
    """A component in the agent architecture."""
    def __init__(
        self,
        component_id: str,
        component_type: ComponentType,
        version: str,
        description: str,
        dependencies: List[str]
    ):
        self.component_id = component_id
        self.component_type = component_type
        self.version = version
        self.description = description
        self.dependencies = dependencies


class DependencyIssue:
    """An issue with a component dependency."""
    def __init__(
        self,
        component_id: str,
        dependency_id: str,
        issue_type: str,
        description: str
    ):
        self.component_id = component_id
        self.dependency_id = dependency_id
        self.issue_type = issue_type
        self.description = description


class LLMRequest:
    """A request to the LLM."""
    def __init__(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        stop_sequences: List[str],
        model_params: Dict[str, Any]
    ):
        self.prompt = prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stop_sequences = stop_sequences
        self.model_params = model_params


class TokenUsage:
    """Token usage information for an LLM request."""
    def __init__(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class ModelInfo:
    """Information about the LLM model used."""
    def __init__(
        self,
        model_id: str,
        version: str,
        provider: str
    ):
        self.model_id = model_id
        self.version = version
        self.provider = provider


class LLMResponse:
    """A response from the LLM."""
    def __init__(
        self,
        text: str,
        usage: TokenUsage,
        model_info: ModelInfo,
        latency: float
    ):
        self.text = text
        self.usage = usage
        self.model_info = model_info
        self.latency = latency


class Tool:
    """A tool that can be used by the agent."""
    def __init__(
        self,
        tool_id: str,
        name: str,
        description: str,
        parameters: List[Dict[str, Any]],
        return_type: str
    ):
        self.tool_id = tool_id
        self.name = name
        self.description = description
        self.parameters = parameters
        self.return_type = return_type


class ToolCall:
    """A call to a tool."""
    def __init__(
        self,
        tool_id: str,
        parameters: Dict[str, Any],
        call_id: str
    ):
        self.tool_id = tool_id
        self.parameters = parameters
        self.call_id = call_id


class ToolResult:
    """The result of a tool call."""
    def __init__(
        self,
        call_id: str,
        success: bool,
        result: Optional[Any],
        error: Optional[str]
    ):
        self.call_id = call_id
        self.success = success
        self.result = result
        self.error = error


class ValidationError:
    """An error in validating a tool call."""
    def __init__(
        self,
        parameter: str,
        error_type: str,
        message: str
    ):
        self.parameter = parameter
        self.error_type = error_type
        self.message = message


class FormatType(Enum):
    """Types of response formats."""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


class StyleGuide:
    """A style guide for formatting responses."""
    def __init__(
        self,
        tone: str,
        length: str,
        formatting: Dict[str, Any]
    ):
        self.tone = tone
        self.length = length
        self.formatting = formatting


class Attachment:
    """An attachment to a response."""
    def __init__(
        self,
        attachment_id: str,
        content_type: str,
        content: Any,
        metadata: Dict[str, Any]
    ):
        self.attachment_id = attachment_id
        self.content_type = content_type
        self.content = content
        self.metadata = metadata


class Response:
    """A response to a user request."""
    def __init__(
        self,
        text: str,
        attachments: List[Attachment],
        metadata: Dict[str, Any]
    ):
        self.text = text
        self.attachments = attachments
        self.metadata = metadata


class QualityIssue:
    """An issue with the quality of a response."""
    def __init__(
        self,
        issue_type: str,
        severity: str,
        description: str,
        location: Optional[str]
    ):
        self.issue_type = issue_type
        self.severity = severity
        self.description = description
        self.location = location


class MessageType(Enum):
    """Types of messages in the UI."""
    NOTIFICATION = "notification"
    QUESTION = "question"
    ERROR = "error"
    SUCCESS = "success"


class UIMessage:
    """A message to be displayed in the UI."""
    def __init__(
        self,
        message_type: MessageType,
        content: str,
        attachments: List[Attachment],
        ui_specific: Dict[str, Any]
    ):
        self.message_type = message_type
        self.content = content
        self.attachments = attachments
        self.ui_specific = ui_specific


class UIEventType(Enum):
    """Types of events from the UI."""
    USER_INPUT = "user_input"
    BUTTON_CLICK = "button_click"
    FILE_UPLOAD = "file_upload"
    PAGE_NAVIGATION = "page_navigation"


class UIEvent:
    """An event from the UI."""
    def __init__(
        self,
        event_type: UIEventType,
        payload: Dict[str, Any],
        timestamp: datetime
    ):
        self.event_type = event_type
        self.payload = payload
        self.timestamp = timestamp


class UIType(Enum):
    """Types of user interfaces."""
    WEB = "web"
    CLI = "cli"
    API = "api"


class UIFeature:
    """A feature supported by a UI type."""
    def __init__(
        self,
        feature_id: str,
        name: str,
        description: str,
        supported_ui_types: List[UIType]
    ):
        self.feature_id = feature_id
        self.name = name
        self.description = description
        self.supported_ui_types = supported_ui_types
