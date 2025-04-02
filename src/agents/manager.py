"""
Research Manager Module

This module implements the ResearchManager class, which orchestrates the research process.
"""

import asyncio
import os
from typing import Dict, List, Optional, Set, Tuple

from src.agents.planning import PlanningAgent, SearchQuery, ResearchPlan
from src.agents.search import SearchAgent, SearchResult
from src.agents.writer import WriterAgent, ResearchReport
from src.models.base import ModelProvider
from src.models.factory import create_model_provider
from src.tools.web_search import WebSearchTool
from src.utils.logger import get_logger
from src.utils.vector_db import RAGProcessor

logger = get_logger(__name__)

class ResearchManager:
    """
    Research Manager class that orchestrates the research process.

    This class coordinates the planning, search, and writing agents to conduct research
    on a given topic and produce a comprehensive report.
    """

    def __init__(self, model_provider: Optional[ModelProvider] = None, model_type: str = "openai", search_provider: str = "duckduckgo", use_rag: bool = False):
        """
        Initialize the ResearchManager.

        Args:
            model_provider (Optional[ModelProvider], optional): The model provider to use. Defaults to None (creates provider based on model_type).
            model_type (str, optional): The type of model to use if model_provider is None. Defaults to "openai".
            search_provider (str, optional): The search provider to use. Defaults to "duckduckgo".
            use_rag (bool, optional): Whether to use RAG for local models. Defaults to False.
        """
        logger.info("Initializing ResearchManager")

        # Initialize the model provider
        self.model_provider = model_provider or create_model_provider(model_type)
        logger.info(f"Using model provider: {self.model_provider.__class__.__name__} with model: {self.model_provider.model_name}")

        # Initialize the search tool
        self.search_tool = WebSearchTool(provider=search_provider)
        logger.info(f"Using search provider: {search_provider}")

        # Initialize the agents with the same model provider
        self.planning_agent = PlanningAgent(model_provider=self.model_provider)
        self.search_agent = SearchAgent(model_provider=self.model_provider, search_tool=self.search_tool)
        self.writer_agent = WriterAgent(model_provider=self.model_provider)

        # Initialize RAG processor for local models if needed
        self.use_rag = use_rag and model_type == "ollama"  # Only use RAG with local models
        self.rag_processor = RAGProcessor(collection_name="research_data") if self.use_rag else None

        if self.use_rag:
            logger.info("Using RAG for local models")

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

        # If using RAG with local models, store the search results in the vector database
        if self.use_rag and self.rag_processor:
            logger.info("Storing search results in vector database for RAG")

            # Process each search result and store in the vector database
            for result in search_results:
                if result.content:
                    # Store the content with metadata
                    metadata = {
                        "title": result.title,
                        "url": result.url,
                        "topic": topic,
                        "query": result.query
                    }
                    self.rag_processor.process_document(result.content, metadata)

            # Enhance the writer agent's prompt with relevant context from the vector database
            prompt_template = """You are researching the topic: {topic}.

            Here is relevant information from previous research:
            {context}

            Use this information along with the search results to generate a comprehensive report."""

            # Add the RAG context to the data
            enhanced_prompt = self.rag_processor.enhance_prompt_with_context(topic, prompt_template)
            data["rag_context"] = enhanced_prompt

        # Generate the report
        return await self.writer_agent.run(data)

    async def run_follow_up_research(self, report: ResearchReport) -> ResearchReport:
        """
        Run follow-up research based on the follow-up questions in a report.

        This method takes the follow-up questions from a previous research report,
        conducts additional research on those questions, and generates a new,
        more comprehensive report.

        Args:
            report (ResearchReport): The original research report

        Returns:
            ResearchReport: The new, more comprehensive research report
        """
        if not report.follow_up_questions or len(report.follow_up_questions) == 0:
            logger.warning("No follow-up questions found in the report")
            return report

        logger.info(f"Running follow-up research with {len(report.follow_up_questions)} questions")
        print(f"\nRunning follow-up research with {len(report.follow_up_questions)} questions")
        print("=" * 50)

        # Store all search results (original + follow-up)
        all_search_results = []

        # Step 1: Execute searches for each follow-up question
        print("\nExecuting follow-up searches...")
        for i, question in enumerate(report.follow_up_questions):
            print(f"  Researching follow-up question {i+1}/{len(report.follow_up_questions)}: {question}")

            # Create a search query for the question
            query = SearchQuery(query=question, reason=f"Follow-up question from previous research")

            # Execute the search
            result = await self.search_agent.run(question)
            all_search_results.append(result)

            print(f"  Completed search for question {i+1}")

        # Step 2: Generate a new, more comprehensive report
        print("\nSynthesizing all information...")

        # Combine original topic with follow-up context
        enhanced_topic = f"{report.topic} (with follow-up research)"

        # Generate the enhanced report
        enhanced_report = await self._generate_report(enhanced_topic, all_search_results)

        # Print a summary of the enhanced report
        print("\nEnhanced Research Summary:")
        print("-" * 50)
        print(enhanced_report.summary)
        print("-" * 50)

        print(f"\nFollow-up research complete! Enhanced report saved.")

        return enhanced_report
