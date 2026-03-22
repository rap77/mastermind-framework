/**
 * GET /api/brains/[id] - Proxy to FastAPI single brain endpoint
 *
 * **Purpose:** Server-side proxy for individual brain details
 * **Context:** Phase 07 - The Nexus (brain detail views)
 *
 * **Flow:**
 * 1. Next.js Server Component calls GET /api/brains/brain-01
 * 2. This route handler reads access_token from httpOnly cookie
 * 3. Proxies to FastAPI with Authorization header
 * 4. Returns brain data to Server Component
 */

import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const apiUrl = process.env.API_URL || 'http://localhost:8001'
  const { id: brainId } = await params  // CRITICAL: await params in Next.js 16

  // CRITICAL: Get JWT token from httpOnly cookie
  const cookieStore = await cookies()  // CRITICAL: await in Next.js 16
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    return NextResponse.json(
      { error: 'Unauthorized - No token found' },
      { status: 401 }
    )
  }

  // Proxy to FastAPI with Authorization header
  const url = `${apiUrl}/api/brains/${brainId}`

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
          { error: `Brain not found: ${brainId}` },
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
    console.error('Brain proxy error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch brain from backend' },
      { status: 500 }
    )
  }
}
