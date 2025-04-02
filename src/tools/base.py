"""
Base Tool Module

This module defines the base interface for tools in the Research Agent.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)

class Tool(ABC):
    """
    Abstract base class for tools.
    
    This class defines the interface that all tools must implement.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize a Tool.
        
        Args:
            name (str): The name of the tool
            description (str): A description of what the tool does
        """
        self.name = name
        self.description = description
        self.logger = get_logger(f"tool.{name}")
        self.logger.info(f"Initializing tool: {name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool with the provided arguments.
        
        Args:
            **kwargs: Arguments for the tool
        
        Returns:
            Any: The result of the tool execution
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for this tool.
        
        This schema is used for function calling with language models.
        
        Returns:
            Dict[str, Any]: The JSON schema for the tool
        """
        # Subclasses should override this method to provide a specific schema
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }

class ToolRegistry:
    """
    Registry for tools in the Research Agent system.
    
    This class provides a way to register and retrieve tools by name.
    """
    
    _tools: Dict[str, Tool] = {}
    
    @classmethod
    def register(cls, tool: Tool) -> None:
        """
        Register a tool in the registry.
        
        Args:
            tool (Tool): The tool to register
        """
        cls._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            name (str): The name of the tool to retrieve
        
        Returns:
            Optional[Tool]: The tool, or None if not found
        """
        return cls._tools.get(name)
    
    @classmethod
    def list_tools(cls) -> List[str]:
        """
        Get a list of all registered tool names.
        
        Returns:
            List[str]: List of tool names
        """
        return list(cls._tools.keys())
    
    @classmethod
    def get_schemas(cls) -> List[Dict[str, Any]]:
        """
        Get the JSON schemas for all registered tools.
        
        Returns:
            List[Dict[str, Any]]: List of tool schemas
        """
        return [tool.get_schema() for tool in cls._tools.values()]
