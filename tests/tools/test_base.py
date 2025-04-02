"""
Tests for the base tool module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.tools.base import Tool, ToolRegistry

# Create a concrete implementation of Tool for testing
class TestTool(Tool):
    """Test implementation of Tool."""
    
    def __init__(self, name="test_tool", description="Test tool description"):
        super().__init__(name, description)
    
    async def execute(self, **kwargs):
        return {"result": "test_result", "args": kwargs}

class TestToolBase:
    """Tests for the Tool base class."""
    
    def test_initialization(self):
        """Test tool initialization."""
        tool = TestTool()
        
        assert tool.name == "test_tool"
        assert tool.description == "Test tool description"
    
    def test_get_schema(self):
        """Test getting the tool schema."""
        tool = TestTool()
        schema = tool.get_schema()
        
        assert schema["name"] == "test_tool"
        assert schema["description"] == "Test tool description"
        assert "parameters" in schema
        assert schema["parameters"]["type"] == "object"
    
    @pytest.mark.asyncio
    async def test_execute(self):
        """Test executing the tool."""
        tool = TestTool()
        result = await tool.execute(arg1="value1", arg2="value2")
        
        assert result["result"] == "test_result"
        assert result["args"] == {"arg1": "value1", "arg2": "value2"}

class TestToolRegistry:
    """Tests for the ToolRegistry class."""
    
    def setup_method(self):
        """Set up the test environment."""
        # Clear the registry before each test
        ToolRegistry._tools = {}
    
    def test_register_and_get_tool(self):
        """Test registering and retrieving a tool."""
        tool = TestTool()
        ToolRegistry.register(tool)
        
        retrieved_tool = ToolRegistry.get("test_tool")
        assert retrieved_tool is tool
    
    def test_get_nonexistent_tool(self):
        """Test retrieving a non-existent tool."""
        retrieved_tool = ToolRegistry.get("nonexistent_tool")
        assert retrieved_tool is None
    
    def test_list_tools(self):
        """Test listing all registered tools."""
        tool1 = TestTool(name="tool1")
        tool2 = TestTool(name="tool2")
        
        ToolRegistry.register(tool1)
        ToolRegistry.register(tool2)
        
        tool_list = ToolRegistry.list_tools()
        assert set(tool_list) == {"tool1", "tool2"}
    
    def test_get_schemas(self):
        """Test getting schemas for all registered tools."""
        tool1 = TestTool(name="tool1")
        tool2 = TestTool(name="tool2")
        
        ToolRegistry.register(tool1)
        ToolRegistry.register(tool2)
        
        schemas = ToolRegistry.get_schemas()
        assert len(schemas) == 2
        assert any(schema["name"] == "tool1" for schema in schemas)
        assert any(schema["name"] == "tool2" for schema in schemas)
