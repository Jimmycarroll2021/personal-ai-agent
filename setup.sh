#!/bin/bash

# Setup script for Personal AI Agent
# This script helps set up the environment for running the Personal AI Agent

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${GREEN}"
echo "========================================================"
echo "          Personal AI Agent Setup Script                "
echo "========================================================"
echo -e "${NC}"

# Check if Docker is installed
echo -e "${YELLOW}Checking if Docker is installed...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}Docker is installed.${NC}"
else
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Check if Docker Compose is installed
echo -e "${YELLOW}Checking if Docker Compose is installed...${NC}"
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}Docker Compose is installed.${NC}"
else
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p data logs config

# Check if config file exists, if not copy the default one
if [ ! -f "config/config.yaml" ]; then
    echo -e "${YELLOW}Copying default configuration file...${NC}"
    cp config.yaml.example config/config.yaml
    echo -e "${GREEN}Default configuration file copied to config/config.yaml${NC}"
    echo -e "${YELLOW}Please edit config/config.yaml to set your API keys and preferences.${NC}"
fi

# Create .env file for environment variables if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file for environment variables...${NC}"
    cat > .env << EOL
# Environment variables for Personal AI Agent
# Replace the placeholder values with your actual API keys

# DeepSeek API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
EOL
    echo -e "${GREEN}.env file created.${NC}"
    echo -e "${YELLOW}Please edit .env file to set your API keys.${NC}"
fi

# Ask if user wants to build and start the containers
echo -e "${YELLOW}Do you want to build and start the containers now? (y/n)${NC}"
read -r answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Building and starting containers...${NC}"
    docker-compose up -d --build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Containers built and started successfully!${NC}"
        echo -e "${GREEN}The Personal AI Agent is now running.${NC}"
        echo -e "${GREEN}API is available at: http://localhost:8000${NC}"
        echo -e "${GREEN}UI is available at: http://localhost:8501${NC}"
    else
        echo -e "${RED}Failed to build and start containers.${NC}"
        echo "Please check the error messages above."
    fi
else
    echo -e "${YELLOW}You can build and start the containers later by running:${NC}"
    echo "docker-compose up -d --build"
fi

echo -e "${GREEN}"
echo "========================================================"
echo "          Setup Complete                               "
echo "========================================================"
echo -e "${NC}"
