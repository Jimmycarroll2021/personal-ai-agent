# Installation Guide: Personal AI Agent

This guide provides step-by-step instructions for installing and setting up your Personal AI Agent in different environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Installation](#docker-installation)
3. [Google Colab Pro Installation](#google-colab-pro-installation)
4. [Local Installation](#local-installation)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing your Personal AI Agent, ensure you have:

### For All Installation Methods
- DeepSeek API key (sign up at https://deepseek.com)

### For Docker Installation
- Docker Engine (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space

### For Google Colab Pro Installation
- Google Colab Pro subscription
- Google Drive account

### For Local Installation
- Python 3.10 or higher
- pip package manager
- Git
- 8GB RAM minimum
- 10GB free disk space

## Docker Installation

Docker provides the easiest and most consistent installation experience.

### Step 1: Clone or Download the Repository

```bash
git clone https://github.com/yourusername/personal-ai-agent.git
cd personal-ai-agent
```

Or extract the provided ZIP file:

```bash
unzip personal-ai-agent.zip
cd personal-ai-agent
```

### Step 2: Run the Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Check for Docker and Docker Compose
- Create necessary directories
- Set up configuration files
- Create a .env file for your API keys

### Step 3: Configure Your API Keys

Edit the .env file to add your DeepSeek API key:

```bash
nano .env
```

Update the following line:

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### Step 4: Build and Start the Containers

If you didn't choose to start the containers during setup, run:

```bash
docker-compose up -d --build
```

### Step 5: Verify Installation

Access the web interface at:
- http://localhost:8501 (UI)
- http://localhost:8000 (API)

## Google Colab Pro Installation

Google Colab Pro provides TPU acceleration for enhanced performance.

### Step 1: Create a New Colab Notebook

Go to https://colab.research.google.com/ and create a new notebook.

### Step 2: Upload the Deployment Script

Upload the `colab_deploy.sh` script to your Colab environment.

### Step 3: Run the Deployment Script

In a code cell, run:

```python
!chmod +x colab_deploy.sh
!./colab_deploy.sh
```

### Step 4: Configure Your API Key

You can either:

1. Enter your API key when prompted, or
2. Set it as an environment variable:

```python
import os
os.environ['DEEPSEEK_API_KEY'] = 'your_deepseek_api_key_here'
```

### Step 5: Launch the Agent

Run the launcher script:

```python
%run /content/personal-ai-agent/launch.py
```

### Step 6: Verify Installation

The agent will start in your Colab notebook and display a welcome message.

## Local Installation

Local installation gives you direct access to all files and components.

### Step 1: Clone or Download the Repository

```bash
git clone https://github.com/yourusername/personal-ai-agent.git
cd personal-ai-agent
```

Or extract the provided ZIP file:

```bash
unzip personal-ai-agent.zip
cd personal-ai-agent
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure the Agent

```bash
mkdir -p config data logs
cp config.yaml.example config/config.yaml
```

Edit the configuration file:

```bash
nano config/config.yaml
```

Update the API key section:

```yaml
llm:
  provider: "deepseek"
  model: "DeepSeek-R1-Distill-Qwen-7B"
  api_key: "your_deepseek_api_key_here"
```

### Step 5: Start the Agent

```bash
chmod +x run.sh
./run.sh
```

### Step 6: Verify Installation

The agent will start and display a welcome message. You can access the web interface at:
- http://localhost:8501

## Configuration

Your Personal AI Agent can be configured through the configuration file:

### Docker Installation
- Edit `config/config.yaml`

### Google Colab Pro Installation
- Edit `/content/personal-ai-agent/config/colab_config.yaml`

### Local Installation
- Edit `config/config.yaml`

### Key Configuration Options

```yaml
# Agent Core Configuration
agent:
  name: "Personal AI Agent"
  max_iterations: 50
  default_timeout: 300  # seconds

# LLM Configuration
llm:
  provider: "deepseek"
  model: "DeepSeek-R1-Distill-Qwen-7B"
  api_key: "your_api_key_here"
  temperature: 0.7
  max_tokens: 4096

# Tool Integration Configuration
tools:
  shell:
    enabled: true
  file:
    enabled: true
  browser:
    enabled: true
  information:
    enabled: true
  message:
    enabled: true
```

## Verification

To verify that your installation is working correctly:

### Run the Test Script

```bash
chmod +x test.sh
./test.sh
```

This will run a series of tests to verify:
- Project structure
- Docker configuration
- Python code
- Configuration files
- Deployment scripts

### Check Component Tests

```bash
cd tests
python -m unittest discover
```

This will run unit tests for all components.

### Test the Agent Interactively

1. Start the agent
2. Send a simple query: "What is the current time?"
3. Send a more complex query: "Create a simple Python function to calculate the factorial of a number"

## Troubleshooting

### Docker Installation Issues

**Issue**: Containers fail to start
**Solution**: Check Docker logs:
```bash
docker-compose logs
```

**Issue**: Permission denied errors
**Solution**: Run Docker commands with sudo or add your user to the docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Google Colab Pro Issues

**Issue**: TPU not detected
**Solution**: Ensure you have TPU runtime enabled in Colab:
1. Runtime > Change runtime type
2. Hardware accelerator > TPU

**Issue**: Memory errors
**Solution**: Reduce batch sizes in the configuration file:
```yaml
embedding:
  batch_size: 4  # Reduce from default 8
```

### Local Installation Issues

**Issue**: Missing dependencies
**Solution**: Install additional system packages:
```bash
sudo apt-get update
sudo apt-get install -y build-essential python3-dev
pip install -r requirements.txt
```

**Issue**: Port conflicts
**Solution**: Change the ports in the configuration:
```yaml
api:
  port: 8080  # Change from default 8000

ui:
  port: 8888  # Change from default 8501
```

### API Key Issues

**Issue**: Invalid API key
**Solution**: Verify your API key is correct and has sufficient credits

**Issue**: API rate limits
**Solution**: Implement exponential backoff in the configuration:
```yaml
llm:
  retry_attempts: 5
  retry_delay: 2  # seconds
```

If you encounter issues not covered here, please check the logs:
- Docker: `docker-compose logs agent`
- Local: Check `logs/agent.log`
- Colab: Check the output in your notebook

---

For additional help, refer to the User Guide and Technical Documentation.
