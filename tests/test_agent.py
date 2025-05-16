import unittest
from unittest.mock import patch, MagicMock
import json
import os

from src.agent import GraphQLAgent

class TestGraphQLAgent(unittest.TestCase):
    @patch('src.agent.GraphQLTool')
    @patch('src.agent.AzureChatOpenAI')
    @patch('src.agent.LLMChain')
    def setUp(self, mock_llm_chain, mock_azure_chat, mock_graphql_tool):
        self.mock_graphql_tool = mock_graphql_tool.return_value
        self.mock_llm = mock_azure_chat.return_value
        self.mock_chain = mock_llm_chain.return_value
        
        # Configure mocks
        self.mock_chain.run.side_effect = self.mock_chain_run
        
        # Sample schema result
        with open(os.path.join(os.path.dirname(__file__), 'sample_schema.json'), 'r') as f:
            self.sample_schema = json.load(f)
        
        self.mock_graphql_tool.get_schema.return_value = self.sample_schema
        
        # Initialize the agent
        self.agent = GraphQLAgent(
            graphql_url="https://example.com/graphql",
            openai_api_key="test_key",
            openai_api_version="test_version",
            openai_api_endpoint="test_endpoint"
        )
        
    def mock_chain_run(self, inputs):
        if 'schema' in inputs and 'question' in inputs:
            # This is the NL to GraphQL chain
            return "{ jobs { title location } }"
        elif 'question' in inputs and 'graphql_query' in inputs and 'result' in inputs:
            # This is the answer chain
            return "There are 3 jobs available: Software Engineer, Data Scientist, and Product Manager."
        else:
            return "Unknown chain input"
    
    def test_query(self):
        # Setup mock for execute_query
        self.mock_graphql_tool.execute_query.return_value = {
            "data": {
                "jobs": [
                    {"title": "Software Engineer", "location": "Seattle"},
                    {"title": "Data Scientist", "location": "New York"},
                    {"title": "Product Manager", "location": "San Francisco"}
                ]
            }
        }
        
        # Test the query method
        result = self.agent.query("What jobs are available?")
        
        # Verify the result
        self.assertEqual(result["graphql_query"], "{ jobs { title location } }")
        self.assertEqual(result["answer"], "There are 3 jobs available: Software Engineer, Data Scientist, and Product Manager.")
        self.assertIn("raw_result", result)
        
        # Verify that the methods were called
        self.mock_graphql_tool.get_schema.assert_called_once()
        self.mock_graphql_tool.execute_query.assert_called_once_with("{ jobs { title location } }")
        
    def test_error_handling(self):
        # Setup mock to raise an exception
        self.mock_graphql_tool.execute_query.side_effect = Exception("Test error")
        
        # Test the query method with an error
        result = self.agent.query("What jobs are available?")
        
        # Verify the result contains an error
        self.assertIn("error", result)
        self.assertIn("Test error", result["answer"])

if __name__ == '__main__':
    unittest.main()