"""
Planning Agent Module

This module implements the planning agent for the Research Agent system.
The planning agent is responsible for breaking down a research topic into specific search queries.
"""

import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.models.base import ModelProvider
from src.models.factory import create_model_provider
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

    def __init__(self,
                 name: str = "PlanningAgent",
                 description: str = "Creates a research plan with search queries",
                 model_provider: Optional[ModelProvider] = None):
        """
        Initialize the PlanningAgent.

        Args:
            name (str, optional): The name of the agent. Defaults to "PlanningAgent".
            description (str, optional): A description of the agent. Defaults to "Creates a research plan with search queries".
            model_provider (Optional[ModelProvider], optional): The model provider to use. Defaults to None (creates OpenAI provider).
        """
        super().__init__(name, description)

        # Initialize the model provider
        self.model_provider = model_provider or create_model_provider("openai")

    async def process(self, topic: str) -> ResearchPlan:
        """
        Process a research topic and create a research plan.

        Args:
            topic (str): The research topic

        Returns:
            ResearchPlan: The research plan with search queries
        """
        self.logger.info(f"Creating research plan for topic: {topic}")

        # Phase 3 implementation - use LLM to generate a research plan
        try:
            # Generate a research plan using the model
            queries = await self._generate_queries_with_llm(topic)

            # Create a description of the research approach
            description = f"Research plan for the topic: {topic}. " \
                         f"This plan includes {len(queries)} search queries to gather information about different aspects of the topic."

            # Create and return the research plan
            plan = ResearchPlan(
                topic=topic,
                description=description,
                queries=queries
            )

            self.logger.info(f"Created research plan with {len(queries)} search queries using LLM")
            return plan

        except Exception as e:
            # Fallback to template-based approach if LLM fails
            self.logger.warning(f"Error generating research plan with LLM: {e}. Falling back to template-based approach.")

            # Create a description of the research approach
            description = f"Research plan for the topic: {topic}. " \
                         f"This plan includes search queries to gather information about different aspects of the topic."

            # Create search queries based on the topic using templates
            queries = self._generate_search_queries(topic)

            # Create and return the research plan
            plan = ResearchPlan(
                topic=topic,
                description=description,
                queries=queries
            )

            self.logger.info(f"Created research plan with {len(queries)} search queries using templates")
            return plan

    async def _generate_queries_with_llm(self, topic: str) -> List[SearchQuery]:
        """
        Generate search queries for a research topic using a language model.

        Args:
            topic (str): The research topic

        Returns:
            List[SearchQuery]: List of search queries
        """
        # Create a prompt for the language model
        prompt = f"""
        You are a research planning assistant. Your task is to create a comprehensive research plan for the topic: "{topic}".

        Please generate 10 specific search queries that would help gather information about different aspects of this topic.
        For each query, provide a brief reason explaining why this query is important for the research.

        Format your response as a JSON array of objects, where each object has two fields:
        - "query": The search query text
        - "reason": The reason for this search query

        Example format:
        [
            {{
                "query": "artificial intelligence overview",
                "reason": "To get a general overview of artificial intelligence"
            }},
            {{
                "query": "history of artificial intelligence",
                "reason": "To understand the historical development of AI"
            }}
        ]

        Make sure your queries cover different aspects of the topic, including:
        - Basic definitions and concepts
        - Historical development
        - Current state and latest developments
        - Future trends and predictions
        - Applications and use cases
        - Advantages and disadvantages
        - Challenges and limitations
        - Key figures or organizations in the field
        - Statistical data and metrics
        - Ethical considerations or controversies

        Provide only the JSON array in your response, with no additional text.
        """

        # Generate text using the model
        response = await self.model_provider.generate_text(
            prompt=prompt,
            temperature=0.7
        )

        # Parse the response as JSON
        try:
            # Extract JSON from the response (it might be surrounded by markdown code blocks or other text)
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()

            # Parse the JSON
            query_data = json.loads(json_str)

            # Convert to SearchQuery objects
            queries = []
            for item in query_data:
                query = SearchQuery(
                    query=item["query"],
                    reason=item["reason"]
                )
                queries.append(query)

            return queries
        except Exception as e:
            self.logger.error(f"Error parsing LLM response as JSON: {e}")
            self.logger.debug(f"LLM response: {response}")
            raise

    def _generate_search_queries(self, topic: str) -> List[SearchQuery]:
        """
        Generate search queries for a research topic using templates.
        This is a fallback method if the LLM-based approach fails.

        Args:
            topic (str): The research topic

        Returns:
            List[SearchQuery]: List of search queries
        """
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
