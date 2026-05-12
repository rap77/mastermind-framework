import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

describe('apiFetch()', () => {
  let fetchSpy: ReturnType<typeof vi.spyOn>

  beforeEach(() => {
    fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('{}', { status: 200 })
    )
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('adds X-Trace-ID header to every request', async () => {
    const { apiFetch } = await import('../api-client')
    await apiFetch('/api/test')

    expect(fetchSpy).toHaveBeenCalledOnce()
    const [, init] = fetchSpy.mock.calls[0]
    const headers = new Headers(init?.headers as HeadersInit)
    const traceId = headers.get('x-trace-id')

    expect(traceId).not.toBeNull()
    expect(typeof traceId).toBe('string')
    expect(UUID_REGEX.test(traceId!)).toBe(true)
  })

  it('X-Trace-ID is a valid UUID v4 (36 chars)', async () => {
    const { apiFetch } = await import('../api-client')
    await apiFetch('/api/test')

    const [, init] = fetchSpy.mock.calls[0]
    const headers = new Headers(init?.headers as HeadersInit)
    const traceId = headers.get('x-trace-id')

    expect(traceId).toHaveLength(36)
  })

  it('merges caller headers without dropping them', async () => {
    const { apiFetch } = await import('../api-client')
    await apiFetch('/api/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer token123',
      },
    })

    const [, init] = fetchSpy.mock.calls[0]
    const headers = new Headers(init?.headers as HeadersInit)

    expect(headers.get('content-type')).toBe('application/json')
    expect(headers.get('authorization')).toBe('Bearer token123')
    expect(headers.get('x-trace-id')).not.toBeNull()
  })

  it('passes through method and body from init', async () => {
    const { apiFetch } = await import('../api-client')
    await apiFetch('/api/test', {
      method: 'POST',
      body: JSON.stringify({ key: 'value' }),
    })

    const [url, init] = fetchSpy.mock.calls[0]
    expect(url).toBe('/api/test')
    expect(init?.method).toBe('POST')
    expect(init?.body).toBe(JSON.stringify({ key: 'value' }))
  })

  it('generates a different X-Trace-ID on each call', async () => {
    const { apiFetch } = await import('../api-client')
    await apiFetch('/api/a')
    await apiFetch('/api/b')

    const [, init1] = fetchSpy.mock.calls[0]
    const [, init2] = fetchSpy.mock.calls[1]
    const id1 = new Headers(init1?.headers as HeadersInit).get('x-trace-id')
    const id2 = new Headers(init2?.headers as HeadersInit).get('x-trace-id')

    expect(id1).not.toBe(id2)
  })
})
