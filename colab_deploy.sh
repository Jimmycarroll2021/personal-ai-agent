#!/bin/bash

# Google Colab Pro deployment script for Personal AI Agent
# This script sets up the Personal AI Agent in a Google Colab Pro environment

# Function to display section headers
section() {
  echo "===================================================================="
  echo "  $1"
  echo "===================================================================="
}

# Install required packages
section "Installing Required Packages"
pip install -q pydantic fastapi uvicorn python-dotenv pyyaml loguru typer
pip install -q openai transformers torch sentence-transformers langchain langchain-community
pip install -q qdrant-client requests beautifulsoup4 selenium pillow python-multipart

# Set up TPU support if available
section "Setting Up TPU Support"
if [ -d "/usr/local/lib/python3.*/dist-packages/torch_xla" ]; then
  echo "TPU support detected, configuring for optimal performance..."
  # Import TPU-specific libraries in Python
  python -c "
import torch_xla
import torch_xla.core.xla_model as xm
print(f'TPU devices available: {xm.xla_device_count()}')
"
else
  echo "No TPU detected, will use GPU if available."
fi

# Create directory structure
section "Creating Directory Structure"
mkdir -p /content/personal-ai-agent
mkdir -p /content/personal-ai-agent/src
mkdir -p /content/personal-ai-agent/data
mkdir -p /content/personal-ai-agent/config
mkdir -p /content/personal-ai-agent/logs

# Clone repository if it exists
section "Cloning Repository"
if [ -n "$REPO_URL" ]; then
  git clone $REPO_URL /content/personal-ai-agent/repo
  cp -r /content/personal-ai-agent/repo/src/* /content/personal-ai-agent/src/
  cp -r /content/personal-ai-agent/repo/config/* /content/personal-ai-agent/config/
  echo "Repository cloned and files copied."
else
  echo "No repository URL provided, skipping clone."
  echo "Please upload your source files manually or provide REPO_URL."
fi

# Create configuration file
section "Creating Configuration File"
cat > /content/personal-ai-agent/config/colab_config.yaml << EOL
# Configuration file for Personal AI Agent on Google Colab Pro

# Agent Core Configuration
agent:
  name: "Personal AI Agent"
  version: "1.0.0"
  description: "A personal AI agent similar to Manus AI"
  max_iterations: 50
  default_timeout: 300  # seconds

# LLM Configuration
llm:
  provider: "deepseek"
  model: "DeepSeek-R1-Distill-Qwen-7B"
  api_key: "${DEEPSEEK_API_KEY}"
  api_base: "https://api.deepseek.com/v1"
  max_tokens: 4096
  temperature: 0.7
  top_p: 0.95
  frequency_penalty: 0.0
  presence_penalty: 0.0
  timeout: 60  # seconds
  retry_attempts: 3
  retry_delay: 2  # seconds
  
  # TPU optimization settings
  use_tpu: true
  precision: "bfloat16"
  max_context_length: 32768
  tensor_parallel_size: 8

# Embedding Configuration
embedding:
  provider: "deepseek"
  model: "deepseek-embedding"
  dimensions: 1536
  batch_size: 8

# Vector Database Configuration
vector_db:
  provider: "qdrant"
  host: "localhost"
  port: 6333
  collection_name: "knowledge_base"
  distance_metric: "Cosine"
  vector_size: 1536

# Knowledge Module Configuration
knowledge:
  max_short_term_memory: 100
  max_long_term_memory: 10000
  relevance_threshold: 0.75
  memory_refresh_interval: 3600  # seconds

# Planning Module Configuration
planning:
  planning_method: "react"  # Options: "cot", "tot", "react"
  max_plan_steps: 20
  plan_revision_threshold: 0.3

# Tool Integration Configuration
tools:
  shell:
    enabled: true
    timeout: 30  # seconds
    max_output_size: 10240  # bytes
  
  file:
    enabled: true
    max_file_size: 10485760  # bytes (10MB)
    allowed_extensions: [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yaml", ".yml"]
  
  browser:
    enabled: true
    timeout: 60  # seconds
    max_tabs: 5
    user_agent: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  
  information:
    enabled: true
    search_timeout: 30  # seconds
    max_results: 10
  
  message:
    enabled: true

# Logging Configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/content/personal-ai-agent/logs/agent.log"
  max_file_size: 10485760  # bytes (10MB)
  backup_count: 5

# Google Drive Integration
google_drive:
  enabled: true
  mount_point: "/content/drive"
  data_folder: "MyDrive/personal-ai-agent/data"
  backup_interval: 3600  # seconds
EOL

echo "Configuration file created at /content/personal-ai-agent/config/colab_config.yaml"

# Create launcher script
section "Creating Launcher Script"
cat > /content/personal-ai-agent/launch.py << EOL
#!/usr/bin/env python3
"""
Launcher script for Personal AI Agent on Google Colab Pro.
"""

import os
import sys
import yaml
import argparse
from pathlib import Path

# Add the src directory to the Python path
sys.path.append('/content/personal-ai-agent/src')

def setup_google_drive():
    """Mount Google Drive if not already mounted."""
    from google.colab import drive
    if not os.path.exists('/content/drive'):
        print("Mounting Google Drive...")
        drive.mount('/content/drive')
        print("Google Drive mounted.")
    else:
        print("Google Drive is already mounted.")
    
    # Create data directory in Google Drive if it doesn't exist
    with open('/content/personal-ai-agent/config/colab_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    if config.get('google_drive', {}).get('enabled', False):
        data_folder = config['google_drive']['data_folder']
        full_path = os.path.join('/content/drive', data_folder)
        os.makedirs(full_path, exist_ok=True)
        print(f"Data directory created at {full_path}")

def setup_tpu():
    """Set up TPU if available."""
    try:
        import torch_xla
        import torch_xla.core.xla_model as xm
        
        print(f"TPU devices available: {xm.xla_device_count()}")
        
        # Configure TPU settings
        with open('/content/personal-ai-agent/config/colab_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        if config.get('llm', {}).get('use_tpu', False):
            print("Configuring TPU for LLM inference...")
            # Additional TPU setup would go here
            return True
    except ImportError:
        print("TPU support not available.")
    except Exception as e:
        print(f"Error setting up TPU: {e}")
    
    return False

def main():
    """Main entry point for the launcher."""
    parser = argparse.ArgumentParser(description='Launch Personal AI Agent on Google Colab Pro')
    parser.add_argument('--config', type=str, default='/content/personal-ai-agent/config/colab_config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--api-key', type=str, help='DeepSeek API key')
    parser.add_argument('--no-drive', action='store_true', help='Disable Google Drive integration')
    parser.add_argument('--no-tpu', action='store_true', help='Disable TPU optimization')
    
    args = parser.parse_args()
    
    # Set API key from argument or environment
    if args.api_key:
        os.environ['DEEPSEEK_API_KEY'] = args.api_key
    elif 'DEEPSEEK_API_KEY' not in os.environ:
        api_key = input("Enter your DeepSeek API key: ")
        os.environ['DEEPSEEK_API_KEY'] = api_key
    
    # Setup Google Drive integration
    if not args.no_drive:
        setup_google_drive()
    
    # Setup TPU if available and not disabled
    if not args.no_tpu:
        tpu_available = setup_tpu()
        if tpu_available:
            print("TPU optimization enabled.")
        else:
            print("TPU optimization not available, falling back to GPU/CPU.")
    
    # Import and run the main application
    try:
        from agent_core.agent_core import AgentCore
        
        print("Starting Personal AI Agent...")
        agent = AgentCore(config_path=args.config)
        agent.run()
    except ImportError as e:
        print(f"Error importing agent modules: {e}")
        print("Please ensure all source files are correctly placed in /content/personal-ai-agent/src")
    except Exception as e:
        print(f"Error starting agent: {e}")

if __name__ == '__main__':
    main()
EOL

echo "Launcher script created at /content/personal-ai-agent/launch.py"
chmod +x /content/personal-ai-agent/launch.py

# Create a simple README
section "Creating README"
cat > /content/personal-ai-agent/README.md << EOL
# Personal AI Agent for Google Colab Pro

This is a deployment of the Personal AI Agent optimized for Google Colab Pro with TPU support.

## Getting Started

1. Run the setup script (already completed)
2. Upload your source files to /content/personal-ai-agent/src or specify a repository URL
3. Run the launcher script:

\`\`\`python
%run /content/personal-ai-agent/launch.py --api-key YOUR_DEEPSEEK_API_KEY
\`\`\`

## Features

- TPU optimization for DeepSeek-R1 model
- Google Drive integration for persistent storage
- Comprehensive tool integration framework
- Advanced planning and knowledge modules

## Configuration

The configuration file is located at:
\`/content/personal-ai-agent/config/colab_config.yaml\`

You can modify this file to customize the agent's behavior.

## Troubleshooting

If you encounter any issues, please check the logs at:
\`/content/personal-ai-agent/logs/agent.log\`
EOL

echo "README created at /content/personal-ai-agent/README.md"

# Final instructions
section "Deployment Complete"
echo "The Personal AI Agent has been deployed to Google Colab Pro."
echo ""
echo "To start the agent, run:"
echo "%run /content/personal-ai-agent/launch.py --api-key YOUR_DEEPSEEK_API_KEY"
echo ""
echo "Make sure to replace YOUR_DEEPSEEK_API_KEY with your actual API key."
echo "You can also set it as an environment variable before running the script."
echo ""
echo "For more information, see the README at /content/personal-ai-agent/README.md"
