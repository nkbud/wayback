"""
Tests for the MCP server functionality
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the server module
try:
    from wayback.mcp_server import server
except ImportError:
    # Skip tests if FastMCP is not available
    import pytest
    pytest.skip("FastMCP not available", allow_module_level=True)


class TestMCPServer(unittest.TestCase):
    
    def test_search_wayback_basic(self):
        """Test basic wayback search functionality"""
        with patch('wayback.mcp_server.server.WaybackClient') as mock_client:
            # Mock the wayback client
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            
            # Mock a CDX record
            mock_record = MagicMock()
            mock_record.timestamp = datetime(2020, 1, 1, 12, 0, 0)
            mock_record.url = "https://example.com"
            mock_record.urlkey = "com,example)/"
            mock_record.status_code = "200"
            mock_record.mime_type = "text/html"
            mock_record.length = "12345"
            mock_record.digest = "abc123"
            
            mock_instance.search.return_value = [mock_record]
            
            # Call the tool function
            result = server.search_wayback("https://example.com", limit=1)
            
            # Parse and verify the result
            data = json.loads(result)
            self.assertEqual(data["query_url"], "https://example.com")
            self.assertEqual(len(data["results"]), 1)
            self.assertEqual(data["results"][0]["url"], "https://example.com")
            self.assertEqual(data["authority_level"], "high")
    
    def test_search_wayback_with_dates(self):
        """Test wayback search with date parameters"""
        with patch('wayback.mcp_server.server.WaybackClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            mock_instance.search.return_value = []
            
            result = server.search_wayback(
                "https://example.com",
                from_date="2020-01-01",
                to_date="2020-12-31",
                limit=5
            )
            
            data = json.loads(result)
            self.assertEqual(data["query_url"], "https://example.com")
            self.assertEqual(data["results"], [])
    
    def test_search_wayback_error_handling(self):
        """Test error handling in wayback search"""
        with patch('wayback.mcp_server.server.WaybackClient') as mock_client:
            mock_client.side_effect = Exception("Test error")
            
            result = server.search_wayback("https://example.com")
            
            data = json.loads(result)
            self.assertIn("error", data)
            self.assertEqual(data["query_url"], "https://example.com")
            self.assertEqual(data["results"], [])
    
    def test_get_api_endpoints_resource(self):
        """Test the API endpoints resource"""
        result = server.get_api_endpoints()
        
        data = json.loads(result)
        self.assertIn("wayback_tools", data)
        self.assertIn("high_authority_sources", data)
        self.assertIn("search_wayback", data["wayback_tools"])
        self.assertIn("search_library_of_congress", data["high_authority_sources"])
    
    def test_get_supported_sources_resource(self):
        """Test the supported sources resource"""
        result = server.get_supported_sources()
        
        data = json.loads(result)
        self.assertIn("internet_archive", data)
        self.assertIn("library_of_congress", data)
        self.assertEqual(data["internet_archive"]["authority_level"], "high")
        self.assertEqual(data["library_of_congress"]["authority_level"], "highest")
    
    @patch('requests.get')
    def test_search_library_of_congress(self, mock_get):
        """Test Library of Congress search functionality"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Test Document",
                    "url": "https://www.loc.gov/item/test",
                    "description": "A test document",
                    "date": "2020",
                    "format": ["text"],
                    "subject": ["testing"]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = server.search_library_of_congress("test query", limit=1)
        
        data = json.loads(result)
        self.assertEqual(data["query"], "test query")
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["title"], "Test Document")
        self.assertEqual(data["authority_level"], "highest")


if __name__ == "__main__":
    unittest.main()