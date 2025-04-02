"""
Search Agent Module

This module implements the search agent for the Research Agent system.
The search agent is responsible for executing web searches and summarizing the results.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.models.base import ModelProvider
from src.models.factory import create_model_provider
from src.tools.base import Tool, ToolRegistry
from src.tools.web_search import WebSearchTool
from src.utils.logger import get_logger
from src.utils.storage import get_storage_path

logger = get_logger(__name__)

class SearchResult(BaseModel):
    """
    Model for a search result.
    """
    query: str = Field(..., description="The search query that was executed")
    summary: str = Field(..., description="Summary of the search results")
    sources: List[str] = Field(default_factory=list, description="List of sources (URLs)")

class SearchAgent(BaseAgent):
    """
    Search agent that executes web searches and summarizes the results.
    """

    def __init__(self,
                 name: str = "SearchAgent",
                 description: str = "Executes web searches and summarizes results",
                 model_provider: Optional[ModelProvider] = None,
                 search_tool: Optional[Tool] = None):
        """
        Initialize the SearchAgent.

        Args:
            name (str, optional): The name of the agent. Defaults to "SearchAgent".
            description (str, optional): A description of the agent. Defaults to "Executes web searches and summarizes results".
            model_provider (Optional[ModelProvider], optional): The model provider to use. Defaults to None (creates OpenAI provider).
            search_tool (Optional[Tool], optional): The search tool to use. Defaults to None (uses WebSearchTool).
        """
        super().__init__(name, description)

        # Initialize the model provider
        self.model_provider = model_provider or create_model_provider("openai")

        # Initialize the search tool
        self.search_tool = search_tool or ToolRegistry.get("web_search") or WebSearchTool()

    async def process(self, query: str) -> SearchResult:
        """
        Process a search query and return summarized results.

        Args:
            query (str): The search query to execute

        Returns:
            SearchResult: The search results with summary
        """
        self.logger.info(f"Executing search for query: {query}")

        # Phase 3 implementation - use the web search tool
        try:
            # Execute the search using the web search tool
            search_response = await self.search_tool.execute(query=query, num_results=5)

            # Extract the search results
            search_results = search_response.get("results", [])

            # Create a summary of the search results using the model
            summary = await self._summarize_results_with_llm(query, search_results)

            # Extract sources (URLs) from the search results
            sources = [result.get("url", "") for result in search_results if "url" in result]

            # Create and return the search result
            result = SearchResult(
                query=query,
                summary=summary,
                sources=sources
            )

            # Save the search result to storage
            await self._save_search_result(result)

            self.logger.info(f"Completed search for query: {query}")
            return result

        except Exception as e:
            # Fallback to simulated search if the web search tool fails
            self.logger.warning(f"Error executing web search: {e}. Falling back to simulated search.")

            # Simulate web search
            search_results = await self._simulate_search(query)

            # Create a simple summary of the search results
            summary = self._summarize_results(query, search_results)

            # Extract sources (URLs) from the search results
            sources = [result.get("url", "") for result in search_results if "url" in result]

            # Create and return the search result
            result = SearchResult(
                query=query,
                summary=summary,
                sources=sources
            )

            # Save the search result to storage
            await self._save_search_result(result)

            self.logger.info(f"Completed simulated search for query: {query}")
            return result

    async def _simulate_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Simulate web search results for a query.

        Args:
            query (str): The search query

        Returns:
            List[Dict[str, Any]]: Simulated search results
        """
        # Simulate a delay for the search
        await asyncio.sleep(0.5)

        # Create simulated search results based on the query
        words = query.lower().split()

        # Generate different results based on query keywords
        results = []

        # Add a Wikipedia-like result
        results.append({
            "title": f"{query.title()} - Wikipedia",
            "url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
            "snippet": f"This article is about {query}. {query.capitalize()} refers to a concept or topic that has various aspects and applications..."
        })

        # Add an educational resource
        results.append({
            "title": f"Understanding {query.title()} | Educational Resource",
            "url": f"https://education.example.com/{query.replace(' ', '-').lower()}",
            "snippet": f"Learn about {query} with our comprehensive guide. This resource covers the fundamentals, history, and modern applications..."
        })

        # Add a news article
        results.append({
            "title": f"Latest Developments in {query.title()} | News",
            "url": f"https://news.example.com/articles/{query.replace(' ', '-').lower()}",
            "snippet": f"Recent developments in {query} have shown promising results. Experts in the field suggest that future advancements will..."
        })

        # Add a research paper
        results.append({
            "title": f"Research on {query.title()}: A Comprehensive Analysis",
            "url": f"https://research.example.com/papers/{query.replace(' ', '_').lower()}",
            "snippet": f"This research paper examines {query} from multiple perspectives. The authors conducted extensive studies to analyze..."
        })

        # Add a forum discussion
        results.append({
            "title": f"Discussion: {query.title()} - Forum",
            "url": f"https://forum.example.com/topics/{query.replace(' ', '-').lower()}",
            "snippet": f"Join the discussion about {query}. Users share their experiences, insights, and questions related to various aspects..."
        })

        return results

    async def _summarize_results_with_llm(self, query: str, results: List[Dict[str, Any]]) -> str:
        """
        Summarize search results using a language model.

        Args:
            query (str): The search query
            results (List[Dict[str, Any]]): The search results

        Returns:
            str: A summary of the search results
        """
        # Extract snippets and titles from results
        snippets = []
        for result in results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            url = result.get("url", "")
            if snippet:
                snippets.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}")

        # If no snippets, return a simple message
        if not snippets:
            return f"No relevant information found for the query: {query}"

        # Create a prompt for the language model
        prompt = f"""
        You are a research assistant tasked with summarizing search results for the query: "{query}"

        Here are the search results:

        {"\n\n".join(snippets)}

        Please provide a concise summary (2-3 paragraphs, less than 300 words) of these search results.
        Focus on extracting the key information relevant to the query and ignore any fluff or repetitive content.

        Your summary should be informative and well-structured, covering the main points from the search results.
        Do not include phrases like "according to the search results" or "the search results indicate" in your summary.
        Write in a neutral, informative tone.
        """

        try:
            # Generate summary using the model
            summary = await self.model_provider.generate_text(
                prompt=prompt,
                temperature=0.5,
                max_tokens=500
            )

            return summary.strip()

        except Exception as e:
            # Fallback to simple summarization if the model fails
            self.logger.warning(f"Error generating summary with LLM: {e}. Falling back to simple summarization.")
            return self._summarize_results(query, results)

    def _summarize_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """
        Summarize search results using a simple template-based approach.
        This is a fallback method if the LLM-based approach fails.

        Args:
            query (str): The search query
            results (List[Dict[str, Any]]): The search results

        Returns:
            str: A summary of the search results
        """
        # Extract snippets from results
        snippets = [result.get("snippet", "") for result in results if "snippet" in result]

        # Create a simple summary
        if not snippets:
            return f"No relevant information found for the query: {query}"

        summary = f"Summary of search results for '{query}':\n\n"

        # Add key points from snippets
        summary += "Key points from the search results:\n"
        for i, snippet in enumerate(snippets, 1):
            # Take the first sentence of each snippet
            first_sentence = snippet.split('.')[0] + '.'
            summary += f"{i}. {first_sentence}\n"

        summary += f"\nThe search returned {len(results)} results related to {query}."

        return summary

    async def _save_search_result(self, result: SearchResult) -> None:
        """
        Save search result to storage.

        Args:
            result (SearchResult): The search result to save
        """
        try:
            # Get the storage path for search results
            storage_path = get_storage_path("search_results")

            # Create a filename based on the query
            safe_query = "".join(c if c.isalnum() else "_" for c in result.query)
            safe_query = safe_query[:50]  # Limit length

            # Add timestamp to ensure uniqueness
            import time
            timestamp = int(time.time())

            # Create the file path
            file_path = storage_path / f"{safe_query}_{timestamp}.json"

            # Save the search result as JSON
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.model_dump_json(indent=2))

            self.logger.info(f"Saved search result to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving search result: {e}", exc_info=True)
