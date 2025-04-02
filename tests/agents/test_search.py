"""
Tests for the search agent module.
"""

import json
import os
import pytest
from pathlib import Path

from src.agents.search import SearchAgent, SearchResult

class TestSearchAgent:
    """Tests for the SearchAgent class."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test search agent initialization."""
        agent = SearchAgent()
        
        assert agent.name == "SearchAgent"
        assert "Executes web searches" in agent.description
    
    @pytest.mark.asyncio
    async def test_process_query(self):
        """Test processing a search query."""
        agent = SearchAgent()
        query = "artificial intelligence"
        
        result = await agent.process(query)
        
        # Check that the result has the correct structure
        assert isinstance(result, SearchResult)
        assert result.query == query
        assert len(result.summary) > 0
        assert len(result.sources) > 0
    
    @pytest.mark.asyncio
    async def test_simulate_search(self):
        """Test the simulated search function."""
        agent = SearchAgent()
        query = "climate change"
        
        # Access the private method for testing
        results = await agent._simulate_search(query)
        
        # Check that the results have the expected structure
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert "title" in result
            assert "url" in result
            assert "snippet" in result
            
            # Check that the query is reflected in the results
            assert query.lower() in result["title"].lower() or query.lower() in result["snippet"].lower()
    
    @pytest.mark.asyncio
    async def test_summarize_results(self):
        """Test the summarization function."""
        agent = SearchAgent()
        query = "quantum computing"
        
        # Create some test results
        results = [
            {
                "title": "Test Title 1",
                "url": "https://example.com/1",
                "snippet": "This is the first test snippet about quantum computing."
            },
            {
                "title": "Test Title 2",
                "url": "https://example.com/2",
                "snippet": "This is the second test snippet with more information."
            }
        ]
        
        # Access the private method for testing
        summary = agent._summarize_results(query, results)
        
        # Check that the summary contains key information
        assert query in summary
        assert "Key points" in summary
        assert "first test snippet" in summary
        assert "second test snippet" in summary
    
    @pytest.mark.asyncio
    async def test_save_search_result(self, monkeypatch, tmp_path):
        """Test saving search results to storage."""
        # Set up a temporary storage path
        monkeypatch.setenv("RESEARCH_DATA_PATH", str(tmp_path))
        
        # Create the search_results directory
        search_results_dir = tmp_path / "search_results"
        search_results_dir.mkdir()
        
        agent = SearchAgent()
        
        # Create a test search result
        result = SearchResult(
            query="test query",
            summary="This is a test summary",
            sources=["https://example.com/1", "https://example.com/2"]
        )
        
        # Save the result
        await agent._save_search_result(result)
        
        # Check that a file was created
        files = list(search_results_dir.glob("*.json"))
        assert len(files) == 1
        
        # Check the file content
        with open(files[0], "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        
        assert saved_data["query"] == "test query"
        assert saved_data["summary"] == "This is a test summary"
        assert len(saved_data["sources"]) == 2

class TestSearchResult:
    """Tests for the SearchResult model."""
    
    def test_search_result_creation(self):
        """Test creating a SearchResult."""
        result = SearchResult(
            query="test query",
            summary="test summary",
            sources=["https://example.com/1", "https://example.com/2"]
        )
        
        assert result.query == "test query"
        assert result.summary == "test summary"
        assert len(result.sources) == 2
        assert result.sources[0] == "https://example.com/1"
    
    def test_search_result_validation(self):
        """Test SearchResult validation."""
        # Query and summary are required
        with pytest.raises(ValueError):
            SearchResult(summary="test")
        
        with pytest.raises(ValueError):
            SearchResult(query="test")
        
        # Sources is optional and defaults to an empty list
        result = SearchResult(query="test", summary="test")
        assert result.sources == []
