/**
 * GET /api/brains - Proxy to FastAPI brains endpoint
 *
 * **Purpose:** Server-side proxy that adds JWT authentication from httpOnly cookie
 * **Context:** Phase 06 - Command Center
 *
 * **Why proxy?**
 * - Server Components can't read cookies at build time
 * - This route handler runs on server, has access to httpOnly cookies
 * - Adds Authorization header with JWT token before proxying to FastAPI
 *
 * **Flow:**
 * 1. Next.js Server Component calls GET /api/brains
 * 2. This route handler reads access_token from httpOnly cookie
 * 3. Proxies to FastAPI with Authorization header
 * 4. Returns brains data to Server Component
 */

import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET(request: NextRequest) {
  const apiUrl = process.env.API_URL || 'http://localhost:8000'

  // CRITICAL: Get JWT token from httpOnly cookie
  const cookieStore = await cookies()  // CRITICAL: await in Next.js 16
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    return NextResponse.json(
      { error: 'Unauthorized - No token found' },
      { status: 401 }
    )
  }

  // Get query params for pagination
  const searchParams = request.nextUrl.searchParams
  const page = searchParams.get('page') || '1'
  const page_size = searchParams.get('page_size') || '24'

  // Proxy to FastAPI with Authorization header
  const url = `${apiUrl}/api/brains?page=${page}&page_size=${page_size}`

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      // No caching - always get fresh data from backend
      cache: 'no-store',
    })

    if (!response.ok) {
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
    console.error('Brains proxy error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch brains from backend' },
      { status: 500 }
    )
  }
}
