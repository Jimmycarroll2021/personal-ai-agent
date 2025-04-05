# README: Personal AI Agent

A complete end-to-end AI agent similar to Manus AI for personal use.

## Overview

This Personal AI Agent is a powerful AI assistant that can help you with a wide range of tasks, including:

- Information gathering, fact-checking, and documentation
- Data processing, analysis, and visualization
- Writing multi-chapter articles and in-depth research reports
- Creating websites, applications, and tools
- Using programming to solve various problems
- Automating processes
- Various tasks that can be accomplished using computers and the internet

The agent is powered by DeepSeek-R1, a state-of-the-art language model, and includes a comprehensive set of tools for interacting with your computer and the internet.

## Features

- **Modular Architecture**: Clearly defined components with clean interfaces
- **Advanced Planning**: Sophisticated planning capabilities using Chain of Thought, Tree of Thoughts, and ReAct
- **Knowledge Management**: Short-term and long-term memory with vector database integration
- **Comprehensive Tool Integration**: Shell, file, browser, information, and message tools
- **Multiple Deployment Options**: Docker, Google Colab Pro with TPU optimization, and local installation
- **Unlimited Context**: Knowledge module handles unlimited context through vector database integration
- **TPU Optimization**: Enhanced performance with TPU acceleration in Google Colab Pro

## Documentation

- [User Guide](docs/user_guide.md): Complete guide to using your Personal AI Agent
- [Technical Documentation](docs/technical_documentation.md): In-depth technical details about the system
- [Installation Guide](docs/installation_guide.md): Step-by-step installation instructions

## Quick Start

### Docker Installation (Recommended)

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

### Google Colab Pro Installation (TPU-Optimized)

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

### Local Installation

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

## System Requirements

### Docker Installation
- Docker Engine (version 20.10.0 or higher)
- Docker Compose (version 2.0.0 or higher)
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space

### Google Colab Pro Installation
- Google Colab Pro subscription
- Google Drive account

### Local Installation
- Python 3.10 or higher
- pip package manager
- Git
- 8GB RAM minimum
- 10GB free disk space

## Architecture

The Personal AI Agent is built on a modular architecture with several key components:

- **Agent Core**: Central coordinator that manages the agent loop, event processing, and state management
- **Planning Module**: Breaks down complex tasks into steps and monitors execution
- **Knowledge Module**: Manages memory and knowledge retrieval
- **LLM Integration**: Provides a unified interface to language models
- **Tool Framework**: Enables the agent to interact with external systems

For more details, see the [Technical Documentation](docs/technical_documentation.md).

## Testing

To verify that your installation is working correctly:

```bash
./test.sh
```

For integration tests:

```bash
./integration_test.sh
```

## Customization

You can customize your Personal AI Agent by editing the configuration file:

- Docker: `config/config.yaml`
- Google Colab: `/content/personal-ai-agent/config/colab_config.yaml`
- Local: `config/config.yaml`

See the [User Guide](docs/user_guide.md) for more details on customization options.

## License

This project is for personal use only. It is not affiliated with Manus AI.

## Acknowledgements

This project was inspired by Manus AI and leverages several open-source technologies:

- DeepSeek-R1 language model
- Qdrant vector database
- FastAPI and Uvicorn for API services
- Various Python libraries for tool integration

## Support

For issues and questions, please refer to the documentation:

- [User Guide](docs/user_guide.md)
- [Technical Documentation](docs/technical_documentation.md)
- [Installation Guide](docs/installation_guide.md)

If you encounter issues not covered in the documentation, check the logs:
- Docker: `docker-compose logs agent`
- Local: Check `logs/agent.log`
- Colab: Check the output in your notebook
