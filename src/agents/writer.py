"""
Writer Agent Module

This module implements the writer agent for the Research Agent system.
The writer agent is responsible for synthesizing search results into a comprehensive report.
"""

import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.agents.search import SearchResult
from src.models.base import ModelProvider
from src.models.factory import create_model_provider
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

    def __init__(self,
                 name: str = "WriterAgent",
                 description: str = "Synthesizes search results into a comprehensive report",
                 model_provider: Optional[ModelProvider] = None):
        """
        Initialize the WriterAgent.

        Args:
            name (str, optional): The name of the agent. Defaults to "WriterAgent".
            description (str, optional): A description of the agent. Defaults to "Synthesizes search results into a comprehensive report".
            model_provider (Optional[ModelProvider], optional): The model provider to use. Defaults to None (creates OpenAI provider).
        """
        super().__init__(name, description)

        # Initialize the model provider
        self.model_provider = model_provider or create_model_provider("openai")

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

        # Phase 3 implementation - use LLM for report generation
        try:
            # Create a summary of the findings using LLM
            summary = await self._create_summary_with_llm(topic, results)

            # Generate follow-up questions using LLM
            follow_up_questions = await self._generate_questions_with_llm(topic, results)

            # Create the full report content using LLM
            content = await self._create_report_with_llm(topic, results, summary, follow_up_questions)
        except Exception as e:
            # Fallback to template-based approach if LLM fails
            self.logger.warning(f"Error generating report with LLM: {e}. Falling back to template-based approach.")

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

    async def _create_summary_with_llm(self, topic: str, results: List[SearchResult]) -> str:
        """
        Create a summary of the research findings using a language model.

        Args:
            topic (str): The research topic
            results (List[SearchResult]): The search results

        Returns:
            str: A summary of the findings
        """
        # Prepare the search results for the prompt
        result_texts = []
        for result in results:
            result_texts.append(f"Query: {result.query}\nSummary: {result.summary}")

        # Create a prompt for the language model
        prompt = f"""
        You are a research assistant tasked with creating a concise summary of research findings on the topic: "{topic}"

        Based on the following search results, create a brief summary (2-3 sentences) that captures the key findings and importance of the topic.

        Search Results:
        {"\n\n".join(result_texts)}

        Your summary should be informative, neutral in tone, and highlight the most important aspects of {topic}.
        Keep it under 100 words.
        """

        try:
            # Generate summary using the model
            summary = await self.model_provider.generate_text(
                prompt=prompt,
                temperature=0.5,
                max_tokens=200
            )

            return summary.strip()

        except Exception as e:
            # Fallback to simple summarization if the model fails
            self.logger.warning(f"Error generating summary with LLM: {e}. Falling back to simple summarization.")
            return self._create_summary(topic, results)

    def _create_summary(self, topic: str, results: List[SearchResult]) -> str:
        """
        Create a summary of the research findings using a template-based approach.
        This is a fallback method if the LLM-based approach fails.

        Args:
            topic (str): The research topic
            results (List[SearchResult]): The search results

        Returns:
            str: A summary of the findings
        """
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

    async def _create_report_with_llm(self, topic: str, results: List[SearchResult], summary: str, follow_up_questions: List[str]) -> str:
        """
        Create a comprehensive research report using a language model.

        Args:
            topic (str): The research topic
            results (List[SearchResult]): The search results
            summary (str): The summary of the findings
            follow_up_questions (List[str]): Follow-up questions for further research

        Returns:
            str: The full report content in markdown format
        """
        # Prepare the search results for the prompt
        result_texts = []
        for result in results:
            result_texts.append(f"Query: {result.query}\nSummary: {result.summary}\nSources: {', '.join(result.sources)}")

        # Format the follow-up questions
        questions_text = "\n".join([f"- {q}" for q in follow_up_questions])

        # Create a prompt for the language model
        prompt = f"""
        You are a research assistant tasked with creating a comprehensive research report on the topic: "{topic}"

        Here is a summary of the findings:
        {summary}

        Here are the search results to incorporate into the report:
        {"\n\n".join(result_texts)}

        Here are follow-up questions to include in the report:
        {questions_text}

        Create a well-structured research report in markdown format with the following sections:
        1. Title (use # heading)
        2. Summary (use ## heading)
        3. Introduction (use ## heading)
        4. Findings (use ## heading, with ### subheadings for different aspects)
        5. Conclusion (use ## heading)
        6. Follow-up Questions (use ## heading, formatted as a bullet list)

        Guidelines:
        - The report should be comprehensive but concise
        - Use proper markdown formatting
        - Organize the findings by themes or categories
        - Include all the follow-up questions in the appropriate section
        - Cite sources where appropriate
        - The tone should be professional and academic

        Provide only the markdown report with no additional text or explanations.
        """

        try:
            # Generate report using the model
            report_content = await self.model_provider.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000
            )

            return report_content.strip()

        except Exception as e:
            # Fallback to template-based report if the model fails
            self.logger.warning(f"Error generating report with LLM: {e}. Falling back to template-based report.")
            return self._create_report_content(topic, results)

    async def _generate_questions_with_llm(self, topic: str, results: List[SearchResult]) -> List[str]:
        """
        Generate follow-up questions for further research using a language model.

        Args:
            topic (str): The research topic
            results (List[SearchResult]): The search results

        Returns:
            List[str]: List of follow-up questions
        """
        # Prepare the search results for the prompt
        result_texts = []
        for result in results:
            result_texts.append(f"Query: {result.query}\nSummary: {result.summary}")

        # Create a prompt for the language model
        prompt = f"""
        You are a research assistant tasked with generating insightful follow-up questions for further research on the topic: "{topic}"

        Based on the following search results, generate 10 thought-provoking questions that would help deepen the understanding of {topic}.

        Search Results:
        {"\n\n".join(result_texts)}

        Your questions should:
        - Cover different aspects of the topic
        - Address gaps in the current research
        - Explore potential implications and applications
        - Consider ethical, social, economic, or regulatory dimensions
        - Identify key experts, organizations, or future trends

        Format your response as a JSON array of strings, with each string being a question.
        Example: ["Question 1?", "Question 2?", ...]

        Provide only the JSON array in your response, with no additional text.
        """

        try:
            # Generate questions using the model
            response = await self.model_provider.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=800
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
                questions = json.loads(json_str)

                # Ensure we have at least a few questions
                if len(questions) < 3:
                    raise ValueError("Too few questions generated")

                return questions
            except Exception as e:
                self.logger.error(f"Error parsing LLM response as JSON: {e}")
                self.logger.debug(f"LLM response: {response}")
                raise

        except Exception as e:
            # Fallback to template-based questions if the model fails
            self.logger.warning(f"Error generating questions with LLM: {e}. Falling back to template-based questions.")
            return self._generate_follow_up_questions(topic, results)

    def _generate_follow_up_questions(self, topic: str, results: List[SearchResult]) -> List[str]:
        """
        Generate follow-up questions for further research using a template-based approach.
        This is a fallback method if the LLM-based approach fails.

        Args:
            topic (str): The research topic
            results (List[SearchResult]): The search results

        Returns:
            List[str]: List of follow-up questions
        """
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
