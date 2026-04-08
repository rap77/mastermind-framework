import websocket from 'k6/x/websocket';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

// Custom metrics for SLI validation
const replayLatency = new Trend('replay_latency'); // Changed to Trend for actual latency values
const connectionErrors = new Rate('connection_errors');
const traceIdPresence = new Rate('trace_id_presence');

export const options = {
  stages: [
    { duration: '30s', target: 1000 },  // Ramp to 1000 connections
    { duration: '1m', target: 1000 },   // Stay at 1000
    { duration: '30s', target: 0 },     // Ramp down
  ],
  thresholds: {
    'replay_latency': [
      { threshold: 'p(95)<500', abortOnFail: true, delayAbortEval: '30s' }, // SLI-1: P95 < 500ms
    ],
    'connection_errors': [
      { threshold: 'rate<0.01', abortOnFail: false }, // Less than 1% errors
    ],
    'trace_id_presence': [
      { threshold: 'rate>0.99', abortOnFail: false }, // 99%+ have trace_id (SLI-3)
    ],
  },
};

const WS_URL = 'ws://localhost:8080/ws';

export default function() {
  const replayStart = new Date();
  let ws;
  let replayReceived = false;

  try {
    ws = new WebSocket(WS_URL);
    connectionErrors.add(false);

    // Combined handler: check connection + request Ghost Mode replay
    ws.onopen = () => {
      check(ws, { 'status connected': (s) => s.readyState === 1 });
      ws.send(JSON.stringify({ type: 'ghost_replay' }));
    };

    ws.onmessage = (message) => {
      let event;
      try {
        event = JSON.parse(message.data);
      } catch (parseError) {
        console.error('Failed to parse message:', parseError);
        return;
      }

      // Check for trace_id presence only for ghost_replay events (SLI-3)
      if (event.type === 'ghost_replay') {
        if (event.trace_id) {
          traceIdPresence.add(true);
        } else {
          traceIdPresence.add(false);
        }

        // Measure Ghost Mode replay latency (SLI-1)
        const latency = new Date() - replayStart;
        replayLatency.add(latency); // Add actual numeric latency value
        replayReceived = true;
      }
    };

    ws.onerror = (error) => {
      connectionErrors.add(true);
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      if (!replayReceived) {
        connectionErrors.add(true);
      }
    };

    // Keep connection open for 30-60 seconds
    sleep(Math.random() * 30 + 30);

  } catch (error) {
    connectionErrors.add(true);
    console.error('Connection failed:', error);
  } finally {
    if (ws) {
      ws.close();
    }
  }
}
