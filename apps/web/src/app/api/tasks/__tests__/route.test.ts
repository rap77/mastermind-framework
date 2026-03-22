/**
 * Server Action Tests: Task Creation
 *
 * **Purpose:** Test POST /api/tasks Server Action with XSS prevention
 * **Context:** Phase 06-03 - Task 3
 *
 * **TDD Phase:** GREEN - Tests passing
 *
 * **Note:** Server Actions run in Node.js environment, so we test validation
 * and sanitization logic directly without mocking fetch
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import DOMPurify from 'dompurify'

// Mock cookies() before importing the route
const mockCookies = vi.fn()
vi.mock('next/headers', () => ({
  cookies: () => mockCookies(),
}))

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

import { createTask } from '@/app/actions/tasks'

describe('createTask Server Action', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    // Default cookies mock
    mockCookies.mockReturnValue({
      get: vi.fn((name: string) => {
        if (name === 'access_token') {
          return { value: 'mock-jwt-token' }
        }
        return undefined
      }),
    })

    // Default fetch mock (success response)
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        task_id: 'test-task-123',
        status: 'pending',
        created_at: new Date().toISOString(),
      }),
    })
  })

  /**
   * Test 1: Returns error message on validation failure (empty)
   */
  it('should return error for empty brief', async () => {
    const result = await createTask('')

    expect(result.success).toBe(false)
    expect(result.error).toContain('Brief is required')
    expect(mockFetch).not.toHaveBeenCalled()
  })

  /**
   * Test 2: Returns error message on validation failure (too short)
   */
  it('should return error for brief < 10 chars', async () => {
    const result = await createTask('short')

    expect(result.success).toBe(false)
    expect(result.error).toContain('at least 10 characters')
    expect(mockFetch).not.toHaveBeenCalled()
  })

  /**
   * Test 3: Server Action creates task via POST to FastAPI
   */
  it('should create task via POST to FastAPI with valid brief', async () => {
    const result = await createTask('Test brief for task creation')

    // Debug output
    if (!result.success) {
      console.log('Error:', result.error)
    }

    expect(result.success).toBe(true)
    expect(result.taskId).toBe('test-task-123')
    expect(mockFetch).toHaveBeenCalledWith(
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
   * Test 4: Returns error when JWT token is missing
   */
  it('should return error when JWT token is missing', async () => {
    mockCookies.mockReturnValue({
      get: vi.fn(() => undefined),
    })

    const result = await createTask('Valid brief with enough length')

    expect(result.success).toBe(false)
    expect(result.error).toContain('Unauthorized')
    expect(mockFetch).not.toHaveBeenCalled()
  })

  /**
   * Test 5: XSS prevention - Sanitizes brief with DOMPurify
   */
  it('should sanitize <script> tags from brief', async () => {
    const maliciousBrief = '<script>alert("XSS")</script>Valid content here'

    await createTask(maliciousBrief)

    const fetchCall = mockFetch.mock.calls[0]
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

    const fetchCall = mockFetch.mock.calls[0]
    const body = JSON.parse(fetchCall[1]?.body as string)

    // Brief should be sanitized (onerror removed)
    expect(body.brief).not.toContain('onerror')
    expect(body.brief).toBe('Valid content')
  })
})
