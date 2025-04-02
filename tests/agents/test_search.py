"""
Tests for the search agent module.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.search import SearchAgent, SearchResult
from src.tools.base import Tool

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
        # Create a mock search tool
        mock_search_tool = MagicMock(spec=Tool)
        mock_search_tool.execute = AsyncMock(return_value={
            "query": "artificial intelligence",
            "num_results": 2,
            "results": [
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
        })

        # Create a mock content tool
        mock_content_tool = MagicMock(spec=Tool)
        mock_content_tool.execute = AsyncMock(return_value={
            "url": "https://example.com/1",
            "success": True,
            "title": "Test Page",
            "content": "This is the detailed content of the page.",
            "summary": "This is a summary of the page content."
        })

        # Create the agent with the mock tools
        agent = SearchAgent(search_tool=mock_search_tool)
        agent.content_tool = mock_content_tool

        # Mock the summarize method to avoid calling the model
        with patch.object(agent, '_summarize_results_with_llm', new_callable=AsyncMock) as mock_summarize:
            mock_summarize.return_value = "This is a test summary of the search results."

            query = "artificial intelligence"
            result = await agent.process(query)

            # Check that the result has the correct structure
            assert isinstance(result, SearchResult)
            assert result.query == query
            assert len(result.summary) > 0
            assert len(result.sources) > 0
            assert result.sources[0] == "https://example.com/1"
            assert result.sources[1] == "https://example.com/2"

    @pytest.mark.asyncio
    async def test_simulate_search(self):
        """Test the simulated search function."""
        # Create a mock search tool
        mock_search_tool = MagicMock(spec=Tool)

        agent = SearchAgent(search_tool=mock_search_tool)
        query = "climate change"

        # Create a mock for the _simulate_search method
        with patch.object(agent, '_simulate_search', new_callable=AsyncMock) as mock_simulate:
            # Set up the mock to return some results
            mock_results = [
                {
                    "title": "Climate Change - Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Climate_Change",
                    "snippet": "Climate change refers to long-term shifts in temperatures and weather patterns."
                },
                {
                    "title": "Understanding Climate Change | Educational Resource",
                    "url": "https://education.example.com/climate-change",
                    "snippet": "Learn about climate change with our comprehensive guide."
                }
            ]
            mock_simulate.return_value = mock_results

            # Call the method
            results = await agent._simulate_search(query)

            # Check that the mock was called
            mock_simulate.assert_called_once_with(query)

            # Check that the results have the expected structure
            assert isinstance(results, list)
            assert len(results) == 2

            for result in results:
                assert "title" in result
                assert "url" in result
                assert "snippet" in result

    @pytest.mark.asyncio
    async def test_summarize_results(self):
        """Test the summarization function."""
        # Create a mock search tool
        mock_search_tool = MagicMock(spec=Tool)

        agent = SearchAgent(search_tool=mock_search_tool)
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

        # Call the method
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

        # Create a mock search tool
        mock_search_tool = MagicMock(spec=Tool)

        agent = SearchAgent(search_tool=mock_search_tool)

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
