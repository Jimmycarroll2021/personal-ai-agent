# User Guide: Personal AI Agent

## Introduction

Welcome to your Personal AI Agent! This guide will help you get started with your new AI assistant, which provides capabilities similar to Manus AI but designed for your personal use.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Deployment Options](#deployment-options)
4. [Using Your Personal AI Agent](#using-your-personal-ai-agent)
5. [Available Tools](#available-tools)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## Overview

Your Personal AI Agent is a powerful AI assistant that can help you with a wide range of tasks, including:

- Information gathering, fact-checking, and documentation
- Data processing, analysis, and visualization
- Writing multi-chapter articles and in-depth research reports
- Creating websites, applications, and tools
- Using programming to solve various problems
- Automating processes
- Various tasks that can be accomplished using computers and the internet

The agent is powered by DeepSeek-R1, a state-of-the-art language model, and includes a comprehensive set of tools for interacting with your computer and the internet.

## Getting Started

### Prerequisites

Before you begin, make sure you have:

- A DeepSeek API key (sign up at https://deepseek.com)
- Docker and Docker Compose (for Docker deployment)
- Python 3.10+ (for local deployment)
- Google Colab Pro account (for TPU-optimized deployment)

### Quick Start

1. Clone the repository or extract the provided package
2. Navigate to the project directory
3. Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

4. Follow the prompts to configure your agent
5. Start using your Personal AI Agent!

## Deployment Options

Your Personal AI Agent can be deployed in several ways:

### Docker Deployment (Recommended)

The easiest way to get started is with Docker:

1. Make sure Docker and Docker Compose are installed
2. Run the setup script:

```bash
./setup.sh
```

3. Edit the `.env` file to add your DeepSeek API key
4. Start the containers:

```bash
docker-compose up -d
```

5. Access the agent at http://localhost:8501

### Google Colab Pro Deployment (TPU-Optimized)

For enhanced performance with TPU acceleration:

1. Upload the `colab_deploy.sh` script to your Google Colab notebook
2. Run the script:

```python
!chmod +x colab_deploy.sh
!./colab_deploy.sh
```

3. Follow the prompts to configure your agent
4. Start the agent:

```python
%run /content/personal-ai-agent/launch.py --api-key YOUR_DEEPSEEK_API_KEY
```

### Local Deployment

For direct installation on your machine:

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Configure your environment:

```bash
cp config.yaml.example config/config.yaml
# Edit config/config.yaml to add your API keys
```

3. Start the agent:

```bash
./run.sh
```

## Using Your Personal AI Agent

### Starting a Conversation

Once your agent is running, you can interact with it through the web interface at http://localhost:8501 (for Docker or local deployment) or directly in your Colab notebook (for Colab deployment).

Start by greeting your agent or asking it a question. For example:

- "Hello, can you help me research the history of artificial intelligence?"
- "I need to create a Python script to analyze some data."
- "Can you help me draft an article about climate change?"

### Task Types

Your Personal AI Agent excels at various tasks:

1. **Research and Information Gathering**
   - "Find information about renewable energy technologies."
   - "Research the latest developments in quantum computing."

2. **Content Creation**
   - "Write a comprehensive article about machine learning algorithms."
   - "Create a blog post about sustainable living."

3. **Programming and Development**
   - "Create a Python script to analyze CSV data."
   - "Help me build a simple website for my portfolio."

4. **Data Analysis**
   - "Analyze this dataset and create visualizations."
   - "Help me understand trends in this financial data."

5. **Problem Solving**
   - "Help me debug this code."
   - "Find a solution to this mathematical problem."

### Best Practices

For the best experience with your Personal AI Agent:

1. **Be Specific**: Clearly describe what you need help with.
2. **Provide Context**: Give background information when necessary.
3. **Break Down Complex Tasks**: For complex projects, break them into smaller steps.
4. **Review and Provide Feedback**: Let the agent know if its responses meet your needs.

## Available Tools

Your Personal AI Agent has access to various tools:

### Shell Tools
- Execute commands on your system
- Install packages
- Run scripts

### File Tools
- Read and write files
- Search for files
- Manipulate file content

### Browser Tools
- Navigate to websites
- Extract information from web pages
- Interact with web elements

### Information Tools
- Search the web for information
- Access knowledge bases
- Verify facts

### Message Tools
- Communicate with you
- Present results
- Ask for clarification when needed

## Customization

You can customize your Personal AI Agent by editing the configuration file:

### Docker Deployment
Edit `config/config.yaml` and restart the containers:

```bash
docker-compose restart
```

### Google Colab Deployment
Edit `/content/personal-ai-agent/config/colab_config.yaml` and restart the agent.

### Local Deployment
Edit `config/config.yaml` and restart the agent:

```bash
./run.sh
```

### Configuration Options

Key configuration options include:

- **LLM Settings**: Model selection, temperature, max tokens
- **Tool Availability**: Enable/disable specific tools
- **Memory Settings**: Short-term and long-term memory capacity
- **Planning Method**: Choose between different planning approaches

## Troubleshooting

### Common Issues

1. **Agent Not Responding**
   - Check if the containers are running: `docker-compose ps`
   - Check the logs: `docker-compose logs agent`

2. **API Key Issues**
   - Verify your DeepSeek API key in the `.env` file
   - Check if the API key has sufficient credits

3. **Memory Issues**
   - Increase the memory allocation in Docker settings
   - Reduce the vector database size in configuration

4. **Tool Execution Errors**
   - Check if the required dependencies are installed
   - Verify permissions for file and shell operations

### Getting Help

If you encounter issues not covered in this guide:

1. Check the logs for error messages
2. Consult the technical documentation
3. Try restarting the agent
4. Check for updates to the agent

## FAQ

**Q: How is my Personal AI Agent different from Manus AI?**
A: Your Personal AI Agent provides similar capabilities to Manus AI but is designed for personal use with your own API keys and deployment options.

**Q: Can I use a different language model?**
A: The agent is optimized for DeepSeek-R1, but the architecture supports integration with other models. Check the technical documentation for details.

**Q: Is my data secure?**
A: Your data remains on your local system or within your Google Colab environment. API calls to DeepSeek are subject to their privacy policy.

**Q: How can I extend the agent's capabilities?**
A: You can add new tool providers by implementing the provider interface. See the technical documentation for details.

**Q: Does the agent have access to the internet?**
A: Yes, the agent can access the internet through browser tools and information tools, allowing it to search for information and visit websites.

**Q: How much does it cost to run?**
A: The only cost is associated with the DeepSeek API usage, which depends on your usage patterns. The agent itself is free to use.

---

Thank you for using your Personal AI Agent! We hope it helps you accomplish your tasks more efficiently and effectively.
