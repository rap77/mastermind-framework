import { NextRequest, NextResponse } from 'next/server'

export interface Thread {
  id: string
  channel: 'whatsapp' | 'instagram' | 'email'
  subject: string
  preview: string
  timestamp: number
  unread: boolean
  status: string
}

/**
 * GET /api/messages - Fetch threads for unified inbox
 *
 * Query params:
 * - channel: 'all' | 'whatsapp' | 'instagram' | 'email' (default: 'all')
 * - limit: number of threads to return (default: 100)
 * - offset: pagination offset (default: 0)
 *
 * Returns: Array of Thread objects
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const channel = searchParams.get('channel') || 'all'
    const limit = parseInt(searchParams.get('limit') || '100')
    const offset = parseInt(searchParams.get('offset') || '0')

    // TODO: Replace with actual backend API call
    // For now, generate mock data
    const mockThreads: Thread[] = Array.from({ length: 1000 }, (_, i) => ({
      id: `thread-${i}`,
      channel: ['whatsapp', 'instagram', 'email'][i % 3] as Thread['channel'],
      subject: `Test Thread ${i + 1}`,
      preview: `This is a preview message for thread ${i + 1}...`,
      timestamp: Date.now() - i * 60000, // 1 minute apart
      unread: i % 5 === 0,
      status: 'active',
    }))

    // Filter by channel
    let filtered = channel === 'all'
      ? mockThreads
      : mockThreads.filter((t) => t.channel === channel)

    // Sort by timestamp descending
    filtered = filtered.sort((a, b) => b.timestamp - a.timestamp)

    // Apply pagination
    const paginated = filtered.slice(offset, offset + limit)

    return NextResponse.json(paginated, {
      headers: {
        'Cache-Control': 'private, max-age=30',
        'X-Total-Count': filtered.length.toString(),
      },
    })
  } catch (error) {
    console.error('Error fetching messages:', error)
    return NextResponse.json(
      { error: 'Failed to fetch messages' },
      { status: 500 }
    )
  }
}
