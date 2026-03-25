/**
 * GET /api/keys  — List active API keys (masked)
 * POST /api/keys — Create API key (show-once full key in response)
 *
 * Proxy to FastAPI /api/keys with JWT from httpOnly cookie.
 * Same pattern as /api/brains/route.ts.
 *
 * Fix: ER-02 — APIKeyManager called this route but it didn't exist (404)
 */

import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

async function getToken(): Promise<string | null> {
  const cookieStore = await cookies()
  return cookieStore.get('access_token')?.value ?? null
}

function unauthorized() {
  return NextResponse.json({ error: 'Unauthorized - No token found' }, { status: 401 })
}

export async function GET() {
  const apiUrl = process.env.API_URL || 'http://localhost:8001'
  const token = await getToken()
  if (!token) return unauthorized()

  try {
    const response = await fetch(`${apiUrl}/api/keys`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      if (response.status === 401) return unauthorized()
      return NextResponse.json({ error: `Backend error: ${response.status}` }, { status: response.status })
    }

    return NextResponse.json(await response.json())
  } catch (error) {
    console.error('Keys proxy GET error:', error)
    return NextResponse.json({ error: 'Failed to fetch API keys' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  const apiUrl = process.env.API_URL || 'http://localhost:8001'
  const token = await getToken()
  if (!token) return unauthorized()

  try {
    const body = await request.text()

    const response = await fetch(`${apiUrl}/api/keys`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: body || '{}',
      cache: 'no-store',
    })

    if (!response.ok) {
      if (response.status === 401) return unauthorized()
      return NextResponse.json({ error: `Backend error: ${response.status}` }, { status: response.status })
    }

    return NextResponse.json(await response.json(), { status: 201 })
  } catch (error) {
    console.error('Keys proxy POST error:', error)
    return NextResponse.json({ error: 'Failed to create API key' }, { status: 500 })
  }
}
