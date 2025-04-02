// Main JavaScript for Research Agent UI

document.addEventListener('DOMContentLoaded', function() {
    // Navigation
    const navNewResearch = document.getElementById('nav-new-research');
    const navReports = document.getElementById('nav-reports');
    const navActiveTasks = document.getElementById('nav-active-tasks');

    const newResearchSection = document.getElementById('new-research-section');
    const reportsSection = document.getElementById('reports-section');
    const activeTasksSection = document.getElementById('active-tasks-section');

    // Show New Research section by default
    navNewResearch.addEventListener('click', function(e) {
        e.preventDefault();
        showSection(newResearchSection);
        setActiveNav(navNewResearch);
    });

    // Show Reports section
    navReports.addEventListener('click', function(e) {
        e.preventDefault();
        showSection(reportsSection);
        setActiveNav(navReports);
        loadReports();
    });

    // Show Active Tasks section
    navActiveTasks.addEventListener('click', function(e) {
        e.preventDefault();
        showSection(activeTasksSection);
        setActiveNav(navActiveTasks);
        loadActiveTasks();
    });

    // Helper function to show a section and hide others
    function showSection(section) {
        newResearchSection.classList.add('d-none');
        reportsSection.classList.add('d-none');
        activeTasksSection.classList.add('d-none');

        section.classList.remove('d-none');
    }

    // Helper function to set active navigation item
    function setActiveNav(navItem) {
        navNewResearch.classList.remove('active');
        navReports.classList.remove('active');
        navActiveTasks.classList.remove('active');

        navItem.classList.add('active');
    }

    // Model provider change handler
    const modelProvider = document.getElementById('model-provider');
    const modelName = document.getElementById('model-name');

    modelProvider.addEventListener('change', function() {
        // Clear existing options
        modelName.innerHTML = '';

        // Add options based on selected provider
        if (this.value === 'openai') {
            addOption(modelName, 'gpt-3.5-turbo', 'GPT-3.5 Turbo');
            addOption(modelName, 'gpt-4', 'GPT-4');
        } else if (this.value === 'ollama') {
            addOption(modelName, 'llama3:7b', 'Llama 3 (7B)');
            addOption(modelName, 'llama3:8b', 'Llama 3 (8B)');
            addOption(modelName, 'mistral:7b', 'Mistral (7B)');
            addOption(modelName, 'phi3:mini', 'Phi-3 Mini');
        }
    });

    // Helper function to add an option to a select element
    function addOption(selectElement, value, text) {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        selectElement.appendChild(option);
    }

    // Research form submission
    const researchForm = document.getElementById('research-form');

    researchForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Get form values
        const topic = document.getElementById('topic').value;
        const modelProvider = document.getElementById('model-provider').value;
        const modelName = document.getElementById('model-name').value;
        const searchProvider = document.getElementById('search-provider').value;
        const verbose = document.getElementById('verbose').checked;

        // Create request data
        const data = {
            topic: topic,
            model_provider: modelProvider,
            model_name: modelName,
            search_provider: searchProvider,
            verbose: verbose
        };

        // Send request to start research
        fetch('/api/research', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.task_id) {
                // Show task progress modal
                showTaskProgress(data.task_id);

                // Reset form
                researchForm.reset();
            } else {
                alert('Error starting research: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error starting research:', error);
            alert('Error starting research: ' + error.message);
        });
    });

    // Task progress modal
    const taskProgressModal = new bootstrap.Modal(document.getElementById('task-progress-modal'));
    let currentTaskId = null;
    let taskUpdateInterval = null;

    function showTaskProgress(taskId) {
        currentTaskId = taskId;

        // Reset modal content
        document.getElementById('task-topic').textContent = '';
        document.getElementById('task-progress-bar').style.width = '0%';
        document.getElementById('task-status').textContent = 'Starting';
        document.getElementById('task-status').className = 'badge bg-starting';
        document.getElementById('task-queries').innerHTML = '<li class="list-group-item text-muted">No queries yet</li>';
        document.getElementById('task-logs').innerHTML = '<p class="text-muted">Waiting for logs...</p>';
        document.getElementById('view-report-btn').classList.add('d-none');
        document.getElementById('follow-up-btn').classList.add('d-none');

        // Show modal
        taskProgressModal.show();

        // Start updating task status
        updateTaskStatus();
        taskUpdateInterval = setInterval(updateTaskStatus, 2000);

        // Clear interval when modal is closed
        document.getElementById('task-progress-modal').addEventListener('hidden.bs.modal', function() {
            clearInterval(taskUpdateInterval);
        });

        // Set up follow-up button handler
        const followUpBtn = document.getElementById('follow-up-btn');
        followUpBtn.addEventListener('click', function() {
            startFollowUpResearch(currentTaskId);
        });
        followUpBtn.classList.add('d-none');
    }

    function updateTaskStatus() {
        if (!currentTaskId) return;

        fetch(`/api/research/${currentTaskId}`)
            .then(response => response.json())
            .then(task => {
                // Update task information
                document.getElementById('task-topic').textContent = task.topic;
                document.getElementById('task-progress-bar').style.width = `${task.progress}%`;
                document.getElementById('task-status').textContent = task.status.charAt(0).toUpperCase() + task.status.slice(1);
                document.getElementById('task-status').className = `badge bg-${task.status}`;

                // Update search queries
                if (task.search_queries && task.search_queries.length > 0) {
                    const queriesList = document.getElementById('task-queries');
                    queriesList.innerHTML = '';

                    task.search_queries.forEach(query => {
                        const li = document.createElement('li');
                        li.className = 'list-group-item';
                        li.textContent = query;
                        queriesList.appendChild(li);
                    });
                }

                // Update logs
                if (task.logs && task.logs.length > 0) {
                    const logsContainer = document.getElementById('task-logs');
                    logsContainer.innerHTML = '';

                    task.logs.forEach(log => {
                        const p = document.createElement('p');
                        p.className = 'mb-1';
                        p.textContent = log;
                        logsContainer.appendChild(p);
                    });

                    // Scroll to bottom
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                }

                // Show report button if completed
                if (task.status === 'completed' && task.report_path) {
                    const viewReportBtn = document.getElementById('view-report-btn');
                    viewReportBtn.classList.remove('d-none');
                    viewReportBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        taskProgressModal.hide();
                        showSection(reportsSection);
                        setActiveNav(navReports);
                        loadReports(task.report_path);
                    });

                    // Show follow-up button if there are follow-up questions
                    if (task.follow_up_questions && task.follow_up_questions.length > 0) {
                        const followUpBtn = document.getElementById('follow-up-btn');
                        followUpBtn.classList.remove('d-none');
                        followUpBtn.textContent = `Run Follow-up Research (${task.follow_up_questions.length} questions)`;
                    }

                    // Stop updating
                    clearInterval(taskUpdateInterval);
                }

                // Stop updating if failed
                if (task.status === 'failed') {
                    clearInterval(taskUpdateInterval);
                }
            })
            .catch(error => {
                console.error('Error updating task status:', error);
                clearInterval(taskUpdateInterval);
            });
    }

    // Load reports
    function loadReports(selectedReportPath = null) {
        const reportsList = document.getElementById('reports-list');
        reportsList.innerHTML = '<div class="text-center p-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        fetch('/api/reports')
            .then(response => response.json())
            .then(reports => {
                reportsList.innerHTML = '';

                if (reports.length === 0) {
                    reportsList.innerHTML = '<p class="text-muted p-3">No reports found.</p>';
                    return;
                }

                reports.forEach(report => {
                    const a = document.createElement('a');
                    a.href = '#';
                    a.className = 'list-group-item list-group-item-action';
                    a.dataset.reportId = report.id;
                    a.dataset.reportPath = report.path;

                    // Format the topic
                    let topic = report.topic;
                    if (topic.length > 40) {
                        topic = topic.substring(0, 37) + '...';
                    }

                    // Format the date
                    const date = new Date(report.created);
                    const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();

                    a.innerHTML = `
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${topic}</h6>
                        </div>
                        <small class="text-muted">${formattedDate}</small>
                    `;

                    a.addEventListener('click', function(e) {
                        e.preventDefault();
                        loadReport(this.dataset.reportId);

                        // Set active report
                        document.querySelectorAll('#reports-list a').forEach(el => {
                            el.classList.remove('active');
                        });
                        this.classList.add('active');
                    });

                    reportsList.appendChild(a);

                    // Select the report if it matches the selected path
                    if (selectedReportPath && report.path === selectedReportPath) {
                        a.click();
                    }
                });

                // Select the first report if none is selected
                if (!selectedReportPath && reports.length > 0) {
                    reportsList.querySelector('a').click();
                }
            })
            .catch(error => {
                console.error('Error loading reports:', error);
                reportsList.innerHTML = '<p class="text-danger p-3">Error loading reports.</p>';
            });
    }

    // Load a specific report
    function loadReport(reportId) {
        const reportTitle = document.getElementById('report-title');
        const reportContent = document.getElementById('report-content');

        reportTitle.textContent = 'Loading...';
        reportContent.innerHTML = '<div class="text-center p-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        fetch(`/api/reports/${reportId}`)
            .then(response => response.json())
            .then(data => {
                if (data.report) {
                    // Extract title from the report (first heading)
                    const titleMatch = data.report.match(/^# (.+)$/m);
                    if (titleMatch) {
                        reportTitle.textContent = titleMatch[1];
                    } else {
                        reportTitle.textContent = 'Research Report';
                    }

                    // Render markdown
                    reportContent.innerHTML = marked.parse(data.report);
                } else {
                    reportTitle.textContent = 'Error';
                    reportContent.innerHTML = '<p class="text-danger">Error loading report: ' + (data.error || 'Unknown error') + '</p>';
                }
            })
            .catch(error => {
                console.error('Error loading report:', error);
                reportTitle.textContent = 'Error';
                reportContent.innerHTML = '<p class="text-danger">Error loading report: ' + error.message + '</p>';
            });
    }

    // Start follow-up research
    function startFollowUpResearch(taskId) {
        if (!taskId) return;

        // Disable the follow-up button
        const followUpBtn = document.getElementById('follow-up-btn');
        followUpBtn.disabled = true;
        followUpBtn.textContent = 'Starting follow-up research...';

        // Send request to start follow-up research
        fetch(`/api/research/${taskId}/follow-up`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.task_id) {
                // Close the current modal
                taskProgressModal.hide();

                // Show the new task progress
                showTaskProgress(data.task_id);

                // Reset the follow-up button
                followUpBtn.disabled = false;
                followUpBtn.classList.add('d-none');
            } else {
                alert('Error starting follow-up research: ' + (data.error || 'Unknown error'));
                followUpBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error starting follow-up research:', error);
            alert('Error starting follow-up research: ' + error.message);
            followUpBtn.disabled = false;
        });
    }

    // Load active tasks
    function loadActiveTasks() {
        const activeTasksContainer = document.getElementById('active-tasks-container');
        activeTasksContainer.innerHTML = '<div class="text-center p-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        // Get active tasks from the server
        fetch('/api/research')
            .then(response => response.json())
            .then(tasks => {
                activeTasksContainer.innerHTML = '';

                if (Object.keys(tasks).length === 0) {
                    activeTasksContainer.innerHTML = '<p class="text-muted">No active research tasks.</p>';
                    return;
                }

                // Create a card for each task
                Object.values(tasks).forEach(task => {
                    const col = document.createElement('div');
                    col.className = 'col-md-4 mb-4';

                    const card = document.createElement('div');
                    card.className = 'card task-card h-100';

                    const cardBody = document.createElement('div');
                    cardBody.className = 'card-body';

                    // Format the topic
                    let topic = task.topic;
                    if (topic.length > 40) {
                        topic = topic.substring(0, 37) + '...';
                    }

                    // Format the status
                    const statusClass = `bg-${task.status}`;
                    const statusText = task.status.charAt(0).toUpperCase() + task.status.slice(1);

                    cardBody.innerHTML = `
                        <h5 class="card-title">${topic}</h5>
                        <div class="mb-2">
                            <span class="badge ${statusClass}">${statusText}</span>
                            <span class="badge bg-secondary">${task.model_provider}</span>
                        </div>
                        <div class="progress mb-3">
                            <div class="progress-bar" role="progressbar" style="width: ${task.progress}%" aria-valuenow="${task.progress}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                        <p class="card-text">
                            <small class="text-muted">Started: ${new Date(task.start_time).toLocaleString()}</small>
                        </p>
                    `;

                    const cardFooter = document.createElement('div');
                    cardFooter.className = 'card-footer';

                    const viewButton = document.createElement('button');
                    viewButton.className = 'btn btn-primary btn-sm';
                    viewButton.textContent = 'View Progress';
                    viewButton.addEventListener('click', function() {
                        showTaskProgress(task.id);
                    });

                    cardFooter.appendChild(viewButton);

                    card.appendChild(cardBody);
                    card.appendChild(cardFooter);
                    col.appendChild(card);
                    activeTasksContainer.appendChild(col);
                });
            })
            .catch(error => {
                console.error('Error loading active tasks:', error);
                activeTasksContainer.innerHTML = '<p class="text-danger">Error loading active tasks: ' + error.message + '</p>';
            });
    }

    // Load models and search providers on page load
    fetch('/api/models')
        .then(response => response.json())
        .then(models => {
            // Populate model provider options
            const modelProvider = document.getElementById('model-provider');
            modelProvider.innerHTML = '';

            Object.keys(models).forEach(provider => {
                const option = document.createElement('option');
                option.value = provider;
                option.textContent = provider.charAt(0).toUpperCase() + provider.slice(1);
                modelProvider.appendChild(option);
            });

            // Populate model name options for the default provider
            const modelName = document.getElementById('model-name');
            modelName.innerHTML = '';

            const defaultProvider = modelProvider.value;
            models[defaultProvider].forEach(model => {
                const option = document.createElement('option');
                option.value = model;

                // Format the model name
                let displayName = model;
                if (model === 'gpt-3.5-turbo') displayName = 'GPT-3.5 Turbo';
                else if (model === 'gpt-4') displayName = 'GPT-4';
                else if (model === 'llama3:7b') displayName = 'Llama 3 (7B)';
                else if (model === 'llama3:8b') displayName = 'Llama 3 (8B)';

                option.textContent = displayName;
                modelName.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading models:', error);
        });

    fetch('/api/search-providers')
        .then(response => response.json())
        .then(providers => {
            // Populate search provider options
            const searchProvider = document.getElementById('search-provider');
            searchProvider.innerHTML = '';

            providers.forEach(provider => {
                const option = document.createElement('option');
                option.value = provider;
                option.textContent = provider.charAt(0).toUpperCase() + provider.slice(1);
                searchProvider.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading search providers:', error);
        });
});
