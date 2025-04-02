"""
Planning Agent Module

This module implements the planning agent for the Research Agent system.
The planning agent is responsible for breaking down a research topic into specific search queries.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SearchQuery(BaseModel):
    """
    Model for a search query.
    """
    query: str = Field(..., description="The search query text")
    reason: str = Field(..., description="The reason for this search query")

class ResearchPlan(BaseModel):
    """
    Model for a research plan.
    """
    topic: str = Field(..., description="The original research topic")
    description: str = Field(..., description="Description of the research approach")
    queries: List[SearchQuery] = Field(..., description="List of search queries to execute")

class PlanningAgent(BaseAgent):
    """
    Planning agent that breaks down a research topic into specific search queries.
    """
    
    def __init__(self, name: str = "PlanningAgent", description: str = "Creates a research plan with search queries"):
        """
        Initialize the PlanningAgent.
        
        Args:
            name (str, optional): The name of the agent. Defaults to "PlanningAgent".
            description (str, optional): A description of the agent. Defaults to "Creates a research plan with search queries".
        """
        super().__init__(name, description)
    
    async def process(self, topic: str) -> ResearchPlan:
        """
        Process a research topic and create a research plan.
        
        Args:
            topic (str): The research topic
        
        Returns:
            ResearchPlan: The research plan with search queries
        """
        self.logger.info(f"Creating research plan for topic: {topic}")
        
        # Phase 2 implementation - create a simple plan with predefined queries
        # In Phase 3, this will be replaced with actual LLM-based planning
        
        # Create a description of the research approach
        description = f"Research plan for the topic: {topic}. " \
                     f"This plan includes search queries to gather information about different aspects of the topic."
        
        # Create search queries based on the topic
        queries = self._generate_search_queries(topic)
        
        # Create and return the research plan
        plan = ResearchPlan(
            topic=topic,
            description=description,
            queries=queries
        )
        
        self.logger.info(f"Created research plan with {len(queries)} search queries")
        return plan
    
    def _generate_search_queries(self, topic: str) -> List[SearchQuery]:
        """
        Generate search queries for a research topic.
        
        Args:
            topic (str): The research topic
        
        Returns:
            List[SearchQuery]: List of search queries
        """
        # Simple query generation for Phase 2
        # This will be replaced with LLM-based query generation in Phase 3
        
        # Basic query templates
        templates = [
            {"suffix": "overview", "reason": "To get a general overview of the topic"},
            {"suffix": "definition", "reason": "To understand the basic definition and concepts"},
            {"suffix": "history", "reason": "To learn about the historical development"},
            {"suffix": "examples", "reason": "To find concrete examples and case studies"},
            {"suffix": "advantages and disadvantages", "reason": "To understand the pros and cons"},
            {"suffix": "latest developments", "reason": "To learn about recent advancements"},
            {"suffix": "future trends", "reason": "To understand future directions and predictions"},
            {"suffix": "applications", "reason": "To discover practical applications"},
            {"suffix": "challenges", "reason": "To identify current challenges and limitations"},
            {"suffix": "statistics", "reason": "To find relevant data and statistics"}
        ]
        
        # Generate queries using the templates
        queries = []
        for template in templates:
            query_text = f"{topic} {template['suffix']}"
            query = SearchQuery(
                query=query_text,
                reason=template["reason"]
            )
            queries.append(query)
        
        return queries
