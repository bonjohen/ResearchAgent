"""
Web Content Tool Module

This module implements a web content fetcher tool for the Research Agent.
"""

import asyncio
import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from src.tools.base import Tool, ToolRegistry
from src.utils.logger import get_logger

logger = get_logger(__name__)

class WebContentTool(Tool):
    """
    Tool for fetching and processing web page content.
    """
    
    def __init__(self, name: str = "web_content", description: str = "Fetch and process content from a web page"):
        """
        Initialize a WebContentTool.
        
        Args:
            name (str, optional): The name of the tool. Defaults to "web_content".
            description (str, optional): A description of what the tool does. Defaults to "Fetch and process content from a web page".
        """
        super().__init__(name, description)
    
    async def execute(self, url: str, max_length: int = 8000) -> Dict[str, Any]:
        """
        Fetch and process content from a web page.
        
        Args:
            url (str): The URL of the web page to fetch
            max_length (int, optional): Maximum length of the content to return. Defaults to 8000.
        
        Returns:
            Dict[str, Any]: The processed web page content
        """
        self.logger.info(f"Fetching content from URL: {url}")
        
        try:
            # Validate the URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f"Invalid URL: {url}")
            
            # Fetch the web page content
            content, status_code = await self._fetch_url(url)
            
            if status_code != 200:
                self.logger.warning(f"Failed to fetch URL: {url} (Status code: {status_code})")
                return {
                    "url": url,
                    "success": False,
                    "error": f"Failed to fetch URL (Status code: {status_code})",
                    "content": "",
                    "title": "",
                    "summary": ""
                }
            
            # Parse the HTML content
            title, text, summary = self._parse_html(content, max_length)
            
            # Create the response
            response = {
                "url": url,
                "success": True,
                "title": title,
                "content": text,
                "summary": summary
            }
            
            self.logger.info(f"Successfully fetched and processed content from URL: {url}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error fetching content from URL: {url} - {e}", exc_info=True)
            return {
                "url": url,
                "success": False,
                "error": str(e),
                "content": "",
                "title": "",
                "summary": ""
            }
    
    async def _fetch_url(self, url: str) -> tuple:
        """
        Fetch content from a URL.
        
        Args:
            url (str): The URL to fetch
        
        Returns:
            tuple: (content, status_code)
        """
        # Set headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Make the request
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=30) as response:
                content = await response.text()
                status_code = response.status
                return content, status_code
    
    def _parse_html(self, html: str, max_length: int) -> tuple:
        """
        Parse HTML content to extract title and main text.
        
        Args:
            html (str): The HTML content to parse
            max_length (int): Maximum length of the text to return
        
        Returns:
            tuple: (title, text, summary)
        """
        # Parse the HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract the title
        title = soup.title.string if soup.title else ""
        
        # Remove script and style elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.extract()
        
        # Get the main content
        main_content = None
        
        # Try to find the main content using common selectors
        for selector in ["main", "article", "#content", ".content", "#main", ".main"]:
            content = soup.select_one(selector)
            if content:
                main_content = content
                break
        
        # If no main content found, use the body
        if not main_content:
            main_content = soup.body
        
        # Extract text from the main content
        if main_content:
            # Get all paragraphs
            paragraphs = main_content.find_all("p")
            text = "\n\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            # If no paragraphs found, get all text
            if not text:
                text = main_content.get_text()
                
                # Clean up the text
                text = re.sub(r'\s+', ' ', text)
                text = text.strip()
        else:
            text = ""
        
        # Truncate the text if it's too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        # Create a summary (first 500 characters)
        summary = text[:500] + "..." if len(text) > 500 else text
        
        return title, text, summary
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for this tool.
        
        Returns:
            Dict[str, Any]: The JSON schema for the tool
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to fetch"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "Maximum length of the content to return",
                        "default": 8000
                    }
                },
                "required": ["url"]
            }
        }

# Register the tool
ToolRegistry.register(WebContentTool())
