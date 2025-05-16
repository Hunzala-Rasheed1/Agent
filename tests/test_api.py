import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    @patch('src.main.agent.query')
    def test_query_endpoint(self, mock_query):
        # Setup mock
        mock_query.return_value = {
            "answer": "There are 3 jobs available.",
            "graphql_query": "{ jobs { title } }",
            "raw_result": {"data": {"jobs": [{"title": "Job 1"}, {"title": "Job 2"}, {"title": "Job 3"}]}}
        }
        
        # Test the endpoint
        response = self.client.post("/query", json={"q": "What jobs are available?"})
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["answer"], "There are 3 jobs available.")
        self.assertEqual(result["graphql_query"], "{ jobs { title } }")
        self.assertNotIn("raw_result", result)  # raw_result should not be in the response
        
        # Verify that the agent was called
        mock_query.assert_called_once_with("What jobs are available?")
        
    @patch('src.main.agent.query')
    def test_query_endpoint_with_error(self, mock_query):
        # Setup mock to return an error
        mock_query.return_value = {
            "answer": "I encountered an error: Test error",
            "error": "Test error"
        }
        
        # Test the endpoint
        response = self.client.post("/query", json={"q": "What jobs are available?"})
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["answer"], "I encountered an error: Test error")
        self.assertEqual(result["error"], "Test error")
        
    def test_empty_query(self):
        # Test with an empty query
        response = self.client.post("/query", json={"q": ""})
        
        # Verify the response
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertIn("detail", result)
        self.assertEqual(result["detail"], "Query cannot be empty")
        
    def test_root_endpoint(self):
        # Test the root endpoint
        response = self.client.get("/")
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("message", result)

if __name__ == '__main__':
    unittest.main()