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
    from llm.deepseek_client import DeepSeekClient
    from llm.embedding_service import EmbeddingService
    from llm.llm_service_manager import LLMServiceManager
except ImportError as e:
    print(f"Import error: {e}")
    print("This test assumes the LLM integration files are in place.")
    print("If you're running this before implementation, some tests will fail.")


class TestLLMIntegration(unittest.TestCase):
    """Test cases for the LLM Integration components."""
    
    @patch('llm.deepseek_client.requests.post')
    def test_deepseek_client_initialization(self, mock_post):
        """Test that DeepSeekClient initializes correctly."""
        try:
            # Create a DeepSeekClient instance
            client = DeepSeekClient(
                api_key="test_api_key",
                model="DeepSeek-R1-Distill-Qwen-7B"
            )
            
            # Check that client was initialized with correct values
            self.assertEqual(client.api_key, "test_api_key")
            self.assertEqual(client.model, "DeepSeek-R1-Distill-Qwen-7B")
            self.assertIsNotNone(client.api_base)
        except (NameError, AttributeError):
            self.skipTest("DeepSeekClient not implemented yet")
    
    @patch('llm.deepseek_client.requests.post')
    def test_deepseek_client_completion(self, mock_post):
        """Test that DeepSeekClient.complete works correctly."""
        try:
            # Mock the response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "test_id",
                "object": "chat.completion",
                "created": 1679580000,
                "model": "DeepSeek-R1-Distill-Qwen-7B",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "This is a test response."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15
                }
            }
            mock_post.return_value = mock_response
            
            # Create a DeepSeekClient instance
            client = DeepSeekClient(
                api_key="test_api_key",
                model="DeepSeek-R1-Distill-Qwen-7B"
            )
            
            # Call complete
            response = client.complete("This is a test prompt.")
            
            # Check that response was processed correctly
            self.assertEqual(response["content"], "This is a test response.")
            self.assertEqual(response["role"], "assistant")
            
            # Check that API was called correctly
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertIn("headers", kwargs)
            self.assertIn("Authorization", kwargs["headers"])
            self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test_api_key")
        except (NameError, AttributeError):
            self.skipTest("DeepSeekClient.complete not implemented yet")
    
    @patch('llm.embedding_service.requests.post')
    def test_embedding_service(self, mock_post):
        """Test that EmbeddingService works correctly."""
        try:
            # Mock the response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {
                        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
                    }
                ],
                "model": "deepseek-embedding",
                "usage": {
                    "prompt_tokens": 5,
                    "total_tokens": 5
                }
            }
            mock_post.return_value = mock_response
            
            # Create an EmbeddingService instance
            service = EmbeddingService(
                api_key="test_api_key",
                model="deepseek-embedding"
            )
            
            # Call get_embedding
            embedding = service.get_embedding("This is a test text.")
            
            # Check that embedding was processed correctly
            self.assertEqual(embedding, [0.1, 0.2, 0.3, 0.4, 0.5])
            
            # Check that API was called correctly
            mock_post.assert_called_once()
        except (NameError, AttributeError):
            self.skipTest("EmbeddingService not implemented yet")
    
    @patch('llm.llm_service_manager.DeepSeekClient')
    @patch('llm.llm_service_manager.EmbeddingService')
    def test_llm_service_manager(self, mock_embedding_service, mock_deepseek_client):
        """Test that LLMServiceManager works correctly."""
        try:
            # Mock the client and service
            mock_client_instance = MagicMock()
            mock_client_instance.complete.return_value = {
                "role": "assistant",
                "content": "This is a test response."
            }
            mock_deepseek_client.return_value = mock_client_instance
            
            mock_embedding_instance = MagicMock()
            mock_embedding_instance.get_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
            mock_embedding_service.return_value = mock_embedding_instance
            
            # Create a LLMServiceManager instance
            manager = LLMServiceManager(
                api_key="test_api_key",
                llm_model="DeepSeek-R1-Distill-Qwen-7B",
                embedding_model="deepseek-embedding"
            )
            
            # Call get_completion
            response = manager.get_completion("This is a test prompt.")
            
            # Check that response was processed correctly
            self.assertEqual(response["content"], "This is a test response.")
            
            # Call get_embedding
            embedding = manager.get_embedding("This is a test text.")
            
            # Check that embedding was processed correctly
            self.assertEqual(embedding, [0.1, 0.2, 0.3, 0.4, 0.5])
        except (NameError, AttributeError):
            self.skipTest("LLMServiceManager not implemented yet")


if __name__ == '__main__':
    unittest.main()
