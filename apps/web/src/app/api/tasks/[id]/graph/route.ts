/**
 * GET /api/tasks/[id]/graph - Proxy to FastAPI task graph endpoint
 *
 * **Purpose:** Server-side proxy for task execution graph (BE-02)
 * **Context:** Phase 08 - Strategy Vault / The Nexus DAG visualization
 *
 * **Flow:**
 * 1. Client calls GET /api/tasks/task-abc/graph
 * 2. This route reads access_token from httpOnly cookie
 * 3. Proxies to FastAPI GET /api/tasks/{id}/graph
 * 4. Returns TaskGraphResponse (nodes, edges, optional subgraph)
 *
 * **Response shape:** TaskGraphResponse — React Flow compatible nodes/edges
 * plus optional Phase 08 niche-clustered subgraph.
 */

import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const apiUrl = process.env.API_URL || 'http://localhost:8001'
  const { id: taskId } = await params  // CRITICAL: await params in Next.js 16

  const cookieStore = await cookies()  // CRITICAL: await in Next.js 16
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    return NextResponse.json(
      { error: 'Unauthorized - No token found' },
      { status: 401 }
    )
  }

  const url = `${apiUrl}/api/tasks/${taskId}/graph`

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: `Task not found: ${taskId}` },
          { status: 404 }
        )
      }
      if (response.status === 401) {
        return NextResponse.json(
          { error: 'Unauthorized - Invalid token' },
          { status: 401 }
        )
      }
      return NextResponse.json(
        { error: `Backend error: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Task graph proxy error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch task graph from backend' },
      { status: 500 }
    )
  }
}
