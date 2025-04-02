"""
Writer Agent Module

This module implements the writer agent for the Research Agent system.
The writer agent is responsible for synthesizing search results into a comprehensive report.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.agents.search import SearchResult
from src.utils.logger import get_logger
from src.utils.storage import save_report

logger = get_logger(__name__)

class ResearchReport(BaseModel):
    """
    Model for a research report.
    """
    topic: str = Field(..., description="The original research topic")
    summary: str = Field(..., description="A brief summary of the findings")
    content: str = Field(..., description="The full report content in markdown format")
    follow_up_questions: List[str] = Field(default_factory=list, description="Follow-up questions for further research")

class WriterAgent(BaseAgent):
    """
    Writer agent that synthesizes search results into a comprehensive report.
    """
    
    def __init__(self, name: str = "WriterAgent", description: str = "Synthesizes search results into a comprehensive report"):
        """
        Initialize the WriterAgent.
        
        Args:
            name (str, optional): The name of the agent. Defaults to "WriterAgent".
            description (str, optional): A description of the agent. Defaults to "Synthesizes search results into a comprehensive report".
        """
        super().__init__(name, description)
    
    async def process(self, data: Dict[str, Any]) -> ResearchReport:
        """
        Process search results and create a comprehensive report.
        
        Args:
            data (Dict[str, Any]): Dictionary containing the topic and search results
                - topic (str): The original research topic
                - results (List[SearchResult]): List of search results
        
        Returns:
            ResearchReport: The comprehensive research report
        """
        topic = data.get("topic", "")
        results = data.get("results", [])
        
        self.logger.info(f"Creating research report for topic: {topic}")
        
        if not topic:
            raise ValueError("Topic is required")
        
        if not results:
            raise ValueError("Search results are required")
        
        # Phase 2 implementation - create a simple report
        # In Phase 6, this will be replaced with actual LLM-based report generation
        
        # Create a summary of the findings
        summary = self._create_summary(topic, results)
        
        # Create the full report content
        content = self._create_report_content(topic, results)
        
        # Generate follow-up questions
        follow_up_questions = self._generate_follow_up_questions(topic, results)
        
        # Create the research report
        report = ResearchReport(
            topic=topic,
            summary=summary,
            content=content,
            follow_up_questions=follow_up_questions
        )
        
        # Save the report to storage
        report_path = save_report(report.content, topic)
        self.logger.info(f"Saved research report to {report_path}")
        
        return report
    
    def _create_summary(self, topic: str, results: List[SearchResult]) -> str:
        """
        Create a summary of the research findings.
        
        Args:
            topic (str): The research topic
            results (List[SearchResult]): The search results
        
        Returns:
            str: A summary of the findings
        """
        # Phase 2 implementation - create a simple summary
        # In Phase 6, this will be replaced with actual LLM-based summarization
        
        summary = f"This report provides an overview of {topic} based on {len(results)} search queries. "
        summary += f"The research covers various aspects including definition, history, applications, and future trends of {topic}. "
        summary += f"Key findings highlight the importance and impact of {topic} in relevant domains."
        
        return summary
    
    def _create_report_content(self, topic: str, results: List[SearchResult]) -> str:
        """
        Create the full report content in markdown format.
        
        Args:
            topic (str): The research topic
            results (List[SearchResult]): The search results
        
        Returns:
            str: The full report content
        """
        # Phase 2 implementation - create a simple report
        # In Phase 6, this will be replaced with actual LLM-based report generation
        
        # Create the report title and introduction
        content = f"# Research Report: {topic.title()}\n\n"
        
        # Add the summary section
        content += "## Summary\n\n"
        content += self._create_summary(topic, results) + "\n\n"
        
        # Add the introduction section
        content += "## Introduction\n\n"
        content += f"This report presents findings from research on {topic}. "
        content += f"The research was conducted using multiple search queries to gather comprehensive information about different aspects of {topic}. "
        content += "The following sections present the findings organized by topic.\n\n"
        
        # Add sections based on search results
        content += "## Findings\n\n"
        
        # Group results by type (based on query)
        result_types = {
            "overview": [],
            "definition": [],
            "history": [],
            "examples": [],
            "advantages and disadvantages": [],
            "latest developments": [],
            "future trends": [],
            "applications": [],
            "challenges": [],
            "statistics": []
        }
        
        # Categorize results
        for result in results:
            for category in result_types.keys():
                if category in result.query.lower():
                    result_types[category].append(result)
                    break
        
        # Add sections for each category with results
        for category, category_results in result_types.items():
            if category_results:
                # Create a section title
                section_title = category.title()
                content += f"### {section_title}\n\n"
                
                # Add content from each result
                for result in category_results:
                    content += result.summary + "\n\n"
                    
                    # Add sources if available
                    if result.sources:
                        content += "Sources:\n"
                        for source in result.sources:
                            content += f"- {source}\n"
                        content += "\n"
        
        # Add conclusion section
        content += "## Conclusion\n\n"
        content += f"The research on {topic} has provided valuable insights into various aspects of the subject. "
        content += f"From understanding the basic concepts to exploring the latest developments and future trends, this report offers a comprehensive overview of {topic}. "
        content += "Further research could explore specific areas in more depth and address the follow-up questions identified.\n\n"
        
        # Add follow-up questions section
        content += "## Follow-up Questions\n\n"
        for question in self._generate_follow_up_questions(topic, results):
            content += f"- {question}\n"
        
        return content
    
    def _generate_follow_up_questions(self, topic: str, results: List[SearchResult]) -> List[str]:
        """
        Generate follow-up questions for further research.
        
        Args:
            topic (str): The research topic
            results (List[SearchResult]): The search results
        
        Returns:
            List[str]: List of follow-up questions
        """
        # Phase 2 implementation - create simple follow-up questions
        # In Phase 6, this will be replaced with actual LLM-based question generation
        
        questions = [
            f"What are the most significant recent advancements in {topic}?",
            f"How does {topic} impact different industries or sectors?",
            f"What are the ethical considerations related to {topic}?",
            f"How does {topic} compare to alternative approaches or technologies?",
            f"What are the long-term implications of {topic} for society?",
            f"Who are the leading experts or organizations in the field of {topic}?",
            f"What are the most promising research directions for {topic} in the next decade?",
            f"How is {topic} regulated or governed in different countries or regions?",
            f"What are the economic implications of {topic}?",
            f"How accessible is {topic} to different populations or communities?"
        ]
        
        return questions
