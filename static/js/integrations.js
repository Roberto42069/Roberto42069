// Integrations Management JavaScript

// Initialize integrations on page load
document.addEventListener('DOMContentLoaded', function() {
    checkIntegrationStatus();
});

// Check status of all integrations
async function checkIntegrationStatus() {
    try {
        const response = await fetch('/api/integrations/status');
        if (!response.ok) {
            console.warn('Integration status check returned non-OK status:', response.status);
            return;
        }

        const data = await response.json();

        if (data.success && data.integrations) {
            updateIntegrationUI(data.integrations);
        } else {
            console.warn('Integration status response missing data:', data);
        }
    } catch (error) {
        console.error('Integration status check failed:', error);
    }
}

function updateIntegrationBadge(elementId, connected) {
    const badge = document.getElementById(elementId);
    if (badge) {
        badge.textContent = connected ? 'Connected' : 'Setup Required';
        badge.className = connected ? 'badge bg-success ms-2' : 'badge bg-warning ms-2';
    }
}

// Helper function to update the UI for all integrations
function updateIntegrationUI(integrations) {
    updateIntegrationBadge('github-status', integrations.github.connected);
}

// GitHub Integration Functions
async function viewGitHubRepos() {
    try {
        const response = await fetch('/api/github/repos');
        const data = await response.json();

        if (data.success && data.data) {
            const repos = data.data;
            const repoList = repos.map(repo => `
                <div class="border-bottom pb-2 mb-2">
                    <div class="fw-bold">${repo.name}</div>
                    <div class="small text-muted">${repo.description || 'No description'}</div>
                    <div class="small">
                        <span class="badge bg-secondary">${repo.language || 'N/A'}</span>
                        <i class="fas fa-star ms-2"></i> ${repo.stargazers_count}
                    </div>
                </div>
            `).join('');

            // Display in chat or show modal
            addBotMessage(`GitHub Repositories:\n\n${repoList}`);
        }
    } catch (error) {
        console.error('GitHub repos fetch failed:', error);
        addBotMessage('Failed to fetch GitHub repositories.');
    }
}

// Helper function to add messages to chat
function addBotMessage(message) {
    const chatHistory = document.getElementById('chat-history');
    if (!chatHistory) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'mb-3 p-3 border rounded bg-secondary';
    messageDiv.innerHTML = `
        <div class="d-flex align-items-start">
            <div class="me-3">
                <i class="fas fa-robot text-info" style="font-size: 1.5em;"></i>
            </div>
            <div class="flex-grow-1">
                <p class="mb-0 small">${message.replace(/\n/g, '<br>')}</p>
            </div>
        </div>
    `;

    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// GitHub Repo Management (called from chat commands)
async function createGitHubRepo(name, description = '', isPrivate = false) {
    try {
        const response = await fetch('/api/github/repo/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, description, private: isPrivate, auto_init: true})
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Repo creation failed:', error);
        return {success: false, error: error.message};
    }
}

// Integration status check with better error handling
async function checkIntegrationStatus() {
    try {
        const response = await fetch('/api/integrations/status');
        if (!response.ok) {
            console.warn('Integration status check returned non-OK status:', response.status);
            return;
        }
        const data = await response.json();
        if (data.success) {
            console.log('✅ Integrations status:', data.integrations);
            return data.integrations;
        } else {
            console.warn('Integration status check failed:', data.error);
            return null;
        }
    } catch (error) {
        console.error('Integration status check failed:', error);
        return null;
    }
}

// Export functions for global access
window.viewGitHubRepos = viewGitHubRepos;
window.createGitHubRepo = createGitHubRepo;
