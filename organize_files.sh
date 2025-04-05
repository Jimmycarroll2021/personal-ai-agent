#!/bin/bash

echo "Starting project file organization..."

# --- Create Directory Structure ---
echo "Creating directories..."
mkdir -p src
mkdir -p src/agent_core
mkdir -p src/planning
mkdir -p src/knowledge
mkdir -p src/llm
mkdir -p src/tools
mkdir -p src/utils # Optional, if needed
mkdir -p docs
mkdir -p tests
mkdir -p config # Should already exist from colab_deploy, but -p makes it safe

# --- Move Python Source Files ---
echo "Moving Python source files..."
# Agent Core
mv agent_core.py src/agent_core/
mv agent_loop_controller.py src/agent_core/
mv event_stream_processor.py src/agent_core/
mv prompt_manager.py src/agent_core/
mv state_manager.py src/agent_core/
mv tool_manager.py src/agent_core/ # agent_core's tool manager
mv models.py src/agent_core/      # Assuming these are agent_core models
mv tool_integration.py src/agent_core/

# Planning
mv planning_module.py src/planning/
mv plan_generator.py src/planning/
mv plan_executor.py src/planning/
mv plan_evaluator.py src/planning/
# Add planning models.py if it exists: # mv planning_models.py src/planning/

# Knowledge
mv knowledge_module.py src/knowledge/
mv memory_manager.py src/knowledge/
mv vector_database.py src/knowledge/
mv retrieval_engine.py src/knowledge/
# Add knowledge models.py if it exists: # mv knowledge_models.py src/knowledge/

# LLM
mv llm_service_manager.py src/llm/ # Corrected name based on image
mv deepseek_client.py src/llm/
mv embedding_service.py src/llm/
mv system_instructions_manager.py src/llm/

# Tools
mv executor.py src/tools/ # tool framework's executor
mv provider.py src/tools/
mv shell_provider.py src/tools/
mv file_provider.py src/tools/
mv browser_provider.py src/tools/
mv information_provider.py src/tools/
mv message_provider.py src/tools/
# Add tools models.py if it exists: # mv tools_models.py src/tools/

# --- Create __init__.py Files ---
echo "Creating __init__.py files..."
touch src/__init__.py # Optional, but good practice
touch src/agent_core/__init__.py
touch src/planning/__init__.py
touch src/knowledge/__init__.py
touch src/llm/__init__.py
touch src/tools/__init__.py
touch src/utils/__init__.py # If utils dir is used

# --- Move Documentation Files ---
echo "Moving documentation files..."
mv agent_core_design.md docs/
mv planning_module_design.md docs/
mv knowledge_module_design.md docs/
mv system_architecture.md docs/
mv deployment_architecture.md docs/
mv research_summary.md docs/
mv technical_documentation.md docs/
mv user_guide.md docs/
mv installation_guide.md docs/
# Note: README.md and todo.md typically stay in the root

# --- Move Test Files ---
echo "Moving test files..."
mv test.sh tests/
mv integration_test.sh tests/
mv test_components.py tests/
mv test_llm_integration.py tests/ # Corrected name based on image
mv test_tool_providers.py tests/
touch tests/__init__.py # Good practice for test discovery

# --- Move Config Files ---
echo "Moving config files..."
# If config.yaml isn't already in config/, move it
if [ -f config.yaml ] && [ ! -f config/config.yaml ]; then
    mv config.yaml config/
fi
# docker-compose.yml stays in root

# --- Files expected to remain in root ---
# Dockerfile, docker-compose.yml, requirements.txt, README.md, todo.md
# setup.sh, run.sh, colab_deploy.sh, .gitignore (if created)

echo "File organization complete."
echo "Please verify the structure before proceeding with Git commands."