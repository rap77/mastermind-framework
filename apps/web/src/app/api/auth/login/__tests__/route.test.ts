import { POST } from '../route'
import { vi, beforeEach, describe, it, expect } from 'vitest'

// Mock fetch
global.fetch = vi.fn() as unknown as typeof fetch

describe('POST /api/auth/login', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    process.env.AGENT_RUNTIME_URL = 'http://localhost:8001'
  })

  it('should successfully login and set cookies', async () => {
    const mockResponse = {
      access_token: 'test_access_token',
      refresh_token: 'test_refresh_token',
      token_type: 'Bearer',
      expires_in: 1800,
    }

    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as Response)

    const request = new Request('http://localhost:3001/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username: 'admin', password: 'password' }),
    })

    const response = await POST(request)
    const data = await response.json()

    expect(response.status).toBe(200)
    expect(data.success).toBe(true)
    expect(data.redirect).toBe('/command-center')

    // Verify cookies are set
    const cookies = response.cookies.getAll()
    expect(cookies).toHaveLength(2)
    expect(cookies.find((c) => c.name === 'access_token')?.value).toBe('test_access_token')
    expect(cookies.find((c) => c.name === 'refresh_token')?.value).toBe('test_refresh_token')
  })

  it('should return 400 for invalid input', async () => {
    const request = new Request('http://localhost:3001/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username: '', password: '' }),
    })

    const response = await POST(request)
    const data = await response.json()

    expect(response.status).toBe(400)
    expect(data.error).toBe('Invalid input')
  })

  it('should return 401 for invalid credentials', async () => {
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ error: 'Invalid credentials' }),
    } as Response)

    const request = new Request('http://localhost:3001/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username: 'admin', password: 'wrong' }),
    })

    const response = await POST(request)
    const data = await response.json()

    expect(response.status).toBe(401)
    expect(data.error).toBe('Invalid credentials')
  })
})
