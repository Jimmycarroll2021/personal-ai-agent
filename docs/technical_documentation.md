# Technical Documentation: Personal AI Agent

## System Architecture

This document provides technical details about the Personal AI Agent architecture, components, and implementation. It is intended for developers who want to understand, modify, or extend the system.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [LLM Integration](#llm-integration)
4. [Tool Framework](#tool-framework)
5. [Deployment Architecture](#deployment-architecture)
6. [Data Flow](#data-flow)
7. [API Reference](#api-reference)
8. [Extension Guide](#extension-guide)

## Architecture Overview

The Personal AI Agent is built on a modular architecture with several key components:

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Agent Core                             │
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐    │
│  │ Event Stream │   │ State       │   │ Tool           │    │
│  │ Processor    │   │ Manager     │   │ Integration    │    │
│  └─────────────┘   └─────────────┘   └─────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│ Planning Module │ │ Knowledge Module│ │ Tool Framework      │
│                 │ │                 │ │                     │
│ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────────┐ │
│ │ Plan        │ │ │ │ Memory      │ │ │ │ Tool Registry   │ │
│ │ Generator   │ │ │ │ Manager     │ │ │ └─────────────────┘ │
│ └─────────────┘ │ │ └─────────────┘ │ │                     │
│                 │ │                 │ │ ┌─────────────────┐ │
│ ┌─────────────┐ │ │ ┌─────────────┐ │ │ │ Tool Providers  │ │
│ │ Plan        │ │ │ │ Vector      │ │ │ └─────────────────┘ │
│ │ Executor    │ │ │ │ Database    │ │ │                     │
│ └─────────────┘ │ │ └─────────────┘ │ │ ┌─────────────────┐ │
│                 │ │                 │ │ │ Tool Executor   │ │
│ ┌─────────────┐ │ │ ┌─────────────┐ │ │ └─────────────────┘ │
│ │ Plan        │ │ │ │ Retrieval   │ │ │                     │
│ │ Evaluator   │ │ │ │ Engine      │ │ └─────────────────────┘
│ └─────────────┘ │ │ └─────────────┘ │           │
└─────────────────┘ └─────────────────┘           │
          │                 │                      │
          └────────────────┬──────────────────────┘
                           │
                           ▼
                  ┌─────────────────────┐
                  │ LLM Service         │
                  │                     │
                  │ ┌─────────────────┐ │
                  │ │ DeepSeek Client │ │
                  │ └─────────────────┘ │
                  │                     │
                  │ ┌─────────────────┐ │
                  │ │ Embedding       │ │
                  │ │ Service         │ │
                  │ └─────────────────┘ │
                  └─────────────────────┘
```

### Key Design Principles

1. **Modularity**: Components are designed with clear interfaces for easy replacement or extension.
2. **Event-Driven**: The system operates on an event stream model, with events flowing through the system.
3. **Separation of Concerns**: Each component has a specific responsibility.
4. **Extensibility**: The tool framework allows for easy addition of new capabilities.
5. **Scalability**: The architecture supports scaling from local development to production deployments.

## Core Components

### Agent Core

The Agent Core is the central coordinator of the system, responsible for:

- Managing the agent loop
- Processing the event stream
- Maintaining agent state
- Coordinating between components
- Integrating with tools

#### Key Classes

- `AgentCore`: Main entry point and coordinator
- `EventStreamProcessor`: Processes events in the event stream
- `StateManager`: Manages the agent's state
- `ToolIntegration`: Integrates with the tool framework
- `PromptManager`: Manages system instructions and prompt templates
- `AgentLoopController`: Controls the agent's main loop

#### Event Model

Events are the primary data structure for communication between components. Each event has:

- `type`: The type of event (MESSAGE, ACTION, OBSERVATION, etc.)
- `source`: The source of the event (user, system, tool, etc.)
- `content`: The content of the event (varies by type)
- `timestamp`: When the event occurred

### Planning Module

The Planning Module is responsible for:

- Breaking down complex tasks into steps
- Generating execution plans
- Monitoring plan execution
- Revising plans based on feedback

#### Key Classes

- `PlanningModule`: Main entry point for planning functionality
- `PlanGenerator`: Generates plans using various methods (CoT, ToT, ReAct)
- `PlanExecutor`: Executes plans by dispatching steps
- `PlanEvaluator`: Evaluates plan success and suggests revisions

#### Planning Methods

The system supports multiple planning methods:

- **Chain of Thought (CoT)**: Linear reasoning through steps
- **Tree of Thoughts (ToT)**: Exploring multiple reasoning paths
- **ReAct**: Reasoning and acting with feedback loops

### Knowledge Module

The Knowledge Module manages the agent's memory and knowledge, including:

- Short-term memory (conversation context)
- Long-term memory (persistent knowledge)
- Vector representations for semantic search
- Knowledge retrieval

#### Key Classes

- `KnowledgeModule`: Main entry point for knowledge functionality
- `MemoryManager`: Manages different types of memory
- `VectorDatabase`: Stores and retrieves vector representations
- `RetrievalEngine`: Retrieves relevant information based on queries

#### Memory Types

The system supports different types of memory:

- `SHORT_TERM`: Recent conversation history
- `LONG_TERM`: Persistent knowledge
- `EPISODIC`: Memory of specific events or experiences
- `SEMANTIC`: Conceptual knowledge

## LLM Integration

The LLM Integration component provides a unified interface to language models:

### Key Classes

- `LLMServiceManager`: Manages LLM services and provides a unified interface
- `DeepSeekClient`: Client for the DeepSeek API
- `EmbeddingService`: Service for generating embeddings
- `SystemInstructionsManager`: Manages system instructions for the LLM

### DeepSeek-R1 Integration

The system is optimized for DeepSeek-R1, with specific features:

- Support for the DeepSeek-R1-Distill-Qwen-7B model
- TPU optimization for Google Colab Pro
- BFloat16 precision for numerical stability
- Tensor parallelism for performance
- Extended context length (32K tokens)

### API Integration

The LLM integration uses the DeepSeek API with:

- Proper authentication
- Rate limiting and retry logic
- Error handling
- Response parsing

## Tool Framework

The Tool Framework enables the agent to interact with external systems:

### Key Classes

- `ToolManager`: Manages tool providers and execution
- `ToolRegistry`: Registers available tools
- `ToolProvider`: Base class for tool providers
- `ToolExecutor`: Executes tool calls

### Tool Categories

The system includes several tool categories:

- `SHELL`: Execute shell commands
- `FILE`: Read, write, and manipulate files
- `BROWSER`: Navigate and interact with web pages
- `INFORMATION`: Search for information
- `MESSAGE`: Communicate with the user

### Tool Providers

Each tool category has a provider:

- `ShellToolProvider`: Provides shell tools
- `FileToolProvider`: Provides file tools
- `BrowserToolProvider`: Provides browser tools
- `InformationToolProvider`: Provides information tools
- `MessageToolProvider`: Provides message tools

### Tool Registration

Tools are registered with the system using:

- Name
- Description
- Parameters (with types and descriptions)
- Function to execute

## Deployment Architecture

The system supports multiple deployment options:

### Docker Deployment

- Multi-container setup with Docker Compose
- Agent container
- Vector database container (Qdrant)
- Shared volumes for persistence
- Environment variables for configuration

### Google Colab Pro Deployment

- TPU-optimized setup
- Google Drive integration for persistence
- Notebook-based interface
- TPU-specific configurations

### Local Deployment

- Direct installation on the host
- Local file system for persistence
- Command-line interface

### Kubernetes Deployment (Advanced)

- Scalable deployment with Kubernetes
- Stateful sets for the vector database
- Deployments for the agent
- Services for networking
- ConfigMaps and Secrets for configuration

## Data Flow

The system's data flow follows this pattern:

1. User input creates a MESSAGE event
2. Event is added to the event stream
3. Agent Core processes the event
4. Planning Module generates or updates a plan
5. Knowledge Module provides relevant context
6. LLM Service generates reasoning and actions
7. Tool Framework executes actions
8. Results are added to the event stream as OBSERVATION events
9. Agent Core processes the observations
10. Cycle continues until task completion

### Example Flow

```
User Input -> MESSAGE Event -> Event Stream -> Agent Core
  -> Planning Module (generate plan)
  -> Knowledge Module (retrieve context)
  -> LLM Service (generate reasoning)
  -> Tool Framework (execute action)
  -> OBSERVATION Event -> Event Stream -> Agent Core
  -> Planning Module (update plan)
  -> ...
  -> Task Completion -> MESSAGE Event (result) -> User
```

## API Reference

### Agent Core API

```python
# Initialize the Agent Core
agent = AgentCore(config_path="config/config.yaml")

# Process an event
event = Event(type=EventType.MESSAGE, source="user", content={"text": "Hello"})
agent.process_event(event)

# Run the agent loop
agent.run()

# Get the current state
state = agent.get_state()
```

### Planning Module API

```python
# Initialize the Planning Module
planning = PlanningModule(config_path="config/config.yaml")

# Generate a plan
plan = planning.generate_plan("Create a Python script to calculate fibonacci numbers")

# Execute a plan
planning.execute_plan(plan)

# Evaluate a plan
evaluation = planning.evaluate_plan(plan)
```

### Knowledge Module API

```python
# Initialize the Knowledge Module
knowledge = KnowledgeModule(config_path="config/config.yaml")

# Add a memory item
item = MemoryItem(content="Python is a programming language", type=MemoryType.FACT)
knowledge.add_memory_item(item)

# Retrieve relevant items
items = knowledge.retrieve_relevant_items("How do I program in Python?", limit=5)
```

### LLM Service API

```python
# Initialize the LLM Service
llm = LLMServiceManager(
    api_key="your_api_key",
    llm_model="DeepSeek-R1-Distill-Qwen-7B",
    embedding_model="deepseek-embedding"
)

# Get a completion
response = llm.get_completion("What is the capital of France?")

# Get an embedding
embedding = llm.get_embedding("This is a test sentence.")
```

### Tool Framework API

```python
# Initialize the Tool Manager
tool_manager = ToolManager()

# Get all available tools
tools = tool_manager.get_all_tools()

# Execute a tool
result = tool_manager.execute_tool("shell_exec", {"id": "test", "exec_dir": "/tmp", "command": "ls -la"})
```

## Extension Guide

### Adding a New Tool Provider

To add a new tool provider:

1. Create a new class that inherits from `ToolProvider`
2. Implement the required methods
3. Register the provider with the `ToolRegistry`

Example:

```python
from tools.provider import ToolProvider
from tools.models import ToolRegistry, ToolCategory

class CustomToolProvider(ToolProvider):
    """Custom tool provider for specific functionality."""
    
    def __init__(self, registry: ToolRegistry):
        """Initialize the provider and register tools."""
        super().__init__(registry, ToolCategory.CUSTOM)
        
        # Register tools
        self.register_tool(
            name="custom_tool",
            description="A custom tool that does something useful",
            function=self.custom_tool,
            parameters=[
                {"name": "param1", "type": "string", "description": "First parameter"},
                {"name": "param2", "type": "integer", "description": "Second parameter"}
            ]
        )
    
    def custom_tool(self, param1: str, param2: int) -> dict:
        """
        Implement the custom tool functionality.
        
        Args:
            param1: First parameter
            param2: Second parameter
            
        Returns:
            dict: Result of the tool execution
        """
        # Implement tool functionality
        result = f"Processed {param1} with value {param2}"
        
        return {
            "success": True,
            "result": result
        }
```

### Extending the LLM Integration

To add support for a new LLM provider:

1. Create a new client class for the provider
2. Implement the required methods
3. Update the `LLMServiceManager` to support the new provider

Example:

```python
class NewLLMClient:
    """Client for a new LLM provider."""
    
    def __init__(self, api_key: str, model: str):
        """Initialize the client."""
        self.api_key = api_key
        self.model = model
        self.api_base = "https://api.newllmprovider.com/v1"
    
    def complete(self, prompt: str) -> dict:
        """
        Generate a completion for the prompt.
        
        Args:
            prompt: The prompt to complete
            
        Returns:
            dict: The completion result
        """
        # Implement API call to the new provider
        # ...
        
        return {
            "role": "assistant",
            "content": "Generated response"
        }
```

### Customizing the Planning Module

To add a new planning method:

1. Create a new planner class
2. Implement the required methods
3. Register the planner with the `PlanningModule`

Example:

```python
from planning.models import Plan, PlanStep

class CustomPlanner:
    """Custom planning method."""
    
    def generate_plan(self, task: str) -> Plan:
        """
        Generate a plan for the task.
        
        Args:
            task: The task to plan for
            
        Returns:
            Plan: The generated plan
        """
        # Implement custom planning logic
        steps = [
            PlanStep(description="First step", status="pending"),
            PlanStep(description="Second step", status="pending")
        ]
        
        return Plan(task=task, steps=steps)
```

### Adding a New Deployment Option

To add a new deployment option:

1. Create deployment scripts for the new environment
2. Update the configuration to support the new environment
3. Document the new deployment option

Example for a new cloud provider:

```bash
#!/bin/bash
# deploy_to_new_cloud.sh

# Set up environment
echo "Setting up environment on New Cloud..."

# Create necessary resources
echo "Creating resources..."

# Deploy the agent
echo "Deploying agent..."

# Configure networking
echo "Configuring networking..."

# Start the agent
echo "Starting agent..."

echo "Deployment complete!"
```

---

This technical documentation provides a comprehensive overview of the Personal AI Agent system. For more detailed information about specific components, refer to the code documentation and comments.
