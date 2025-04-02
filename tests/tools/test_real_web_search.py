"""
Tests for the real web search tool.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.tools.real_web_search import RealWebSearchTool

class TestRealWebSearchTool:
    """Tests for the RealWebSearchTool class."""
    
    def test_initialization(self):
        """Test tool initialization."""
        tool = RealWebSearchTool()
        
        assert tool.name == "web_search"
        assert "Search the web" in tool.description
    
    def test_initialization_with_custom_provider(self):
        """Test tool initialization with a custom search provider."""
        tool = RealWebSearchTool(search_provider="google")
        
        assert tool.search_provider == "google"
    
    def test_initialization_with_environment_provider(self):
        """Test tool initialization with a search provider from the environment."""
        # Set the search provider in the environment
        os.environ["SEARCH_ENGINE"] = "google"
        
        tool = RealWebSearchTool()
        
        # Check that it used the environment variable
        assert tool.search_provider == "google"
        
        # Clean up
        del os.environ["SEARCH_ENGINE"]
    
    def test_get_schema(self):
        """Test getting the tool schema."""
        tool = RealWebSearchTool()
        schema = tool.get_schema()
        
        assert schema["name"] == "web_search"
        assert "description" in schema
        assert "parameters" in schema
        assert "properties" in schema["parameters"]
        assert "query" in schema["parameters"]["properties"]
        assert "num_results" in schema["parameters"]["properties"]
        assert schema["parameters"]["required"] == ["query"]
    
    @pytest.mark.asyncio
    async def test_execute_with_duckduckgo(self):
        """Test executing the tool with DuckDuckGo."""
        tool = RealWebSearchTool(search_provider="duckduckgo")
        
        # Mock the DuckDuckGo search method
        with patch.object(tool, "_search_duckduckgo", new_callable=AsyncMock) as mock_search:
            # Set up the mock to return some results
            mock_results = [
                {
                    "title": "Test Result 1",
                    "url": "https://example.com/1",
                    "snippet": "This is a test result."
                },
                {
                    "title": "Test Result 2",
                    "url": "https://example.com/2",
                    "snippet": "This is another test result."
                }
            ]
            mock_search.return_value = mock_results
            
            # Execute the tool
            result = await tool.execute(query="test query")
            
            # Check that the search method was called
            mock_search.assert_called_once_with("test query", 5)
            
            # Check the result
            assert result["query"] == "test query"
            assert result["num_results"] == 2
            assert result["results"] == mock_results
    
    @pytest.mark.asyncio
    async def test_execute_with_google(self):
        """Test executing the tool with Google."""
        # Set up the environment for Google search
        os.environ["SEARCH_API_KEY"] = "test_api_key"
        os.environ["GOOGLE_CSE_ID"] = "test_cse_id"
        
        tool = RealWebSearchTool(search_provider="google")
        
        # Mock the Google search method
        with patch.object(tool, "_search_google", new_callable=AsyncMock) as mock_search:
            # Set up the mock to return some results
            mock_results = [
                {
                    "title": "Test Result 1",
                    "url": "https://example.com/1",
                    "snippet": "This is a test result."
                },
                {
                    "title": "Test Result 2",
                    "url": "https://example.com/2",
                    "snippet": "This is another test result."
                }
            ]
            mock_search.return_value = mock_results
            
            # Execute the tool
            result = await tool.execute(query="test query")
            
            # Check that the search method was called
            mock_search.assert_called_once_with("test query", 5)
            
            # Check the result
            assert result["query"] == "test query"
            assert result["num_results"] == 2
            assert result["results"] == mock_results
        
        # Clean up
        del os.environ["SEARCH_API_KEY"]
        del os.environ["GOOGLE_CSE_ID"]
    
    @pytest.mark.asyncio
    async def test_execute_with_error(self):
        """Test executing the tool with an error."""
        tool = RealWebSearchTool()
        
        # Mock the search method to raise an exception
        with patch.object(tool, "_search_duckduckgo", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = Exception("Test error")
            
            # Execute the tool
            result = await tool.execute(query="test query")
            
            # Check that the search method was called
            mock_search.assert_called_once_with("test query", 5)
            
            # Check the result
            assert result["query"] == "test query"
            assert result["num_results"] == 0
            assert result["results"] == []
            assert "error" in result
            assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_search_google(self):
        """Test the Google search method."""
        # Set up the environment for Google search
        os.environ["SEARCH_API_KEY"] = "test_api_key"
        os.environ["GOOGLE_CSE_ID"] = "test_cse_id"
        
        tool = RealWebSearchTool(search_provider="google")
        
        # Mock the aiohttp ClientSession
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "items": [
                {
                    "title": "Test Result 1",
                    "link": "https://example.com/1",
                    "snippet": "This is a test result."
                },
                {
                    "title": "Test Result 2",
                    "link": "https://example.com/2",
                    "snippet": "This is another test result."
                }
            ]
        })
        
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = AsyncMock(return_value=mock_response)
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            # Execute the search
            results = await tool._search_google("test query", 2)
            
            # Check the results
            assert len(results) == 2
            assert results[0]["title"] == "Test Result 1"
            assert results[0]["url"] == "https://example.com/1"
            assert results[0]["snippet"] == "This is a test result."
        
        # Clean up
        del os.environ["SEARCH_API_KEY"]
        del os.environ["GOOGLE_CSE_ID"]
