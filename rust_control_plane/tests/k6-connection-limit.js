import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics for SLI-4 validation
const connection429Rate = new Rate('connection_429');

export const options = {
  stages: [
    { duration: '10s', target: 2000 },  // Ramp to max_connections (2000)
    { duration: '5s', target: 2100 },   // Try to exceed limit (SLI-4: expect 429)
    { duration: '5s', target: 0 },      // Ramp down
  ],
  thresholds: {
    'connection_429': [
      { threshold: 'rate>0.05', abortOnFail: false }, // At least 5% should be rejected after 2000
    ],
  },
};

const WS_URL = 'http://localhost:8080/ws'; // Use HTTP for WebSocket upgrade test

export default function() {
  // Try to upgrade HTTP connection to WebSocket
  // This will fail with HTTP 429 if max_connections exceeded
  const response = http.get(WS_URL, {
    headers: {
      'Upgrade': 'websocket',
      'Connection': 'Upgrade',
    },
  });

  const is429 = response.status === 429;

  if (is429) {
    connection429Rate.add(true);
    console.log(`Connection correctly rejected with HTTP ${response.status}`);
  } else {
    connection429Rate.add(false);
    if (response.status !== 426) { // 426 = Upgrade Required (expected for valid WebSocket)
      console.log(`Connection status: ${response.status}`);
    }
  }

  // Brief pause
  sleep(0.1);
}
