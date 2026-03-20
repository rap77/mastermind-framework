/**
 * WebSocket SLIs/SLOs for Command Center
 *
 * **Purpose:** Track WebSocket health and performance
 * **Context:** Phase 06-02 - Command Center Bento Grid
 *
 * **Production Integration:**
 * - Export metrics to Prometheus/Datadog for monitoring
 * - Set up alerts for SLO violations
 * - Use these metrics for capacity planning
 */

/**
 * WebSocket Service Level Indicators (SLIs)
 *
 * These are the measurable metrics we track to assess WebSocket performance.
 */
export interface WebSocketSLIs {
  /**
   * Connection Success Rate
   *
   * Percentage of WebSocket connection attempts that succeed.
   *
   * **Target:** > 99% (SLO)
   * **Measurement:** (successful_connections / total_connection_attempts) * 100
   *
   * **Why:** Users cannot receive real-time updates if connections fail.
   * High failure rate indicates network issues, server overload, or auth problems.
   */
  connection_success_rate: number;

  /**
   * Message Latency (p99)
   *
   * Time from server sending message to client receiving it (99th percentile).
   *
   * **Target:** < 200ms (SLO)
   * **Measurement:** Timestamp difference between server send and client receive
   *
   * **Why:** High latency causes noticeable lag in status updates.
   * Users expect real-time feedback (< 200ms feels instant).
   */
  message_latency_p99: number;

  /**
   * Reconnection Rate
   *
   * Number of WebSocket reconnections per minute.
   *
   * **Target:** < 0.1/min (SLO)
   * **Measurement:** Count reconnection events in 1-minute windows
   *
   * **Why:** Frequent reconnections indicate unstable connections or server issues.
   * Each reconnection causes brief interruption in real-time updates.
   */
  reconnection_rate: number;
}

/**
 * WebSocket Service Level Objectives (SLOs)
 *
 * These are the target values we commit to for each SLI.
 */
export const WS_SLOS: WebSocketSLIs = {
  connection_success_rate: 0.99, // 99% success rate
  message_latency_p99: 200, // 200ms p99 latency
  reconnection_rate: 0.1, // < 0.1 reconnections per minute
};

/**
 * Metric Collection Helpers
 *
 * Use these functions to track metrics in production.
 * **Note:** For v2.1, we document the structure. Actual monitoring integration is deferred to v2.2.
 */

/**
 * Record a WebSocket connection attempt
 *
 * @param success - Whether the connection succeeded
 *
 * **Production Usage:**
 * ```typescript
 * import { recordConnectionAttempt } from '@/lib/websocket-metrics';
 *
 * ws.addEventListener('open', () => recordConnectionAttempt(true));
 * ws.addEventListener('error', () => recordConnectionAttempt(false));
 * ```
 */
export function recordConnectionAttempt(success: boolean): void {
  // TODO: Send to monitoring system (Prometheus/Datadog)
  console.log(`[WebSocket Metrics] Connection attempt: ${success ? 'SUCCESS' : 'FAILURE'}`);
}

/**
 * Record message latency
 *
 * @param latencyMs - Latency in milliseconds
 *
 * **Production Usage:**
 * ```typescript
 * import { recordMessageLatency } from '@/lib/websocket-metrics';
 *
 * ws.addEventListener('message', (event) => {
 *   const serverTimestamp = JSON.parse(event.data).timestamp;
 *   const latency = Date.now() - serverTimestamp;
 *   recordMessageLatency(latency);
 * });
 * ```
 */
export function recordMessageLatency(latencyMs: number): void {
  // TODO: Send to monitoring system (Prometheus/Datadog)
  if (latencyMs > WS_SLOS.message_latency_p99) {
    console.warn(`[WebSocket Metrics] High latency: ${latencyMs}ms (SLO: ${WS_SLOS.message_latency_p99}ms)`);
  }
}

/**
 * Record a reconnection event
 *
 * **Production Usage:**
 * ```typescript
 * import { recordReconnection } from '@/lib/websocket-metrics';
 *
 * function reconnect() {
 *   recordReconnection();
 *   ws = new WebSocket(url);
 * }
 * ```
 */
export function recordReconnection(): void {
  // TODO: Send to monitoring system (Prometheus/Datadog)
  console.log('[WebSocket Metrics] Reconnection event');
}

/**
 * SLO Validation Helper
 *
 * Check if current metrics meet SLOs.
 *
 * @returns Object indicating which SLOs are met/violated
 *
 * **Example:**
 * ```typescript
 * const currentMetrics: WebSocketSLIs = {
 *   connection_success_rate: 0.985,
 *   message_latency_p99: 180,
 *   reconnection_rate: 0.05
 * };
 *
 * const validation = validateSLOs(currentMetrics);
 * // { met: ['connection_success_rate', 'message_latency_p99', 'reconnection_rate'], violated: [] }
 * ```
 */
export function validateSLOs(current: WebSocketSLIs): {
  met: string[];
  violated: string[];
} {
  const met: string[] = [];
  const violated: string[] = [];

  if (current.connection_success_rate >= WS_SLOS.connection_success_rate) {
    met.push('connection_success_rate');
  } else {
    violated.push('connection_success_rate');
  }

  if (current.message_latency_p99 <= WS_SLOS.message_latency_p99) {
    met.push('message_latency_p99');
  } else {
    violated.push('message_latency_p99');
  }

  if (current.reconnection_rate <= WS_SLOS.reconnection_rate) {
    met.push('reconnection_rate');
  } else {
    violated.push('reconnection_rate');
  }

  return { met, violated };
}

/**
 * Phase 06-02 Notes
 *
 * **Current Implementation:**
 * - We define SLIs/SLOs here for documentation and future monitoring
 * - No actual metrics collection in v2.1 (deferred to v2.2)
 * - Manual validation via browser DevTools for now
 *
 * **Next Steps (v2.2):**
 * - Integrate with monitoring system (Prometheus/Datadog)
 * - Set up alerts for SLO violations
 * - Build metrics dashboard for operations team
 *
 * **Verification (Phase 06-02):**
 * - Manual check: Open DevTools → Network → WS tab
 * - Verify connection succeeds (no errors in Console)
 * - Check message timestamps for latency (should be < 200ms)
 * - Monitor reconnection events (should be rare)
 */
