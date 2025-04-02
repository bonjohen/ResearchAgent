"""
Tests for the web content tool.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.tools.web_content import WebContentTool

class TestWebContentTool:
    """Tests for the WebContentTool class."""
    
    def test_initialization(self):
        """Test tool initialization."""
        tool = WebContentTool()
        
        assert tool.name == "web_content"
        assert "Fetch and process content" in tool.description
    
    def test_get_schema(self):
        """Test getting the tool schema."""
        tool = WebContentTool()
        schema = tool.get_schema()
        
        assert schema["name"] == "web_content"
        assert "description" in schema
        assert "parameters" in schema
        assert "properties" in schema["parameters"]
        assert "url" in schema["parameters"]["properties"]
        assert "max_length" in schema["parameters"]["properties"]
        assert schema["parameters"]["required"] == ["url"]
    
    @pytest.mark.asyncio
    async def test_execute(self):
        """Test executing the tool."""
        tool = WebContentTool()
        
        # Mock the fetch_url method
        with patch.object(tool, "_fetch_url", new_callable=AsyncMock) as mock_fetch:
            # Set up the mock to return some HTML content
            html_content = """
            <html>
                <head>
                    <title>Test Page</title>
                </head>
                <body>
                    <main>
                        <p>This is a test paragraph.</p>
                        <p>This is another test paragraph.</p>
                    </main>
                </body>
            </html>
            """
            mock_fetch.return_value = (html_content, 200)
            
            # Execute the tool
            result = await tool.execute(url="https://example.com")
            
            # Check that the fetch method was called
            mock_fetch.assert_called_once_with("https://example.com")
            
            # Check the result
            assert result["url"] == "https://example.com"
            assert result["success"] is True
            assert result["title"] == "Test Page"
            assert "This is a test paragraph." in result["content"]
            assert "This is another test paragraph." in result["content"]
            assert "This is a test paragraph." in result["summary"]
    
    @pytest.mark.asyncio
    async def test_execute_with_invalid_url(self):
        """Test executing the tool with an invalid URL."""
        tool = WebContentTool()
        
        # Execute the tool with an invalid URL
        result = await tool.execute(url="invalid-url")
        
        # Check the result
        assert result["url"] == "invalid-url"
        assert result["success"] is False
        assert "error" in result
        assert "Invalid URL" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_with_fetch_error(self):
        """Test executing the tool with a fetch error."""
        tool = WebContentTool()
        
        # Mock the fetch_url method to return an error status
        with patch.object(tool, "_fetch_url", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = ("", 404)
            
            # Execute the tool
            result = await tool.execute(url="https://example.com")
            
            # Check that the fetch method was called
            mock_fetch.assert_called_once_with("https://example.com")
            
            # Check the result
            assert result["url"] == "https://example.com"
            assert result["success"] is False
            assert "error" in result
            assert "Failed to fetch URL" in result["error"]
    
    @pytest.mark.asyncio
    async def test_fetch_url(self):
        """Test the fetch_url method."""
        tool = WebContentTool()
        
        # Mock the aiohttp ClientSession
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html><body>Test content</body></html>")
        
        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = AsyncMock(return_value=mock_response)
        
        with patch("aiohttp.ClientSession", return_value=mock_session):
            # Execute the fetch
            content, status_code = await tool._fetch_url("https://example.com")
            
            # Check the results
            assert content == "<html><body>Test content</body></html>"
            assert status_code == 200
    
    def test_parse_html(self):
        """Test the parse_html method."""
        tool = WebContentTool()
        
        # Create some HTML content
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <main>
                    <p>This is a test paragraph.</p>
                    <p>This is another test paragraph.</p>
                </main>
            </body>
        </html>
        """
        
        # Parse the HTML
        title, text, summary = tool._parse_html(html_content, 1000)
        
        # Check the results
        assert title == "Test Page"
        assert "This is a test paragraph." in text
        assert "This is another test paragraph." in text
        assert "This is a test paragraph." in summary
