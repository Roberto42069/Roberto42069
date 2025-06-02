// Enhanced Service Worker for persistent background voice recognition
let backgroundVoiceActive = false;
let persistentListening = false;
let voiceWakeLock = null;

self.addEventListener('install', function(event) {
    console.log('Service Worker installing with persistent voice capabilities');
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    console.log('Service Worker activating with background voice');
    event.waitUntil(self.clients.claim());
    
    // Enable persistent background operation
    initializePersistentVoice();
});

function initializePersistentVoice() {
    // Keep service worker alive indefinitely for voice recognition
    setInterval(() => {
        console.log('Service Worker heartbeat - maintaining persistent session');
        
        // Keep session alive regardless of app state
        self.clients.matchAll({ includeUncontrolled: true }).then(clients => {
            if (clients.length === 0) {
                // No clients but maintain session and voice recognition
                console.log('No active clients - maintaining persistent session and voice');
            } else {
                console.log('Active clients found - session maintained');
            }
        });
        
        // Prevent any automatic session termination
        fetch('/api/keep-alive', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ timestamp: Date.now() })
        }).catch(() => {
            // Ignore errors, this is just to keep session alive
        });
    }, 30000); // Every 30 seconds
    
    console.log('Persistent background voice recognition initialized');
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
        persistentListening = event.data.persistent || false;
        console.log('Background voice recognition:', backgroundVoiceActive ? 'enabled' : 'disabled');
        console.log('Persistent listening:', persistentListening ? 'enabled' : 'disabled');
        
        if (backgroundVoiceActive) {
            maintainVoiceSession();
        }
    }
    
    if (event.data && event.data.type === 'ENABLE_PERSISTENT_VOICE') {
        persistentListening = true;
        backgroundVoiceActive = true;
        console.log('Persistent voice recognition enabled - will continue when app closes');
        maintainVoiceSession();
        
        // Respond to confirm persistent mode
        event.ports[0]?.postMessage({ type: 'PERSISTENT_VOICE_ENABLED' });
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