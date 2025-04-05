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
    from tools.shell_provider import ShellToolProvider
    from tools.file_provider import FileToolProvider
    from tools.browser_provider import BrowserToolProvider
    from tools.information_provider import InformationToolProvider
    from tools.message_provider import MessageToolProvider
    from tools.models import ToolRegistry
except ImportError as e:
    print(f"Import error: {e}")
    print("This test assumes the tool provider files are in place.")
    print("If you're running this before implementation, some tests will fail.")


class TestToolProviders(unittest.TestCase):
    """Test cases for the Tool Provider components."""
    
    def test_tool_registry(self):
        """Test that ToolRegistry works correctly."""
        try:
            # Create a ToolRegistry instance
            registry = ToolRegistry()
            
            # Check that registry was initialized correctly
            self.assertIsNotNone(registry.tools)
            self.assertEqual(len(registry.tools), 0)
        except (NameError, AttributeError):
            self.skipTest("ToolRegistry not implemented yet")
    
    @patch('tools.shell_provider.ShellToolProvider.shell_exec')
    def test_shell_tool_provider(self, mock_shell_exec):
        """Test that ShellToolProvider works correctly."""
        try:
            # Mock the shell_exec method
            mock_shell_exec.return_value = {
                "success": True,
                "output": "Test output",
                "error": None,
                "exit_code": 0
            }
            
            # Create a ToolRegistry instance
            registry = ToolRegistry()
            
            # Create a ShellToolProvider instance
            provider = ShellToolProvider(registry)
            
            # Check that provider registered tools with registry
            self.assertGreater(len(registry.tools), 0)
            self.assertIn("shell_exec", registry.tools)
            
            # Get the shell_exec tool
            tool = registry.get_tool("shell_exec")
            
            # Check that tool was registered correctly
            self.assertEqual(tool.name, "shell_exec")
            self.assertIsNotNone(tool.function)
            
            # Call the tool function
            result = tool.function("test_id", "/tmp", "echo 'test'")
            
            # Check that function was called correctly
            mock_shell_exec.assert_called_once_with("test_id", "/tmp", "echo 'test'")
            
            # Check that result was processed correctly
            self.assertEqual(result["success"], True)
            self.assertEqual(result["output"], "Test output")
        except (NameError, AttributeError):
            self.skipTest("ShellToolProvider not implemented yet")
    
    @patch('tools.file_provider.FileToolProvider.file_read')
    def test_file_tool_provider(self, mock_file_read):
        """Test that FileToolProvider works correctly."""
        try:
            # Mock the file_read method
            mock_file_read.return_value = {
                "success": True,
                "content": "Test content",
                "line_count": 1,
                "file_size": 12
            }
            
            # Create a ToolRegistry instance
            registry = ToolRegistry()
            
            # Create a FileToolProvider instance
            provider = FileToolProvider(registry)
            
            # Check that provider registered tools with registry
            self.assertGreater(len(registry.tools), 0)
            self.assertIn("file_read", registry.tools)
            
            # Get the file_read tool
            tool = registry.get_tool("file_read")
            
            # Check that tool was registered correctly
            self.assertEqual(tool.name, "file_read")
            self.assertIsNotNone(tool.function)
            
            # Call the tool function
            result = tool.function("/tmp/test.txt")
            
            # Check that function was called correctly
            mock_file_read.assert_called_once_with("/tmp/test.txt")
            
            # Check that result was processed correctly
            self.assertEqual(result["success"], True)
            self.assertEqual(result["content"], "Test content")
        except (NameError, AttributeError):
            self.skipTest("FileToolProvider not implemented yet")
    
    @patch('tools.browser_provider.BrowserToolProvider.browser_navigate')
    def test_browser_tool_provider(self, mock_browser_navigate):
        """Test that BrowserToolProvider works correctly."""
        try:
            # Mock the browser_navigate method
            mock_browser_navigate.return_value = {
                "success": True,
                "url": "https://example.com",
                "title": "Example Domain",
                "status_code": 200
            }
            
            # Create a ToolRegistry instance
            registry = ToolRegistry()
            
            # Create a BrowserToolProvider instance
            provider = BrowserToolProvider(registry)
            
            # Check that provider registered tools with registry
            self.assertGreater(len(registry.tools), 0)
            self.assertIn("browser_navigate", registry.tools)
            
            # Get the browser_navigate tool
            tool = registry.get_tool("browser_navigate")
            
            # Check that tool was registered correctly
            self.assertEqual(tool.name, "browser_navigate")
            self.assertIsNotNone(tool.function)
            
            # Call the tool function
            result = tool.function("https://example.com")
            
            # Check that function was called correctly
            mock_browser_navigate.assert_called_once_with("https://example.com")
            
            # Check that result was processed correctly
            self.assertEqual(result["success"], True)
            self.assertEqual(result["url"], "https://example.com")
        except (NameError, AttributeError):
            self.skipTest("BrowserToolProvider not implemented yet")
    
    @patch('tools.information_provider.InformationToolProvider.info_search_web')
    def test_information_tool_provider(self, mock_info_search_web):
        """Test that InformationToolProvider works correctly."""
        try:
            # Mock the info_search_web method
            mock_info_search_web.return_value = {
                "success": True,
                "query": "test query",
                "date_range": "all",
                "results": [
                    {
                        "title": "Test Result",
                        "url": "https://example.com/result",
                        "snippet": "This is a test result."
                    }
                ],
                "result_count": 1
            }
            
            # Create a ToolRegistry instance
            registry = ToolRegistry()
            
            # Create an InformationToolProvider instance
            provider = InformationToolProvider(registry)
            
            # Check that provider registered tools with registry
            self.assertGreater(len(registry.tools), 0)
            self.assertIn("info_search_web", registry.tools)
            
            # Get the info_search_web tool
            tool = registry.get_tool("info_search_web")
            
            # Check that tool was registered correctly
            self.assertEqual(tool.name, "info_search_web")
            self.assertIsNotNone(tool.function)
            
            # Call the tool function
            result = tool.function("test query")
            
            # Check that function was called correctly
            mock_info_search_web.assert_called_once_with("test query")
            
            # Check that result was processed correctly
            self.assertEqual(result["success"], True)
            self.assertEqual(result["query"], "test query")
            self.assertEqual(len(result["results"]), 1)
        except (NameError, AttributeError):
            self.skipTest("InformationToolProvider not implemented yet")
    
    @patch('tools.message_provider.MessageToolProvider.message_notify_user')
    def test_message_tool_provider(self, mock_message_notify_user):
        """Test that MessageToolProvider works correctly."""
        try:
            # Mock the message_notify_user method
            mock_message_notify_user.return_value = {
                "success": True,
                "message_type": "notification",
                "text": "Test message",
                "attachments": [],
                "attachment_count": 0
            }
            
            # Create a ToolRegistry instance
            registry = ToolRegistry()
            
            # Create a MessageToolProvider instance
            provider = MessageToolProvider(registry)
            
            # Check that provider registered tools with registry
            self.assertGreater(len(registry.tools), 0)
            self.assertIn("message_notify_user", registry.tools)
            
            # Get the message_notify_user tool
            tool = registry.get_tool("message_notify_user")
            
            # Check that tool was registered correctly
            self.assertEqual(tool.name, "message_notify_user")
            self.assertIsNotNone(tool.function)
            
            # Call the tool function
            result = tool.function("Test message")
            
            # Check that function was called correctly
            mock_message_notify_user.assert_called_once_with("Test message")
            
            # Check that result was processed correctly
            self.assertEqual(result["success"], True)
            self.assertEqual(result["text"], "Test message")
        except (NameError, AttributeError):
            self.skipTest("MessageToolProvider not implemented yet")


if __name__ == '__main__':
    unittest.main()
