"""
Tests for the writer agent module.
"""

import pytest
from pathlib import Path

from src.agents.writer import WriterAgent, ResearchReport
from src.agents.search import SearchResult

class TestWriterAgent:
    """Tests for the WriterAgent class."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test writer agent initialization."""
        agent = WriterAgent()
        
        assert agent.name == "WriterAgent"
        assert "Synthesizes search results" in agent.description
    
    @pytest.mark.asyncio
    async def test_process_results(self):
        """Test processing search results."""
        agent = WriterAgent()
        
        # Create test search results
        results = [
            SearchResult(
                query="artificial intelligence overview",
                summary="AI is a field of computer science focused on creating systems that can perform tasks requiring human intelligence.",
                sources=["https://example.com/ai-overview"]
            ),
            SearchResult(
                query="artificial intelligence applications",
                summary="AI applications include natural language processing, computer vision, and autonomous vehicles.",
                sources=["https://example.com/ai-applications"]
            )
        ]
        
        # Create input data
        data = {
            "topic": "artificial intelligence",
            "results": results
        }
        
        # Process the data
        report = await agent.process(data)
        
        # Check that the report has the correct structure
        assert isinstance(report, ResearchReport)
        assert report.topic == "artificial intelligence"
        assert len(report.summary) > 0
        assert len(report.content) > 0
        assert len(report.follow_up_questions) > 0
    
    @pytest.mark.asyncio
    async def test_missing_topic(self):
        """Test processing with missing topic."""
        agent = WriterAgent()
        
        # Create input data without topic
        data = {
            "results": [
                SearchResult(
                    query="test query",
                    summary="test summary",
                    sources=["https://example.com"]
                )
            ]
        }
        
        # Check that it raises a ValueError
        with pytest.raises(ValueError, match="Topic is required"):
            await agent.process(data)
    
    @pytest.mark.asyncio
    async def test_missing_results(self):
        """Test processing with missing results."""
        agent = WriterAgent()
        
        # Create input data without results
        data = {
            "topic": "test topic"
        }
        
        # Check that it raises a ValueError
        with pytest.raises(ValueError, match="Search results are required"):
            await agent.process(data)
    
    @pytest.mark.asyncio
    async def test_create_summary(self):
        """Test creating a summary."""
        agent = WriterAgent()
        topic = "climate change"
        
        # Create test search results
        results = [
            SearchResult(
                query="climate change overview",
                summary="Climate change refers to long-term shifts in temperatures and weather patterns.",
                sources=["https://example.com/climate-overview"]
            ),
            SearchResult(
                query="climate change impacts",
                summary="Climate change impacts include rising sea levels, extreme weather events, and ecosystem disruption.",
                sources=["https://example.com/climate-impacts"]
            )
        ]
        
        # Access the private method for testing
        summary = agent._create_summary(topic, results)
        
        # Check that the summary contains key information
        assert topic in summary
        assert str(len(results)) in summary
    
    @pytest.mark.asyncio
    async def test_create_report_content(self):
        """Test creating report content."""
        agent = WriterAgent()
        topic = "renewable energy"
        
        # Create test search results
        results = [
            SearchResult(
                query="renewable energy overview",
                summary="Renewable energy comes from sources that are naturally replenished.",
                sources=["https://example.com/renewable-overview"]
            ),
            SearchResult(
                query="renewable energy examples",
                summary="Examples of renewable energy include solar, wind, and hydroelectric power.",
                sources=["https://example.com/renewable-examples"]
            )
        ]
        
        # Access the private method for testing
        content = agent._create_report_content(topic, results)
        
        # Check that the content has the expected structure
        assert content.startswith(f"# Research Report: {topic.title()}")
        assert "## Summary" in content
        assert "## Introduction" in content
        assert "## Findings" in content
        assert "## Conclusion" in content
        assert "## Follow-up Questions" in content
        
        # Check that the content includes information from the search results
        assert "Renewable energy comes from sources" in content
        assert "Examples of renewable energy include" in content
    
    @pytest.mark.asyncio
    async def test_generate_follow_up_questions(self):
        """Test generating follow-up questions."""
        agent = WriterAgent()
        topic = "quantum computing"
        
        # Create test search results
        results = [
            SearchResult(
                query="quantum computing overview",
                summary="Quantum computing uses quantum mechanics to perform computations.",
                sources=["https://example.com/quantum-overview"]
            )
        ]
        
        # Access the private method for testing
        questions = agent._generate_follow_up_questions(topic, results)
        
        # Check that questions were generated
        assert isinstance(questions, list)
        assert len(questions) > 0
        
        # Check that the questions include the topic
        for question in questions:
            assert topic in question

class TestResearchReport:
    """Tests for the ResearchReport model."""
    
    def test_research_report_creation(self):
        """Test creating a ResearchReport."""
        report = ResearchReport(
            topic="test topic",
            summary="test summary",
            content="# Test Content\n\nThis is test content.",
            follow_up_questions=["Question 1?", "Question 2?"]
        )
        
        assert report.topic == "test topic"
        assert report.summary == "test summary"
        assert report.content == "# Test Content\n\nThis is test content."
        assert len(report.follow_up_questions) == 2
        assert report.follow_up_questions[0] == "Question 1?"
    
    def test_research_report_validation(self):
        """Test ResearchReport validation."""
        # Topic, summary, and content are required
        with pytest.raises(ValueError):
            ResearchReport(summary="test", content="test")
        
        with pytest.raises(ValueError):
            ResearchReport(topic="test", content="test")
        
        with pytest.raises(ValueError):
            ResearchReport(topic="test", summary="test")
        
        # Follow-up questions is optional and defaults to an empty list
        report = ResearchReport(topic="test", summary="test", content="test")
        assert report.follow_up_questions == []
