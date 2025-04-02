"""
Web UI Application for Research Agent

This module provides a web-based user interface for the Research Agent.
"""

import asyncio
import os
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, render_template, request, send_from_directory

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.manager import ResearchManager
from src.models.factory import create_model_provider
from src.utils.logger import get_logger, setup_logger
from src.utils.storage import get_storage_path

# Set up logging
setup_logger()
logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

# Store active research tasks
active_tasks: Dict[str, Dict] = {}

# Store completed research tasks
completed_tasks: Dict[str, Dict] = {}

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")

@app.route("/api/models", methods=["GET"])
def get_models():
    """Get available models."""
    models = {
        "openai": ["gpt-3.5-turbo", "gpt-4"],
        "ollama": ["llama3:7b", "llama3:8b", "mistral:7b", "phi3:mini"]
    }
    return jsonify(models)

@app.route("/api/search-providers", methods=["GET"])
def get_search_providers():
    """Get available search providers."""
    providers = ["duckduckgo", "google", "serper", "tavily"]
    return jsonify(providers)

@app.route("/api/research", methods=["POST"])
def start_research():
    """Start a new research task."""
    data = request.json
    topic = data.get("topic", "")
    model_provider = data.get("model_provider", "openai")
    model_name = data.get("model_name", None)
    search_provider = data.get("search_provider", None)
    verbose = data.get("verbose", False)
    
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    
    # Set environment variables for the research task
    if search_provider:
        os.environ["SEARCH_ENGINE"] = search_provider
    
    # Set log level based on verbose flag
    if verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"
    else:
        os.environ["LOG_LEVEL"] = "INFO"
    
    # Generate a unique task ID
    task_id = str(uuid.uuid4())
    
    # Create a new task
    task = {
        "id": task_id,
        "topic": topic,
        "model_provider": model_provider,
        "model_name": model_name,
        "search_provider": search_provider,
        "verbose": verbose,
        "status": "starting",
        "progress": 0,
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "report_path": None,
        "logs": [],
        "search_queries": [],
        "search_results": [],
        "follow_up_questions": []
    }
    
    # Store the task
    active_tasks[task_id] = task
    
    # Start the research task in a background thread
    thread = threading.Thread(target=run_research_task, args=(task_id, task))
    thread.daemon = True
    thread.start()
    
    return jsonify({"task_id": task_id})

@app.route("/api/research/<task_id>", methods=["GET"])
def get_research_status(task_id):
    """Get the status of a research task."""
    # Check if the task is active
    if task_id in active_tasks:
        return jsonify(active_tasks[task_id])
    
    # Check if the task is completed
    if task_id in completed_tasks:
        return jsonify(completed_tasks[task_id])
    
    return jsonify({"error": "Task not found"}), 404

@app.route("/api/research/<task_id>/report", methods=["GET"])
def get_research_report(task_id):
    """Get the research report for a task."""
    # Check if the task is completed
    if task_id in completed_tasks and completed_tasks[task_id]["report_path"]:
        report_path = completed_tasks[task_id]["report_path"]
        
        # Read the report content
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
        
        return jsonify({"report": report_content})
    
    return jsonify({"error": "Report not found"}), 404

@app.route("/api/reports", methods=["GET"])
def get_reports():
    """Get a list of all reports."""
    try:
        # Get the reports directory
        reports_dir = get_storage_path("reports")
        
        # Get all report files
        report_files = list(reports_dir.glob("*.md"))
        
        # Create a list of report metadata
        reports = []
        for report_file in report_files:
            # Extract the topic from the filename
            topic = report_file.stem.replace("_", " ")
            
            # Get the file creation time
            created_time = datetime.fromtimestamp(report_file.stat().st_ctime).isoformat()
            
            reports.append({
                "id": report_file.stem,
                "topic": topic,
                "created": created_time,
                "path": str(report_file)
            })
        
        # Sort reports by creation time (newest first)
        reports.sort(key=lambda x: x["created"], reverse=True)
        
        return jsonify(reports)
    
    except Exception as e:
        logger.error(f"Error getting reports: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/api/reports/<report_id>", methods=["GET"])
def get_report(report_id):
    """Get a specific report by ID."""
    try:
        # Get the reports directory
        reports_dir = get_storage_path("reports")
        
        # Find the report file
        report_files = list(reports_dir.glob(f"{report_id}*.md"))
        
        if not report_files:
            return jsonify({"error": "Report not found"}), 404
        
        # Read the report content
        with open(report_files[0], "r", encoding="utf-8") as f:
            report_content = f.read()
        
        return jsonify({"report": report_content})
    
    except Exception as e:
        logger.error(f"Error getting report: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

def run_research_task(task_id: str, task: Dict):
    """Run a research task in the background."""
    try:
        # Update task status
        task["status"] = "running"
        task["progress"] = 5
        task["logs"].append(f"Starting research on topic: {task['topic']}")
        
        # Initialize the model provider
        model_provider = create_model_provider(
            provider_type=task["model_provider"],
            model_name=task["model_name"]
        )
        
        # Initialize the research manager
        manager = ResearchManager(model_provider=model_provider)
        
        # Run the planning phase
        task["logs"].append("Planning research approach...")
        task["progress"] = 10
        
        # Create a custom event loop for the thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the research plan
        plan = loop.run_until_complete(manager.plan_research(task["topic"]))
        
        # Update task with search queries
        task["search_queries"] = [query.query for query in plan.queries]
        task["progress"] = 20
        task["logs"].append(f"Created research plan with {len(plan.queries)} search queries")
        
        # Run the search phase
        task["logs"].append("Executing web searches...")
        task["progress"] = 30
        
        # Execute the searches
        search_results = loop.run_until_complete(manager.execute_searches(plan))
        
        # Update task with search results
        task["search_results"] = [result.summary for result in search_results]
        task["progress"] = 60
        task["logs"].append(f"Completed {len(search_results)} searches")
        
        # Run the writing phase
        task["logs"].append("Synthesizing information...")
        task["progress"] = 70
        
        # Generate the report
        report = loop.run_until_complete(manager.generate_report(task["topic"], search_results))
        
        # Update task with report path and follow-up questions
        task["report_path"] = report.file_path
        task["follow_up_questions"] = report.follow_up_questions
        task["progress"] = 100
        task["status"] = "completed"
        task["end_time"] = datetime.now().isoformat()
        task["logs"].append("Research complete!")
        
        # Move the task to completed tasks
        completed_tasks[task_id] = task
        del active_tasks[task_id]
        
    except Exception as e:
        # Update task with error
        task["status"] = "failed"
        task["logs"].append(f"Error: {str(e)}")
        task["end_time"] = datetime.now().isoformat()
        
        # Move the task to completed tasks
        completed_tasks[task_id] = task
        del active_tasks[task_id]
        
        logger.error(f"Error running research task: {e}", exc_info=True)

def run_app(host="127.0.0.1", port=5000, debug=False):
    """Run the Flask application."""
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_app(debug=True)
