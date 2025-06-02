// Service Worker for background functionality with continuous voice recognition
let backgroundVoiceActive = false;
let recognition = null;

self.addEventListener('install', function(event) {
    console.log('Service Worker installing with voice capabilities');
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    console.log('Service Worker activating with background voice');
    event.waitUntil(self.clients.claim());
    
    // Initialize background voice recognition
    initializeBackgroundVoice();
});

function initializeBackgroundVoice() {
    // This will be managed by the main app but kept alive by service worker
    console.log('Background voice recognition initialized');
}

// Handle background sync for messages
self.addEventListener('sync', function(event) {
    if (event.tag === 'background-chat') {
        event.waitUntil(handleBackgroundChat());
    }
});

// Handle audio focus for background operation
self.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'AUDIO_FOCUS') {
        // Maintain audio session in background
        event.waitUntil(maintainAudioSession());
    }
});

async function maintainAudioSession() {
    // Keep audio session alive for voice recognition
    console.log('Maintaining audio session in background');
}

// Keep connection alive in background
self.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'KEEP_ALIVE') {
        // Respond to keep connection active
        event.ports[0].postMessage({ type: 'ALIVE' });
    }
    
    if (event.data && event.data.type === 'VOICE_ACTIVE') {
        backgroundVoiceActive = event.data.active;
        console.log('Background voice recognition:', backgroundVoiceActive ? 'enabled' : 'disabled');
        
        if (backgroundVoiceActive) {
            // Keep service worker alive for voice recognition
            maintainVoiceSession();
        }
    }
});

async function maintainVoiceSession() {
    // Prevent service worker from being terminated during voice recognition
    setInterval(() => {
        if (backgroundVoiceActive) {
            console.log('Maintaining voice session in background');
            
            // Notify main app to keep voice recognition alive
            self.clients.matchAll().then(clients => {
                clients.forEach(client => {
                    client.postMessage({ 
                        type: 'KEEP_VOICE_ALIVE',
                        timestamp: Date.now()
                    });
                });
            });
        }
    }, 10000); // Every 10 seconds
}

// Handle background chat processing
async function handleBackgroundChat() {
    try {
        // Process any queued messages when app comes back online
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({ type: 'PROCESS_QUEUE' });
        });
    } catch (error) {
        console.error('Background chat error:', error);
    }
}

// Keep service worker alive
setInterval(() => {
    console.log('Service Worker heartbeat');
}, 30000);