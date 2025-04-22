// Main JavaScript for the Jira to GPT-4o to Beautiful AI Integration

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle form submissions with AJAX
    const pipelineForm = document.getElementById('pipeline-form');
    if (pipelineForm) {
        pipelineForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading indicator
            const submitButton = pipelineForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.innerHTML = '<span class="loading-spinner"></span> Running...';
            submitButton.disabled = true;
            
            // Submit form with AJAX
            fetch(pipelineForm.action, {
                method: 'POST',
                body: new FormData(pipelineForm),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showAlert('success', 'Pipeline executed successfully!');
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    showAlert('danger', 'Pipeline execution failed: ' + data.message);
                }
            })
            .catch(error => {
                showAlert('danger', 'An error occurred: ' + error);
            })
            .finally(() => {
                // Restore button state
                submitButton.innerHTML = originalButtonText;
                submitButton.disabled = false;
            });
        });
    }

    // Settings form validation
    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            const jiraUrl = document.getElementById('jira_url').value;
            const jiraUsername = document.getElementById('jira_username').value;
            const jiraApiToken = document.getElementById('jira_api_token').value;
            const openaiApiKey = document.getElementById('openai_api_key').value;

            if (!jiraUrl || !jiraUsername || !jiraApiToken || !openaiApiKey) {
                e.preventDefault();
                showAlert('danger', 'Please fill in all required fields');
            }
        });
    }

    // Update status periodically on dashboard
    const statusContainer = document.getElementById('status-container');
    if (statusContainer) {
        // Update status every 30 seconds
        setInterval(updateStatus, 30000);
    }

    // Function to update status via AJAX
    function updateStatus() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                // Update UI components based on status
                if (data.status === 'ok') {
                    updateStatusIndicators(data);
                }
            })
            .catch(error => {
                console.error('Error updating status:', error);
            });
    }

    // Function to update status indicators
    function updateStatusIndicators(data) {
        // Update components based on data
        // This would be implemented based on the actual API response structure
    }

    // Function to show alerts
    function showAlert(type, message) {
        const alertsContainer = document.getElementById('alerts-container');
        if (alertsContainer) {
            const alert = document.createElement('div');
            alert.className = `alert alert-${type} alert-dismissible fade show`;
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            alertsContainer.appendChild(alert);

            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => {
                    alertsContainer.removeChild(alert);
                }, 150);
            }, 5000);
        }
    }

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-to-clipboard');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-clipboard-text');
            navigator.clipboard.writeText(textToCopy)
                .then(() => {
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Could not copy text: ', err);
                });
        });
    });
});
