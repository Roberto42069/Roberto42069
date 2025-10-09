// Integrations Management JavaScript
let spotifyMonitorInterval = null;

// Initialize integrations on page load
document.addEventListener('DOMContentLoaded', function() {
    checkIntegrationStatus();
    startSpotifyMonitoring();
});

// Check status of all integrations
async function checkIntegrationStatus() {
    try {
        const response = await fetch('/api/integrations/status');
        const data = await response.json();
        
        if (data.success) {
            // Update UI based on connection status
            updateIntegrationBadge('spotify-status', data.integrations.spotify.connected);
            updateIntegrationBadge('github-status', data.integrations.github.connected);
            updateIntegrationBadge('youtube-status', data.integrations.youtube.connected);
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

// Spotify Real-time Monitoring
function startSpotifyMonitoring() {
    // Check immediately
    updateSpotifyNowPlaying();
    
    // Then check every 10 seconds
    spotifyMonitorInterval = setInterval(updateSpotifyNowPlaying, 10000);
}

function stopSpotifyMonitoring() {
    if (spotifyMonitorInterval) {
        clearInterval(spotifyMonitorInterval);
        spotifyMonitorInterval = null;
    }
}

async function updateSpotifyNowPlaying() {
    try {
        const response = await fetch('/api/spotify/current');
        const data = await response.json();
        
        const container = document.getElementById('spotify-now-playing');
        if (!container) return;
        
        if (data.success && data.data && data.data.item) {
            const track = data.data.item;
            const artists = track.artists.map(a => a.name).join(', ');
            const isPlaying = data.data.is_playing;
            
            container.innerHTML = `
                <div class="${isPlaying ? 'text-success' : 'text-muted'}">
                    <i class="fas ${isPlaying ? 'fa-play' : 'fa-pause'} me-1"></i>
                    ${isPlaying ? 'Now Playing' : 'Paused'}
                </div>
                <div class="fw-bold text-truncate">${track.name}</div>
                <div class="small text-muted text-truncate">${artists}</div>
                <div class="small text-muted">${track.album.name}</div>
            `;
        } else if (data.data && data.data.error && data.data.error.status === 204) {
            container.innerHTML = '<div class="text-muted small">No active playback</div>';
        } else {
            container.innerHTML = '<div class="text-muted small">Checking playback...</div>';
        }
    } catch (error) {
        console.error('Spotify playback check failed:', error);
    }
}

async function spotifyRefresh() {
    await updateSpotifyNowPlaying();
    
    // Also get recent tracks
    try {
        const response = await fetch('/api/spotify/recent?limit=10');
        const data = await response.json();
        
        if (data.success && data.data && data.data.items) {
            console.log('Recently played:', data.data.items);
            // Store listening history in database
        }
    } catch (error) {
        console.error('Recent tracks fetch failed:', error);
    }
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

// YouTube Integration Functions
async function viewYouTubeChannel() {
    try {
        const response = await fetch('/api/youtube/channel');
        const data = await response.json();
        
        if (data.success && data.data && data.data.items && data.data.items.length > 0) {
            const channel = data.data.items[0];
            const stats = channel.statistics;
            const snippet = channel.snippet;
            
            const channelInfo = `
YouTube Channel: ${snippet.title}
Subscribers: ${parseInt(stats.subscriberCount).toLocaleString()}
Total Views: ${parseInt(stats.viewCount).toLocaleString()}
Videos: ${stats.videoCount}
            `;
            
            addBotMessage(channelInfo);
        }
    } catch (error) {
        console.error('YouTube channel fetch failed:', error);
        addBotMessage('Failed to fetch YouTube channel information.');
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

// Spotify Playlist Management (called from chat commands)
async function createSpotifyPlaylist(name, description = '') {
    try {
        const response = await fetch('/api/spotify/playlist/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, description, public: true})
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Playlist creation failed:', error);
        return {success: false, error: error.message};
    }
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

// Stop monitoring when page is unloaded
window.addEventListener('beforeunload', function() {
    stopSpotifyMonitoring();
});

// Export functions for global access
window.spotifyRefresh = spotifyRefresh;
window.viewGitHubRepos = viewGitHubRepos;
window.viewYouTubeChannel = viewYouTubeChannel;
window.createSpotifyPlaylist = createSpotifyPlaylist;
window.createGitHubRepo = createGitHubRepo;
