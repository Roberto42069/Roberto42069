// Service Worker for background functionality
self.addEventListener('install', function(event) {
    console.log('Service Worker installing');
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    console.log('Service Worker activating');
    event.waitUntil(self.clients.claim());
});

// Handle background sync for messages
self.addEventListener('sync', function(event) {
    if (event.tag === 'background-chat') {
        event.waitUntil(handleBackgroundChat());
    }
});

// Keep connection alive in background
self.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'KEEP_ALIVE') {
        // Respond to keep connection active
        event.ports[0].postMessage({ type: 'ALIVE' });
    }
});

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