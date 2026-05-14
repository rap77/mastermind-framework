/**
 * Tests for createTask Server Action — C2.07
 *
 * Verifies model_profile is included in the request body sent to the control plane.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock next/headers before importing the module under test
vi.mock('next/headers', () => ({
  cookies: vi.fn().mockResolvedValue({
    get: vi.fn().mockReturnValue({ value: 'test-jwt-token' }),
  }),
}))

// Capture the fetch payload to verify model_profile is sent
const mockFetch = vi.fn()

beforeEach(() => {
  mockFetch.mockReset()
  vi.stubGlobal('fetch', mockFetch)
})

describe('createTask — C2.07 model_profile in request', () => {
  it('sends model_profile=balanced by default', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ task_id: 'task-123' }),
    })

    const { createTask } = await import('../tasks')
    const result = await createTask('This is a brief with enough chars')

    expect(result.success).toBe(true)

    const callArgs = mockFetch.mock.calls[0]
    const body = JSON.parse(callArgs[1].body as string)
    expect(body.model_profile).toBe('balanced')
  })

  it('sends model_profile=quality when specified', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ task_id: 'task-456' }),
    })

    const { createTask } = await import('../tasks')
    const result = await createTask('This is a brief with enough chars', 'quality')

    expect(result.success).toBe(true)

    const callArgs = mockFetch.mock.calls[0]
    const body = JSON.parse(callArgs[1].body as string)
    expect(body.model_profile).toBe('quality')
  })

  it('sends model_profile=budget when specified', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ task_id: 'task-789' }),
    })

    const { createTask } = await import('../tasks')
    await createTask('This is a brief with enough chars', 'budget')

    const callArgs = mockFetch.mock.calls[0]
    const body = JSON.parse(callArgs[1].body as string)
    expect(body.model_profile).toBe('budget')
  })

  it('returns error for brief shorter than 10 chars without calling fetch', async () => {
    const { createTask } = await import('../tasks')
    const result = await createTask('short')

    expect(result.success).toBe(false)
    expect(result.error).toContain('10 characters')
    expect(mockFetch).not.toHaveBeenCalled()
  })
})
