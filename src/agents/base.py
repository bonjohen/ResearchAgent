"""
Base Agent Module

This module provides the base agent class and related functionality for the Research Agent.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from src.utils.logger import get_logger

logger = get_logger(__name__)

class BaseAgent(ABC):
    """
    Base class for all agents in the Research Agent system.
    
    This abstract class defines the interface that all agents must implement.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a BaseAgent.
        
        Args:
            name (str): The name of the agent
            description (str, optional): A description of the agent. Defaults to "".
        """
        self.name = name
        self.description = description
        self.logger = get_logger(f"agent.{name}")
        self.logger.info(f"Initializing agent: {name}")
    
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """
        Process input data and return a result.
        
        This is the main method that all agents must implement.
        
        Args:
            input_data (Any): The input data to process
        
        Returns:
            Any: The processing result
        """
        pass
    
    async def run(self, input_data: Any) -> Any:
        """
        Run the agent on the input data.
        
        This method handles logging, timing, and error handling.
        
        Args:
            input_data (Any): The input data to process
        
        Returns:
            Any: The processing result
        
        Raises:
            Exception: If an error occurs during processing
        """
        self.logger.info(f"Running agent: {self.name}")
        try:
            import time
            start_time = time.time()
            
            result = await self.process(input_data)
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Agent {self.name} completed in {elapsed_time:.2f} seconds")
            
            return result
        except Exception as e:
            self.logger.error(f"Error in agent {self.name}: {e}", exc_info=True)
            raise

class AgentRegistry:
    """
    Registry for agents in the Research Agent system.
    
    This class provides a way to register and retrieve agents by name.
    """
    
    _agents: Dict[str, BaseAgent] = {}
    
    @classmethod
    def register(cls, agent: BaseAgent) -> None:
        """
        Register an agent in the registry.
        
        Args:
            agent (BaseAgent): The agent to register
        """
        cls._agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name.
        
        Args:
            name (str): The name of the agent to retrieve
        
        Returns:
            Optional[BaseAgent]: The agent, or None if not found
        """
        return cls._agents.get(name)
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """
        Get a list of all registered agent names.
        
        Returns:
            List[str]: List of agent names
        """
        return list(cls._agents.keys())

class AgentPipeline:
    """
    Pipeline for executing multiple agents in sequence.
    
    This class allows chaining agents together, where the output of one agent
    becomes the input to the next agent.
    """
    
    def __init__(self, agents: List[BaseAgent]):
        """
        Initialize an AgentPipeline.
        
        Args:
            agents (List[BaseAgent]): The agents to include in the pipeline
        """
        self.agents = agents
        self.logger = get_logger("agent.pipeline")
        agent_names = [agent.name for agent in agents]
        self.logger.info(f"Initializing agent pipeline with agents: {', '.join(agent_names)}")
    
    async def run(self, initial_input: Any) -> Any:
        """
        Run the pipeline on the initial input.
        
        Args:
            initial_input (Any): The initial input to the pipeline
        
        Returns:
            Any: The final output from the pipeline
        """
        self.logger.info("Starting agent pipeline")
        current_input = initial_input
        
        for agent in self.agents:
            self.logger.info(f"Pipeline step: {agent.name}")
            current_input = await agent.run(current_input)
        
        self.logger.info("Agent pipeline completed")
        return current_input

class ParallelAgents:
    """
    Class for executing multiple agents in parallel.
    
    This class allows running multiple agents concurrently on the same input
    and collecting their results.
    """
    
    def __init__(self, agents: List[BaseAgent]):
        """
        Initialize a ParallelAgents instance.
        
        Args:
            agents (List[BaseAgent]): The agents to run in parallel
        """
        self.agents = agents
        self.logger = get_logger("agent.parallel")
        agent_names = [agent.name for agent in agents]
        self.logger.info(f"Initializing parallel agents: {', '.join(agent_names)}")
    
    async def run(self, input_data: Any) -> List[Any]:
        """
        Run all agents in parallel on the same input.
        
        Args:
            input_data (Any): The input data for all agents
        
        Returns:
            List[Any]: List of results from all agents
        """
        self.logger.info("Starting parallel agent execution")
        
        tasks = [agent.run(input_data) for agent in self.agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Error in agent {self.agents[i].name}: {result}")
        
        self.logger.info("Parallel agent execution completed")
        return results
