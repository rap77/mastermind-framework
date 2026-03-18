/** Dashboard UI logic with Alpine.js.
 *
 * Handles task management, export functionality, and UI state.
 *
 * Requirements: UI-06, UI-10
 */

function dashboard() {
    return {
        authenticated: false,
        username: '',
        tasks: [],
        metrics: { totalTasks: 0, running: 0, completed: 0 },
        logs: [],
        logsCollapsed: false,
        loginError: '',
        taskError: '',

        // Graph state
        currentGraph: null,
        activeTaskId: null,

        async init() {
            // Check auth status
            const token = localStorage.getItem('access_token');
            if (token) {
                this.authenticated = true;
                const user = JSON.parse(localStorage.getItem('user') || '{}');
                this.username = user.id || 'User';
                await this.loadTasks();
            }
        },

        async login(event) {
            event.preventDefault();
            const form = event.target;
            const username = form.username.value;
            const password = form.password.value;

            try {
                await authStore().login(username, password);
                this.authenticated = true;
                this.username = username;
                this.loginError = '';
                await this.loadTasks();
            } catch (error) {
                this.loginError = 'Invalid username or password';
            }
        },

        logout() {
            authStore().logout();
            this.authenticated = false;
            window.location.reload();
        },

        async loadTasks() {
            try {
                const response = await fetch('/api/tasks', {
                    headers: authStore().getAuthHeaders()
                });

                if (!response.ok) throw new Error('Failed to load tasks');

                const data = await response.json();
                this.tasks = data.tasks;
                this.updateMetrics(data.tasks);
            } catch (error) {
                console.error('Failed to load tasks:', error);
            }
        },

        updateMetrics(tasks) {
            this.metrics.totalTasks = tasks.length;
            this.metrics.running = tasks.filter(t => t.status === 'running').length;
            this.metrics.completed = tasks.filter(t => t.status === 'completed').length;
        },

        async createTask(event) {
            event.preventDefault();
            const form = event.target;
            const brief = form.brief.value;
            const flow = form.flow.value;
            const maxIterations = parseInt(form.max_iterations.value);

            try {
                const response = await fetch('/api/tasks', {
                    method: 'POST',
                    headers: {
                        ...authStore().getAuthHeaders(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        brief,
                        flow: flow || null,
                        max_iterations: maxIterations
                    })
                });

                if (!response.ok) throw new Error('Failed to create task');

                const data = await response.json();
                this.tasks.unshift({
                    id: data.task_id,
                    brief,
                    status: data.status,
                    created_at: data.created_at
                });

                this.taskError = '';
                form.reset();
                this.updateMetrics(this.tasks);

                // TODO: Connect WebSocket for real-time updates
            } catch (error) {
                this.taskError = 'Failed to create task';
                console.error(error);
            }
        },

        async cancelTask(taskId) {
            try {
                const response = await fetch(`/api/tasks/${taskId}`, {
                    method: 'DELETE',
                    headers: authStore().getAuthHeaders()
                });

                if (!response.ok) throw new Error('Failed to cancel task');

                const task = this.tasks.find(t => t.id === taskId);
                if (task) {
                    task.status = 'cancelled';
                    this.updateMetrics(this.tasks);
                }

                this.addLog('info', `Task ${taskId} cancelled`);
            } catch (error) {
                console.error('Failed to cancel task:', error);
            }
        },

        async exportTask(taskId, format) {
            try {
                const response = await fetch(`/api/tasks/${taskId}`, {
                    headers: authStore().getAuthHeaders()
                });

                if (!response.ok) throw new Error('Failed to fetch task');

                const task = await response.json();
                let content, filename, mimeType;

                switch (format) {
                    case 'json':
                        content = JSON.stringify(task, null, 2);
                        filename = `task-${taskId}-${Date.now()}.json`;
                        mimeType = 'application/json';
                        break;

                    case 'yaml':
                        if (typeof jsyaml === 'undefined') {
                            throw new Error('js-yaml library not loaded');
                        }
                        content = jsyaml.dump(task, {
                            indent: 2,
                            lineWidth: -1,
                            sortKeys: false
                        });
                        filename = `task-${taskId}-${Date.now()}.yaml`;
                        mimeType = 'text/yaml';
                        break;

                    case 'markdown':
                        content = this._renderMarkdown(task);
                        filename = `task-${taskId}-${Date.now()}.md`;
                        mimeType = 'text/markdown';
                        break;

                    default:
                        throw new Error(`Unsupported export format: ${format}`);
                }

                // Trigger browser download
                const blob = new Blob([content], { type: mimeType });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);

                this.addLog('success', `Exported task ${taskId} as ${format.toUpperCase()}`);
            } catch (error) {
                console.error('Export failed:', error);
                this.addLog('error', `Failed to export task ${taskId}: ${error.message}`);
            }
        },

        _renderMarkdown(task) {
            let md = `# Task Result\n\n`;
            md += `**Task ID:** ${task.id || 'N/A'}\n\n`;
            md += `**Status:** ${task.status || 'N/A'}\n\n`;
            md += `**Created:** ${task.created_at ? new Date(task.created_at).toLocaleString() : 'N/A'}\n\n`;

            if (task.brief) {
                md += `## Brief\n\n${task.brief}\n\n`;
            }

            if (task.flow_config) {
                md += `## Flow Config\n\n\`\`\njson\n${task.flow_config}\n\`\`\n\n`;
            }

            if (task.error) {
                md += `## Error\n\n\`\`\n${task.error}\n\`\`\n\n`;
            }

            return md;
        },

        addLog(level, message) {
            this.logs.unshift({
                id: Date.now() + Math.random(),
                level,
                message
            });
            if (this.logs.length > 100) {
                this.logs.pop();
            }
        }
    };
}

// Initialize dashboard
document.addEventListener('alpine:init', () => {
    Alpine.data('dashboard', dashboard);
});
