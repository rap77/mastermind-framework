/**
 * GET /api/executions/[id] - Proxy to FastAPI execution detail endpoint
 *
 * **Purpose:** Server-side proxy that adds JWT authentication from httpOnly cookie
 * **Context:** Phase 08-02 - Strategy Vault
 *
 * **Flow:**
 * 1. Client component (ExecutionDetail) calls GET /api/executions/{id}
 * 2. This route handler reads access_token from httpOnly cookie
 * 3. Proxies to FastAPI /api/executions/{id} with Authorization header
 * 4. Returns execution detail with graph_snapshot + brain_outputs
 */

import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> } // CRITICAL: Promise in Next.js 16
) {
  // CRITICAL: await params — required in Next.js 16
  const { id } = await params

  const apiUrl = process.env.API_URL || 'http://localhost:8001'

  // CRITICAL: Get JWT token from httpOnly cookie
  const cookieStore = await cookies() // CRITICAL: await in Next.js 16
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    return NextResponse.json(
      { error: 'Unauthorized — No token found' },
      { status: 401 }
    )
  }

  const url = `${apiUrl}/api/executions/${id}`

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}))
      return NextResponse.json(errorBody, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error'
    return NextResponse.json(
      { error: `Proxy error: ${message}` },
      { status: 502 }
    )
  }
}
