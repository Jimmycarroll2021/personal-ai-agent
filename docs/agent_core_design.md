# Agent Core/Brain Design Specification

## Overview

The Agent Core (or Brain) is the central component of the personal AI agent architecture. It serves as the coordinator that orchestrates the flow of operations, manages the agent loop, and integrates with other components such as the Planning Module, Knowledge Module, and Tool Integration Framework.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Agent Core/Brain                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │                 │    │                 │    │              │ │
│  │  Agent Loop     │◄───┤  Prompt Manager │◄───┤  User        │ │
│  │  Controller     │    │                 │    │  Interface   │ │
│  │                 │    │                 │    │  Adapter     │ │
│  └────────┬────────┘    └─────────────────┘    └──────────────┘ │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │                 │    │                 │    │              │ │
│  │  State Manager  │◄───┤  Event Stream   │◄───┤  Component   │ │
│  │                 │    │  Processor      │    │  Registry    │ │
│  │                 │    │                 │    │              │ │
│  └────────┬────────┘    └─────────────────┘    └──────────────┘ │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │                 │    │                 │    │              │ │
│  │  LLM Interface  │◄───┤  Tool Executor  │◄───┤  Response    │ │
│  │                 │    │                 │    │  Generator   │ │
│  │                 │    │                 │    │              │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Subcomponents

### 1. Agent Loop Controller

The Agent Loop Controller manages the iterative process of understanding user requests, planning actions, executing tools, and generating responses.

**Key Functions:**
- Initialize and manage the agent loop lifecycle
- Coordinate the flow between different components
- Handle loop termination and error recovery
- Implement loop optimization strategies

**Data Structures:**
```python
class AgentLoopState:
    user_request: str
    current_step: int
    execution_plan: List[PlanStep]
    execution_history: List[Event]
    is_complete: bool
    error_state: Optional[ErrorState]
```

**Interface:**
```python
class AgentLoopController:
    def initialize(self, user_request: str) -> AgentLoopState
    def step(self, state: AgentLoopState) -> AgentLoopState
    def is_complete(self, state: AgentLoopState) -> bool
    def handle_error(self, state: AgentLoopState, error: Exception) -> AgentLoopState
```

### 2. Prompt Manager

The Prompt Manager handles system instructions and prompt templates, ensuring effective communication with the LLM.

**Key Functions:**
- Manage system instructions and prompt templates
- Construct prompts for different agent operations
- Handle prompt optimization and versioning
- Implement prompt security measures

**Data Structures:**
```python
class PromptTemplate:
    template_id: str
    template_text: str
    variables: List[str]
    version: str
    
class SystemInstruction:
    instruction_id: str
    instruction_text: str
    priority: int
    category: str
```

**Interface:**
```python
class PromptManager:
    def get_template(self, template_id: str) -> PromptTemplate
    def render_prompt(self, template_id: str, variables: Dict[str, Any]) -> str
    def get_system_instructions(self, categories: List[str]) -> List[SystemInstruction]
    def construct_full_prompt(self, user_input: str, system_categories: List[str], 
                             history: List[Message], tools: List[Tool]) -> str
```

### 3. State Manager

The State Manager maintains the current state of the agent, including execution history, active plans, and context.

**Key Functions:**
- Maintain agent state across loop iterations
- Track execution history and context
- Manage state persistence and recovery
- Implement state optimization strategies

**Data Structures:**
```python
class AgentState:
    session_id: str
    user_context: UserContext
    execution_context: ExecutionContext
    memory_context: MemoryContext
    tool_context: ToolContext
    
class ExecutionContext:
    current_plan: Optional[Plan]
    execution_history: List[Event]
    active_tools: List[str]
    last_llm_response: Optional[LLMResponse]
```

**Interface:**
```python
class StateManager:
    def initialize_state(self, session_id: str, user_context: UserContext) -> AgentState
    def update_state(self, state: AgentState, events: List[Event]) -> AgentState
    def get_current_context(self, state: AgentState) -> Dict[str, Any]
    def persist_state(self, state: AgentState) -> bool
    def load_state(self, session_id: str) -> Optional[AgentState]
```

### 4. Event Stream Processor

The Event Stream Processor handles the flow of events between components, including user messages, tool results, and system events.

**Key Functions:**
- Process incoming events from various sources
- Route events to appropriate components
- Maintain event history and context
- Implement event filtering and prioritization

**Data Structures:**
```python
class Event:
    event_id: str
    event_type: EventType
    timestamp: datetime
    source: str
    payload: Dict[str, Any]
    
class EventStream:
    events: List[Event]
    filters: List[EventFilter]
    max_history: int
```

**Interface:**
```python
class EventStreamProcessor:
    def add_event(self, event: Event) -> bool
    def get_events(self, filters: List[EventFilter]) -> List[Event]
    def get_latest_events(self, count: int, event_types: List[EventType]) -> List[Event]
    def clear_events(self, older_than: datetime) -> int
```

### 5. Component Registry

The Component Registry manages the registration and discovery of agent components, such as tools, planning modules, and knowledge sources.

**Key Functions:**
- Register and manage agent components
- Provide component discovery and lookup
- Handle component versioning and dependencies
- Implement component lifecycle management

**Data Structures:**
```python
class Component:
    component_id: str
    component_type: ComponentType
    version: str
    description: str
    dependencies: List[str]
    
class ComponentRegistry:
    components: Dict[str, Component]
```

**Interface:**
```python
class ComponentRegistryManager:
    def register_component(self, component: Component) -> bool
    def get_component(self, component_id: str) -> Optional[Component]
    def get_components_by_type(self, component_type: ComponentType) -> List[Component]
    def check_dependencies(self, component_id: str) -> List[DependencyIssue]
```

### 6. LLM Interface

The LLM Interface provides a standardized way to interact with the underlying language model, whether it's hosted or local.

**Key Functions:**
- Manage communication with the LLM
- Handle request formatting and response parsing
- Implement retry and fallback strategies
- Monitor LLM performance and usage

**Data Structures:**
```python
class LLMRequest:
    prompt: str
    temperature: float
    max_tokens: int
    stop_sequences: List[str]
    model_params: Dict[str, Any]
    
class LLMResponse:
    text: str
    usage: TokenUsage
    model_info: ModelInfo
    latency: float
```

**Interface:**
```python
class LLMInterface:
    def initialize(self, config: LLMConfig) -> bool
    def generate(self, request: LLMRequest) -> LLMResponse
    def generate_with_tools(self, request: LLMRequest, tools: List[Tool]) -> LLMResponseWithToolCalls
    def get_embedding(self, text: str) -> List[float]
```

### 7. Tool Executor

The Tool Executor manages the execution of tools requested by the LLM, handling input/output formatting and error management.

**Key Functions:**
- Execute tools based on LLM requests
- Handle tool input validation and output formatting
- Manage tool execution errors and retries
- Track tool usage and performance

**Data Structures:**
```python
class ToolCall:
    tool_id: str
    parameters: Dict[str, Any]
    call_id: str
    
class ToolResult:
    call_id: str
    success: bool
    result: Optional[Any]
    error: Optional[str]
```

**Interface:**
```python
class ToolExecutor:
    def execute_tool(self, tool_call: ToolCall) -> ToolResult
    def execute_tools(self, tool_calls: List[ToolCall]) -> List[ToolResult]
    def get_available_tools(self) -> List[Tool]
    def validate_tool_call(self, tool_call: ToolCall) -> List[ValidationError]
```

### 8. Response Generator

The Response Generator formats the final output to be presented to the user, ensuring consistency and quality.

**Key Functions:**
- Generate user-facing responses
- Format responses based on user preferences
- Ensure response quality and consistency
- Handle multi-modal response generation

**Data Structures:**
```python
class ResponseFormat:
    format_type: FormatType
    style_guide: Optional[StyleGuide]
    max_length: Optional[int]
    
class Response:
    text: str
    attachments: List[Attachment]
    metadata: Dict[str, Any]
```

**Interface:**
```python
class ResponseGenerator:
    def generate_response(self, llm_output: str, state: AgentState, 
                         format: ResponseFormat) -> Response
    def format_tool_results(self, results: List[ToolResult]) -> str
    def check_response_quality(self, response: Response) -> List[QualityIssue]
```

### 9. User Interface Adapter

The User Interface Adapter handles communication between the agent core and various user interfaces.

**Key Functions:**
- Adapt between different UI protocols
- Handle message formatting for different UIs
- Manage UI-specific features and limitations
- Implement UI event handling

**Data Structures:**
```python
class UIMessage:
    message_type: MessageType
    content: str
    attachments: List[Attachment]
    ui_specific: Dict[str, Any]
    
class UIEvent:
    event_type: UIEventType
    payload: Dict[str, Any]
    timestamp: datetime
```

**Interface:**
```python
class UserInterfaceAdapter:
    def format_for_ui(self, response: Response, ui_type: UIType) -> UIMessage
    def parse_from_ui(self, ui_event: UIEvent) -> Event
    def get_supported_ui_features(self, ui_type: UIType) -> List[UIFeature]
```

## Agent Core Workflow

### Initialization Phase
1. Load configuration and system instructions
2. Register components and tools
3. Initialize state manager
4. Set up event stream processor
5. Connect to LLM service

### Request Processing Phase
1. Receive user request via UI adapter
2. Create new agent state or load existing session
3. Generate initial prompt using prompt manager
4. Send prompt to LLM via LLM interface
5. Parse LLM response for tool calls or direct response

### Execution Phase
1. If tool calls are present, validate and execute via tool executor
2. Process tool results and update state
3. If planning is needed, invoke planning module
4. Update event stream with new events
5. Determine next action based on updated state

### Response Generation Phase
1. Generate final response using response generator
2. Format response for target UI using UI adapter
3. Send response to user
4. Update state with response information
5. Persist state for future sessions

## Integration Points

### Planning Module Integration
- Agent Core invokes Planning Module to create execution plans
- Planning Module updates Agent State with plan information
- Agent Loop Controller uses plan to guide execution

### Knowledge Module Integration
- Agent Core queries Knowledge Module for relevant information
- Knowledge Module provides context for LLM prompts
- State Manager tracks knowledge retrievals in execution context

### Tool Framework Integration
- Component Registry manages tool registration
- Tool Executor invokes tools from the Tool Framework
- Event Stream Processor handles tool execution events

### LLM Service Integration
- LLM Interface connects to hosted or local LLM service
- Prompt Manager formats requests for the specific LLM
- Response parsing handles LLM-specific output formats

## Implementation Considerations

### Performance Optimization
- Implement caching for frequent LLM requests
- Optimize state management for memory efficiency
- Use asynchronous processing for tool execution
- Implement batching for LLM requests when possible

### Security Measures
- Validate all user inputs before processing
- Implement prompt injection protection
- Secure storage of sensitive state information
- Rate limiting for LLM and tool usage

### Error Handling
- Implement comprehensive error recovery strategies
- Log detailed error information for debugging
- Provide user-friendly error messages
- Implement graceful degradation for component failures

### Extensibility
- Design for easy addition of new components
- Use dependency injection for component coupling
- Implement versioned interfaces for backward compatibility
- Provide plugin architecture for custom extensions

## Next Steps

1. Detailed design of Planning Module
2. Detailed design of Knowledge Module
3. Interface specifications for Tool Framework
4. Implementation plan for Agent Core components
