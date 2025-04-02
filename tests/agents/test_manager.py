"""
Tests for the research manager module.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.manager import ResearchManager
from src.agents.planning import ResearchPlan, SearchQuery
from src.agents.search import SearchResult
from src.agents.writer import ResearchReport

class TestResearchManager:
    """Tests for the ResearchManager class."""
    
    def test_initialization(self):
        """Test manager initialization."""
        manager = ResearchManager()
        
        # Check that the agents are initialized
        assert manager.planning_agent is not None
        assert manager.search_agent is not None
        assert manager.writer_agent is not None
    
    @pytest.mark.asyncio
    async def test_plan_research(self):
        """Test planning research."""
        manager = ResearchManager()
        
        # Mock the planning agent
        manager.planning_agent.run = AsyncMock()
        
        # Create a mock research plan
        mock_plan = ResearchPlan(
            topic="test topic",
            description="test description",
            queries=[
                SearchQuery(query="test query 1", reason="test reason 1"),
                SearchQuery(query="test query 2", reason="test reason 2")
            ]
        )
        manager.planning_agent.run.return_value = mock_plan
        
        # Call the method
        result = await manager._plan_research("test topic")
        
        # Check that the planning agent was called
        manager.planning_agent.run.assert_called_once_with("test topic")
        
        # Check the result
        assert result is mock_plan
    
    @pytest.mark.asyncio
    async def test_execute_searches(self):
        """Test executing searches."""
        manager = ResearchManager()
        
        # Mock the search agent
        manager.search_agent.run = AsyncMock()
        
        # Create mock search queries
        queries = [
            SearchQuery(query="test query 1", reason="test reason 1"),
            SearchQuery(query="test query 2", reason="test reason 2")
        ]
        
        # Create mock search results
        mock_results = [
            SearchResult(query="test query 1", summary="test summary 1", sources=["https://example.com/1"]),
            SearchResult(query="test query 2", summary="test summary 2", sources=["https://example.com/2"])
        ]
        manager.search_agent.run.side_effect = mock_results
        
        # Call the method
        results = await manager._execute_searches(queries)
        
        # Check that the search agent was called for each query
        assert manager.search_agent.run.call_count == len(queries)
        manager.search_agent.run.assert_any_call("test query 1")
        manager.search_agent.run.assert_any_call("test query 2")
        
        # Check the results
        assert len(results) == len(queries)
        assert results[0].query == "test query 1"
        assert results[1].query == "test query 2"
    
    @pytest.mark.asyncio
    async def test_generate_report(self):
        """Test generating a report."""
        manager = ResearchManager()
        
        # Mock the writer agent
        manager.writer_agent.run = AsyncMock()
        
        # Create mock search results
        search_results = [
            SearchResult(query="test query 1", summary="test summary 1", sources=["https://example.com/1"]),
            SearchResult(query="test query 2", summary="test summary 2", sources=["https://example.com/2"])
        ]
        
        # Create a mock research report
        mock_report = ResearchReport(
            topic="test topic",
            summary="test summary",
            content="test content",
            follow_up_questions=["test question 1", "test question 2"]
        )
        manager.writer_agent.run.return_value = mock_report
        
        # Call the method
        result = await manager._generate_report("test topic", search_results)
        
        # Check that the writer agent was called with the correct data
        manager.writer_agent.run.assert_called_once()
        call_args = manager.writer_agent.run.call_args[0][0]
        assert call_args["topic"] == "test topic"
        assert call_args["results"] == search_results
        
        # Check the result
        assert result is mock_report
    
    @pytest.mark.asyncio
    async def test_run_end_to_end(self):
        """Test the full research process."""
        manager = ResearchManager()
        
        # Mock all the agent methods
        manager._plan_research = AsyncMock()
        manager._execute_searches = AsyncMock()
        manager._generate_report = AsyncMock()
        
        # Create mock objects for each step
        mock_plan = MagicMock()
        mock_plan.queries = [MagicMock(), MagicMock()]
        manager._plan_research.return_value = mock_plan
        
        mock_search_results = [MagicMock(), MagicMock()]
        manager._execute_searches.return_value = mock_search_results
        
        mock_report = MagicMock()
        mock_report.summary = "Test summary"
        manager._generate_report.return_value = mock_report
        
        # Call the run method
        result = await manager.run("test topic")
        
        # Check that each step was called with the correct arguments
        manager._plan_research.assert_called_once_with("test topic")
        manager._execute_searches.assert_called_once_with(mock_plan.queries)
        manager._generate_report.assert_called_once_with("test topic", mock_search_results)
        
        # Check the result
        assert result is mock_report
