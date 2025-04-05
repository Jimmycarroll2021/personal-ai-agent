#!/bin/bash

# Test script for Personal AI Agent
# This script runs tests to validate the Personal AI Agent implementation

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${GREEN}"
echo "========================================================"
echo "          Personal AI Agent Test Suite                  "
echo "========================================================"
echo -e "${NC}"

# Create test directory
mkdir -p tests/results

# Function to run a test and report results
run_test() {
  local test_name=$1
  local test_command=$2
  
  echo -e "${YELLOW}Running test: ${test_name}${NC}"
  echo "Command: ${test_command}"
  
  # Run the test and capture output
  output=$(eval ${test_command} 2>&1)
  exit_code=$?
  
  # Save output to file
  echo "${output}" > "tests/results/${test_name}.log"
  
  # Report result
  if [ ${exit_code} -eq 0 ]; then
    echo -e "${GREEN}✓ Test passed: ${test_name}${NC}"
    return 0
  else
    echo -e "${RED}✗ Test failed: ${test_name}${NC}"
    echo "Error output:"
    echo "${output}" | tail -n 10
    echo "See tests/results/${test_name}.log for full output"
    return 1
  fi
}

# Test 1: Validate project structure
test_project_structure() {
  echo "Validating project structure..."
  
  # Check for required directories
  for dir in src config data; do
    if [ ! -d "$dir" ]; then
      echo "Missing directory: $dir"
      return 1
    fi
  done
  
  # Check for required files
  for file in Dockerfile docker-compose.yml requirements.txt setup.sh run.sh; do
    if [ ! -f "$file" ]; then
      echo "Missing file: $file"
      return 1
    fi
  done
  
  # Check for core components
  for component in agent_core planning knowledge tools llm; do
    if [ ! -d "src/$component" ]; then
      echo "Missing component directory: src/$component"
      return 1
    fi
  done
  
  return 0
}

# Test 2: Validate Docker configuration
test_docker_config() {
  echo "Validating Docker configuration..."
  
  # Check if Docker is installed
  if ! command -v docker &> /dev/null; then
    echo "Docker is not installed, skipping Docker validation"
    return 0
  fi
  
  # Validate Dockerfile
  if ! docker build --quiet --file Dockerfile . -t personal-ai-agent:test; then
    echo "Dockerfile validation failed"
    return 1
  fi
  
  # Validate docker-compose.yml
  if ! docker-compose config; then
    echo "docker-compose.yml validation failed"
    return 1
  fi
  
  return 0
}

# Test 3: Validate Python code
test_python_code() {
  echo "Validating Python code..."
  
  # Check if Python is installed
  if ! command -v python3 &> /dev/null; then
    echo "Python is not installed, skipping Python code validation"
    return 0
  fi
  
  # Check for syntax errors in Python files
  find src -name "*.py" -print0 | while IFS= read -r -d '' file; do
    if ! python3 -m py_compile "$file"; then
      echo "Syntax error in: $file"
      return 1
    fi
  done
  
  return 0
}

# Test 4: Validate configuration files
test_config_files() {
  echo "Validating configuration files..."
  
  # Check if Python is installed
  if ! command -v python3 &> /dev/null; then
    echo "Python is not installed, skipping configuration validation"
    return 0
  fi
  
  # Validate YAML configuration
  python3 -c "
import yaml
import sys
try:
    with open('config/config.yaml', 'r') as f:
        yaml.safe_load(f)
    print('Configuration file is valid YAML')
    sys.exit(0)
except Exception as e:
    print(f'Error validating configuration file: {e}')
    sys.exit(1)
"
  return $?
}

# Test 5: Validate deployment scripts
test_deployment_scripts() {
  echo "Validating deployment scripts..."
  
  # Check if bash is available
  if ! command -v bash &> /dev/null; then
    echo "Bash is not available, skipping script validation"
    return 0
  fi
  
  # Validate shell scripts with bash -n
  for script in setup.sh run.sh colab_deploy.sh; do
    if ! bash -n "$script"; then
      echo "Syntax error in: $script"
      return 1
    fi
  done
  
  return 0
}

# Run all tests
echo -e "${YELLOW}Starting test suite...${NC}"

# Initialize counters
passed=0
failed=0
total=0

# Run tests and count results
run_test "project_structure" "test_project_structure"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

run_test "docker_config" "test_docker_config"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

run_test "python_code" "test_python_code"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

run_test "config_files" "test_config_files"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

run_test "deployment_scripts" "test_deployment_scripts"
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

# Print summary
echo -e "${GREEN}"
echo "========================================================"
echo "          Test Summary                                 "
echo "========================================================"
echo -e "${NC}"
echo -e "Total tests: ${total}"
echo -e "Passed: ${GREEN}${passed}${NC}"
echo -e "Failed: ${RED}${failed}${NC}"

# Exit with appropriate code
if [ ${failed} -eq 0 ]; then
  echo -e "${GREEN}All tests passed!${NC}"
  exit 0
else
  echo -e "${RED}Some tests failed. See test logs for details.${NC}"
  exit 1
fi
