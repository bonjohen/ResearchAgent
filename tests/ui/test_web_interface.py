"""
Web Interface Tests

This module contains tests for the Research Agent web interface using Selenium.
"""

import os
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Add the src directory to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui.app import app


class TestWebInterface(unittest.TestCase):
    """Tests for the web interface using Selenium."""
    
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
        
        # Start the Flask app in a separate thread
        import threading
        cls.server_thread = threading.Thread(target=lambda: app.run(port=5001, debug=False))
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Wait for the server to start
        time.sleep(2)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests."""
        cls.driver.quit()
    
    def setUp(self):
        """Set up before each test."""
        # Navigate to the home page
        self.driver.get("http://localhost:5001")
        
        # Wait for the page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "research-form"))
        )
    
    def test_page_title(self):
        """Test that the page title is correct."""
        self.assertEqual("Research Agent", self.driver.title)
    
    def test_navigation_links(self):
        """Test that the navigation links work correctly."""
        # Click on Reports link
        self.driver.find_element(By.ID, "nav-reports").click()
        
        # Check that the Reports section is visible
        reports_section = self.driver.find_element(By.ID, "reports-section")
        self.assertTrue(reports_section.is_displayed())
        
        # Click on Active Tasks link
        self.driver.find_element(By.ID, "nav-active-tasks").click()
        
        # Check that the Active Tasks section is visible
        active_tasks_section = self.driver.find_element(By.ID, "active-tasks-section")
        self.assertTrue(active_tasks_section.is_displayed())
        
        # Click on New Research link
        self.driver.find_element(By.ID, "nav-new-research").click()
        
        # Check that the New Research section is visible
        new_research_section = self.driver.find_element(By.ID, "new-research-section")
        self.assertTrue(new_research_section.is_displayed())
    
    def test_model_provider_change(self):
        """Test that changing the model provider updates the model name options."""
        # Get the model provider select element
        model_provider = Select(self.driver.find_element(By.ID, "model-provider"))
        
        # Get the model name select element
        model_name = Select(self.driver.find_element(By.ID, "model-name"))
        
        # Check initial options (OpenAI)
        self.assertEqual("openai", model_provider.first_selected_option.get_attribute("value"))
        self.assertTrue(any(option.get_attribute("value") == "gpt-3.5-turbo" for option in model_name.options))
        
        # Change to Ollama
        model_provider.select_by_value("ollama")
        
        # Wait for the options to update
        WebDriverWait(self.driver, 10).until(
            lambda driver: any(option.get_attribute("value") == "llama3:7b" for option in Select(driver.find_element(By.ID, "model-name")).options)
        )
        
        # Check that the model name options have been updated
        model_name = Select(self.driver.find_element(By.ID, "model-name"))
        self.assertTrue(any(option.get_attribute("value") == "llama3:7b" for option in model_name.options))
    
    @patch('src.ui.app.threading.Thread')
    def test_start_research(self, mock_thread):
        """Test starting a research task."""
        # Set up the mock
        mock_thread.return_value.start = MagicMock()
        
        # Fill in the research form
        self.driver.find_element(By.ID, "topic").send_keys("Test Topic")
        
        # Submit the form
        self.driver.find_element(By.ID, "research-form").submit()
        
        # Wait for the task progress modal to appear
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "task-progress-modal"))
        )
        
        # Check that the modal is visible
        modal = self.driver.find_element(By.ID, "task-progress-modal")
        self.assertTrue(modal.is_displayed())
        
        # Check that a thread was started
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    @patch('src.ui.app.threading.Thread')
    def test_follow_up_button(self, mock_thread):
        """Test the follow-up research button."""
        # Set up the mock
        mock_thread.return_value.start = MagicMock()
        
        # Fill in the research form
        self.driver.find_element(By.ID, "topic").send_keys("Test Topic")
        
        # Submit the form
        self.driver.find_element(By.ID, "research-form").submit()
        
        # Wait for the task progress modal to appear
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "task-progress-modal"))
        )
        
        # Simulate a completed task with follow-up questions
        # This would normally be done by the background thread
        # For testing, we'll use JavaScript to modify the DOM
        self.driver.execute_script("""
            document.getElementById('task-status').textContent = 'Completed';
            document.getElementById('task-status').className = 'badge bg-completed';
            document.getElementById('task-progress-bar').style.width = '100%';
            document.getElementById('view-report-btn').classList.remove('d-none');
            document.getElementById('follow-up-btn').classList.remove('d-none');
            document.getElementById('follow-up-btn').textContent = 'Run Follow-up Research (3 questions)';
        """)
        
        # Check that the follow-up button is visible
        follow_up_btn = self.driver.find_element(By.ID, "follow-up-btn")
        self.assertTrue(follow_up_btn.is_displayed())
        
        # Click the follow-up button
        follow_up_btn.click()
        
        # Check that a new thread was started for follow-up research
        self.assertEqual(2, mock_thread.call_count)
        self.assertEqual(2, mock_thread.return_value.start.call_count)
    
    def test_reports_list(self):
        """Test the reports list functionality."""
        # Navigate to the Reports section
        self.driver.find_element(By.ID, "nav-reports").click()
        
        # Wait for the reports list to load
        WebDriverWait(self.driver, 10).until(
            lambda driver: "Loading..." not in driver.find_element(By.ID, "reports-list").text
        )
        
        # Check that the reports list is visible
        reports_list = self.driver.find_element(By.ID, "reports-list")
        self.assertTrue(reports_list.is_displayed())
        
        # If there are reports, test clicking on one
        try:
            report_items = self.driver.find_elements(By.CSS_SELECTOR, "#reports-list a")
            if report_items:
                # Click on the first report
                report_items[0].click()
                
                # Wait for the report content to load
                WebDriverWait(self.driver, 10).until(
                    lambda driver: "Select a report" not in driver.find_element(By.ID, "report-title").text
                )
                
                # Check that the report content is visible
                report_content = self.driver.find_element(By.ID, "report-content")
                self.assertTrue(report_content.is_displayed())
                self.assertNotEqual("", report_content.text.strip())
        except Exception as e:
            print(f"No reports found or error clicking report: {e}")
    
    def test_active_tasks(self):
        """Test the active tasks functionality."""
        # Start a research task
        with patch('src.ui.app.threading.Thread') as mock_thread:
            mock_thread.return_value.start = MagicMock()
            
            # Fill in the research form
            self.driver.find_element(By.ID, "topic").send_keys("Test Active Task")
            
            # Submit the form
            self.driver.find_element(By.ID, "research-form").submit()
            
            # Wait for the task progress modal to appear
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "task-progress-modal"))
            )
            
            # Close the modal
            self.driver.find_element(By.CSS_SELECTOR, ".modal-header .btn-close").click()
            
            # Wait for the modal to close
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "task-progress-modal"))
            )
            
            # Navigate to the Active Tasks section
            self.driver.find_element(By.ID, "nav-active-tasks").click()
            
            # Wait for the active tasks to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: "No active research tasks" not in driver.find_element(By.ID, "active-tasks-container").text
            )
            
            # Check that there is at least one active task
            task_cards = self.driver.find_elements(By.CSS_SELECTOR, ".task-card")
            self.assertGreaterEqual(len(task_cards), 1)
            
            # Check that the task has the correct topic
            task_title = task_cards[0].find_element(By.CSS_SELECTOR, ".card-title")
            self.assertEqual("Test Active Task", task_title.text)


if __name__ == "__main__":
    unittest.main()
