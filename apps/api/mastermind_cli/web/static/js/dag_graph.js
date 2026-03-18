/**
 * D3.js-based DAG Graph Visualization for MasterMind Framework.
 *
 * Renders dependency graphs with layered layout, state-based coloring,
 * and real-time updates via WebSocket.
 *
 * Requirements: UI-09, PERF-03
 */

/**
 * DAGGraph - Main class for dependency graph visualization.
 *
 * Features:
 * - Layered left-to-right layout by execution level
 * - State-based node coloring (pending, running, completed, failed, cancelled)
 * - Interactive hover, click, zoom, and pan
 * - Real-time state updates
 * - Path highlighting for failed nodes (Ripple Effect)
 *
 * @example
 * const graph = new DAGGraph('#dag-graph', graphData);
 * graph.render();
 * graph.on('nodeClick', (nodeId) => console.log('Clicked:', nodeId));
 */
class DAGGraph {
    /**
     * Initialize DAGGraph instance.
     *
     * @param {string} containerId - CSS selector for container element
     * @param {Object} data - Graph data from API
     * @param {Array} data.nodes - Node array with id, label, level, state
     * @param {Array} data.edges - Edge array with from, to
     */
    constructor(containerId, data) {
        this.containerId = containerId;
        this.data = data;
        this.nodes = data.nodes || [];
        this.edges = data.edges || [];
        this.maxLevel = data.max_level || 0;

        // D3 selections
        this.svg = null;
        this.g = null;
        this.nodeSelection = null;
        this.edgeSelection = null;

        // Layout constants
        this.nodeWidth = 120;
        this.nodeHeight = 50;
        this.levelSpacing = 200;
        this.nodeSpacing = 70;

        // State colors
        this.colors = {
            pending: '#64748B',   // gray
            running: '#3B82F6',   // blue (animated)
            completed: '#10B981', // green
            failed: '#EF4444',    // red (pulsing)
            cancelled: '#F59E0B'  // yellow
        };

        // Event listeners
        this.listeners = {};

        // Zoom behavior
        this.zoom = null;
    }

    /**
     * Calculate node positions based on layered layout.
     * Groups nodes by level and positions them left-to-right.
     *
     * @returns {Map} Map of node ID to {x, y} position
     */
    _calculateLayout() {
        const positions = new Map();

        // Group nodes by level
        const levelGroups = new Map();
        for (const node of this.nodes) {
            if (!levelGroups.has(node.level)) {
                levelGroups.set(node.level, []);
            }
            levelGroups.get(node.level).push(node);
        }

        // Calculate positions
        for (const [level, levelNodes] of levelGroups) {
            const x = level * this.levelSpacing + 100; // Offset from left
            const totalHeight = levelNodes.length * this.nodeSpacing;
            const startY = Math.max(100, (600 - totalHeight) / 2); // Center vertically

            levelNodes.forEach((node, idx) => {
                const y = startY + idx * this.nodeSpacing;
                positions.set(node.id, { x, y });
            });
        }

        return positions;
    }

    /**
     * Render the graph to SVG.
     * Creates SVG element, nodes, edges, and sets up interactions.
     */
    render() {
        const container = document.querySelector(this.containerId);
        if (!container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }

        // Clear existing content
        container.textContent = '';

        // Calculate layout
        const positions = this._calculateLayout();
        this.nodePositions = positions;

        // Create SVG
        const width = Math.max(800, (this.maxLevel + 1) * this.levelSpacing + 200);
        const height = Math.max(500, this.nodes.length * this.nodeSpacing + 200);

        this.svg = d3.select(this.containerId)
            .append('svg')
            .attr('width', '100%')
            .attr('height', height)
            .attr('viewBox', `0 0 ${width} ${height}`)
            .attr('class', 'dag-graph-svg');

        // Create main group for zoom/pan
        this.g = this.svg.append('g')
            .attr('class', 'dag-graph-group');

        // Setup zoom behavior
        this.zoom = d3.zoom()
            .scaleExtent([0.5, 3])
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });

        this.svg.call(this.zoom);

        // Create defs for arrowheads
        const defs = this.svg.append('defs');
        defs.append('marker')
            .attr('id', 'arrowhead')
            .attr('viewBox', '0 0 10 10')
            .attr('refX', 9)
            .attr('refY', 5)
            .attr('markerWidth', 6)
            .attr('markerHeight', 4)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M 0 0 L 10 5 L 0 10 z')
            .attr('fill', '#475569');

        // Create edges
        this.edgeSelection = this.g.append('g')
            .attr('class', 'edges')
            .selectAll('path')
            .data(this.edges)
            .enter()
            .append('path')
            .attr('class', 'edge')
            .attr('id', (d, i) => `edge-${i}`)
            .attr('fill', 'none')
            .attr('stroke', '#475569')
            .attr('stroke-width', 2)
            .attr('marker-end', 'url(#arrowhead)')
            .attr('d', (d) => this._edgePath(d, positions));

        // Create nodes
        this.nodeSelection = this.g.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(this.nodes)
            .enter()
            .append('g')
            .attr('class', 'node')
            .attr('id', (d) => `node-${d.id}`)
            .attr('transform', (d) => {
                const pos = positions.get(d.id);
                return `translate(${pos.x}, ${pos.y})`;
            })
            .on('click', (event, d) => this._handleNodeClick(event, d))
            .on('mouseenter', (event, d) => this._handleNodeHover(event, d))
            .on('mouseleave', () => this._handleNodeLeave());

        // Node rectangles
        this.nodeSelection.append('rect')
            .attr('width', this.nodeWidth)
            .attr('height', this.nodeHeight)
            .attr('x', -this.nodeWidth / 2)
            .attr('y', -this.nodeHeight / 2)
            .attr('rx', 6)
            .attr('class', (d) => `node-rect node-${d.state}`)
            .attr('fill', (d) => this.colors[d.state])
            .attr('stroke', '#1E293B')
            .attr('stroke-width', 2);

        // Node labels
        this.nodeSelection.append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '.35em')
            .attr('fill', 'white')
            .attr('font-size', '12px')
            .attr('font-weight', '500')
            .text((d) => d.label.length > 15 ? d.label.substring(0, 13) + '...' : d.label);
    }

    /**
     * Generate SVG path for edge (curved link).
     *
     * @param {Object} edge - Edge with from and to
     * @param {Map} positions - Node position map
     * @returns {string} SVG path d attribute
     */
    _edgePath(edge, positions) {
        const fromPos = positions.get(edge.from);
        const toPos = positions.get(edge.to);

        if (!fromPos || !toPos) return '';

        const x1 = fromPos.x + this.nodeWidth / 2;
        const y1 = fromPos.y;
        const x2 = toPos.x - this.nodeWidth / 2;
        const y2 = toPos.y;

        // Bezier curve with horizontal control points
        const cx1 = x1 + (x2 - x1) / 2;
        const cy1 = y1;
        const cx2 = x1 + (x2 - x1) / 2;
        const cy2 = y2;

        return `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`;
    }

    /**
     * Update node state with animation.
     *
     * @param {string} nodeId - Node ID to update
     * @param {string} newState - New state (pending, running, completed, failed, cancelled)
     */
    updateNodeState(nodeId, newState) {
        const node = this.nodeSelection.select(`#node-${nodeId} rect`);
        if (node.empty()) return;

        // Remove all state classes
        node.classed('node-pending', false)
            .classed('node-running', false)
            .classed('node-completed', false)
            .classed('node-failed', false)
            .classed('node-cancelled', false);

        // Update color with transition
        node.transition()
            .duration(500)
            .attr('fill', this.colors[newState]);

        // Add new state class
        node.classed(`node-${newState}`, true);

        // Update node data
        const nodeData = this.nodes.find(n => n.id === nodeId);
        if (nodeData) {
            nodeData.state = newState;
        }
    }

    /**
     * Highlight path to/from a node (Ripple Effect).
     * Dims non-ancestor nodes and highlights the path.
     *
     * @param {string} nodeId - Node to highlight path for
     * @param {string} mode - 'ancestors' or 'descendants'
     */
    highlightPath(nodeId, mode = 'ancestors') {
        // Get all ancestors or descendants
        const relatedNodes = this._getRelatedNodes(nodeId, mode);

        // Dim all nodes
        this.nodeSelection.transition()
            .duration(300)
            .style('opacity', 0.3);

        // Highlight related nodes
        relatedNodes.forEach(id => {
            this.nodeSelection.select(`#node-${id}`)
                .transition()
                .duration(300)
                .style('opacity', 1);
        });

        // Highlight edges to/from node
        this.edgeSelection.transition()
            .duration(300)
            .style('opacity', 0.2);

        const relatedEdges = this._getRelatedEdges(nodeId, mode);
        relatedEdges.forEach(edge => {
            this.edgeSelection.filter(d => d.from === edge.from && d.to === edge.to)
                .transition()
                .duration(300)
                .style('opacity', 1)
                .attr('stroke', '#EF4444')
                .attr('stroke-width', 3);
        });
    }

    /**
     * Clear path highlighting.
     */
    clearHighlight() {
        this.nodeSelection.transition()
            .duration(300)
            .style('opacity', 1);

        this.edgeSelection.transition()
            .duration(300)
            .style('opacity', 1)
            .attr('stroke', '#475569')
            .attr('stroke-width', 2);
    }

    /**
     * Get all ancestors or descendants of a node.
     *
     * @param {string} nodeId - Starting node
     * @param {string} mode - 'ancestors' or 'descendants'
     * @returns {Set} Set of related node IDs
     */
    _getRelatedNodes(nodeId, mode) {
        const related = new Set();

        if (mode === 'ancestors') {
            // Find all nodes that lead to this node
            const toVisit = [nodeId];
            while (toVisit.length > 0) {
                const current = toVisit.pop();
                for (const edge of this.edges) {
                    if (edge.to === current && !related.has(edge.from)) {
                        related.add(edge.from);
                        toVisit.push(edge.from);
                    }
                }
            }
        } else {
            // Find all nodes that depend on this node
            const toVisit = [nodeId];
            while (toVisit.length > 0) {
                const current = toVisit.pop();
                for (const edge of this.edges) {
                    if (edge.from === current && !related.has(edge.to)) {
                        related.add(edge.to);
                        toVisit.push(edge.to);
                    }
                }
            }
        }

        return related;
    }

    /**
     * Get all edges related to a node path.
     *
     * @param {string} nodeId - Starting node
     * @param {string} mode - 'ancestors' or 'descendants'
     * @returns {Array} Array of related edges
     */
    _getRelatedEdges(nodeId, mode) {
        const relatedNodes = this._getRelatedNodes(nodeId, mode);
        const relatedEdges = [];

        if (mode === 'ancestors') {
            for (const edge of this.edges) {
                if (edge.to === nodeId || relatedNodes.has(edge.from)) {
                    if (relatedNodes.has(edge.from) || edge.to === nodeId) {
                        relatedEdges.push(edge);
                    }
                }
            }
        }

        return relatedEdges;
    }

    /**
     * Pan and zoom to a specific node.
     *
     * @param {string} nodeId - Node to zoom to
     */
    zoomTo(nodeId) {
        const node = this.nodes.find(n => n.id === nodeId);
        if (!node || !this.nodePositions) return;

        const pos = this.nodePositions.get(nodeId);
        if (!pos) return;

        this.svg.transition()
            .duration(750)
            .call(this.zoom.transform,
                d3.zoomIdentity
                    .translate(400 - pos.x, 250 - pos.y)
                    .scale(1.5)
            );
    }

    /**
     * Register event listener.
     *
     * @param {string} event - Event name ('nodeClick', 'nodeHover')
     * @param {Function} callback - Callback function
     */
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    /**
     * Handle node click event.
     */
    _handleNodeClick(event, d) {
        this.zoomTo(d.id);
        if (this.listeners['nodeClick']) {
            this.listeners['nodeClick'].forEach(cb => cb(d.id, d));
        }
    }

    /**
     * Handle node hover event.
     */
    _handleNodeHover(event, d) {
        this.highlightPath(d.id, 'ancestors');
        if (this.listeners['nodeHover']) {
            this.listeners['nodeHover'].forEach(cb => cb(d.id, d));
        }
    }

    /**
     * Handle node mouse leave.
     */
    _handleNodeLeave() {
        this.clearHighlight();
    }

    /**
     * Destroy the graph and clean up.
     */
    destroy() {
        if (this.svg) {
            this.svg.remove();
            this.svg = null;
        }
        this.listeners = {};
    }
}

// Export for use in dashboard
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DAGGraph };
}
