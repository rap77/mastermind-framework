/** WebSocket client for real-time progress updates.
 *
 * Manages WebSocket connection with Ghost Mode reconnection and adaptive polling fallback.
 *
 * Requirements: UI-04, PAR-08
 */

class WebSocketManager {
    constructor() {
        this.ws = null;
        this.taskId = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1s
        this.listeners = {};
        this.pollingInterval = null;
        this.usingPolling = false;
    }

    connect(taskId, token) {
        this.taskId = taskId;
        const wsUrl = `ws://localhost:8000/ws/tasks/${taskId}?token=${token}`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;
                this.usingPolling = false;
                this.emit('connected');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.emit(data.type, data);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.emit('disconnected');

                // Try to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    setTimeout(() => {
                        this.reconnectAttempts++;
                        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 16000);
                        this.connect(this.taskId, token);
                    }, this.reconnectDelay);
                } else {
                    // Fall back to polling
                    this.startPolling(taskId, token);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.startPolling(taskId, token);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.stopPolling();
    }

    startPolling(taskId, token) {
        if (this.usingPolling) return;

        console.log('Falling back to polling');
        this.usingPolling = true;
        this.poll(taskId, token);
    }

    async poll(taskId, token) {
        if (!this.usingPolling) return;

        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const task = await response.json();
                this.emit('task_update', { task_id: taskId, status: task.status });
            }

            // Poll more frequently when active, less when idle
            const delay = task.status === 'running' ? 2000 : 10000;
            this.pollingInterval = setTimeout(() => {
                this.poll(taskId, token);
            }, delay);

        } catch (error) {
            console.error('Polling error:', error);
            this.pollingInterval = setTimeout(() => {
                this.poll(taskId, token);
            }, 5000);
        }
    }

    stopPolling() {
        if (this.pollingInterval) {
            clearTimeout(this.pollingInterval);
            this.pollingInterval = null;
        }
        this.usingPolling = false;
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => {
                callback(data);
            });
        }
    }
}

// Global WebSocket manager instance
const wsManager = new WebSocketManager();

// Integrate with Alpine.js dashboard
document.addEventListener('alpine:init', () => {
    Alpine.effect(() => {
        const dashboard = Alpine.store('dashboard');
        if (!dashboard) return;

        // Listen for task updates
        wsManager.on('task_update_batch', (data) => {
            // Update tasks in dashboard
            data.data.forEach(update => {
                const task = dashboard.tasks.find(t => t.id === update.task_id);
                if (task) {
                    task.status = update.status;
                    dashboard.updateMetrics(dashboard.tasks);
                    dashboard.addLog('info', `Task ${update.task_id}: ${update.status}`);
                }
            });
        });

        wsManager.on('task_complete', (data) => {
            const task = dashboard.tasks.find(t => t.id === data.task_id);
            if (task) {
                task.status = 'completed';
                dashboard.updateMetrics(dashboard.tasks);
                dashboard.addLog('success', `Task ${data.task_id} completed successfully`);
            }
        });

        wsManager.on('task_failed', (data) => {
            const task = dashboard.tasks.find(t => t.id === data.task_id);
            if (task) {
                task.status = 'failed';
                dashboard.updateMetrics(dashboard.tasks);
                dashboard.addLog('error', `Task ${data.task_id} failed: ${data.error || 'Unknown error'}`);
            }
        });
    });
});
