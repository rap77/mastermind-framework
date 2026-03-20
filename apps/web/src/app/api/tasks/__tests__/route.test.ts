/**
 * Server Action Tests: Task Creation
 *
 * **Purpose:** Test POST /api/tasks Server Action with XSS prevention
 * **Context:** Phase 06-03 - Task 3
 *
 * **TDD Phase:** RED - Tests should fail (Server Action doesn't exist yet)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createTask } from '../route'

// Mock cookies()
vi.mock('next/headers', () => ({
  cookies: vi.fn(() => ({
    get: vi.fn(({ name }) => {
      if (name === 'access_token') {
        return { value: 'mock-jwt-token' }
      }
      return undefined
    }),
  })),
}))

// Mock fetch to call FastAPI
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () =>
      Promise.resolve({
        task_id: 'test-task-123',
        status: 'pending',
        created_at: new Date().toISOString(),
      }),
  }),
) as unknown as typeof fetch

describe('createTask Server Action', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  /**
   * Test 1: Server Action creates task via POST to FastAPI
   */
  it('should create task via POST to FastAPI', async () => {
    const result = await createTask('Test brief for task creation')

    expect(result.success).toBe(true)
    expect(result.taskId).toBe('test-task-123')
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/tasks'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          Authorization: 'Bearer mock-jwt-token',
        }),
      })
    )
  })

  /**
   * Test 2: Returns error message on validation failure
   */
  it('should return error for empty brief', async () => {
    const result = await createTask('')

    expect(result.success).toBe(false)
    expect(result.error).toContain('Brief is required')
  })

  /**
   * Test 3: Returns error message on validation failure (too short)
   */
  it('should return error for brief < 10 chars', async () => {
    const result = await createTask('short')

    expect(result.success).toBe(false)
    expect(result.error).toContain('at least 10 characters')
  })

  /**
   * Test 4: Includes JWT token in request headers
   */
  it('should include JWT token in Authorization header', async () => {
    await createTask('Valid brief with enough length')

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer mock-jwt-token',
        }),
      })
    )
  })

  /**
   * Test 5: XSS prevention - Sanitizes brief with DOMPurify
   */
  it('should sanitize <script> tags from brief', async () => {
    const maliciousBrief = '<script>alert("XSS")</script>Valid content here'

    await createTask(maliciousBrief)

    const fetchCall = (global.fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0]
    const body = JSON.parse(fetchCall[1]?.body as string)

    // Brief should be sanitized (script tags removed)
    expect(body.brief).not.toContain('<script>')
    expect(body.brief).toBe('Valid content here')
  })

  /**
   * Test 6: Stored XSS prevented - Malicious brief stored safely
   */
  it('should remove on* attributes from brief', async () => {
    const maliciousBrief = '<img src=x onerror="alert(1)">Valid content'

    await createTask(maliciousBrief)

    const fetchCall = (global.fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0]
    const body = JSON.parse(fetchCall[1]?.body as string)

    // Brief should be sanitized (onerror removed)
    expect(body.brief).not.toContain('onerror')
    expect(body.brief).toBe('Valid content')
  })
})
