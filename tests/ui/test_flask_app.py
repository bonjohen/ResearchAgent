"""
Tests for the Flask app.
"""

import unittest
from pathlib import Path

# Add the src directory to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui.app import app


class TestFlaskApp(unittest.TestCase):
    """Tests for the Flask app."""

    def setUp(self):
        """Set up the test environment."""
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index_route(self):
        """Test the index route."""
        response = self.client.get('/')
        self.assertEqual(200, response.status_code)
        self.assertIn(b'Research Agent', response.data)

    def test_get_models(self):
        """Test the models API endpoint."""
        response = self.client.get('/api/models')
        self.assertEqual(200, response.status_code)

        data = response.get_json()
        self.assertIn('openai', data)
        self.assertIn('ollama', data)
        self.assertIn('gpt-3.5-turbo', data['openai'])
        self.assertIn('llama3:7b', data['ollama'])

    def test_get_search_providers(self):
        """Test the search providers API endpoint."""
        response = self.client.get('/api/search-providers')
        self.assertEqual(200, response.status_code)

        data = response.get_json()
        self.assertIn('duckduckgo', data)
        self.assertIn('google', data)
        self.assertIn('serper', data)
        self.assertIn('tavily', data)

    def test_follow_up_research_endpoint_not_found(self):
        """Test the follow-up research API endpoint with a non-existent task."""
        response = self.client.post('/api/research/non-existent-task/follow-up')
        self.assertEqual(404, response.status_code)

        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual('Task not found', data['error'])

    def test_follow_up_research_endpoint_no_questions(self):
        """Test the follow-up research API endpoint with a task that has no follow-up questions."""
        # Add a completed task with no follow-up questions
        from src.ui.app import completed_tasks
        completed_tasks['test-task'] = {
            'id': 'test-task',
            'topic': 'Test Topic',
            'follow_up_questions': []
        }

        # Make the request
        response = self.client.post('/api/research/test-task/follow-up')
        self.assertEqual(400, response.status_code)

        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual('No follow-up questions available', data['error'])

        # Clean up
        del completed_tasks['test-task']

    def test_follow_up_research_endpoint_with_questions(self):
        """Test the follow-up research API endpoint with a task that has follow-up questions."""
        # Add a completed task with follow-up questions
        from src.ui.app import completed_tasks, active_tasks
        from unittest.mock import patch

        completed_tasks['test-task-with-questions'] = {
            'id': 'test-task-with-questions',
            'topic': 'Test Topic',
            'model_provider': 'openai',
            'model_name': 'gpt-3.5-turbo',
            'search_provider': 'duckduckgo',
            'verbose': False,
            'follow_up_questions': ['Question 1', 'Question 2', 'Question 3']
        }

        # Mock the threading.Thread to avoid actually starting a background thread
        with patch('src.ui.app.threading.Thread') as mock_thread:
            # Make the request
            response = self.client.post('/api/research/test-task-with-questions/follow-up')
            self.assertEqual(200, response.status_code)

            data = response.get_json()
            self.assertIn('task_id', data)

            # Check that a new task was created
            self.assertIn(data['task_id'], active_tasks)

            # Check that the new task has the correct properties
            new_task = active_tasks[data['task_id']]
            self.assertEqual('Test Topic (Follow-up)', new_task['topic'])
            self.assertEqual('openai', new_task['model_provider'])
            self.assertEqual('gpt-3.5-turbo', new_task['model_name'])
            self.assertEqual('duckduckgo', new_task['search_provider'])
            self.assertEqual(['Question 1', 'Question 2', 'Question 3'], new_task['search_queries'])

            # Check that a thread was started
            mock_thread.assert_called_once()
            mock_thread.return_value.start.assert_called_once()

            # Clean up
            del completed_tasks['test-task-with-questions']
            del active_tasks[data['task_id']]


if __name__ == '__main__':
    unittest.main()
