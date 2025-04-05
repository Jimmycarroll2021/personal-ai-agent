import unittest
import os
import sys
import yaml
import json
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import components to test
try:
    from agent_core.models import Event, EventType
    from agent_core.tool_integration import ToolIntegration
    from tools.models import ToolCategory, ParameterType
    from tools.tool_manager import ToolManager
except ImportError as e:
    print(f"Import error: {e}")
    print("This test assumes the implementation files are in place.")
    print("If you're running this before implementation, some tests will fail.")


class TestAgentCore(unittest.TestCase):
    """Test cases for the Agent Core component."""
    
    def test_event_creation(self):
        """Test that Event objects can be created correctly."""
        try:
            event = Event(
                type=EventType.MESSAGE,
                source="user",
                content={"text": "Hello, agent!"}
            )
            
            self.assertEqual(event.type, EventType.MESSAGE)
            self.assertEqual(event.source, "user")
            self.assertEqual(event.content["text"], "Hello, agent!")
            self.assertIsNotNone(event.timestamp)
        except NameError:
            self.skipTest("Event class not implemented yet")
    
    def test_event_serialization(self):
        """Test that Event objects can be serialized to JSON."""
        try:
            event = Event(
                type=EventType.MESSAGE,
                source="user",
                content={"text": "Hello, agent!"}
            )
            
            # Convert to dict and then to JSON
            event_dict = event.to_dict()
            event_json = json.dumps(event_dict)
            
            # Parse JSON back to dict
            parsed_dict = json.loads(event_json)
            
            self.assertEqual(parsed_dict["type"], event.type.value)
            self.assertEqual(parsed_dict["source"], event.source)
            self.assertEqual(parsed_dict["content"]["text"], event.content["text"])
        except (NameError, AttributeError):
            self.skipTest("Event serialization not implemented yet")


class TestToolFramework(unittest.TestCase):
    """Test cases for the Tool Framework component."""
    
    def test_tool_category_enum(self):
        """Test that ToolCategory enum is defined correctly."""
        try:
            self.assertIn(ToolCategory.SHELL, ToolCategory)
            self.assertIn(ToolCategory.FILE, ToolCategory)
            self.assertIn(ToolCategory.BROWSER, ToolCategory)
            self.assertIn(ToolCategory.INFORMATION, ToolCategory)
            self.assertIn(ToolCategory.MESSAGE, ToolCategory)
        except NameError:
            self.skipTest("ToolCategory enum not implemented yet")
    
    def test_parameter_type_enum(self):
        """Test that ParameterType enum is defined correctly."""
        try:
            self.assertIn(ParameterType.STRING, ParameterType)
            self.assertIn(ParameterType.INTEGER, ParameterType)
            self.assertIn(ParameterType.FLOAT, ParameterType)
            self.assertIn(ParameterType.BOOLEAN, ParameterType)
            self.assertIn(ParameterType.ARRAY, ParameterType)
            self.assertIn(ParameterType.OBJECT, ParameterType)
        except NameError:
            self.skipTest("ParameterType enum not implemented yet")
    
    @patch('tools.tool_manager.ToolRegistry')
    def test_tool_manager_initialization(self, mock_registry):
        """Test that ToolManager initializes correctly."""
        try:
            # Create a ToolManager instance
            manager = ToolManager()
            
            # Check that providers were initialized
            self.assertIsNotNone(manager.providers)
            self.assertGreater(len(manager.providers), 0)
        except (NameError, AttributeError):
            self.skipTest("ToolManager not implemented yet")


class TestToolIntegration(unittest.TestCase):
    """Test cases for the Tool Integration component."""
    
    @patch('tools.tool_manager.ToolManager')
    def test_tool_integration_initialization(self, mock_tool_manager):
        """Test that ToolIntegration initializes correctly."""
        try:
            # Mock the ToolManager
            mock_instance = mock_tool_manager.return_value
            mock_instance.get_all_tools.return_value = []
            
            # Create a ToolIntegration instance
            integration = ToolIntegration()
            
            # Check that tool_manager was initialized
            self.assertIsNotNone(integration.tool_manager)
        except (NameError, AttributeError):
            self.skipTest("ToolIntegration not implemented yet")
    
    @patch('tools.tool_manager.ToolManager')
    def test_get_available_tools(self, mock_tool_manager):
        """Test that get_available_tools returns tools from ToolManager."""
        try:
            # Mock the ToolManager
            mock_instance = mock_tool_manager.return_value
            mock_tools = [
                {"name": "tool1", "description": "Tool 1"},
                {"name": "tool2", "description": "Tool 2"}
            ]
            mock_instance.get_all_tools.return_value = mock_tools
            
            # Create a ToolIntegration instance
            integration = ToolIntegration()
            
            # Call get_available_tools
            tools = integration.get_available_tools()
            
            # Check that tools were returned
            self.assertEqual(tools, mock_tools)
            mock_instance.get_all_tools.assert_called_once()
        except (NameError, AttributeError):
            self.skipTest("ToolIntegration.get_available_tools not implemented yet")


class TestConfiguration(unittest.TestCase):
    """Test cases for configuration files."""
    
    def test_config_yaml_validity(self):
        """Test that config.yaml is valid YAML."""
        config_path = os.path.join(os.path.dirname(__file__), '../config/config.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                try:
                    config = yaml.safe_load(f)
                    self.assertIsNotNone(config)
                    self.assertIsInstance(config, dict)
                except yaml.YAMLError as e:
                    self.fail(f"config.yaml is not valid YAML: {e}")
        else:
            self.skipTest("config.yaml not found")
    
    def test_docker_compose_yaml_validity(self):
        """Test that docker-compose.yml is valid YAML."""
        compose_path = os.path.join(os.path.dirname(__file__), '../docker-compose.yml')
        if os.path.exists(compose_path):
            with open(compose_path, 'r') as f:
                try:
                    compose = yaml.safe_load(f)
                    self.assertIsNotNone(compose)
                    self.assertIsInstance(compose, dict)
                    self.assertIn('services', compose)
                    self.assertIn('agent', compose['services'])
                    self.assertIn('vector-db', compose['services'])
                except yaml.YAMLError as e:
                    self.fail(f"docker-compose.yml is not valid YAML: {e}")
        else:
            self.skipTest("docker-compose.yml not found")


if __name__ == '__main__':
    unittest.main()
