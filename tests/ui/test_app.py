"""
Tests for the web UI application.
"""

import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.ui.app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestWebUI:
    """Tests for the web UI application."""
    
    def test_index_route(self, client):
        """Test the index route."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Research Agent' in response.data
    
    def test_get_models(self, client):
        """Test the models API endpoint."""
        response = client.get('/api/models')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'openai' in data
        assert 'ollama' in data
        assert 'gpt-3.5-turbo' in data['openai']
        assert 'llama3:7b' in data['ollama']
    
    def test_get_search_providers(self, client):
        """Test the search providers API endpoint."""
        response = client.get('/api/search-providers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'duckduckgo' in data
        assert 'google' in data
        assert 'serper' in data
        assert 'tavily' in data
    
    @patch('src.ui.app.threading.Thread')
    def test_start_research(self, mock_thread, client):
        """Test starting a research task."""
        # Create test data
        data = {
            'topic': 'Test Topic',
            'model_provider': 'openai',
            'model_name': 'gpt-3.5-turbo',
            'search_provider': 'duckduckgo',
            'verbose': True
        }
        
        # Make the request
        response = client.post('/api/research', json=data)
        assert response.status_code == 200
        
        # Check the response
        response_data = json.loads(response.data)
        assert 'task_id' in response_data
        
        # Check that a thread was started
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    def test_get_research_status_not_found(self, client):
        """Test getting the status of a non-existent research task."""
        response = client.get('/api/research/non-existent-task')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error']
