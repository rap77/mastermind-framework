/**
 * GET /api/brains/[id]/yaml — Proxy to FastAPI brain YAML config endpoint
 *
 * Returns brain configuration as YAML text (not JSON).
 * Used by BrainYAMLViewer component for display + copy-to-clipboard.
 *
 * Fix: ER-03 — BrainYAMLViewer fetched this route but it didn't exist
 */

import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const apiUrl = process.env.API_URL || 'http://localhost:8001'
  const { id: brainId } = await params  // CRITICAL: await params in Next.js 16

  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized - No token found' }, { status: 401 })
  }

  try {
    const response = await fetch(`${apiUrl}/api/brains/${brainId}/yaml`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      if (response.status === 401) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
      if (response.status === 404) return NextResponse.json({ error: `Brain not found: ${brainId}` }, { status: 404 })
      return NextResponse.json({ error: `Backend error: ${response.status}` }, { status: response.status })
    }

    const yaml = await response.text()
    return new NextResponse(yaml, {
      status: 200,
      headers: { 'Content-Type': 'application/yaml' },
    })
  } catch (error) {
    console.error('Brain YAML proxy error:', error)
    return NextResponse.json({ error: 'Failed to fetch brain YAML' }, { status: 500 })
  }
}
