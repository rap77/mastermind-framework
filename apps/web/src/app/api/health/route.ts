/**
 * GET /api/health - Health check proxy to both backend services
 *
 * **Purpose:** Aggregate health status from Python (Agent Runtime) and Rust (Control Plane)
 * **Context:** B3.3 — Health Endpoints
 *
 * **Flow:**
 * 1. Fetches /health from Python FastAPI (AGENT_RUNTIME_URL, default :8001)
 * 2. Fetches /health from Rust Control Plane (CONTROL_PLANE_URL, default :8002)
 * 3. Returns combined status — 200 if both healthy, 503 if either fails
 *
 * **No auth required** — health endpoints are public by design.
 */

import { NextResponse } from 'next/server'

interface ServiceHealth {
  status: string
  [key: string]: unknown
}

interface HealthResponse {
  status: 'ok' | 'degraded'
  services: {
    python: ServiceHealth | { status: 'error'; error: string }
    rust: ServiceHealth | { status: 'error'; error: string }
  }
}

async function fetchServiceHealth(url: string): Promise<ServiceHealth> {
  const response = await fetch(`${url}/health`, {
    cache: 'no-store',
    signal: AbortSignal.timeout(5000),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return response.json() as Promise<ServiceHealth>
}

export async function GET(): Promise<NextResponse<HealthResponse>> {
  const agentRuntimeUrl =
    process.env.AGENT_RUNTIME_URL ?? 'http://localhost:8001'
  const controlPlaneUrl =
    process.env.CONTROL_PLANE_URL ?? 'http://localhost:8002'

  const [pythonResult, rustResult] = await Promise.allSettled([
    fetchServiceHealth(agentRuntimeUrl),
    fetchServiceHealth(controlPlaneUrl),
  ])

  const pythonHealth: ServiceHealth | { status: 'error'; error: string } =
    pythonResult.status === 'fulfilled'
      ? pythonResult.value
      : { status: 'error', error: (pythonResult.reason as Error).message }

  const rustHealth: ServiceHealth | { status: 'error'; error: string } =
    rustResult.status === 'fulfilled'
      ? rustResult.value
      : { status: 'error', error: (rustResult.reason as Error).message }

  const allHealthy =
    pythonResult.status === 'fulfilled' &&
    rustResult.status === 'fulfilled' &&
    pythonHealth.status === 'ok' &&
    rustHealth.status === 'ok'

  const httpStatus = allHealthy ? 200 : 503

  return NextResponse.json(
    {
      status: allHealthy ? 'ok' : 'degraded',
      services: {
        python: pythonHealth,
        rust: rustHealth,
      },
    },
    { status: httpStatus }
  )
}
