/**
 * GET /api/executions/history - Proxy to FastAPI execution history endpoint
 *
 * **Purpose:** Server-side proxy that adds JWT authentication from httpOnly cookie
 * **Context:** Phase 08-02 - Strategy Vault
 *
 * **Flow:**
 * 1. Client component (ExecutionList) calls GET /api/executions/history
 * 2. This route handler reads access_token from httpOnly cookie
 * 3. Proxies to FastAPI /api/executions/history with Authorization header
 * 4. Returns paginated execution history
 */

import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET(request: NextRequest) {
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

  // Forward cursor query param for pagination
  const searchParams = request.nextUrl.searchParams
  const cursor = searchParams.get('cursor')
  const params = new URLSearchParams()
  if (cursor) params.append('cursor', cursor)

  const url = `${apiUrl}/api/executions/history?${params.toString()}`

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      cache: 'no-store', // Always fresh — execution history grows
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
