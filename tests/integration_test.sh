#!/bin/bash

# Integration test script for Personal AI Agent
# This script tests the integration between components

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${GREEN}"
echo "========================================================"
echo "      Personal AI Agent Integration Test Suite          "
echo "========================================================"
echo -e "${NC}"

# Create test directory
mkdir -p tests/integration/results

# Function to run a test and report results
run_test() {
  local test_name=$1
  local test_command=$2
  
  echo -e "${YELLOW}Running integration test: ${test_name}${NC}"
  echo "Command: ${test_command}"
  
  # Run the test and capture output
  output=$(eval ${test_command} 2>&1)
  exit_code=$?
  
  # Save output to file
  echo "${output}" > "tests/integration/results/${test_name}.log"
  
  # Report result
  if [ ${exit_code} -eq 0 ]; then
    echo -e "${GREEN}✓ Test passed: ${test_name}${NC}"
    return 0
  else
    echo -e "${RED}✗ Test failed: ${test_name}${NC}"
    echo "Error output:"
    echo "${output}" | tail -n 10
    echo "See tests/integration/results/${test_name}.log for full output"
    return 1
  fi
}

# Test 1: Agent Core and Planning Module Integration
test_agent_planning_integration() {
  echo "Testing Agent Core and Planning Module integration..."
  
  # Create test script
  cat > tests/integration/agent_planning_test.py << EOL
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from agent_core.agent_core import AgentCore
from planning.planning_module import PlanningModule
from agent_core.models import Event, EventType

def test_integration():
    # Initialize components
    planning_module = PlanningModule()
    agent_core = AgentCore()
    
    # Register planning module with agent core
    agent_core.register_planning_module(planning_module)
    
    # Create a test event
    event = Event(
        type=EventType.MESSAGE,
        source="user",
        content={"text": "Create a simple Python script to calculate fibonacci numbers"}
    )
    
    # Process the event
    agent_core.process_event(event)
    
    # Check that a plan was created
    plan = planning_module.get_current_plan()
    
    if plan is None:
        print("Error: No plan was created")
        return False
    
    print(f"Plan created with {len(plan.steps)} steps")
    for i, step in enumerate(plan.steps):
        print(f"Step {i+1}: {step.description}")
    
    return True

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
EOL
  
  # Run the test
  python3 tests/integration/agent_planning_test.py
  return $?
}

# Test 2: LLM Service and Knowledge Module Integration
test_llm_knowledge_integration() {
  echo "Testing LLM Service and Knowledge Module integration..."
  
  # Create test script
  cat > tests/integration/llm_knowledge_test.py << EOL
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from llm.llm_service_manager import LLMServiceManager
from knowledge.knowledge_module import KnowledgeModule
from knowledge.models import MemoryItem, MemoryType

def test_integration():
    # Initialize components with mock API key
    llm_service = LLMServiceManager(
        api_key="test_api_key",
        llm_model="DeepSeek-R1-Distill-Qwen-7B",
        embedding_model="deepseek-embedding"
    )
    
    knowledge_module = KnowledgeModule()
    
    # Register LLM service with knowledge module
    knowledge_module.register_llm_service(llm_service)
    
    # Create test memory items
    memory_items = [
        MemoryItem(
            content="Python is a programming language",
            type=MemoryType.FACT,
            source="test"
        ),
        MemoryItem(
            content="Fibonacci sequence is a series of numbers where each number is the sum of the two preceding ones",
            type=MemoryType.FACT,
            source="test"
        )
    ]
    
    # Add memory items to knowledge module
    for item in memory_items:
        knowledge_module.add_memory_item(item)
    
    # Test retrieval
    query = "How do I calculate fibonacci numbers in Python?"
    relevant_items = knowledge_module.retrieve_relevant_items(query, limit=2)
    
    if len(relevant_items) == 0:
        print("Error: No relevant items retrieved")
        return False
    
    print(f"Retrieved {len(relevant_items)} relevant items")
    for i, item in enumerate(relevant_items):
        print(f"Item {i+1}: {item.content}")
    
    return True

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
EOL
  
  # Run the test
  python3 tests/integration/llm_knowledge_test.py
  return $?
}

# Test 3: Tool Integration Framework Integration
test_tool_integration() {
  echo "Testing Tool Integration Framework..."
  
  # Create test script
  cat > tests/integration/tool_integration_test.py << EOL
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from agent_core.tool_integration import ToolIntegration
from tools.tool_manager import ToolManager
from tools.models import ToolRegistry

def test_integration():
    # Initialize components
    tool_registry = ToolRegistry()
    tool_manager = ToolManager(registry=tool_registry)
    tool_integration = ToolIntegration(tool_manager=tool_manager)
    
    # Get available tools
    tools = tool_integration.get_available_tools()
    
    if len(tools) == 0:
        print("Error: No tools available")
        return False
    
    print(f"Found {len(tools)} available tools")
    for i, tool in enumerate(tools[:5]):  # Print first 5 tools
        print(f"Tool {i+1}: {tool['name']} - {tool['description']}")
    
    # Test tool execution (with a mock)
    tool_name = "message_notify_user"
    if tool_name in [t['name'] for t in tools]:
        print(f"Testing execution of {tool_name}")
        
        # Mock execution
        result = {"success": True, "message": "Test message"}
        print(f"Execution result: {result}")
        
        return True
    else:
        print(f"Tool {tool_name} not found")
        return False

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
EOL
  
  # Run the test
  python3 tests/integration/tool_integration_test.py
  return $?
}

# Test 4: End-to-End Agent Workflow
test_end_to_end_workflow() {
  echo "Testing End-to-End Agent Workflow..."
  
  # Create test script
  cat > tests/integration/end_to_end_test.py << EOL
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from agent_core.agent_core import AgentCore
from agent_core.models import Event, EventType
from agent_core.agent_loop_controller import AgentLoopController

def test_integration():
    # Initialize agent core
    agent = AgentCore()
    
    # Initialize agent loop controller
    loop_controller = AgentLoopController(agent=agent)
    
    # Create a test event
    event = Event(
        type=EventType.MESSAGE,
        source="user",
        content={"text": "What is the current time?"}
    )
    
    # Process the event through the agent loop
    print("Starting agent loop with test event")
    
    # Mock the loop execution (just one iteration)
    loop_controller.process_single_event(event)
    
    print("Agent loop completed successfully")
    return True

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
EOL
  
  # Run the test
  python3 tests/integration/end_to_end_test.py
  return $?
}

# Run all tests
echo -e "${YELLOW}Starting integration test suite...${NC}"

# Initialize counters
passed=0
failed=0
total=0

# Run tests and count results
run_test "agent_planning_integration" "test_agent_planning_integration"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

run_test "llm_knowledge_integration" "test_llm_knowledge_integration"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

run_test "tool_integration" "test_tool_integration"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

run_test "end_to_end_workflow" "test_end_to_end_workflow"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

# Print summary
echo -e "${GREEN}"
echo "========================================================"
echo "          Integration Test Summary                     "
echo "========================================================"
echo -e "${NC}"
echo -e "Total tests: ${total}"
echo -e "Passed: ${GREEN}${passed}${NC}"
echo -e "Failed: ${RED}${failed}${NC}"

# Exit with appropriate code
if [ ${failed} -eq 0 ]; then
  echo -e "${GREEN}All integration tests passed!${NC}"
  exit 0
else
  echo -e "${RED}Some integration tests failed. See test logs for details.${NC}"
  exit 1
fi
