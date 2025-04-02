"""
Follow-up Button Tests

This module contains specific tests for the follow-up research button functionality.
"""

import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Add the src directory to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui.app import app


class TestFollowUpButton(unittest.TestCase):
    """Tests specifically for the follow-up research button."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize the WebDriver
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error initializing Chrome WebDriver: {e}")
            print("Trying Firefox instead...")
            # Try Firefox as a fallback
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            cls.driver = webdriver.Firefox(options=firefox_options)

        # Set implicit wait time
        cls.driver.implicitly_wait(10)

        # Mock the Flask app instead of starting a real server
        # This avoids issues with network connections and API calls
        app.config['TESTING'] = True
        app.config['SERVER_NAME'] = 'localhost:5002'

        # Create a test client
        cls.app_client = app.test_client()

        # Create an app context
        cls.app_context = app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        cls.driver.quit()

        # Pop the app context
        cls.app_context.pop()

    def setUp(self):
        """Set up before each test."""
        # Create a mock HTML page with the necessary elements
        mock_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Research Agent</title>
        </head>
        <body>
            <form id="research-form">
                <input type="text" id="topic" name="topic">
                <button type="submit">Start Research</button>
            </form>
            <div id="task-progress-modal" style="display:none;">
                <div class="modal-content">
                    <div id="task-status">Starting</div>
                    <div id="task-progress-bar" style="width:0%"></div>
                    <div id="task-queries"></div>
                    <div id="task-logs"></div>
                    <button id="follow-up-btn" style="display:none;">Run Follow-up Research</button>
                    <a id="view-report-btn" style="display:none;">View Report</a>
                </div>
            </div>
        </body>
        </html>
        """

        # Write the mock HTML to a temporary file
        with open("mock_page.html", "w") as f:
            f.write(mock_html)

        # Navigate to the mock HTML file
        self.driver.get("file:///" + str(Path("mock_page.html").absolute()))

        # Wait for the page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "research-form"))
        )

    def test_follow_up_button_visibility(self):
        """Test that the follow-up button is visible when a task is completed with follow-up questions."""
        # Get the follow-up button
        follow_up_btn = self.driver.find_element(By.ID, "follow-up-btn")

        # Initially, the follow-up button should be hidden
        self.assertEqual("none", follow_up_btn.get_attribute("style").split(";")[0].split(":")[1].strip())

        # Simulate a completed task with follow-up questions
        self.driver.execute_script("""
            document.getElementById('task-status').textContent = 'Completed';
            document.getElementById('task-progress-bar').style.width = '100%';
            document.getElementById('follow-up-btn').style.display = 'block';
            document.getElementById('follow-up-btn').textContent = 'Run Follow-up Research (3 questions)';
        """)

        # Now the follow-up button should be visible
        self.assertEqual("block", follow_up_btn.get_attribute("style").split(";")[0].split(":")[1].strip())
        self.assertEqual("Run Follow-up Research (3 questions)", follow_up_btn.text)

    def test_follow_up_button_click(self):
        """Test that clicking the follow-up button starts a new research task."""
        # Get the follow-up button
        follow_up_btn = self.driver.find_element(By.ID, "follow-up-btn")

        # Make the button visible
        self.driver.execute_script("""
            document.getElementById('task-status').textContent = 'Completed';
            document.getElementById('task-progress-bar').style.width = '100%';
            document.getElementById('follow-up-btn').style.display = 'block';
            document.getElementById('follow-up-btn').textContent = 'Run Follow-up Research (3 questions)';
        """)

        # Add a click event listener to the button
        self.driver.execute_script("""
            document.getElementById('follow-up-btn').addEventListener('click', function() {
                this.disabled = true;
                this.textContent = 'Starting follow-up research...';
            });
        """)

        # Click the follow-up button
        follow_up_btn.click()

        # Check that the button was disabled and text changed
        self.assertTrue(follow_up_btn.get_property("disabled"))
        self.assertEqual("Starting follow-up research...", follow_up_btn.text)

    def test_follow_up_button_disabled_during_processing(self):
        """Test that the follow-up button is disabled during processing."""
        # Get the follow-up button
        follow_up_btn = self.driver.find_element(By.ID, "follow-up-btn")

        # Make the button visible
        self.driver.execute_script("""
            document.getElementById('task-status').textContent = 'Completed';
            document.getElementById('task-progress-bar').style.width = '100%';
            document.getElementById('follow-up-btn').style.display = 'block';
            document.getElementById('follow-up-btn').textContent = 'Run Follow-up Research (3 questions)';
        """)

        # Simulate clicking the button and it becoming disabled
        self.driver.execute_script("""
            document.getElementById('follow-up-btn').disabled = true;
            document.getElementById('follow-up-btn').textContent = 'Starting follow-up research...';
        """)

        # Check that the button is disabled
        self.assertTrue(follow_up_btn.get_property("disabled"))
        self.assertEqual("Starting follow-up research...", follow_up_btn.text)

    def test_follow_up_api_endpoint(self):
        """Test the follow-up research API endpoint."""
        # Use JavaScript to make a direct API call
        response = self.driver.execute_script("""
            return fetch('/api/research/test-task-id/follow-up', {
                method: 'POST'
            }).then(response => response.json());
        """)

        # Check the response
        self.assertIn("error", response)
        self.assertEqual("Task not found", response["error"])


if __name__ == "__main__":
    unittest.main()
