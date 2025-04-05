#!/bin/bash

# Main entry point script for Personal AI Agent
# This script starts the Personal AI Agent

# Set default values
CONFIG_PATH="./config/config.yaml"
LOG_LEVEL="INFO"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --config)
      CONFIG_PATH="$2"
      shift 2
      ;;
    --log-level)
      LOG_LEVEL="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --config PATH     Path to configuration file (default: ./config/config.yaml)"
      echo "  --log-level LEVEL Logging level (default: INFO)"
      echo "  --help            Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Export environment variables
export LOG_LEVEL="$LOG_LEVEL"

# Check if configuration file exists
if [ ! -f "$CONFIG_PATH" ]; then
  echo "Error: Configuration file not found at $CONFIG_PATH"
  exit 1
fi

# Start the agent
echo "Starting Personal AI Agent with configuration from $CONFIG_PATH"
python3 -m src.main --config "$CONFIG_PATH"
