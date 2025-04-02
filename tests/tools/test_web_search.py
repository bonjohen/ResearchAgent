"""
Tests for the web search tool.
"""

import pytest

from src.tools.base import ToolRegistry
from src.tools.web_search import WebSearchTool

class TestWebSearchTool:
    """Tests for the WebSearchTool class."""
    
    def test_initialization(self):
        """Test tool initialization."""
        tool = WebSearchTool()
        
        assert tool.name == "web_search"
        assert "Search the web" in tool.description
    
    def test_initialization_with_custom_name(self):
        """Test tool initialization with a custom name."""
        tool = WebSearchTool(name="custom_search")
        
        assert tool.name == "custom_search"
    
    def test_get_schema(self):
        """Test getting the tool schema."""
        tool = WebSearchTool()
        schema = tool.get_schema()
        
        assert schema["name"] == "web_search"
        assert "description" in schema
        assert "parameters" in schema
        assert "properties" in schema["parameters"]
        assert "query" in schema["parameters"]["properties"]
        assert "num_results" in schema["parameters"]["properties"]
        assert schema["parameters"]["required"] == ["query"]
    
    @pytest.mark.asyncio
    async def test_execute(self):
        """Test executing the tool."""
        tool = WebSearchTool()
        result = await tool.execute(query="test query")
        
        assert result["query"] == "test query"
        assert "num_results" in result
        assert "results" in result
        assert len(result["results"]) > 0
        
        # Check that each result has the expected structure
        for search_result in result["results"]:
            assert "title" in search_result
            assert "url" in search_result
            assert "snippet" in search_result
    
    @pytest.mark.asyncio
    async def test_execute_with_num_results(self):
        """Test executing the tool with a specific number of results."""
        tool = WebSearchTool()
        result = await tool.execute(query="test query", num_results=3)
        
        assert result["query"] == "test query"
        assert result["num_results"] == 3
        assert len(result["results"]) == 3
    
    def test_tool_registry(self):
        """Test that the tool is registered in the ToolRegistry."""
        # Get the tool from the registry
        tool = ToolRegistry.get("web_search")
        
        # Check that it's a WebSearchTool
        assert isinstance(tool, WebSearchTool)
        
        # Check that it's in the list of tools
        assert "web_search" in ToolRegistry.list_tools()
        
        # Check that its schema is in the list of schemas
        schemas = ToolRegistry.get_schemas()
        assert any(schema["name"] == "web_search" for schema in schemas)
