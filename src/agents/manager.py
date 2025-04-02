"""
Research Manager Module

This module implements the ResearchManager class, which orchestrates the research process.
"""

import asyncio
import os
from typing import List, Optional

from src.agents.planning import PlanningAgent, SearchQuery, ResearchPlan
from src.agents.search import SearchAgent, SearchResult
from src.agents.writer import WriterAgent, ResearchReport
from src.models.base import ModelProvider
from src.models.factory import create_model_provider
from src.tools.web_search import WebSearchTool
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ResearchManager:
    """
    Research Manager class that orchestrates the research process.

    This class coordinates the planning, search, and writing agents to conduct research
    on a given topic and produce a comprehensive report.
    """

    def __init__(self, model_provider: Optional[ModelProvider] = None, model_type: str = "openai"):
        """
        Initialize the ResearchManager.

        Args:
            model_provider (Optional[ModelProvider], optional): The model provider to use. Defaults to None (creates provider based on model_type).
            model_type (str, optional): The type of model to use if model_provider is None. Defaults to "openai".
        """
        logger.info("Initializing ResearchManager")

        # Initialize the model provider
        self.model_provider = model_provider or create_model_provider(model_type)
        logger.info(f"Using model provider: {self.model_provider.__class__.__name__} with model: {self.model_provider.model_name}")

        # Initialize the search tool
        self.search_tool = WebSearchTool()

        # Initialize the agents with the same model provider
        self.planning_agent = PlanningAgent(model_provider=self.model_provider)
        self.search_agent = SearchAgent(model_provider=self.model_provider, search_tool=self.search_tool)
        self.writer_agent = WriterAgent(model_provider=self.model_provider)

    async def run(self, query: str) -> ResearchReport:
        """
        Run the research process for the given query.

        Args:
            query (str): The research topic or question

        Returns:
            ResearchReport: The generated research report
        """
        logger.info(f"Starting research on: {query}")

        print(f"\nResearching: {query}")
        print("=" * 50)

        # Step 1: Plan the research
        print("\nPlanning research approach...")
        research_plan = await self._plan_research(query)
        print(f"Created research plan with {len(research_plan.queries)} search queries")

        # Step 2: Execute the search queries
        print("\nExecuting web searches...")
        search_results = await self._execute_searches(research_plan.queries)
        print(f"Completed {len(search_results)} searches")

        # Step 3: Generate the research report
        print("\nSynthesizing information...")
        report = await self._generate_report(query, search_results)

        # Print a summary of the report
        print("\nResearch Summary:")
        print("-" * 50)
        print(report.summary)
        print("-" * 50)

        print(f"\nResearch complete! Report saved.")

        return report

    async def _plan_research(self, topic: str) -> ResearchPlan:
        """
        Plan the research by generating search queries.

        Args:
            topic (str): The research topic

        Returns:
            ResearchPlan: The research plan with search queries
        """
        logger.info(f"Planning research for topic: {topic}")
        return await self.planning_agent.run(topic)

    async def _execute_searches(self, queries: List[SearchQuery]) -> List[SearchResult]:
        """
        Execute the search queries in parallel.

        Args:
            queries (List[SearchQuery]): The search queries to execute

        Returns:
            List[SearchResult]: The search results
        """
        logger.info(f"Executing {len(queries)} search queries")

        # Create a list to store the results
        results = []

        # Process queries in batches to avoid overwhelming the system
        batch_size = 5
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i+batch_size]

            # Create tasks for each query in the batch
            tasks = []
            for query in batch:
                print(f"  Searching for: {query.query}")
                tasks.append(self.search_agent.run(query.query))

            # Execute the batch of searches in parallel
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            # Print progress
            print(f"  Completed {len(results)}/{len(queries)} searches")

        return results

    async def _generate_report(self, topic: str, search_results: List[SearchResult]) -> ResearchReport:
        """
        Generate a research report from the search results.

        Args:
            topic (str): The research topic
            search_results (List[SearchResult]): The search results

        Returns:
            ResearchReport: The generated research report
        """
        logger.info(f"Generating research report for topic: {topic}")

        # Prepare the input data for the writer agent
        data = {
            "topic": topic,
            "results": search_results
        }

        # Generate the report
        return await self.writer_agent.run(data)


