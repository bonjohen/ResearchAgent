"""
Tests for the planning agent module.
"""

import pytest

from src.agents.planning import PlanningAgent, SearchQuery, ResearchPlan

class TestPlanningAgent:
    """Tests for the PlanningAgent class."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test planning agent initialization."""
        agent = PlanningAgent()
        
        assert agent.name == "PlanningAgent"
        assert "Creates a research plan" in agent.description
    
    @pytest.mark.asyncio
    async def test_process_topic(self):
        """Test processing a research topic."""
        agent = PlanningAgent()
        topic = "artificial intelligence"
        
        plan = await agent.process(topic)
        
        # Check that the plan has the correct structure
        assert isinstance(plan, ResearchPlan)
        assert plan.topic == topic
        assert topic in plan.description
        assert len(plan.queries) > 0
    
    @pytest.mark.asyncio
    async def test_generated_queries(self):
        """Test the generated search queries."""
        agent = PlanningAgent()
        topic = "climate change"
        
        plan = await agent.process(topic)
        
        # Check that each query is properly formed
        for query in plan.queries:
            assert isinstance(query, SearchQuery)
            assert topic in query.query
            assert query.reason
    
    @pytest.mark.asyncio
    async def test_query_count(self):
        """Test the number of generated queries."""
        agent = PlanningAgent()
        topic = "quantum computing"
        
        plan = await agent.process(topic)
        
        # The current implementation should generate 10 queries
        assert len(plan.queries) == 10
    
    @pytest.mark.asyncio
    async def test_query_uniqueness(self):
        """Test that generated queries are unique."""
        agent = PlanningAgent()
        topic = "renewable energy"
        
        plan = await agent.process(topic)
        
        # Check that all queries are unique
        query_texts = [query.query for query in plan.queries]
        assert len(query_texts) == len(set(query_texts))
    
    @pytest.mark.asyncio
    async def test_different_topics(self):
        """Test that different topics produce different queries."""
        agent = PlanningAgent()
        topic1 = "machine learning"
        topic2 = "blockchain"
        
        plan1 = await agent.process(topic1)
        plan2 = await agent.process(topic2)
        
        # Check that the queries are different for different topics
        queries1 = [query.query for query in plan1.queries]
        queries2 = [query.query for query in plan2.queries]
        
        # No query from topic1 should be in topic2's queries
        assert not any(query in queries2 for query in queries1)

class TestSearchQuery:
    """Tests for the SearchQuery model."""
    
    def test_search_query_creation(self):
        """Test creating a SearchQuery."""
        query = SearchQuery(
            query="artificial intelligence applications",
            reason="To discover practical applications"
        )
        
        assert query.query == "artificial intelligence applications"
        assert query.reason == "To discover practical applications"
    
    def test_search_query_validation(self):
        """Test SearchQuery validation."""
        # Both query and reason are required
        with pytest.raises(ValueError):
            SearchQuery(query="test")
        
        with pytest.raises(ValueError):
            SearchQuery(reason="test")

class TestResearchPlan:
    """Tests for the ResearchPlan model."""
    
    def test_research_plan_creation(self):
        """Test creating a ResearchPlan."""
        queries = [
            SearchQuery(query="test query 1", reason="reason 1"),
            SearchQuery(query="test query 2", reason="reason 2")
        ]
        
        plan = ResearchPlan(
            topic="test topic",
            description="test description",
            queries=queries
        )
        
        assert plan.topic == "test topic"
        assert plan.description == "test description"
        assert len(plan.queries) == 2
        assert plan.queries[0].query == "test query 1"
    
    def test_research_plan_validation(self):
        """Test ResearchPlan validation."""
        queries = [
            SearchQuery(query="test query", reason="test reason")
        ]
        
        # All fields are required
        with pytest.raises(ValueError):
            ResearchPlan(description="test", queries=queries)
        
        with pytest.raises(ValueError):
            ResearchPlan(topic="test", queries=queries)
        
        with pytest.raises(ValueError):
            ResearchPlan(topic="test", description="test")
