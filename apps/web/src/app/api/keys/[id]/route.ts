/**
 * DELETE /api/keys/[id] — Revoke an API key (soft-delete)
 *
 * Proxy to FastAPI DELETE /api/keys/{id} with JWT from httpOnly cookie.
 *
 * Fix: ER-02 — KeyListTable calls DELETE /api/keys/{id} but this route didn't exist
 */

import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'

export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const apiUrl = process.env.API_URL || 'http://localhost:8001'
  const { id: keyId } = await params  // CRITICAL: await params in Next.js 16

  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized - No token found' }, { status: 401 })
  }

  try {
    const response = await fetch(`${apiUrl}/api/keys/${keyId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      if (response.status === 401) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
      if (response.status === 404) return NextResponse.json({ error: 'API key not found' }, { status: 404 })
      if (response.status === 403) return NextResponse.json({ error: 'Access denied' }, { status: 403 })
      return NextResponse.json({ error: `Backend error: ${response.status}` }, { status: response.status })
    }

    return NextResponse.json(await response.json())
  } catch (error) {
    console.error('Keys proxy DELETE error:', error)
    return NextResponse.json({ error: 'Failed to revoke API key' }, { status: 500 })
  }
}
