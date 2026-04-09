import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

const LoginRequestSchema = z.object({
  username: z.string().min(1).max(100),
  password: z.string().min(1).max(100),
})

const TokenResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string().default('Bearer'),
  expires_in: z.number().default(1800),
})

/**
 * API Route for user authentication.
 * Proxies login requests to the backend API and sets httpOnly cookies.
 *
 * This replaces Server Actions to work correctly in Next.js 16 standalone mode.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const validated = LoginRequestSchema.safeParse(body)
    if (!validated.success) {
      return NextResponse.json(
        { error: 'Invalid input', details: validated.error.issues },
        { status: 400 }
      )
    }

    const apiUrl = process.env.AGENT_RUNTIME_URL || 'http://localhost:8001'

    // Logging happens on backend side; Next.js API route is a thin proxy

    const response = await fetch(`${apiUrl}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(validated.data),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Invalid credentials' }))
      return NextResponse.json(
        { error: errorData.error || 'Invalid credentials' },
        { status: response.status }
      )
    }

    const data = await response.json()

    const parsed = TokenResponseSchema.safeParse(data)
    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid server response' },
        { status: 500 }
      )
    }

    // Create JSON response (not redirect) - client will handle navigation
    const res = NextResponse.json(
      { success: true, redirect: '/command-center' },
      { status: 200 }
    )

    // Set httpOnly cookies
    res.cookies.set('access_token', parsed.data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: parsed.data.expires_in,
      path: '/',
    })

    res.cookies.set('refresh_token', parsed.data.refresh_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 86400, // 24h
      path: '/',
    })

    return res
  } catch (error) {
    return NextResponse.json(
      { error: 'Login failed. Please try again.' },
      { status: 500 }
    )
  }
}
